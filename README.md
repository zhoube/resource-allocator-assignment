# HealthScheduler

Python implementation of the assignment resource allocator. The project generates a synthetic health activity catalog, generates synthetic scheduling constraints, selects a smaller action plan, then asks an OpenAI model to propose a schedule. Deterministic code validates the proposal and exports the final results.

## Structure

- `docs/assignment/`
  Assignment reference files and supporting images.
- `data/inputs/`
  Saved activity catalog, constraints, and action plans.
- `data/outputs/`
  Generated schedules and calendar exports.
- `scripts/`
  Runnable entry scripts.
- `health_scheduler/`
  Package code split into `domain`, `services`, `io`, `config`, `utils`, and `cli`.

## Code Architecture

- `health_scheduler/domain/activities/`
  Core activity entities. `Activity` is the base class, `Frequency` captures recurrence, and the category subclasses represent fitness, food, medication, therapy, and consultation activities.
- `health_scheduler/domain/constraints/`
  Constraint source definitions used to generate the saved CSV inputs. These classes define the recurring client availability, travel plans, provider availability, and equipment availability.
- `health_scheduler/domain/scheduling/`
  Scheduling entities such as `ScheduledEvent`. This is the normalized output model used by validation and export.
- `health_scheduler/services/generation/`
  Synthetic data generation logic. This layer creates random activity definitions, builds the catalog, builds the action plan, and generates the saved constraint files.
- `health_scheduler/services/scheduling/`
  Runtime scheduling logic. This is the most important layer for the live run:
  - `scheduler.py`: orchestration
  - `scheduler_prompt.py`: the single prompt template
  - `llm_scheduler.py`: one OpenAI API call
  - `schedule_parser.py`: parse the LLM JSON response
  - `schedule_validator.py`: deterministic validation against constraints
  - `occurrence_builder.py`: legacy frequency-expansion helper that is no longer part of the live validation path
- `health_scheduler/io/storage/`
  JSON and CSV file reading/writing helpers.
- `health_scheduler/io/exporters/`
  Exporters for CSV, JSON, HTML, and ICS schedule outputs.
- `health_scheduler/config/`
  Project paths, settings, and `.env` loading.
- `health_scheduler/utils/`
  Shared datetime utilities.
- `health_scheduler/cli/`
  Real entrypoints used by the thin `scripts/` wrappers.

## Code Flow

The project has four main stages:

1. Generate the activity catalog.
   - `python scripts/generate_activities.py`
   - Calls [generate_activities.py](C:/Users/Kelvin/Desktop/HealthScheduler/health_scheduler/cli/generate_activities.py), which uses [activity_catalog_builder.py](C:/Users/Kelvin/Desktop/HealthScheduler/health_scheduler/services/generation/activity_catalog_builder.py) and [activity_generator.py](C:/Users/Kelvin/Desktop/HealthScheduler/health_scheduler/services/generation/activity_generator.py).
   - Output: a full catalog of synthetic activities saved to JSON and CSV.

2. Generate the scheduling constraints.
   - `python scripts/generate_constraints.py`
   - Calls [generate_constraints.py](C:/Users/Kelvin/Desktop/HealthScheduler/health_scheduler/cli/generate_constraints.py), which uses [constraints_builder.py](C:/Users/Kelvin/Desktop/HealthScheduler/health_scheduler/services/generation/constraints_builder.py).
   - Output: saved CSV inputs for client availability, travel plans, specialists, allied health, and equipment.
   - Important: these CSVs now store recurring availability templates such as weekday patterns and available time ranges, instead of one row per day.

3. Select an action plan.
   - `python scripts/select_action_plan.py --plan-size X`
   - Calls [select_action_plan.py](C:/Users/Kelvin/Desktop/HealthScheduler/health_scheduler/cli/select_action_plan.py), which reads the saved catalog and uses [action_plan_builder.py](C:/Users/Kelvin/Desktop/HealthScheduler/health_scheduler/services/generation/action_plan_builder.py).
   - Output: a smaller subset of activities to schedule.

4. Run the scheduler.
   - `python scripts/main.py`
   - Calls [main.py](C:/Users/Kelvin/Desktop/HealthScheduler/health_scheduler/cli/main.py), which:
     - loads the saved catalog, action plan, and constraint CSVs
     - parses activities into objects
     - builds the prompt payload
     - sends one scheduling request through [llm_scheduler.py](C:/Users/Kelvin/Desktop/HealthScheduler/health_scheduler/services/scheduling/llm_scheduler.py)
     - parses the model response with [schedule_parser.py](C:/Users/Kelvin/Desktop/HealthScheduler/health_scheduler/services/scheduling/schedule_parser.py)
     - validates each proposed event with [schedule_validator.py](C:/Users/Kelvin/Desktop/HealthScheduler/health_scheduler/services/scheduling/schedule_validator.py)
     - exports final results through [calendar_exporter.py](C:/Users/Kelvin/Desktop/HealthScheduler/health_scheduler/io/exporters/calendar_exporter.py)

The current live validation logic is intentionally simple:
- it checks that proposed events do not clash with each other
- it checks client availability
- it checks travel rules
- it checks required providers
- it checks required equipment
- it does not currently enforce full frequency coverage

## Scripts

- `python scripts/generate_activities.py`
  Generates the saved activity catalog in `data/inputs/activities/`.
- `python scripts/generate_constraints.py`
  Generates the saved scheduling constraints in `data/inputs/constraints/`.
- `python scripts/select_action_plan.py`
  Randomly selects a smaller action plan from the saved activity catalog into `data/inputs/action_plans/`.
- `python scripts/main.py`
  Reads the saved catalog, constraints, and action plan, then schedules the plan and exports results.

## LLM Scheduler

- Only scheduling is done by the LLM.
- Data generation, parsing, validation, and export remain deterministic code.
- Put your local settings in [`.env`](C:/Users/Kelvin/Desktop/HealthScheduler/.env) before running `python scripts/main.py`.
- A checked-in template is available at [`.env.example`](C:/Users/Kelvin/Desktop/HealthScheduler/.env.example).
- Default model: `gpt-5.4`
- Useful overrides:
  - `HEALTH_SCHEDULER_OPENAI_MODEL`
  - `HEALTH_SCHEDULER_OPENAI_BASE_URL`
  - `HEALTH_SCHEDULER_OPENAI_REASONING_EFFORT`

## Input Files

These are the files the scheduler reads from `data/inputs/`.

- `data/inputs/activities/activity_catalog.json`
  Full activity catalog in JSON. This is the main structured source for activity parsing.
- `data/inputs/activities/activity_catalog.csv`
  Spreadsheet-friendly copy of the same catalog.
- `data/inputs/action_plans/action_plan.json`
  The selected subset of activities to schedule.
- `data/inputs/action_plans/action_plan.csv`
  Spreadsheet-friendly copy of the selected action plan.
- `data/inputs/constraints/client_schedule.csv`
  Client availability templates. Each row describes either a recurring weekday availability pattern or a date-specific override.
- `data/inputs/constraints/travel_plans.csv`
  Travel windows with destination, time range, and `remote_only` flag.
- `data/inputs/constraints/specialists.csv`
  One row per specialist. Each row stores role, location, remote support, weekday pattern, and available time ranges.
- `data/inputs/constraints/allied_health.csv`
  One row per allied health provider. Same template-style format as specialists.
- `data/inputs/constraints/equipment.csv`
  One row per equipment resource. Stores equipment type, location, weekday pattern, and available time ranges.
- `data/inputs/constraints/constraints_bundle.json`
  JSON bundle of the generated constraints for inspection/debugging.

## Output Files

These are the files produced in `data/outputs/` after running `python scripts/main.py`.

- `data/outputs/scheduled_plan.csv`
  Accepted scheduled events after deterministic validation.
- `data/outputs/unscheduled_plan.csv`
  Proposed events that were rejected, with the rejection reason.
- `data/outputs/schedule_bundle.json`
  Combined machine-readable output containing both scheduled and unscheduled items.
- `data/outputs/personalized_plan.html`
  Human-readable schedule report.
- `data/outputs/personalized_plan.ics`
  Calendar export for import into calendar apps.

## Notes

- The data is synthetic and intended only for assignment testing.
- The scheduler makes one OpenAI call for the full schedule request, then validates and exports the result.
- The implementation still uses only the Python standard library for HTTP, parsing, validation, and export.
