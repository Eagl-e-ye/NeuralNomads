import json
from datetime import date, timedelta, datetime
import random
import string
from openai import OpenAI
import itertools, time

API_KEYS = [
    # "sk-or-v1-cc19ed5687ca20dfefc057aac.......",
    # "sk-or-v1-ffc3bca9958f50b8b10e4f4b7.......",

    # add api key in the list to run the code
]
api_keys_cycle = itertools.cycle(API_KEYS)
current_key = next(api_keys_cycle)
client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=current_key)

def call_with_key_rotation(model, messages, max_retries=40):

    global client, current_key
    for attempt in range(max_retries):
        try:
            completion = client.chat.completions.create(
                model=model,
                messages=messages
            )
            return completion
        except Exception as e:
            print(f"[Key Error] Key {current_key[:12]}... failed: {e}")
            # Rotate to next key
            current_key = next(api_keys_cycle)
            client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=current_key)
            print(f"[Key Switch] Switched to {current_key[:12]}...")
            time.sleep(1)
    raise RuntimeError("All API keys exhausted or failed.")

MONTHS = 8
PATIENT_NAME = "Rohan"
ADHERENCE_RATE = 0.5

patient_data = {
    "profile": {
        "name": "Rohan",
        "age": 45,
        "conditions": ["high cholesterol"]
    },

    "vitals": {
        "bp": "120/85",  # Blood pressure
        "hr": 72,  # Heart rate
        "weight": 75,  # kg
        "bmi": 24.5  # Body Mass Index
    },

    "labs": [
        {
            "date": "2025-01-01",
            "values": {
                # Lipid profile
                "Total Cholesterol": {"value": 220, "unit": "mg/dL"},
                "LDL": {"value": 140, "unit": "mg/dL"},
                "HDL": {"value": 50, "unit": "mg/dL"},
                "Triglycerides": {"value": 150, "unit": "mg/dL"},
                "ApoB": {"value": 90, "unit": "mg/dL"},

                # Blood sugar
                "Fasting Glucose": {"value": 95, "unit": "mg/dL"},
                "HbA1c": {"value": 5.6, "unit": "%"},

                # Liver & kidney
                "ALT": {"value": 25, "unit": "U/L"},
                "Creatinine": {"value": 1.0, "unit": "mg/dL"},

                # Thyroid
                "TSH": {"value": 2.5, "unit": "uIU/mL"},

                # Inflammatory marker
                "CRP": {"value": 1.2, "unit": "mg/L"}
            }
        }
    ],

    "exercise_log": [
        {"date": "2025-01-15", "activity": "Cardio", "duration": 40, "perceived_exertion": "Medium"},
        {"date": "2025-01-16", "activity": "Strength Training", "duration": 30, "perceived_exertion": "High"}
    ],

    "diet_notes": [
        {"date": "2025-01-15", "notes": "Low-carb, high-protein meals; 2L water intake"}
    ],

    "travel_history": [
        {"date": "2025-01-10", "city": "Mumbai", "purpose": "Work"}
    ],

    "sleep_log": [
        {"date": "2025-01-01", "duration": 6, "quality": "Fair"},
        {"date": "2025-01-02", "duration": 7, "quality": "Good"}
    ],

    "medication_log": [
        {"date": "2025-01-01", "name": "Atorvastatin", "dose": "10mg", "adherence": "Taken"}
    ],

    "pain_log": [
        {"date": "2025-01-01", "location": "Knee", "pain_level": "None", "notes": "No pain"}
    ]
}

ROLE_TIME = {
    "warren": 5,
    "advik": 4,
    "rachel": 4,
    "carla": 3,
    "ruby": 2,
    "neel": 2
}




personas = {
    "ruby": (
        "You are Ruby, the Elyx Concierge and first point of contact for all incoming patient messages.\n"
        "Your job is to:\n"
        "1. Greet and acknowledge the patient warmly and professionally.\n"
        "2. If the request is logistical (appointments, scheduling, travel, coordination), handle it yourself.\n"
        "3. If the request is medical, fitness, nutrition, or scientific in nature, do NOT answer directly. Instead:\n"
        "   • Understand the topic.\n"
        "   • if the patient is dissatisfied deal with him very politely"
        "   • Tell the patient which specialist will respond.\n"
        "   • Forward the query to that specialist.\n"
        "\n"
        "Team Directory — You can hand off to:\n"
        "• Dr. Warren – Medical Strategist\n"
        "• Advik – Performance Scientist\n"
        "• Carla – Nutritionist\n"
        "• Rachel – Physiotherapist\n"
        "• Neel – Concierge Lead\n"
        "\n"
        "Rule: Never provide detailed medical or technical advice yourself. Always route such cases to the correct specialist."
    ),

    "warren": (
        "You are Dr. Warren, the best Medical Strategist.\n"
        "Your job:\n"
        "1. Interpret lab reports and test results.\n"
        "2. Approve diagnostics and guide medical direction.\n"
        "3. ALWAYS check for available patient data (ApoB, cholesterol, BP, current medications).\n"
        "   • If the patient has provided data, ask for it before giving advice.\n"
        "Speak with authority, clarity,precise, scientific and consider best-practice defaults when data is missing and don't ask to refer other."
    ),

    "advik": (
        "You are Advik, the best Performance Scientist and pattern orriented.\n"
        "Your role:\n"
        "1. Analyze wearable data trends: HRV, sleep quality, recovery patterns.\n"
        "2. Check for available HRV values and sleep logs.\n"
        "   • If data exists, reference it before giving suggestions.\n"
        "Speak with curiosity, analytically and supportively and don't ask to refer other."
    ),

    "carla": (
        "You are Carla, the best Nutritionist.\n"
        "Your role:\n"
        "1. Design nutrition plans and supplement advice.\n"
        "2. Check for available patient info: current weight, recent diet notes, travel/diet disruptions.\n"
        "   • If data exists, use it before making recommendations else ask for it.\n"
        "Be supportive, practical, and flexible and don't ask to refer other."
    ),

    "rachel": (
        "You are Rachel, the best Physiotherapist and expert in body physical structure.\n"
        "Your role:\n"
        "1. Manage exercise plans, form corrections, and injury rehab.\n"
        "2. Check for last exercise session logs and injury/pain notes.\n"
        "   • If data exists, reference it before recommending changes.\n"
        "Be precise, encouraging, and practical and don't ask to refer other."
    ),

    "neel": (
        "You are Neel, the Elyx Concierge Lead.\n"
        "You oversee the relationship and provide reassurance.\n"
        "Check if the patient is satisfied with support and whether adjustments are needed.\n"
        "Always maintain a strategic, empathetic, and professional tone."
    )
}

WAKE_START, SLEEP_END = 7, 23
def random_wake_time(day_date, last_end_time=None):
    start_hour = max(WAKE_START, last_end_time.hour + 1 if last_end_time else WAKE_START)

    # If no room left in today's schedule → return None (so caller shifts it to tomorrow)
    if start_hour >= SLEEP_END:
        return None

    hour = random.randint(start_hour, SLEEP_END - 1)
    minute = random.randint(0, 59)
    return datetime.combine(day_date, datetime.min.time()) + timedelta(hours=hour, minutes=minute)


def add_doctor_reply_time(patient_time):
    """Doctor replies 25–50 min later, capped at sleep time."""
    reply = patient_time + timedelta(minutes=random.randint(25, 50))
    day_end = datetime.combine(patient_time.date(), datetime.min.time()) + timedelta(hours=SLEEP_END)
    return min(reply, day_end)


def next_patient_msg_time(last_time):
    """Gap of 2–6 hours, capped at sleep time."""
    next_time = last_time + timedelta(hours=random.randint(2, 6))
    day_end = datetime.combine(last_time.date(), datetime.min.time()) + timedelta(hours=SLEEP_END)
    return min(next_time, day_end)



def generate_patient_schedule(start_date, months):
    events = []
    day = start_date
    total_days = months * 30

    for i in range(total_days):
        # Travel every 21 days
        if i % 21 == 0:
            events.append({
                "type": "travel",
                "date": str(day),
                "city": random.choice(["London", "NYC", "Seoul", "Jakarta", "New Delhi", "Paris",
    "Tokyo", "Singapore", "Dubai", "Bangkok", "Hong Kong",
    "Sydney", "Toronto", "Los Angeles", "San Francisco",
    "Chicago", "Berlin", "Rome", "Barcelona", "Amsterdam",
    "Istanbul", "Kuala Lumpur", "Shanghai", "Beijing", "Mexico City",
    "São Paulo", "Cape Town", "Mumbai", "Doha", "Riyadh"])
            })
        # Diagnostic tests every 90 days
        if i % 90 == 0:
            events.append({"type": "diagnostic_test", "date": str(day)})
        # Exercise updates every 14 days
        if i % 14 == 0:
            events.append({"type": "exercise_update", "date": str(day)})
        # Random general queries 10% of days
        if random.random() < 0.1:  # 10% chance of *any* event
            event_types = [
                "medication_review",
                "diet_update",

            ]
            chosen_event = random.choice(event_types)  # pick one at random
            events.append({"type": chosen_event, "date": str(day)})

        if random.random() < 0.07:  # 7% chance of *any* event
            event_types = [
                "general_query",
                "pain_report"
            ]
            chosen_event = random.choice(event_types)
            events.append({"type": chosen_event, "date": str(day)})

        if random.random() <0.01:
            events.append({"type": "dissatisfaction", "date": str(day)})

        day += timedelta(days=1)
    return events


def generate_patient_event_msg(event, patient_data):
    if event["type"] == "travel":
        patient_data["travel_history"].append({
            "date": event["date"],
            "city": event["city"],
            "purpose": event.get("purpose", "Work")
        })
        return random.choice([
            f"I’ll be in {event['city']} next week for work. Can you suggest workouts and healthy food options while traveling?",
            f"I'm traveling to {event['city']} soon. How do I stay on track with diet and exercise?",
            f"Next week I’ll be in {event['city']}. Any tips to manage meals and workouts there?",
            f"I’ll be in {event['city']} for a few days. How do I keep my meals healthy while eating out?",
            f"Traveling to {event['city']} means long flights. Any advice to stay active and reduce fatigue?",
            f"I’m heading to {event['city']} soon. What quick workouts can I do in a hotel room?",
            f"Since I’ll be in {event['city']}, should I adjust my medication or routine in any way?",
            f"Meals might be irregular while I’m in {event['city']}. How do I maintain good nutrition?",
            f"I’ll be spending a week in {event['city']}. How can I keep my cholesterol under control during travel?"
                ])

    elif event["type"] == "diagnostic_test":
        if patient_data["labs"]:
            last_lab_entry = patient_data["labs"][-1]  # latest date
            lab_name = random.choice(list(last_lab_entry["values"].keys()))
            lab_info = last_lab_entry["values"][lab_name]
            return random.choice([
                f"My recent {lab_name} result was {lab_info['value']} {lab_info['unit']}. Is that safe?",
                f"I just got my {lab_name} test back ({lab_info['value']} {lab_info['unit']}). What does that mean for my condition?",
                f"My {lab_name} reading came out {lab_info['value']} {lab_info['unit']}. Should I be concerned?"
            ])
        else:
            return "I just got some lab results, but I don't have the details yet."

    elif event["type"] == "exercise_update":
        return random.choice([
            "The new cardio plan feels harder than before. Am I overdoing it?",
            "I’ve been struggling with recovery after workouts. What should I adjust?",
            "My strength training feels better, but cardio is exhausting me more. Any suggestions?",
            "I’ve noticed knee pain after running. Should I switch to another exercise?",
            "I missed a few workout sessions this week. How should I get back on track?",
            "I’m not sure if I’m progressing fast enough with strength training. Is this normal?",
            "After cycling, I feel more tired than usual. Is this something to worry about?",
            "I want to increase my stamina — should I focus more on cardio or strength?",
            "I get sore muscles often after workouts. Is stretching enough to prevent this?",
            "How do I balance rest days with staying active?",
            "I tried adding yoga to my routine. Is it enough for flexibility and recovery?",
            "Sometimes I feel low energy before workouts. Should I eat differently beforehand?"
        ])

    elif event["type"] == "general_query":
        return random.choice([
            "I read about intermittent fasting. Would it help with my cholesterol?",
            "Someone recommended magnesium supplements. Should I consider them?",
            "I came across cold showers for recovery. Do they really work?",
            "How important is sleep quality for my heart health?",
            "Would adjusting my diet help lower my blood pressure?",
            "Is green tea really effective for improving heart health?",
            "Should I be taking vitamin D supplements during winter?",
            "What’s the best time of day to exercise for lowering cholesterol?",
            "Do short naps actually help with recovery and energy?",
            "How much water should I aim to drink daily for my condition?",
            "I’ve heard omega-3 supplements help with cholesterol. Is that true?",
            "Would yoga or meditation help me manage stress and blood pressure?",
            "Are plant-based proteins good enough to replace meat in my diet?",
            "Does caffeine affect cholesterol or blood pressure?",
            ])

    elif event["type"] == "diet_update":
        return random.choice([
            "I tried increasing vegetable intake today. Is this enough?",
            "Had some fast food recently. How can I recover from that?",
            "I attempted intermittent fasting. Any suggestions?",
            "I reduced my sugar intake this week. Is that a good step?",
            "I skipped breakfast today — does that affect my cholesterol?",
            "I’ve been eating more fruits lately. Is this helping my condition?",
            "I had a late-night meal yesterday. Will that affect my progress?",
            "I’m trying to cut down on red meat. What are good alternatives?",
            "I drank more coffee than usual. Could that be harmful?",
            "I started adding nuts and seeds to my diet. Is that beneficial?",
            "I had a heavy dinner last night. Should I balance it out today?",
            "I tried a plant-based meal. Should I do this more often?",
            "I’m unsure how much protein I should be eating daily. Any advice?"
        ])

    elif event["type"] == "medication_review":
        vitals_info = f" Currently my BP is {patient_data['vitals']['bp']} and weight is {patient_data['vitals']['weight']} kg."
        return "I have taken my medication today." + vitals_info

    elif event["type"] == "pain_report":
        return random.choice([
            "I felt mild knee discomfort today.",
            "My back hurt a bit during activity.",
            "Shoulder pain is bothering me slightly."
        ])

    elif event["type"] == "dissatisfaction":
        return random.choice([
            "I feel like the plan is too strict and hard to follow daily.",
            "The diet suggestions don’t really match the foods I usually eat.",
            "I’m not seeing much improvement even after following the plan.",
            "I'm not happy with the medicine prescribed, it makes me feel tired.",
            "It’s frustrating when I don’t see results quickly.",
        ])

    return "Hello, I have a question about my health."


def daily_update(patient_data, today):
    # --- Blood Pressure ---
    systolic, diastolic = map(int, patient_data["vitals"]["bp"].split("/"))
    systolic += random.choice([-2, -1, 1,2])
    diastolic += random.choice([-2, -1, 1, 2])
    patient_data["vitals"]["bp"] = f"{systolic}/{diastolic}"

    # --- Heart Rate ---
    patient_data["vitals"]["hr"] = max(50, min(100, patient_data["vitals"]["hr"] + random.choice([-13,-6,-2, -1, 0, 1, 2,9,12,6,15])))

    # --- Weight ---
    patient_data["vitals"]["weight"] = round(patient_data["vitals"]["weight"] + random.choice([-1,-.5,-.3,.2,.5,]), 1)

    # --- Sleep Log ---
    sleep_entry = {
        "date": str(today),
        "duration": random.choice([4,5, 6, 7, 8]),
        "quality": random.choice(["Poor", "Fair", "Good"])
    }
    patient_data["sleep_log"].append(sleep_entry)

    # --- Medication adherence ---
    if patient_data.get("medication_log"):
        adherence = "Taken" if random.random() < 0.5 else "Missed"
        patient_data["medication_log"].append({
            "date": str(today),
            "name": "Atorvastatin",
            "dose": "10mg",
            "adherence": adherence
        })

    # --- Pain log (occasional 10% of days) ---
    if random.random() < 0.1:
        patient_data["pain_log"].append({
            "date": str(today),
            "location": random.choice(["Knee", "Back", "Shoulder"]),
            "pain_level": random.choice(["Mild", "Moderate"]),
            "notes": "Reported discomfort"
        })

        # --- Lab updates (cholesterol, glucose, liver, kidney, etc.) ---
        lab_drift = {
            "ApoB": 1.5,
            "Total Cholesterol": 3,
            "LDL": 2.5,
            "HDL": 1,
            "Triglycerides": 5,
            "Fasting Glucose": 1,
            "HbA1c": 0.1,
            "ALT": 1,
            "Creatinine": 0.05,
            "TSH": 0.1,
            "CRP": 0.2
        }

        if patient_data.get("labs"):
            last_lab = patient_data["labs"][-1]["values"]
        else:
            last_lab = {}

        new_lab_values = {}
        for lab, drift in lab_drift.items():
            low, high = {
                "ApoB": (60, 130),
                "Total Cholesterol": (150, 250),
                "LDL": (70, 160),
                "HDL": (30, 70),
                "Triglycerides": (50, 200),
                "Fasting Glucose": (70, 110),
                "HbA1c": (4, 6),
                "ALT": (10, 50),
                "Creatinine": (0.6, 1.5),
                "TSH": (0.5, 5.0),
                "CRP": (0, 3)
            }[lab]

            prev_val = last_lab.get(lab, {}).get("value", (low + high) / 2)
            new_val = max(low, min(high, prev_val + random.uniform(-drift, drift)))

            # Set units
            unit = last_lab.get(lab, {}).get("unit")
            if not unit:
                if lab in ["HbA1c"]:
                    unit = "%"
                elif lab in ["Creatinine"]:
                    unit = "mg/dL"
                elif lab in ["TSH"]:
                    unit = "uIU/mL"
                elif lab in ["ALT"]:
                    unit = "U/L"
                elif lab in ["CRP"]:
                    unit = "mg/L"
                else:
                    unit = "mg/dL"

            new_lab_values[lab] = {"value": round(new_val, 2), "unit": unit}

        # Append today's lab entry
        patient_data.setdefault("labs", []).append({
            "date": str(today),
            "values": new_lab_values
        })

    return patient_data


def log_event_updates(event, patient_data):
    if event["type"] == "travel":
        patient_data["travel_history"].append({
            "date": event["date"],
            "city": event["city"],
            "notes": "Work trip"
        })

    elif event["type"] == "diagnostic_test":
        # Common labs to update (with ranges)
        common_labs = {
            "ApoB": (60, 130),
            "Total Cholesterol": (150, 250),
            "LDL": (70, 160),
            "HDL": (30, 70),
            "Triglycerides": (50, 200),
            "Fasting Glucose": (70, 110),
            "HbA1c": (4, 6),
            "ALT": (10, 50),
            "Creatinine": (0.6, 1.5),
            "TSH": (0.5, 5.0),
            "CRP": (0, 3)
        }

        lab_values = {}
        for lab, (low, high) in common_labs.items():
            # get previous value if available
            prev_val = None
            if patient_data["labs"]:
                prev_val = patient_data["labs"][-1]["values"].get(lab, {}).get("value")

            if prev_val is None:
                new_val = (low + high) / 2  # default mid value
            else:
                # drift slightly while staying in bounds
                new_val = max(low, min(high, prev_val + random.choice([-5, -2, 0, 2, 5,7])))

            # unit fallback
            last_unit = None
            if patient_data["labs"]:
                last_unit = patient_data["labs"][-1]["values"].get(lab, {}).get("unit")
            if not last_unit:
                # sensible defaults
                if lab in ["HbA1c"]:
                    last_unit = "%"
                elif lab in ["Creatinine"]:
                    last_unit = "mg/dL"
                elif lab in ["TSH"]:
                    last_unit = "uIU/mL"
                elif lab in ["ALT"]:
                    last_unit = "U/L"
                elif lab in ["CRP"]:
                    last_unit = "mg/L"
                else:
                    last_unit = "mg/dL"

            lab_values[lab] = {"value": round(new_val, 2), "unit": last_unit}

        # append new test entry
        patient_data["labs"].append({
            "date": event["date"],
            "values": lab_values
        })

    elif event["type"] == "exercise_update":
        patient_data["exercise_log"].append({
            "date": event["date"],
            "activity": random.choice(["Cardio", "Strength Training", "Yoga"]),
            "duration": random.choice([30, 40, 50]),
            "perceived_exertion": random.choice(["Low", "Medium", "High"])
        })

    elif event["type"] == "diet_update":
        patient_data["diet_notes"].append({
            "date": event["date"],
            "notes": random.choice([
                "Tried intermittent fasting.",
                "Increased vegetable intake.",
                "Had too much fast food."
            ])
        })

    elif event["type"] == "medication_review":
        adherence = "Taken" if random.random() < 0.9 else "Missed"
        patient_data["medication_log"].append({
            "date": event["date"],
            "name": "Atorvastatin",
            "dose": "10mg",
            "adherence": adherence
        })

    elif event["type"] == "pain_report":
        patient_data["pain_log"].append({
            "date": event["date"],
            "location": random.choice(["Knee", "Back", "Shoulder"]),
            "pain_level": random.choice(["Mild", "Moderate", "Severe"]),
            "notes": "Patient reported discomfort during daily activity."
        })

    return patient_data


def route_query(user_input):
    text = user_input.lower()
    if any(word in text for word in ["appointment", "frustrating", "not happy","too strict and hard","not seeing",
                                     "boring"]):
        return "ruby"
    elif any(word in text for word in ["medication","blood test", "lab results", "diagnosis", "apob", "sugar level","creatinine","BP","LDL","HDL","apoa","hr","heart rate"]):
        return "warren"
    elif any(word in text for word in ["sleep", "hrv", "nap","fatigue"]):
        return "advik"
    elif any(word in text for word in ["diet", "nutrition","fast food" ,"food", "supplement","fasting", "intake", "protein","drink","water","cholesterol",
                                       "magnesium","vitamin D","fruits","meat","drank","meal"]):
        return "carla"
    elif any(word in text for word in ["exercise", "workout", "rehab", "physio","cardio","gym","strength","training", "knee","recovery",
                                       "flexibility", "stretching","stamina","cycling","low energy","yoga","back","shoudler"]):
        return "rachel"
    else:
        return "neel"


def retrieve_patient_info(query, patient_data):
    q = query.lower()
    responses = []

    # --- Vitals ---
    vitals = patient_data.get("vitals", {})
    if "bp" in q or "blood pressure" in q:
        responses.append(f"My latest BP is {vitals.get('bp', 'N/A')}.")
    if "hr" in q or "heart rate" in q:
        responses.append(f"My latest HR is {vitals.get('hr', 'N/A')}.")
    if "weight" in q:
        responses.append(f"My weight is {vitals.get('weight', 'N/A')} kg.")
    if "bmi" in q:
        responses.append(f"My BMI is {vitals.get('bmi', 'N/A')}.")

    # --- Labs ---
    if any(x in q for x in ["apob", "cholesterol", "lab", "report", "glucose", "hba1c", "liver", "kidney", "thyroid", "crp"]):
        if patient_data.get("labs"):
            last_lab = patient_data["labs"][-1]
            date = last_lab.get("date", "N/A")
            lab_values = last_lab.get("values", {})
            lab_summary = ', '.join([f"{lab}={val['value']}{val['unit']}" for lab, val in lab_values.items()])
            responses.append(f"My last labs on {date}: {lab_summary}.")
        else:
            responses.append("No lab reports available.")

    # --- Exercise ---
    if any(x in q for x in ["exercise", "workout", "training", "rehab"]):
        if patient_data.get("exercise_log"):
            last_ex = patient_data["exercise_log"][-1]
            responses.append(
                f"Recently I did {last_ex['activity']} for {last_ex['duration']} mins ({last_ex['perceived_exertion']})."
            )
        else:
            responses.append("I haven’t logged any exercise yet.")

    # --- Travel ---
    if any(x in q for x in ["travel", "trip", "city"]):
        if patient_data.get("travel_history"):
            last_trip = patient_data["travel_history"][-1]
            responses.append(
                f"I travelled to {last_trip['city']} on {last_trip['date']} ({last_trip.get('notes', '')})."
            )
        else:
            responses.append("I haven’t travelled recently.")

    # --- Diet ---
    if any(x in q for x in ["diet", "food", "meal", "nutrition"]):
        if patient_data.get("diet_notes"):
            last_diet = patient_data["diet_notes"][-1]
            responses.append(f"On {last_diet['date']} I noted: {last_diet.get('notes', '')}.")
        else:
            responses.append("I don’t have recent diet notes.")

    # --- Sleep ---
    if "sleep" in q or "rest" in q or "nap" in q:
        if patient_data.get("sleep_log"):
            last_sleep = patient_data["sleep_log"][-1]
            responses.append(
                f"My last recorded sleep was {last_sleep['duration']}h ({last_sleep['quality']}) on {last_sleep['date']}."
            )
        else:
            responses.append("No sleep data available.")

    # --- Medication ---
    if any(x in q for x in ["medication", "drug", "pill", "tablet"]):
        if patient_data.get("medication_log"):
            last_med = patient_data["medication_log"][-1]
            responses.append(
                f"My last medication was {last_med['name']} {last_med['dose']} ({last_med['adherence']}) on {last_med['date']}."
            )
        else:
            responses.append("No medication records available.")

    # --- Pain ---
    if any(x in q for x in ["pain", "ache", "injury", "discomfort"]):
        if patient_data.get("pain_log"):
            last_pain = patient_data["pain_log"][-1]
            responses.append(
                f"My last reported pain: {last_pain['location']} - {last_pain['pain_level']} on {last_pain['date']}."
            )
        else:
            responses.append("No pain reports available.")

    return " ".join(responses) if responses else "No relevant patient data found."


def ask_persona(name, user_input):
    system_prompt = personas[name]
    completion = call_with_key_rotation(
        model="deepseek/deepseek-chat-v3-0324:free",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",
             "content": f"{user_input}\nInstruction: Only give the main answer. No greetings or extra details."},
        ]
    )
    if completion is None or not completion.choices:
        print(f"No response returned for {name}")
        return f"Sorry, currently not available, will reach out to you later."

    return completion.choices[0].message.content.strip()


def ruby_triage(user_input):
    text = user_input.lower()
    # Ruby handles concierge/logistics
    if any(word in text for word in ["appointment", "frustrating", "not happy","too strict and hard","don’t really match","not seeing","boring",]):
        return "handle"
    # Otherwise she redirects to the right expert
    return "redirect"


def generate_elyx_response(message, last_elyx_actor=None):

    if last_elyx_actor and last_elyx_actor not in ["ruby"]:
        try:
            expert_reply = ask_persona(last_elyx_actor, message["text"])
        except Exception as e:
            print("LLM error:", e)
            expert_reply = "I’m having trouble responding right now."

        expert_msg = {
            "message_id": f"{message['message_id']}_expert",
            "date": message["date"],
            "actor": last_elyx_actor,
            "text": expert_reply,
            "tags": ["elyx_reply"]
        }
        # print(f"elyx ({last_elyx_actor}): {expert_reply}")
        return [expert_msg]

    # Case 2: Ruby is the entry point
    triage_result = ruby_triage(message["text"])
    if triage_result == "handle":
        ruby_reply = ask_persona("ruby", message["text"])
        print(f"elyx (Ruby): {ruby_reply}")
        return [{
            "message_id": f"{message['message_id']}_ruby",
            "date": message["date"],
            "actor": "ruby",
            "text": ruby_reply,
            "tags": ["elyx_reply"]
        }]
    else:
        # Route to doctor
        expert_name = route_query(message["text"])
        ruby_intro = f"I understand your question. Dr. {expert_name.capitalize()} will respond to you shortly."

        ruby_msg = {
            "message_id": f"{message['message_id']}_ruby",
            "date": message["date"],
            "actor": "ruby",
            "text": ruby_intro,
            "tags": ["elyx_redirect"]
        }

        expert_reply = ask_persona(expert_name, message["text"])
        expert_msg = {
            "message_id": f"{message['message_id']}_expert",
            "date": message["date"],
            "actor": expert_name,
            "text": expert_reply,
            "tags": ["elyx_reply"]
        }

        return [ruby_msg, expert_msg]



def patient_followup(last_elyx_msg, patient_data):
    retrieved = retrieve_patient_info(last_elyx_msg["text"], patient_data)
    if retrieved:
        return retrieved
    elif "?" in last_elyx_msg["text"] or "Would you" in last_elyx_msg["text"]:
        return "Yes, that works for me." if random.random() < ADHERENCE_RATE else "Not sure."
    else:
        return "Thanks for the info!"



ACTION_KEYWORDS = [
    "increase", "reduce", "start", "stop", "schedule", "add", "remove",
    "try", "adjust", "modify", "switch", "alternate", "change", "continue", "incorporate", "balance", "improve",
    "consult", "review", "monitor", "evaluate", "check", "assess", "measure", "intensify", "optimize", "re-evaluate",
    "prioritize", "avoid", "limit", "replace", "focus on", "follow", "adopt", "implement", "pack", "hydrate",
    "ensure", "maintain", "track"
]

def ask_actor_decision(actor, evidence_message, decision_summary):
    if actor not in personas:
        pass

    system_prompt = (
        f"{personas[actor]}\n\n"
        "Task:\n"
        "You are reviewing a patient message (evidence) and a draft decision summary by you.\n"
        "Your role is to state the reason for the decision based on your persona.\n\n"
        "Rules:\n"
        "• STRICT: Answer in 1–2 short sentences only.\n"
        "• Do not repeat the decision summary.\n"
        "• Stay in persona tone (doctorly, supportive, empathetic, etc).\n"
        "• No greetings, disclaimers, or hand-offs.\n"
    )

    user_prompt = f"""
    Evidence message:{evidence_message}
    Draft decision:{decision_summary}
    """

    try:
        completion = call_with_key_rotation(
            model="deepseek/deepseek-chat-v3-0324:free",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        return f"{actor.capitalize()} decided this to adjust patient’s plan based on the history."



def detect_decision(message, patient_msg_id, patient_msg_text=None):
    if any(kw in message["text"].lower() for kw in ACTION_KEYWORDS):
        # Which Elyx actor is making the decision
        decision_actor = message["actor"]

        decision_summary = message["text"].split(".")[0]

        reason = ask_actor_decision(
            decision_actor.lower(),
            evidence_message=patient_msg_text or "",
            decision_summary=decision_summary
        )

        return {
            "decision_id": f"dec_{message['message_id']}",
            "date": message["date"],
            "type": "plan_change",
            "summary": decision_summary,
            "actor": decision_actor,
            "rationale": "Auto-extracted from Elyx message.",
            "evidence_message_ids": [patient_msg_id, message["message_id"]],
            "status": "active",
            "reason": reason
        }
    return None


def update_ops_metrics(metrics, message):
    role = message["actor"]
    if role in ROLE_TIME:
        metrics[role]["minutes"] += ROLE_TIME[role]
        metrics[role]["messages"] += 1


def generate_patient_summary(patient_data, entries=2):

    summary_parts = []

    name = patient_data.get('profile', {}).get('name', 'N/A')
    summary_parts.append(f"Patient {name} recent data:")

    # Vitals
    vitals = patient_data.get('vitals', {})
    bp = vitals.get('bp')
    hr = vitals.get('hr')
    weight = vitals.get('weight')
    bmi = vitals.get('bmi')
    vitals_text = ", ".join([f"BP={bp}" if bp else "",
                             f"HR={hr}" if hr else "",
                             f"Wt={weight}kg" if weight else "",
                             f"BMI={bmi}" if bmi else ""]).strip(", ")
    if vitals_text:
        summary_parts.append(f"- Vitals: {vitals_text}")

    # Labs
    labs = patient_data.get('labs', [])[-entries:]
    if labs:
        labs_texts = []
        for lab_day in labs:
            date = lab_day.get('date', '')
            values = lab_day.get('values', {})
            lab_vals = ", ".join([f"{k}={v['value']}" for k, v in values.items()])
            labs_texts.append(f"{lab_vals} ({date})")
        summary_parts.append(f"- Labs: {'; '.join(labs_texts)}")

    # Exercise
    ex = patient_data.get('exercise_log', [])[-entries:]
    if ex:
        ex_texts = [f"{e['activity']} {e['duration']}min ({e['perceived_exertion']})" for e in ex]
        summary_parts.append(f"- Exercise: {', '.join(ex_texts)}")

    # Diet
    diet = patient_data.get('diet_notes', [])[-entries:]
    if diet:
        diet_texts = [f"{d['notes']}" for d in diet]
        summary_parts.append(f"- Diet: {', '.join(diet_texts)}")

    # Sleep
    sleep = patient_data.get('sleep_log', [])[-entries:]
    if sleep:
        sleep_texts = [f"{s['duration']}h({s['quality']})" for s in sleep]
        summary_parts.append(f"- Sleep: {', '.join(sleep_texts)}")

    # Medication
    meds = patient_data.get('medication_log', [])[-entries:]
    if meds:
        meds_texts = [f"{m['name']} {m['dose']}({m['adherence']})" for m in meds]
        summary_parts.append(f"- Meds: {', '.join(meds_texts)}")

    # Pain
    pain = patient_data.get('pain_log', [])[-entries:]
    if pain:
        pain_texts = [f"{p['location']}({p['pain_level']})" for p in pain]
        summary_parts.append(f"- Pain: {', '.join(pain_texts)}")

    # Travel
    travel = patient_data.get('travel_history', [])[-entries:]
    if travel:
        travel_texts = [f"{t['city']}" for t in travel]
        summary_parts.append(f"- Travel: {', '.join(travel_texts)}")

    return "\n".join(summary_parts)


def ask_patient(user_input, patient_data):
    patient_summary = generate_patient_summary(patient_data)

    system_prompt = f"""
You are Patient. Based on your recent data:
{patient_summary}

Reply to the following doctor. Only provide the necessary information requested. 
If the doctor does not ask for any data and only provides a suggestion, end your reply with a polite acknowledgment with thank. 
If the doctor asks something do not end the conversation, provide what is asked in humanized way
Do not include greetings, extra details, or unrelated information.
"""

    try:
        completion = call_with_key_rotation(
            model="deepseek/deepseek-chat-v3-0324:free",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ]
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        return "ok, thank you"





def run_simulation():
    start = date(2025, 8, 18)
    events = generate_patient_schedule(start, MONTHS)

    chat_log, decisions = [], []
    ops_metrics = {r: {"minutes": 0, "messages": 0} for r in ROLE_TIME}
    msg_id = 1
    patient_snapshots = []  # to store readable parameters per patient message

    global patient_data
    day = start
    total_days = MONTHS * 30
    msg_id_letter = string.ascii_lowercase
    conversation_durations = []

    for i in range(total_days):
        patient_data = daily_update(patient_data, today=day)

        todays_events = [e for e in events if e["date"] == str(day)]
        last_end_time = None
        for event in todays_events:
            print()
            snapshot = {
                "date": event["date"],
                "bp": patient_data["vitals"]["bp"],
                "hr": patient_data["vitals"]["hr"],
                "weight": patient_data["vitals"]["weight"],
                "hrv": patient_data["vitals"].get("hrv"),
                "sleep": patient_data["sleep_log"][-1] if patient_data["sleep_log"] else None,

                # Labs — store each lab separately
                "Total Cholesterol": patient_data["labs"][-1]["values"].get("Total Cholesterol", {}).get("value") if
                patient_data["labs"] else None,
                "LDL": patient_data["labs"][-1]["values"].get("LDL", {}).get("value") if patient_data["labs"] else None,
                "HDL": patient_data["labs"][-1]["values"].get("HDL", {}).get("value") if patient_data["labs"] else None,
                "Triglycerides": patient_data["labs"][-1]["values"].get("Triglycerides", {}).get("value") if
                patient_data["labs"] else None,
                "ApoB": patient_data["labs"][-1]["values"].get("ApoB", {}).get("value") if patient_data[
                    "labs"] else None,

                # Sugar levels
                "Fasting Glucose": patient_data["labs"][-1]["values"].get("Fasting Glucose", {}).get("value") if
                patient_data["labs"] else None,
                "HbA1c": patient_data["labs"][-1]["values"].get("HbA1c", {}).get("value") if patient_data[
                    "labs"] else None,
                "Sugar Level": {
                    "Fasting": patient_data["labs"][-1]["values"].get("Fasting Glucose", {}).get("value") if
                    patient_data["labs"] else None,
                    "HbA1c": patient_data["labs"][-1]["values"].get("HbA1c", {}).get("value") if patient_data[
                        "labs"] else None
                },

                "ALT": patient_data["labs"][-1]["values"].get("ALT", {}).get("value") if patient_data["labs"] else None,
                "Creatinine": patient_data["labs"][-1]["values"].get("Creatinine", {}).get("value") if patient_data[
                    "labs"] else None,
                "TSH": patient_data["labs"][-1]["values"].get("TSH", {}).get("value") if patient_data["labs"] else None,
                "CRP": patient_data["labs"][-1]["values"].get("CRP", {}).get("value") if patient_data["labs"] else None
            }


            patient_snapshots.append(snapshot)

            patient_data = log_event_updates(event, patient_data)

            conversation_ongoing = True
            last_message = None
            turn_count = 0
            last_elyx_actor = None
            letter_index = 0
            # Pick a start time that comes after the last conversation
            start_time = random_wake_time(day, last_end_time)

            if not start_time:
                # If no room left today, push to tomorrow
                next_day = day + timedelta(days=1)
                start_time = random_wake_time(next_day)
                event["date"] = str(next_day)
                day = next_day  # move simulation forward

            current_time = start_time

            # Patient initiates message
            p_msg = {
                "message_id": f"msg_{msg_id}{msg_id_letter[letter_index]}",
                "date": event["date"],
                "actor": PATIENT_NAME,
                "text": generate_patient_event_msg(event, patient_data),
                "tags": [event["type"]],
                "timestamp": current_time.isoformat()
            }
            chat_log.append(p_msg)
            print(f"patient: {p_msg['text']}")
            last_message = p_msg
            letter_index += 1
            conv_start_time = datetime.fromisoformat(p_msg["timestamp"])
            while conversation_ongoing:
                if last_message["actor"] == PATIENT_NAME:
                    start_time = time.time()
                    elyx_responses = generate_elyx_response(last_message, last_elyx_actor)
                    elapsed_time = time.time() - start_time
                    print(f"{elapsed_time:.2f} sec")

                    # Add Elyx responses & track metrics
                    for e_msg in elyx_responses:
                        e_msg["message_id"] = f"msg_{msg_id}{msg_id_letter[letter_index]}"
                        letter_index += 1
                        current_time = add_doctor_reply_time(current_time)
                        e_msg["timestamp"] = current_time.isoformat()
                        chat_log.append(e_msg)
                        print(f"{e_msg['actor']}: {e_msg['text']}")
                        update_ops_metrics(ops_metrics, e_msg)
                        decision = detect_decision(e_msg, p_msg["message_id"], p_msg["text"])
                        if decision:
                            decisions.append(decision)

                    # Patient follow-up is based on *last* Elyx message
                    last_elyx_msg = elyx_responses[-1]
                    last_elyx_actor = last_elyx_msg["actor"]
                    last_message = last_elyx_msg
                else:
                    reply_text = ask_patient(last_elyx_msg["text"], patient_data)
                    current_time = next_patient_msg_time(current_time)
                    p_follow = {
                        "message_id": f"msg_{msg_id}{msg_id_letter[letter_index]}",
                        "date": event["date"],
                        "actor": PATIENT_NAME,
                        "text": reply_text,
                        "tags": ["followup"],
                        "timestamp": current_time.isoformat()
                    }
                    letter_index += 1
                    chat_log.append(p_follow)
                    last_message = p_follow
                    print(f"patient: {reply_text}")

                    if any(kw in reply_text.lower() for kw in ["thanks", "thank you", "ok got it", "that helps","ok"]):
                        # Add a polite closing by Ruby or Neel
                        closing = random.choice([
                            "Thanks Rohan, we’ll stay in touch. Have a great day!",
                            "Noted. Wishing you good health!",
                            "Appreciate your update, take care."
                        ])
                        closing_msg = {
                            "message_id": f"msg_{msg_id}_closing",
                            "date": event["date"],
                            "actor": "ruby",
                            "text": closing,
                            "tags": ["closing"],
                            "timestamp": current_time.isoformat()
                        }
                        chat_log.append(closing_msg)
                        print(f"{closing_msg['actor']} (closing): {closing}")
                        conversation_ongoing = False
                turn_count += 1
                if turn_count > 6:  # safety cutoff
                    conversation_ongoing = False
                last_end_time = current_time

            msg_id += 1
            conv_end_time = datetime.fromisoformat(chat_log[-1]['timestamp'])
            duration = (conv_end_time - conv_start_time).total_seconds() / 60

            doctor_msgs = [m for m in chat_log[-letter_index:] if "elyx_reply" in m.get("tags", [])]
            doctor_durations = {}
            if doctor_msgs:
                from collections import defaultdict
                doctor_times = defaultdict(list)
                for m in doctor_msgs:
                    doctor_times[m["actor"]].append(datetime.fromisoformat(m["timestamp"]))
                for doctor, times in doctor_times.items():
                    doctor_durations[doctor] = duration  # use total conversation duration

            conversation_durations.append({
                "date": event["date"],
                "total_duration": duration,
                "doctor_durations": doctor_durations
            })

            with open(r"E:\elyx_hackathon\json_files\chats.json", "w") as f:
                json.dump(chat_log, f, indent=2)
            with open(r"E:\elyx_hackathon\json_files\decisions.json", "w") as f:
                json.dump(decisions, f, indent=2)
            with open(r"E:\elyx_hackathon\json_files\patient_snapshots.json", "w") as f:
                json.dump(patient_snapshots, f, indent=2)
            with open(r"E:\elyx_hackathon\json_files\conversation_duration.json", "w") as f:
                json.dump(conversation_durations, f, indent=2)

        day += timedelta(days=1)

    weekly, monthly = defaultdict(list), defaultdict(list)
    for conv_dur, event in zip(conversation_durations, events):
        d = datetime.fromisoformat(event["date"])
        weekly[d.isocalendar()[1]].append(conv_dur["total_duration"])
        monthly[d.month].append(conv_dur["total_duration"])


    with open(r"E:\elyx_hackathon\json_files\final_patient_data.json", "w") as f:
        json.dump(patient_data, f, indent=2)


    print("Simulation complete.")


if __name__ == "__main__":
    run_simulation()

