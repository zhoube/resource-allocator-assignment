# HealthScheduler

Simple Python implementation of the assignment resource allocator.

## Scripts

- `python src/generate_activities.py`
  Generates the saved activity catalog in `data/activities/`.
- `python src/generate_constraints.py`
  Generates the saved scheduling constraints in `data/constraints/`.
- `python src/select_action_plan.py`
  Randomly selects a smaller action plan from the saved activity catalog into `data/action_plans/`.
- `python src/main.py`
  Reads the saved catalog, constraints, and action plan, then schedules the plan and exports results.

## Outputs

- `data/activities/activity_catalog.json`
- `data/activities/activity_catalog.csv`
- `data/action_plans/action_plan.json`
- `data/action_plans/action_plan.csv`
- `data/constraints/client_schedule.csv`
- `data/constraints/travel_plans.csv`
- `data/constraints/specialists.csv`
- `data/constraints/allied_health.csv`
- `data/constraints/equipment.csv`
- `data/constraints/constraints_bundle.json`
- `output/scheduled_plan.csv`
- `output/unscheduled_plan.csv`
- `output/schedule_bundle.json`
- `output/personalized_plan.html`
- `output/personalized_plan.ics`

## Notes

- The data is synthetic and intended only for assignment testing.
- The scheduler is deterministic and heuristic-based rather than solver-based.
- The implementation uses only the Python standard library.
