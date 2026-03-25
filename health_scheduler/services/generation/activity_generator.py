from __future__ import annotations

import random
from typing import Callable

from health_scheduler.domain.activities.activity import Activity
from health_scheduler.domain.activities.frequency import Frequency
from health_scheduler.domain.enums.activity_category import ActivityCategory
from health_scheduler.domain.enums.title_suffix import title_suffixes_for_category
from health_scheduler.services.generation.activity_factory import create_activity, normalize_category


def create_random_activity(category: ActivityCategory | str, activity_id: str, rng: random.Random, used_titles: set[str]) -> Activity:
    normalized = normalize_category(category)
    return RANDOM_ACTIVITY_DISPATCH[normalized](activity_id, rng, used_titles)


def build_random_activity(
    category: ActivityCategory | str,
    activity_id: str,
    title_root: str,
    details: str,
    metrics: list[str],
    roles: list[str],
    locations: list[str],
    remote: bool,
    equipment: list[str],
    prep: list[str],
    durations: list[int],
    frequencies: list[Frequency],
    _unused_time_hints: list[str],
    rng: random.Random,
    used_titles: set[str],
) -> Activity:
    normalized = normalize_category(category)
    role = rng.choice(roles)
    location = normalize_location(rng.choice(locations), role)
    return create_activity(
        category=normalized,
        id=activity_id,
        title=build_unique_title(title_root, normalized, used_titles, rng),
        priority=random_priority_for(normalized, title_root, rng),
        duration_minutes=rng.choice(durations),
        details=details,
        frequency=rng.choice(frequencies),
        facilitator_role=role,
        location=location,
        remote_allowed=bool(remote and role != "self_guided") or location in {"office", "travel"},
        equipment_required=[rng.choice(equipment)] if equipment and location != "park" else [],
        prep_required=rng.sample(prep, 1 if len(prep) == 1 else rng.randint(1, min(2, len(prep)))),
        backup_activity_ids=[],
        skip_adjustment=skip_adjustment_for(normalized, title_root),
        metrics=rng.sample(metrics, 1 if len(metrics) == 1 else rng.randint(2, min(3, len(metrics)))),
    )


def build_unique_title(base: str, category: ActivityCategory | str, used_titles: set[str], rng: random.Random) -> str:
    suffixes = title_suffixes_for_category(category)
    for suffix in rng.sample(suffixes, len(suffixes)):
        title = f"{base} - {suffix}"
        if title not in used_titles:
            used_titles.add(title)
            return title
    index = 2
    while True:
        title = f"{base} - Plan Variant {index}"
        if title not in used_titles:
            used_titles.add(title)
            return title
        index += 1


def random_priority_for(category: ActivityCategory | str, title_root: str, rng: random.Random) -> int:
    normalized = normalize_category(category)
    base = {
        ActivityCategory.FITNESS: 68,
        ActivityCategory.FOOD: 64,
        ActivityCategory.MEDICATION: 85,
        ActivityCategory.THERAPY: 70,
        ActivityCategory.CONSULTATION: 78,
    }[normalized]
    if "Primary Care" in title_root or "Prescription" in title_root or "Lab" in title_root:
        base += 8
    return min(100, base + rng.randint(-8, 8))


def skip_adjustment_for(category: ActivityCategory | str, title_root: str) -> str:
    normalized = normalize_category(category)
    if "Lab" in title_root:
        return "Book the next morning lab slot and preserve fasting instructions."
    return {
        ActivityCategory.FITNESS: "Move to the next free slot within 48 hours and lower intensity by one step.",
        ActivityCategory.FOOD: "Replace with the closest balanced meal option and record deviation in the nutrition log.",
        ActivityCategory.MEDICATION: "Flag for clinician review if skipped; do not double dose without instructions.",
        ActivityCategory.THERAPY: "Reschedule within the same week if symptoms are stable; otherwise mark for manual review.",
        ActivityCategory.CONSULTATION: "Rebook the next available provider slot and send the latest metrics summary ahead of time.",
    }[normalized]


def normalize_location(location: str, role: str) -> str:
    if role == "self_guided" and location == "clinic":
        return "home"
    return location


def random_fitness_activity(activity_id: str, rng: random.Random, used_titles: set[str]) -> Activity:
    pattern = rng.choice(["run", "strength", "mobility", "bike", "yoga", "walk", "eye"])
    if pattern == "run":
        return build_random_activity(ActivityCategory.FITNESS, activity_id, f"{rng.choice(['Zone 2', 'Aerobic Base', 'Cardio Recovery'])} {rng.choice(['Run', 'Treadmill Session'])}", "Maintain a sustainable aerobic effort and log exertion after the session.", ["heart_rate_average", "distance_km", "rpe"], ["exercise_physiologist", "strength_coach", "self_guided"], ["gym", "park"], True, ["treadmill"], ["Light dynamic warm-up", "Bring water bottle"], [45, 60], [Frequency(times=2, period="week"), Frequency(times=3, period="week")], rng, used_titles)
    if pattern == "strength":
        return build_random_activity(ActivityCategory.FITNESS, activity_id, f"{rng.choice(['Resistance', 'Strength', 'Posterior Chain'])} Session", "Complete compound lifts with controlled tempo and moderate load progression.", ["sets_completed", "load_used", "session_rpe"], ["strength_coach", "exercise_physiologist"], ["gym"], True, ["dumbbell_set"], ["Prepare workout log", "Complete activation drills"], [60, 75], [Frequency(times=2, period="week")], rng, used_titles)
    if pattern == "mobility":
        return build_random_activity(ActivityCategory.FITNESS, activity_id, f"{rng.choice(['Mobility', 'Joint Care', 'Posture'])} Flow", "Move through controlled range-of-motion work and keep breathing relaxed.", ["mobility_minutes", "pain_score", "stiffness_score"], ["physiotherapist", "self_guided"], ["home", "gym"], True, ["yoga_mat"], ["Quiet floor space", "Yoga mat ready"], [20, 30], [Frequency(times=3, period="week"), Frequency(times=1, period="day")], rng, used_titles)
    if pattern == "bike":
        return build_random_activity(ActivityCategory.FITNESS, activity_id, f"{rng.choice(['Interval', 'Tempo', 'Cadence'])} Bike Session", "Alternate harder efforts with recovery segments and track response across intervals.", ["peak_heart_rate", "interval_count", "session_rpe"], ["exercise_physiologist", "self_guided"], ["gym"], True, ["stationary_bike"], ["Hydrate before session", "Review interval targets"], [30, 45], [Frequency(times=1, period="week"), Frequency(times=2, period="week")], rng, used_titles)
    if pattern == "yoga":
        return build_random_activity(ActivityCategory.FITNESS, activity_id, f"{rng.choice(['Guided Yoga', 'Recovery Yoga', 'Breath-Led Yoga'])}", "Use slow transitions and extended exhales to support recovery and mobility.", ["session_minutes", "stress_score_post", "sleep_readiness"], ["physiotherapist", "health_coach", "self_guided"], ["home", "studio"], True, ["yoga_mat"], ["Set up quiet room", "Reduce screen exposure beforehand"], [30, 45], [Frequency(times=2, period="week")], rng, used_titles)
    if pattern == "walk":
        return build_random_activity(ActivityCategory.FITNESS, activity_id, f"{rng.choice(['Outdoor', 'Recovery', 'Low-Impact'])} Walk", "Walk at a pace that slightly elevates breathing while keeping posture tall.", ["steps", "distance_km", "average_pace"], ["self_guided"], ["park"], False, [], ["Comfortable walking shoes"], [30, 45], [Frequency(times=3, period="week"), Frequency(times=4, period="week")], rng, used_titles)
    return build_random_activity(ActivityCategory.FITNESS, activity_id, f"{rng.choice(['Eye', 'Visual', 'Focus'])} Mobility Routine", "Alternate near and far focus work with controlled visual tracking drills.", ["eye_strain_score", "routine_minutes", "screen_break_count"], ["occupational_therapist", "self_guided"], ["home", "office"], True, [], ["Screen brightness reduced", "Timer prepared"], [15, 20], [Frequency(times=1, period="day")], rng, used_titles)


def random_food_activity(activity_id: str, rng: random.Random, used_titles: set[str]) -> Activity:
    pattern = rng.choice(["breakfast", "lunch", "smoothie", "hydration", "dinner", "supplement"])
    if pattern == "breakfast":
        return build_random_activity(ActivityCategory.FOOD, activity_id, f"{rng.choice(['Protein-Forward', 'Balanced', 'High-Fiber'])} Breakfast", "Build breakfast around protein, fiber, and steady energy release.", ["protein_grams", "fiber_grams", "post_meal_energy"], ["dietitian", "self_guided"], ["home", "office"], True, ["blender_station"], ["Ingredients prepped the night before", "Breakfast logged in nutrition app"], [20, 30], [Frequency(times=3, period="week"), Frequency(times=4, period="week")], ["early_morning", "morning"], rng, used_titles)
    if pattern == "lunch":
        return build_random_activity(ActivityCategory.FOOD, activity_id, f"{rng.choice(['Mediterranean', 'Low-Glycemic', 'Recovery'])} Lunch", "Use lean protein, vegetables, and stable carbohydrates for lunch composition.", ["vegetable_servings", "satiety_score", "post_meal_glucose"], ["dietitian", "self_guided"], ["home", "office"], True, [], ["Meal prep container ready"], [30], [Frequency(times=2, period="week"), Frequency(times=3, period="week")], ["midday"], rng, used_titles)
    if pattern == "smoothie":
        return build_random_activity(ActivityCategory.FOOD, activity_id, f"{rng.choice(['Recovery', 'Protein', 'Post-Workout'])} Smoothie", "Blend protein and hydration-supportive ingredients after higher-load training.", ["protein_grams", "hydration_ml", "recovery_score_next_day"], ["dietitian", "self_guided"], ["home"], True, ["blender_station"], ["Frozen ingredients portioned"], [15], [Frequency(times=2, period="week")], ["morning", "evening"], rng, used_titles)
    if pattern == "hydration":
        return build_random_activity(ActivityCategory.FOOD, activity_id, f"{rng.choice(['Hydration', 'Electrolyte', 'Fluid'])} Checkpoint", "Pause for a structured hydration target and record intake progress.", ["hydration_ml", "electrolyte_serving", "urine_color_score"], ["self_guided", "health_coach"], ["home", "office", "travel"], True, [], ["Water bottle filled"], [10], [Frequency(times=1, period="day")], ["morning", "midday", "evening"], rng, used_titles)
    if pattern == "dinner":
        return build_random_activity(ActivityCategory.FOOD, activity_id, f"{rng.choice(['Fiber-Rich', 'Balanced', 'Sleep-Support'])} Dinner", "Build dinner around vegetables, legumes, and a moderate portion of lean protein.", ["fiber_grams", "meal_finish_time", "sleep_quality_next_day"], ["dietitian", "self_guided"], ["home"], True, [], ["Dinner ingredients thawed", "Vegetables chopped in advance"], [30, 40], [Frequency(times=2, period="week"), Frequency(times=3, period="week")], ["evening"], rng, used_titles)
    return build_random_activity(ActivityCategory.FOOD, activity_id, f"{rng.choice(['Supplement', 'Nutrient', 'Adherence'])} With Meal", "Pair supplements with a balanced meal to improve consistency.", ["supplement_taken", "meal_timestamp", "stomach_tolerance"], ["self_guided"], ["home", "office", "travel"], False, [], ["Supplement pack ready"], [10], [Frequency(times=4, period="week"), Frequency(times=5, period="week")], ["morning", "midday"], rng, used_titles)


def random_medication_activity(activity_id: str, rng: random.Random, used_titles: set[str]) -> Activity:
    pattern = rng.choice(["vitamin", "magnesium", "prescription", "injection", "refill"])
    if pattern == "vitamin":
        return build_random_activity(ActivityCategory.MEDICATION, activity_id, f"{rng.choice(['Morning', 'Daily', 'Consistency'])} Vitamin Dose", "Take the planned vitamin dose with food and mark adherence in the tracker.", ["dose_taken", "time_taken", "missed_dose_flag"], ["self_guided"], ["home", "travel"], False, [], ["Medication organizer refilled"], [10], [Frequency(times=1, period="day")], ["morning"], rng, used_titles)
    if pattern == "magnesium":
        return build_random_activity(ActivityCategory.MEDICATION, activity_id, f"{rng.choice(['Evening', 'Sleep-Support', 'Recovery'])} Magnesium Dose", "Take magnesium in the evening and monitor any effect on sleep readiness.", ["dose_taken", "sleep_latency", "GI_tolerance"], ["self_guided"], ["home", "travel"], False, [], ["Medication organizer refilled"], [10], [Frequency(times=1, period="day")], ["evening"], rng, used_titles)
    if pattern == "prescription":
        return build_random_activity(ActivityCategory.MEDICATION, activity_id, f"{rng.choice(['Prescription', 'Maintenance', 'Daily'])} Medication Dose", "Take the prescribed maintenance medication exactly as listed in the plan.", ["dose_taken", "side_effect_score", "blood_pressure_reading"], ["self_guided"], ["home", "travel"], False, ["blood_pressure_cuff"], ["Medication organizer refilled", "Dose reminder active"], [10], [Frequency(times=1, period="day")], ["morning", "evening"], rng, used_titles)
    if pattern == "injection":
        return build_random_activity(ActivityCategory.MEDICATION, activity_id, f"{rng.choice(['Weekly', 'Planned', 'Adherence'])} Injection Window", "Administer the weekly medication during a stable routine window and record the site used.", ["dose_taken", "injection_site", "symptom_score_next_day"], ["self_guided"], ["home"], False, [], ["Injection supplies prepared", "Sharps bin nearby"], [15], [Frequency(times=1, period="week")], ["evening"], rng, used_titles)
    return build_random_activity(ActivityCategory.MEDICATION, activity_id, f"{rng.choice(['Medication', 'Refill', 'Supply'])} Check", "Review remaining medication supply and place a refill request before the final week of stock.", ["days_of_supply_left", "refill_requested", "med_list_updated"], ["health_coach", "self_guided"], ["home", "office"], True, [], ["Pharmacy details available"], [20], [Frequency(times=1, period="month")], ["midday", "evening"], rng, used_titles)


def random_therapy_activity(activity_id: str, rng: random.Random, used_titles: set[str]) -> Activity:
    pattern = rng.choice(["sauna", "cold", "compression", "breathing", "manual"])
    if pattern == "sauna":
        return build_random_activity(ActivityCategory.THERAPY, activity_id, f"{rng.choice(['Sauna', 'Heat Recovery', 'Thermal'])} Session", "Use a moderate-duration heat exposure and cool down gradually afterwards.", ["session_minutes", "pre_weight", "post_weight"], ["self_guided", "health_coach"], ["recovery_center"], False, ["sauna_room"], ["Hydrate 30 minutes before", "Bring towel"], [30, 40], [Frequency(times=1, period="week")], ["evening"], rng, used_titles)
    if pattern == "cold":
        return build_random_activity(ActivityCategory.THERAPY, activity_id, f"{rng.choice(['Cold Exposure', 'Ice Recovery', 'Cooling'])} Session", "Keep the cold exposure controlled and note recovery response after the session.", ["session_minutes", "recovery_score", "mood_after"], ["self_guided", "health_coach"], ["recovery_center"], False, ["ice_bath"], ["Breathing reset before entry"], [15, 20], [Frequency(times=1, period="week")], ["evening"], rng, used_titles)
    if pattern == "compression":
        return build_random_activity(ActivityCategory.THERAPY, activity_id, f"{rng.choice(['Compression', 'Recovery Boot', 'Circulation'])} Session", "Use lower-limb compression after demanding training blocks to support recovery.", ["session_minutes", "leg_heaviness_score", "recovery_score"], ["self_guided"], ["recovery_center"], False, ["compression_boots"], ["Elevate legs after session"], [20, 30], [Frequency(times=1, period="week"), Frequency(times=2, period="week")], ["evening"], rng, used_titles)
    if pattern == "breathing":
        return build_random_activity(ActivityCategory.THERAPY, activity_id, f"{rng.choice(['Guided Breathing', 'Evening Breathwork', 'Stress Reset'])}", "Use slow exhale-biased breathing to lower evening stress load and improve sleep onset.", ["session_minutes", "stress_score_post", "sleep_latency"], ["health_coach", "self_guided"], ["home"], True, [], ["Phone on silent", "Lights dimmed"], [15, 20], [Frequency(times=3, period="week")], ["evening"], rng, used_titles)
    return build_random_activity(ActivityCategory.THERAPY, activity_id, f"{rng.choice(['Manual Therapy', 'Soft Tissue', 'Recovery Manual'])} Session", "Complete targeted recovery therapy for the current mobility restriction or pain point.", ["pain_score_pre", "pain_score_post", "range_of_motion_change"], ["physiotherapist"], ["clinic"], False, [], ["Pain notes updated before appointment"], [45, 60], [Frequency(times=2, period="month")], ["morning", "afternoon"], rng, used_titles)


def random_consultation_activity(activity_id: str, rng: random.Random, used_titles: set[str]) -> Activity:
    pattern = rng.choice(["primary_care", "dietitian", "physio", "sleep", "lab"])
    if pattern == "primary_care":
        return build_random_activity(ActivityCategory.CONSULTATION, activity_id, "Primary Care Review", "Review symptoms, medication adherence, and recent health trends with the physician.", ["blood_pressure_reading", "weight", "questions_answered"], ["primary_care_physician"], ["clinic"], True, [], ["Prepare question list", "Upload recent metrics summary"], [45], [Frequency(times=1, period="month")], ["morning", "afternoon"], rng, used_titles)
    if pattern == "dietitian":
        return build_random_activity(ActivityCategory.CONSULTATION, activity_id, "Dietitian Consultation", "Review meal adherence, travel eating patterns, and nutrition barriers.", ["meal_adherence_score", "weight_trend", "action_items_created"], ["dietitian"], ["clinic"], True, [], ["Food diary updated", "Photos of recent meals available"], [45], [Frequency(times=2, period="month")], ["midday", "afternoon"], rng, used_titles)
    if pattern == "physio":
        return build_random_activity(ActivityCategory.CONSULTATION, activity_id, "Physiotherapy Review", "Assess mobility constraints and exercise tolerance, then adjust the movement plan.", ["pain_score", "range_of_motion", "exercise_modifications"], ["physiotherapist"], ["clinic"], True, [], ["Training log available", "Pain notes updated"], [45, 60], [Frequency(times=2, period="month")], ["morning", "afternoon"], rng, used_titles)
    if pattern == "sleep":
        return build_random_activity(ActivityCategory.CONSULTATION, activity_id, "Sleep Coaching Call", "Review bedtime consistency, evening routine, and overnight recovery patterns.", ["sleep_duration", "sleep_latency", "action_items_created"], ["sleep_physician", "health_coach"], ["home"], True, [], ["Sleep tracker summary exported"], [30], [Frequency(times=1, period="week")], ["evening"], rng, used_titles)
    return build_random_activity(ActivityCategory.CONSULTATION, activity_id, "Lab Testing Appointment", "Complete planned bloodwork or diagnostic testing and confirm follow-up routing.", ["test_completed", "sample_quality", "follow_up_booked"], ["lab_technician"], ["lab"], False, ["lab_kit"], ["Bring requisition form", "Follow fasting instructions"], [30, 45], [Frequency(times=1, period="month")], ["morning"], rng, used_titles)


RANDOM_ACTIVITY_DISPATCH: dict[ActivityCategory, Callable[[str, random.Random, set[str]], Activity]] = {
    ActivityCategory.FITNESS: random_fitness_activity,
    ActivityCategory.FOOD: random_food_activity,
    ActivityCategory.MEDICATION: random_medication_activity,
    ActivityCategory.THERAPY: random_therapy_activity,
    ActivityCategory.CONSULTATION: random_consultation_activity,
}
