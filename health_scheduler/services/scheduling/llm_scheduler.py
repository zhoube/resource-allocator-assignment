from __future__ import annotations

import json
import os
from typing import Any
from urllib import error, request

from health_scheduler.config.settings import (
    OPENAI_API_BASE,
    OPENAI_MODEL,
    OPENAI_REASONING_EFFORT,
    OPENAI_TIMEOUT_RETRY_REASONING_EFFORT,
    OPENAI_TIMEOUT_SECONDS,
)
from health_scheduler.services.scheduling.schedule_parser import SCHEDULE_RESPONSE_SCHEMA
from health_scheduler.services.scheduling.scheduler_prompt import SCHEDULER_PROMPT_TEMPLATE


class OpenAISchedulingAgent:
    def __init__(
        self,
        api_key: str | None = None,
        model: str = OPENAI_MODEL,
        base_url: str = OPENAI_API_BASE,
        reasoning_effort: str = OPENAI_REASONING_EFFORT,
        timeout_seconds: int = OPENAI_TIMEOUT_SECONDS,
        timeout_retry_reasoning_effort: str = OPENAI_TIMEOUT_RETRY_REASONING_EFFORT,
    ) -> None:
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "")
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.reasoning_effort = reasoning_effort
        self.timeout_seconds = timeout_seconds
        self.timeout_retry_reasoning_effort = timeout_retry_reasoning_effort
        if not self.api_key:
            raise RuntimeError("OPENAI_API_KEY is required to run the LLM scheduler.")

    def request_schedule(self, activities_payload: list[dict], constraints_payload: dict) -> str:
        prompt = SCHEDULER_PROMPT_TEMPLATE.format(
            activities=json.dumps(activities_payload, indent=2),
            planning_window=self._format_prompt_section(constraints_payload.get("planning_window", {})),
            client_availability=self._format_prompt_section(constraints_payload.get("client_availability", [])),
            travel_plans=self._format_prompt_section(constraints_payload.get("travel_plans", [])),
            specialists=self._format_prompt_section(constraints_payload.get("specialists", [])),
            allied_health=self._format_prompt_section(constraints_payload.get("allied_health", [])),
            equipment=self._format_prompt_section(constraints_payload.get("equipment", [])),
        )
        print(f"      Prompt payload prepared with {len(activities_payload)} activities and {len(prompt):,} characters.")
        return self._request_json_response(prompt, SCHEDULE_RESPONSE_SCHEMA)

    def _format_prompt_section(self, value: Any) -> str:
        if isinstance(value, list) and all(isinstance(item, str) for item in value):
            return "\n\n".join(value) if value else "[]"
        return json.dumps(value, indent=2)

    def _request_json_response(self, prompt: str, schema: dict[str, Any]) -> str:
        attempts = self._build_attempts(schema)
        failures: list[str] = []
        for attempt_index, (attempt_schema, attempt_effort) in enumerate(attempts, start=1):
            schema_mode = "structured" if attempt_schema is not None else "unstructured"
            try:
                payload = self._build_payload(prompt, attempt_schema, attempt_effort)
                response = self._post(payload, attempt_index, len(attempts), schema_mode, attempt_effort)
                output_text = self._extract_output_text(response)
                if not output_text:
                    failures.append(f"attempt {attempt_index}: response contained no text output")
                    continue
                return output_text
            except error.HTTPError as exc:
                failures.append(self._describe_http_error(attempt_index, schema_mode, attempt_effort, exc))
                continue
            except TimeoutError:
                failures.append(
                    f"attempt {attempt_index} ({schema_mode}, reasoning={attempt_effort}) timed out after {self.timeout_seconds}s"
                )
                continue
            except error.URLError as exc:
                if isinstance(exc.reason, TimeoutError):
                    failures.append(
                        f"attempt {attempt_index} ({schema_mode}, reasoning={attempt_effort}) timed out after {self.timeout_seconds}s"
                    )
                else:
                    failures.append(
                        f"attempt {attempt_index} ({schema_mode}, reasoning={attempt_effort}) failed with URL error: {exc.reason}"
                    )
                continue
        raise RuntimeError(
            "OpenAI scheduling request failed after all retries. "
            + " | ".join(failures)
        )

    def _build_payload(self, prompt: str, schema: dict[str, Any] | None, reasoning_effort: str) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "model": self.model,
            "reasoning": {"effort": reasoning_effort},
            "input": [
                {
                    "role": "user",
                    "content": [{"type": "input_text", "text": prompt}],
                }
            ],
        }
        if schema is not None:
            payload["text"] = {
                "format": {
                    "type": "json_schema",
                    "name": "schedule_response",
                    "schema": schema,
                    "strict": True,
                }
            }
        return payload

    def _build_attempts(self, schema: dict[str, Any] | None) -> list[tuple[dict[str, Any] | None, str]]:
        attempts: list[tuple[dict[str, Any] | None, str]] = []

        def add_attempt(attempt_schema: dict[str, Any] | None, effort: str) -> None:
            pair = (attempt_schema, effort)
            if pair not in attempts:
                attempts.append(pair)

        add_attempt(schema, self.reasoning_effort)
        if self.timeout_retry_reasoning_effort:
            add_attempt(schema, self.timeout_retry_reasoning_effort)
        if schema is not None:
            add_attempt(None, self.reasoning_effort)
            if self.timeout_retry_reasoning_effort:
                add_attempt(None, self.timeout_retry_reasoning_effort)
        return attempts

    def _post(
        self,
        payload: dict[str, Any],
        attempt_index: int,
        attempt_count: int,
        schema_mode: str,
        reasoning_effort: str,
    ) -> dict[str, Any]:
        body = json.dumps(payload).encode("utf-8")
        http_request = request.Request(
            f"{self.base_url}/responses",
            data=body,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        print(
            f"      Calling OpenAI model `{self.model}` "
            f"(attempt {attempt_index}/{attempt_count}, {schema_mode}, reasoning={reasoning_effort}, timeout={self.timeout_seconds}s)..."
        )
        with request.urlopen(http_request, timeout=self.timeout_seconds) as handle:
            return json.loads(handle.read().decode("utf-8"))

    def _describe_http_error(
        self,
        attempt_index: int,
        schema_mode: str,
        reasoning_effort: str,
        exc: error.HTTPError,
    ) -> str:
        response_body = ""
        try:
            response_body = exc.read().decode("utf-8", errors="replace").strip()
        except Exception:
            response_body = ""
        details = f"attempt {attempt_index} ({schema_mode}, reasoning={reasoning_effort}) failed with HTTP {exc.code}"
        if response_body:
            details += f": {response_body}"
        return details

    def _extract_output_text(self, payload: dict[str, Any]) -> str:
        direct = payload.get("output_text")
        if isinstance(direct, str) and direct.strip():
            return direct.strip()
        outputs = payload.get("output", [])
        for item in outputs:
            for content in item.get("content", []):
                if content.get("type") == "output_text":
                    text = content.get("text", "")
                    if isinstance(text, str) and text.strip():
                        return text.strip()
        return ""
