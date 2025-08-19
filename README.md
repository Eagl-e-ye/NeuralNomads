# NeuralNomads

# Elyx Chatbot Simulation

## 📌 Overview
This project is an **8-month long chatbot simulation** that models interactions between a patient and a team of virtual healthcare experts.  

We used **DeepSeek R1 630B** through the OpenRouter API to:
- Simulate a **patient persona** who reports daily updates, symptoms, and questions.  
- Simulate multiple **health experts** (doctor, nutritionist, physiotherapist, etc.) who respond to the patient based on predefined roles, tone, and rules.  

The system not only tracks conversations but also:
- **Simulates patient health parameters daily** using algorithms (vitals, labs, sleep, medication adherence, etc.).  
- **Rotates API keys** to bypass token usage limits.  
- **Tracks decisions** made by experts and explains their rationale.  
- **Generates structured logs** (conversations, decisions, patient snapshots, operational metrics).  

⚠️ **Note:** All the conversations are generated using **LLMs (DeepSeek R1 630B)** and are AI-simulated.

---
## 🖥️ Webpage Visualization
A **webpage interface** is included to visualize how the simulation took place.  
- It loads the JSON files (`chats.json`, `decisions.json`, etc.).  
- Displays **conversation timelines** between the patient and experts.  
- Highlights **decision points** and operational metrics.  

This allows a clear replay of the 8-month simulation in a user-friendly format.

---

## 🖼️ Demo & Screenshots
**CHATS_OUTPUT_.txt** → **Human-readable transcript of all chats**. 

The `screenshots/` folder contains:
- Example screenshots of patient–expert conversations.  
- A walkthrough **video demo** showing how the simulation unfolds.

## 🖼️ Screenshots

<p align="center">
  <img src="Screenshots/Screenshot%202025-08-19%20204444.png" width="30%">
  <img src="Screenshots/Screenshot%202025-08-19%20204519.png" width="30%">
  <img src="Screenshots/Screenshot%202025-08-19%20204606.png" width="30%">
</p>

## 🎥 Demo Video
[▶️ Watch the demo](Screenshots/how%20to%20use.mp4)

---
## 🏗️ Simulation Design

### Personas (Experts)
Each expert has a **system prompt persona**:
- **Ruby** – Concierge & triage (routes to specialists or handles logistics).  
- **Dr. Warren** – Medical strategist (lab interpretation, medical direction).  
- **Advik** – Performance scientist (sleep, HRV, recovery).  
- **Carla** – Nutritionist (diet, supplements, meal adjustments).  
- **Rachel** – Physiotherapist (exercise, rehab, injuries).  
- **Neel** – Concierge lead (relationship management, reassurance).  

### Patient
- Named **Rohan**, age 45, with high cholesterol.  
- Daily updates in vitals, sleep, diet, exercise, medication, labs, and pain logs.  
- Simulated **adherence rate** of 50% to recommendations.  

### Conversation Loop
1. Patient event is generated (travel, diagnostic test, diet update, pain report, etc.).  
2. **Patient message** starts the conversation.  
3. **Ruby triages** the query → either responds or routes to the right expert.  
4. Expert replies in their tone and role.  
5. Patient follows up with contextual replies based on their data.  
6. Conversation closes politely (Ruby/Neel).  

### Key Features
- **Decision Extraction**: Detects when an expert makes a treatment/plan change and records the reason.  
- **Operational Metrics**: Tracks time spent and messages per role.  
- **API Key Rotation**: Ensures uninterrupted simulation by cycling through API keys.  
- **Patient Summary**: Concise health summary used to guide patient responses.  

---

## 📂 Code Structure (`elyx.py`)

### 🔑 API Handling
- `API_KEYS` list stores multiple API keys.  
- `call_with_key_rotation()` rotates keys when rate limits or failures occur.  

### 🧑‍⚕️ Simulation Functions
- `generate_patient_schedule()` → defines events over 8 months.  
- `generate_patient_event_msg()` → creates realistic patient queries.  
- `daily_update()` → updates vitals, labs, sleep, meds, and pain logs daily.  
- `log_event_updates()` → logs structured updates based on events.  

### 🧠 Query Routing & Responses
- `route_query()` → decides which expert handles the message.  
- `ask_persona()` → queries DeepSeek with expert persona.  
- `ruby_triage()` → decides if Ruby handles or forwards.  
- `generate_elyx_response()` → generates expert responses (with Ruby introduction if needed).  
- `ask_patient()` → generates patient’s natural reply based on current health summary.  

### 📝 Decision Tracking
- `detect_decision()` → checks if expert response implies a plan change.  
- `ask_actor_decision()` → asks the expert persona to explain reasoning.  

### 📊 Metrics & Logging
The simulation produces **multiple structured outputs** (all attached in this repository):

**CHATS_OUTPUT_.txt** → **Human-readable transcript of all chats**. 
- `chats.json` → Full structured conversation logs with metadata.  
- `decisions.json` → Extracted expert decisions and their rationale.  
- `patient_snapshots.json` → Daily patient health states (vitals, labs, adherence).  
- `conversation_duration.json` → Time and length of conversations per event.  
- `final_patient_data.json` → Final patient state after 8 months.  

👉 These files clearly demonstrate how the simulation ran end-to-end and are essential to understanding the project.

---

## 📊 Example Data Flow
1. Patient: *"I’ll be in Mumbai next week. How do I stay on track with diet and exercise?"*  
2. Ruby: *"I understand your question. Carla (Nutritionist) will respond to you shortly."*  
3. Carla: *"Since you’ll be traveling, focus on lighter meals and portable snacks like fruits and nuts."*  
4. Patient: *"Thanks, I’ll do that."*  
5. Ruby: *"Wishing you good health!"*  

---


## ⚙️ Requirements
- Python 3.9+  
- OpenAI Python SDK  
- Valid OpenRouter API keys (add to `API_KEYS` list).  

Install dependencies:
```bash
pip install openai
