from __future__ import annotations

import json
import os
from typing import Any
from urllib import error, request

from health_scheduler.config.settings import OPENAI_API_BASE, OPENAI_MODEL, OPENAI_REASONING_EFFORT
from health_scheduler.services.scheduling.schedule_parser import SCHEDULE_RESPONSE_SCHEMA
from health_scheduler.services.scheduling.scheduler_prompt import SCHEDULER_PROMPT_TEMPLATE


class OpenAISchedulingAgent:
    def __init__(
        self,
        api_key: str | None = None,
        model: str = OPENAI_MODEL,
        base_url: str = OPENAI_API_BASE,
        reasoning_effort: str = OPENAI_REASONING_EFFORT,
    ) -> None:
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "")
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.reasoning_effort = reasoning_effort
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
        try:
            payload = self._build_payload(prompt, schema)
            response = self._post(payload)
        except error.HTTPError:
            fallback_payload = self._build_payload(prompt, None)
            response = self._post(fallback_payload)
        output_text = self._extract_output_text(response)
        if not output_text:
            raise RuntimeError("OpenAI response did not contain any text output.")
        return output_text

    def _build_payload(self, prompt: str, schema: dict[str, Any] | None) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "model": self.model,
            "reasoning": {"effort": self.reasoning_effort},
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

    def _post(self, payload: dict[str, Any]) -> dict[str, Any]:
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
        print(f"      Calling OpenAI model `{self.model}`...")
        with request.urlopen(http_request, timeout=240) as handle:
            return json.loads(handle.read().decode("utf-8"))

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
