# -*- coding: utf-8 -*-
"""
AUB Compass – AUB Tutoring & Course Advisor
Ready-to-deploy Gradio app for Hugging Face Spaces.
"""

import os, datetime, textwrap, csv, json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from dotenv import load_dotenv
from pypdf import PdfReader
from openai import OpenAI
import gradio as gr

# --- Setup Paths ---
root = Path(".")
(me := root / "me").mkdir(parents=True, exist_ok=True)
(logs := root / "logs").mkdir(exist_ok=True)

# --- Service Definition ---
academic_service = {
    "name": "AUB Compass Tutoring Service",
    "mission": "Empower AUB students with personalized course recommendations and tutoring support to make confident academic decisions and excel in their studies.",
    "services": [
        "AI Course Advisor - answers questions about AUB courses, majors, electives, and prerequisites.",
        "Study Planner - helps organize semester schedules and balance workloads.",
        "Skill Path Finder - recommends electives and minors for goals like data science, writing, or communication.",
        "Tutoring Resource Hub - provides study tips and subject guidance.",
        "Feedback Tracker - records common questions to improve service quality."
    ],
    "team": [
        {"name": "Academic Director - Dr. Layla Haddad", "bio": "Oversees tutoring quality and curriculum alignment."},
        {"name": "Technical Lead - Rami Choueiri", "bio": "Responsible for the AUB Compass AI platform and integrations."},
        {"name": "Student Success Lead - Nour Mansour", "bio": "Coordinates tutoring sessions and student onboarding."}
    ],
    "value_prop": [
        "Combines academic expertise with intelligent guidance for fast, accurate advice.",
        "Encourages students to verify choices with official AUB advisors before registration.",
        "Provides consistent, supportive, and ethical tutoring help."
    ],
    "contact": "support@aubcompass.example (fictional)",
    "copyright": f"(c) {datetime.datetime.utcnow().year} AUB Compass Tutoring Service - Fictional service for coursework."
}

def ascii_safe(s):
    for k, v in [("—","-"),("–","-")]:
        s = s.replace(k,v)
    return s

# --- Create Service Identity Files ---
lines = [
    academic_service["name"] + " - Service Profile",
    "",
    "Mission: " + academic_service["mission"],
    "",
    "Services:"
] + ["* " + s for s in academic_service["services"]] + [
    "",
    "Team:"
] + ["* " + m["name"] + ": " + m["bio"] for m in academic_service["team"]] + [
    "",
    "Value Proposition:"
] + ["* " + v for v in academic_service["value_prop"]] + [
    "",
    "Contact: " + academic_service["contact"],
    academic_service["copyright"]
]
lines = [ascii_safe(x) for x in lines]

def save_text_as_pdf(lines, path):
    width, height, margin, line_h = 1240, 1754, 28, 28
    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()
    y = margin
    for raw in lines:
        for w in textwrap.wrap(raw, width=95) or [""]:
            if y + line_h > height - margin:
                break
            draw.text((margin, y), w, font=font, fill=(0,0,0))
            y += line_h
    img.save(path, "PDF", resolution=150.0)

pdf_path = me / "about_service.pdf"
save_text_as_pdf(lines, str(pdf_path))

summary_lines = [
    academic_service["name"] + " - Summary",
    "",
    "Mission",
    "-------",
    academic_service["mission"],
    "",
    "What We Offer",
    "-------------",
] + ["- " + s for s in academic_service["services"]] + [
    "",
    "Team",
    "----",
] + ["- " + m["name"] + ": " + m["bio"] for m in academic_service["team"]] + [
    "",
    "Value Proposition",
    "-----------------",
] + ["- " + v for v in academic_service["value_prop"]] + [
    "",
    "Contact",
    "-------",
    academic_service["contact"],
    "",
    "(For academic use - fictional tutoring service identity.)",
]
(me / "service_summary.txt").write_text("\n".join(summary_lines), encoding="utf-8")

# --- Tool Functions ---
students_csv = logs / "students.csv"
feedback_csv = logs / "feedback.csv"

if not students_csv.exists():
    with open(students_csv, "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow(["ts_iso", "email", "name", "message"])
if not feedback_csv.exists():
    with open(feedback_csv, "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow(["ts_iso", "question", "notes"])

def record_student_interest(email: str, name: str, message: str):
    ts = datetime.datetime.utcnow().isoformat()
    with open(students_csv, "a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow([ts, email, name, message])
    return {"ok": True, "ts": ts}

def record_feedback(question: str):
    ts = datetime.datetime.utcnow().isoformat()
    with open(feedback_csv, "a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow([ts, question, "model didn't know"])
    return {"ok": True, "ts": ts}

# --- Sample Course Catalog ---
courses = {
    "CMPS 270": "Machine Learning - Introduction to algorithms and model training. Prereq: CMPS 200.",
    "DATA 200": "Introduction to Data Science - Fundamentals of data visualization and analysis.",
    "STAT 233": "Probability and Statistics - Covers probability theory, random variables, and data analysis.",
    "ECON 222": "Econometrics I - Quantitative methods for economics and social sciences.",
    "ENGL 203": "Academic Writing - Advanced academic writing and research composition.",
    "BIOL 201": "Cell and Molecular Biology - Core molecular and cellular biology principles."
}

# --- Load Context ---
load_dotenv()
SUMMARY_PATH = "me/service_summary.txt"
PDF_PATH = "me/about_service.pdf"

def load_service_context():
    summary, pdf_text = "", ""
    if os.path.exists(SUMMARY_PATH):
        with open(SUMMARY_PATH, "r", encoding="utf-8") as f:
            summary = f.read()
    if os.path.exists(PDF_PATH):
        try:
            reader = PdfReader(PDF_PATH)
            for page in reader.pages:
                pdf_text += page.extract_text() + "\n"
        except Exception as e:
            pdf_text = f"(PDF text unavailable: {e})"
    return summary, pdf_text

# --- Agent System Prompt ---
SYSTEM_PROMPT = (
    "You are AUB Compass, the official tutoring and course-advising assistant for the American University of Beirut (AUB). "
    "You help students explore courses, understand prerequisites, plan study paths, and find tutoring help. "
    "Keep your tone professional, encouraging, and factual. "
    "If unsure, call record_feedback with the question. "
    "If student seeks tutoring, call record_student_interest with their info."
)

# --- AI Agent Logic ---
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

tools = [
    {"type": "function", "function": {
        "name": "record_student_interest",
        "description": "Store student info for follow-up.",
        "parameters": {
            "type": "object",
            "properties": {
                "email": {"type": "string"},
                "name": {"type": "string"},
                "message": {"type": "string"}
            },
            "required": ["email", "name", "message"]
        }
    }},
    {"type": "function", "function": {
        "name": "record_feedback",
        "description": "Log unanswered question.",
        "parameters": {
            "type": "object",
            "properties": {
                "question": {"type": "string"}
            },
            "required": ["question"]
        }
    }}
]

def run_agent(user_text, history):
    summary, pdf_text = load_service_context()
    course_block = "AUB Courses:\n" + "\n".join([f"- {k}: {v}" for k,v in courses.items()])
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "system", "content": f"SUMMARY:\n{summary}"},
        {"role": "system", "content": f"PDF:\n{pdf_text}"},
        {"role": "system", "content": course_block}
    ]
    for role, content in history:
        messages.append({"role": role, "content": content})
    messages.append({"role": "user", "content": user_text})

    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=tools,
        tool_choice="auto",
        temperature=0.2
    )
    msg = resp.choices[0].message
    if getattr(msg, 'tool_calls', None):
        for call in msg.tool_calls:
            args = json.loads(call.function.arguments or "{}")
            if call.function.name == "record_student_interest":
                record_student_interest(**args)
            elif call.function.name == "record_feedback":
                record_feedback(**args)
        return "Thanks! Your message was logged for follow-up."
    return msg.content

# --- Gradio Interface ---
with gr.Blocks(title="AUB Compass – Tutoring & Course Advisor") as demo:
    gr.Markdown("## 🎓 AUB Compass — Intelligent Tutoring & Course Advisor")
    gr.Markdown("Ask about AUB courses, electives, or tutoring help (fictional demo).")
    chat = gr.Chatbot()
    state = gr.State([])

    def respond(user, history, st):
        linear = []
        for u, a in history:
            if u: linear.append(("user", u))
            if a: linear.append(("assistant", a))
        reply = run_agent(user, linear)
        history.append([user, reply])
        st.append(("user", user)); st.append(("assistant", reply))
        return history, st

    inp = gr.Textbox(placeholder="Ask about AUB courses, tutoring, or recommendations...", label="Message")
    inp.submit(respond, [inp, chat, state], [chat, state])

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
