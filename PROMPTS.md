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

## Prompt 43
> from now on, every prompt here needs to be logged in prompts.md
>
> look at the entire directory, lets rethink how we should arrange the various files

## Prompt 44
> ok i accept this new structure

## Prompt 45
> run the scheduler to see if it works

## Prompt 46
> in many of the imports, Unresolved reference 'health_scheduler'

## Prompt 47
> now run through with me the scheduler and its logic/flow

## Prompt 48
> ive just been told that they want an AI to do the scheduling, so instead of writing a deterministic code to do the scheduling, we write an AI Agent using an OpenAI LLM (probably GPT 5.4) to do the scheduling

## Prompt 49
> yes so the data generating, data parsing, validation and export all done by code, only the scheduler is done by LLM

## Prompt 50
> okay do it

## Prompt 51
> where do i set the open ai api key

## Prompt 52
> can we just save this key in the repo

## Prompt 53
> ok, lets put these info in .env

## Prompt 54
> ok lets try running it

## Prompt 55
> lets try another method
>
> prompt = """
> Pick exactly ONE chart type from <CHART_SPECIFICATIONS> that best answers the user's question based on the raw_data snapshot and user_requirements. <CHART_SPECIFICATIONS> is a concatenated list of candidate chart definitions, and each definition includes its ChartType id. Use the relevant chart definition(s) and the raw_data snapshot to ensure the chart can be constructed.
>
> Think Step-by-Step as Follows:
> 1) Intent + preferences: from <USER_REQUIREMENTS>, derive:
> 	- primary_goal (trend / compare / rank / part_to_whole / distribution / relationship / composition_over_time / deviation / kpi)
> 	- explicit_preferences (must_use, explicitly_avoid, stacking, normalize, sort, top_n, percent/share, orientation, other flags)
> 2) Candidate evaluation: consider all chart ids defined in <CHART_SPECIFICATIONS>. For each compatible chart, score (0-10):
> 	1. data sufficiency
> 	2. task_fit
> 	3. readability
> 	4. preference_match
> 	Tie-break: 1 -> 2 -> 3 -> 4
> 3) Output: return ONLY the chosen ChartType identifier as a single string, exactly matching a chart id defined in <CHART_SPECIFICATIONS>:
>
> <USER_REQUIREMENTS>
> {user_requirements}
> </USER_REQUIREMENTS>
>
> <RAW_DATA>
> {raw_data}
> </RAW_DATA>
>
> <CHART_SPECIFICATIONS>
> {chart_specifications}
> </CHART_SPECIFICATIONS>
> """.strip()
>
> lets try to provide all the activities and constraints to the LLM, and then ask the LLM to provide the output in a specific format, similar to what this prompt does

## Prompt 56
> so did you make the file changes to be 1 prompt driven?

## Prompt 57
> i think you might be mistaken
>
> the LLM should only run once, so we just load in the activities, constraints and then output once only
>
> so we dont need so much code, just one file to call the LLM, one file as a prompt (just a string), and then one file to parse the output

## Prompt 58
> put in some print statements around the major steps describing what its doing so that when i run the code i can see the progress

## Prompt 59
> lets make action plan only include 2 activities, maybe 10 is too much

## Prompt 60
> we can also change the way we present our constraints, we dont need to have our constraints be like data/inputs/constraints/allied_health.csv, we can just put the information in a concise manner to let the LLM read it

## Prompt 61
> is there a better way to parse the constraint csvs and pass into the LLM without giving in all this too much info

## Prompt 62
> ok first thing we do, is for constraints, we cut down some information
>
> when we parse the client schedule, we should just take note of what are the timings where it is avaialble to put an activity, instead of the entire schedule into the LLM
>
> for equipment, every equipment should be its own json object, with its availablity listted as a field
>
> same for specialists, and allied health

## Prompt 63
> i think there is no need to use occurrence, because LLM can see the activities frequency and decide how to schedule

## Prompt 64
> ok do that

## Prompt 65
> make all availbility be a string instead
>
> for example
>
> Date: Apr 1, 2026
> Available: 0800 to 1200, 1300-1800
> Date: Apr 2, 2026
> Available: 0800 to 1200, 1300-1800

## Prompt 66
> now lets try a 10 actvity action plan

## Prompt 67
> yes we should make the LLM generate the schedule based on the frequency requested.

## Prompt 68
> {"scheduled_events":[{"activity_id":"activity_064","start":"2026-04-01T20:00:00"},{"activity_id":"activity_095","start":"2026-04-01T09:00:00"},{"activity_id":"activity_007","start":"2026-04-01T08:00:00"},{"activity_id":"activity_051","start":"2026-04-01T18:00:00"},{"activity_id":"activity_076","start":"2026-04-01T07:30:00"},{"activity_id":"activity_114","start":"2026-04-02T08:00:00"},{"activity_id":"activity_064","start":"2026-04-02T20:00:00"},{"activity_id":"activity_079","start":"2026-04-02T12:30:00"},{"activity_id":"activity_066","start":"2026-04-02T12:30:00"},{"activity_id":"activity_065","start":"2026-04-02T19:00:00"},{"activity_id":"activity_051","start":"2026-04-02T18:00:00"},{"activity_id":"activity_064","start":"2026-04-03T20:00:00"},{"activity_id":"activity_076","start":"2026-04-03T07:30:00"},{"activity_id":"activity_007","start":"2026-04-04T08:00:00"},{"activity_id":"activity_095","start":"2026-04-05T11:00:00"},{"activity_id":"activity_064","start":"2026-04-05T20:00:00"},{"activity_id":"activity_065","start":"2026-04-05T19:00:00"},{"activity_id":"activity_109","start":"2026-04-07T09:30:00"},{"activity_id":"activity_076","start":"2026-04-07T07:30:00"},{"activity_id":"activity_064","start":"2026-04-08T20:00:00"},{"activity_id":"activity_114","start":"2026-04-09T08:30:00"},{"activity_id":"activity_079","start":"2026-04-09T12:30:00"},{"activity_id":"activity_065","start":"2026-04-09T19:30:00"},{"activity_id":"activity_095","start":"2026-04-12T09:30:00"},{"activity_id":"activity_109","start":"2026-04-14T11:00:00"},{"activity_id":"activity_065","start":"2026-04-16T20:00:00"},{"activity_id":"activity_007","start":"2026-04-18T09:00:00"},{"activity_id":"activity_095","start":"2026-04-19T11:00:00"},{"activity_id":"activity_109","start":"2026-04-21T12:00:00"},{"activity_id":"activity_114","start":"2026-04-23T10:00:00"},{"activity_id":"activity_066","start":"2026-04-23T12:30:00"},{"activity_id":"activity_095","start":"2026-04-26T14:00:00"}]}
>
> see in output.txt, it shows the LLM response is this, but the final says it, Accepted 5 decisions and rejected/unscheduled 27.

## Prompt 69
> no, we need to figure out why the LLM fails to produce valid events in the first place

## Prompt 70
> why does the validator has hidden hard timing? i dont think we need to have morning/afternoon right? just validate the availability should be enough right

## Prompt 71
> we need to rewrite the prompt
> while looping through each activity (ordered based on priority)
> step 1 should be to consider its various constraints (explain each constraint specifically),
>
> step 2 should be to find availibility from the constraints and schedule the event based on availability
>
> step 3 would be to update the client schedule so that subsequent events dont clash with current events

## Prompt 72
>    - `required_instance_count`: the exact number of events you should try to schedule for this activity.  --> think this is redundant, we dont need this at all right?
>
>
> Rules:
> - For each activity, return exactly `required_instance_count` scheduled events whenever possible.
> - If you cannot satisfy every required instance for an activity, still return as many valid events as possible for that activity.
> - Treat the client schedule as cumulative state: once an event is placed, that slot is no longer available for any later event.
> - Pay close attention to daily and weekly activities, because they usually require many repeated events.
> - Do not invent new activity ids, providers, equipment, or times outside the supplied data.
> - Treat each provider and each equipment object as having its own availability string.
> - Use client availability and resource availability as the hard timing source, not the preferred time window names.
> - Do not return explanations or markdown.
>
> we shouldnt have this, if any of these is important, put it inside the steps
>
> we might also want to explain at the start, what constraints there are --> or maybe we want to split the constraint input into the different parts so is easier for the LLM to read

## Prompt 73
> is our activities list already sorted by priority?

## Prompt 74
> so do we need step 2 to resort it?

## Prompt 75
> ok then we remove step 2

## Prompt 76
> check output.txt, the LLM had an error

## Prompt 77
> how can we further reduce the prompt size?

## Prompt 78
> lets change how we generate and save all these availibility to save it in that kind of format, but it must be in CSV

## Prompt 79
> ok regenerate all the constraints

## Prompt 80
> why do we still build_occurrence and still have backup activity

## Prompt 81
> nah for validation, we just need to validate that the activity does not clash, and its constraints are made available, so we probably dont need to validate frequency. and yes remove backup

## Prompt 82
> lets look at a 5 activity action plan instead of 10
