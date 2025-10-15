## 🧭 AUB Compass: AI-Powered Tutoring & Course Advisor

### 📘 Overview

**AUB Compass** is an intelligent tutoring and course-advising assistant built for the **American University of Beirut (AUB)**.
It helps students explore courses, understand prerequisites, plan their study paths, and get tutoring guidance — all through an AI-powered chat interface.

This project demonstrates how an academic guidance assistant can combine structured university data with conversational AI to deliver contextual academic support.

---

### ✨ Features

* **AI Course Advisor:** Answers questions about AUB courses, prerequisites, and electives.
* **Study Planner:** Suggests semester plans and balanced workloads.
* **Skill Path Finder:** Recommends electives or minors for specific career goals (e.g. Data Science, Communication).
* **Tutoring Hub:** Offers study tips and guidance from fictional academic staff.
* **Feedback Logger:** Collects unanswered questions to improve the model.

---

### 🧠 Architecture

| Component                   | Description                                              |
| --------------------------- | -------------------------------------------------------- |
| `run_agent()`               | Core logic connecting the chat interface and OpenAI API. |
| `record_student_interest()` | Logs student tutoring requests (email, name, message).   |
| `record_feedback()`         | Records unknown or unclear user queries.                 |
| `save_text_as_pdf()`        | Creates service profile documents for context.           |
| `gradio` UI                 | Provides a user-friendly chat interface for students.    |

---

### ⚙️ Installation

```bash
pip install -U openai gradio python-dotenv pypdf pillow
```

---

### 🚀 Running the Demo

Run the Gradio web demo locally:

```bash
saad_agent_powered.ipynb
```

Then open the Gradio link (shown in terminal) to start chatting with **AUB Compass**.

Alternatively, in Google Colab:


---

### Running python file
```bash
conda create -n aubcompass python=3.10
conda activate aubcompass
pip install -r requirements.txt

```
### Running in Hugging Face

https://huggingface.co/spaces/zainabsaad/Agent-Powered

### 🧩 Example Conversation

**User:** “I'm a sophomore in Computer Science. Which electives help with data skills?”
**AUB Compass:** “You could consider *DATA 200 – Introduction to Data Science* and *STAT 233 – Probability and Statistics*. If you’ve completed *CMPS 200*, you may also take *CMPS 270 – Machine Learning* next semester.”

---

### 👩‍🏫 Credits

**Developed by:** *Zainab Saad (202472448)*
