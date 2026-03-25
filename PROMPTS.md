# Codex Thread Prompt Log

This file records the user prompts from this Codex thread in order.

## Prompt 1
> What approach should we do for this assignment

## Prompt 2
> Lets get started on making the scripts then!

## Prompt 3
> lets use proper OOP concepts, make a Activity class, and then have the different types of activities all inherit from the Activity class, then we can define functions to parse and create each activity

## Prompt 4
> is using CATALOG the best way to generate activities? it should use RNG to decide what activity to generate, then use activity_model to generate the corresponding activity. there shouldnt be a long list of pre generated activity inside generate_data

## Prompt 5
> SPECIALIST_RESOURCES, ALLIED_HEALTH_RESOURCES, EQUIPMENT_RESOURCES, TRAVEL_PLAN_BLUEPRINTS
>
> all of these should be its own class, and all the code to generate them should be put there

## Prompt 6
> no, move each of them into its own class, own file, not all together in actitivy

## Prompt 7
```python
SPECIALIST_ROLES = {
    "primary_care_physician",
    "endocrinologist",
    "cardiologist",
    "sleep_physician",
    "sports_physician",
    "lab_technician",
    "ophthalmologist",
}

ALLIED_HEALTH_ROLES = {
    "physiotherapist",
    "dietitian",
    "exercise_physiologist",
    "health_coach",
    "occupational_therapist",
    "speech_therapist",
    "strength_coach",
}

TRAVEL_FRIENDLY_LOCATIONS = {"park", "office", "travel"}

ACTIVITY_FIELDNAMES = [
    "id",
    "title",
    "category",
    "priority",
    "duration_minutes",
    "details",
    "frequency",
    "facilitator_role",
    "resource_pool",
    "location",
    "remote_allowed",
    "equipment_required",
    "prep_required",
    "backup_activity_ids",
    "skip_adjustment",
    "metrics",
    "preferred_time_windows",
]

TITLE_SUFFIXES = {
    "Fitness routine / exercise": ["Aerobic Base", "Mobility Reset", "Core Stability", "Recovery Focus", "Joint Care"],
    "Food consumption": ["Metabolic Support", "Recovery Plate", "Energy Stabilizer", "Protein Rebuild", "Gut Support"],
    "Medication consumption": ["Daily Adherence", "Travel-Safe Pack", "Morning Routine", "Evening Routine", "Maintenance Cycle"],
    "Therapy": ["Recovery Session", "Inflammation Support", "Stress Reset", "Sleep Support", "Circulation Boost"],
    "Consultation": ["Progress Review", "Check-In", "Plan Tuning", "Quarterly Review", "Follow-Up"],
}
```

> why is this in actvity models? these constants should be defined as enum in a enum folder

## Prompt 8
> stop all pipeline runs, and dont run them unless i say so

## Prompt 9
> the resources class should be a resources file, and shnould use the enums defined when ceeating them

## Prompt 10
```python
CATEGORY_TARGETS = {
    "Fitness routine / exercise": 35,
    "Food consumption": 25,
    "Medication consumption": 20,
    "Therapy": 20,
    "Consultation": 20,
}
```

> this should use the enums too

## Prompt 11
> all these
>
> random_fitness_seed
> random_food_seed
> random_medication_seed
> random_therapy_seed
> random_consultation_seed
>
> why cant we just create the activity object here, instead of putting it in a json and then create them after, why not just do it here after its chosen by rng

## Prompt 12
> ok now walk me through the flow when generate_activities is called

## Prompt 13
> why isnt the random_xxx_activity using the Frequency class?

## Prompt 14
> yes, lets do that

## Prompt 15
> so run through the generate_client_schedule flow

## Prompt 16
```python
    travel_plans = TravelPlanBlueprint.generate_rows(start_date)
    specialists = SpecialistResource.generate_rows(start_date, end_date, rng)
    allied_health = AlliedHealthResource.generate_rows(start_date, end_date, rng)
    equipment = EquipmentResource.generate_rows(start_date, end_date, rng)
```

> so what about these 3

## Prompt 17
> so how does the schedular logic work

## Prompt 18
> what does try_place mean and do

## Prompt 19
> if an occurance includes an activity, why not just save the activity within an Occurance object, then we dont have to pass activity and occurance

## Prompt 20
> lets do that

## Prompt 21
> rename try_place to something that is more explanatory

## Prompt 22
```python
{"event_id": occurrence.occurrence_id, "activity_id": activity.id, "activity_title": activity.title, "category": activity.category, "priority": activity.priority, "start": candidate_start.isoformat(), "end": candidate_end.isoformat(), "duration_minutes": activity.duration_minutes, "location": location, "mode": mode, "assigned_provider": provider, "assigned_equipment": assigned_equipment, "backup_for": backup_for or "", "details": activity.details, "metrics": activity.metrics}
```

> is this an event? if so can we make this an object so its not pure json

## Prompt 23
> candidate_starts
>
> what does this do

## Prompt 24
> i think you should rename both the function candidate_starts and the variable to make it clearer

## Prompt 25
> put the entities into their own subfolder, and each file should only have one entity

## Prompt 26
> within entities, further split into resources activities and put them in their dedicated subfolders

## Prompt 27
> instead of calling it resources, lets call it constraints, then each file and object change name to its original
>
> Equipment, Specialists, ClientSchedule, TravelPlans, AlliedHealth

## Prompt 28
> lets run the pipeline and check the results

## Prompt 29
> we asked for 100 activities, why are there almost 4000

## Prompt 30
> ok so we have 120 activity definitions, but we dont need to use them all, an action plan maybe only takes 10 of those activities, then we just schedule it

## Prompt 31
> ok so we have already generated our large catalog of activities and constraints right? so run pipeline doesnt have to generate it again everytime

## Prompt 32
> ok so instead of having this run pipeline, we need a
>
> main.py --> reads the activities, the constraints, and the action plan
>
> we also need
>
> a script that generats the activities
> a script that generates the constraints
> a scrip thtat randomly chooses X activities from the activities list
>
> all of these should be saved in a specific location that main.py looks for when it retrieves them to run scheduling

## Prompt 33
> now lets delete some of the obsolete files and code

## Prompt 34
> so now are the constraints, activities and action plan located in the correct location? or do we need to regenerate

## Prompt 35
> ok do that

## Prompt 36
> activity_models.py --> what exactly does this do, and why isnt it in entities/activity

## Prompt 37
> yes split and rename it

## Prompt 38
> ok lets run the pipeline now and see the results

## Prompt 39
> ok lets put this up on github

## Prompt 40
> do i need to create a new github repo first before i run the 2 commands

## Prompt 41
> can you list down all the prompts i used in this codex thread

## Prompt 42
> yes, do that
