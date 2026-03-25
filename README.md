# HealthScheduler

Simple Python implementation of the assignment resource allocator.

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

## Scripts

- `python scripts/generate_activities.py`
  Generates the saved activity catalog in `data/inputs/activities/`.
- `python scripts/generate_constraints.py`
  Generates the saved scheduling constraints in `data/inputs/constraints/`.
- `python scripts/select_action_plan.py`
  Randomly selects a smaller action plan from the saved activity catalog into `data/inputs/action_plans/`.
- `python scripts/main.py`
  Reads the saved catalog, constraints, and action plan, then schedules the plan and exports results.

## Outputs

- `data/inputs/activities/activity_catalog.json`
- `data/inputs/activities/activity_catalog.csv`
- `data/inputs/action_plans/action_plan.json`
- `data/inputs/action_plans/action_plan.csv`
- `data/inputs/constraints/client_schedule.csv`
- `data/inputs/constraints/travel_plans.csv`
- `data/inputs/constraints/specialists.csv`
- `data/inputs/constraints/allied_health.csv`
- `data/inputs/constraints/equipment.csv`
- `data/inputs/constraints/constraints_bundle.json`
- `data/outputs/scheduled_plan.csv`
- `data/outputs/unscheduled_plan.csv`
- `data/outputs/schedule_bundle.json`
- `data/outputs/personalized_plan.html`
- `data/outputs/personalized_plan.ics`

## Notes

- The data is synthetic and intended only for assignment testing.
- The scheduler is deterministic and heuristic-based rather than solver-based.
- The implementation uses only the Python standard library.
