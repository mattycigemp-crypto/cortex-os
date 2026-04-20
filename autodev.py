import requests
import time
import os
import json
from datetime import datetime

# ---------------- CONFIG ----------------
OLLAMA_URL = "http://localhost:11434/api/chat"

BASE_DIR = r"C:\AI-Dev-Swarm"
TASK_FILE = os.path.join(BASE_DIR, "tasks.txt")
WORKSPACE = os.path.join(BASE_DIR, "workspace")
LOG_FILE = os.path.join(BASE_DIR, "logs", "log.txt")
STATE_FILE = os.path.join(BASE_DIR, "state", "state.json")

os.makedirs(WORKSPACE, exist_ok=True)
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)

# ---------------- UTIL ----------------

def log(msg):
    line = f"[{datetime.now()}] {msg}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def load_state():
    if not os.path.exists(STATE_FILE):
        return {"done": []}
    return json.load(open(STATE_FILE, "r", encoding="utf-8"))


def save_state(state):
    json.dump(state, open(STATE_FILE, "w", encoding="utf-8"), indent=2)


def get_tasks():
    if not os.path.exists(TASK_FILE):
        return []
    with open(TASK_FILE, "r", encoding="utf-8") as f:
        return [t.strip() for t in f.readlines() if t.strip()]


# ---------------- OLLAMA CALL ----------------

def call(model, prompt):
    r = requests.post(OLLAMA_URL, json={
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False
    })
    return r.json()["message"]["content"]


# ---------------- AGENTS ----------------

def planner(task):
    return call("qwen2.5-coder:14b", f"""
You are a software architect.

Break this into steps and file changes:

{task}
""")


def executor(plan):
    return call("deepseek-coder:6.7b", f"""
You are a senior developer.

Write the actual code or file changes:

{plan}
""")


def reviewer(code):
    return call("qwen2.5-coder:14b", f"""
You are a strict code reviewer.

Find bugs, issues, or missing logic:

{code}
""")


# ---------------- FILE OUTPUT ----------------

def save_output(task, content):
    safe_name = str(abs(hash(task)))
    file_path = os.path.join(WORKSPACE, f"task_{safe_name}.txt")

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

    return file_path


# ---------------- PIPELINE ----------------

def run_task(task):
    log(f"🧠 Planning: {task}")
    plan = planner(task)

    log("⚙️ Executing...")
    code = executor(plan)

    log("🔍 Reviewing...")
    review = reviewer(code)

    if any(word in review.lower() for word in ["bug", "error", "fix", "issue"]):
        log("🔁 Fixing issues...")
        code = executor(plan + "\n\nFix this:\n" + review)

    path = save_output(task, code)
    log(f"💾 Saved output: {path}")

    return path


# ---------------- MAIN LOOP ----------------

def main():
    log("🚀 AI Dev Swarm Started")

    state = load_state()

    while True:
        tasks = get_tasks()

        for task in tasks:
            if task in state["done"]:
                continue

            try:
                run_task(task)
                state["done"].append(task)
                save_state(state)

            except Exception as e:
                log(f"❌ ERROR: {e}")

        time.sleep(5)

import time
import os
import json
from datetime import datetime

# ---------------- CONFIG ----------------
OLLAMA_URL = "http://localhost:11434/api/chat"

BASE_DIR = r"C:\AI-Dev-Swarm"
TASK_FILE = os.path.join(BASE_DIR, "tasks.txt")
WORKSPACE = os.path.join(BASE_DIR, "workspace")
LOG_FILE = os.path.join(BASE_DIR, "logs", "log.txt")
STATE_FILE = os.path.join(BASE_DIR, "state", "state.json")

os.makedirs(WORKSPACE, exist_ok=True)
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)

# ---------------- UTIL ----------------

def log(msg):
    line = f"[{datetime.now()}] {msg}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def load_state():
    if not os.path.exists(STATE_FILE):
        return {"done": []}
    return json.load(open(STATE_FILE, "r", encoding="utf-8"))


def save_state(state):
    json.dump(state, open(STATE_FILE, "w", encoding="utf-8"), indent=2)


def get_tasks():
    if not os.path.exists(TASK_FILE):
        return []
    with open(TASK_FILE, "r", encoding="utf-8") as f:
        return [t.strip() for t in f.readlines() if t.strip()]


# ---------------- OLLAMA CALL ----------------

def call(model, prompt):
    r = requests.post(OLLAMA_URL, json={
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False
    })
    return r.json()["message"]["content"]


# ---------------- AGENTS ----------------

def planner(task):
    return call("qwen2.5-coder:14b", f"""
You are a software architect.

Break this into steps and file changes:

{task}
""")


def executor(plan):
    return call("deepseek-coder:6.7b", f"""
You are a senior developer.

Write the actual code or file changes:

{plan}
""")


def reviewer(code):
    return call("qwen2.5-coder:14b", f"""
You are a strict code reviewer.

Find bugs, issues, or missing logic:

{code}
""")


# ---------------- FILE OUTPUT ----------------

def save_output(task, content):
    safe_name = str(abs(hash(task)))
    file_path = os.path.join(WORKSPACE, f"task_{safe_name}.txt")

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

    return file_path


# ---------------- PIPELINE ----------------

def run_task(task):
    log(f"🧠 Planning: {task}")
    plan = planner(task)

    log("⚙️ Executing...")
    code = executor(plan)

    log("🔍 Reviewing...")
    review = reviewer(code)

    if any(word in review.lower() for word in ["bug", "error", "fix", "issue"]):
        log("🔁 Fixing issues...")
        code = executor(plan + "\n\nFix this:\n" + review)

    path = save_output(task, code)
    log(f"💾 Saved output: {path}")

    return path


# ---------------- MAIN LOOP ----------------

def main():
    log("🚀 AI Dev Swarm Started")

    state = load_state()

    while True:
        tasks = get_tasks()

        for task in tasks:
            if task in state["done"]:
                continue

            try:
                run_task(task)
                state["done"].append(task)
                save_state(state)

            except Exception as e:
                log(f"❌ ERROR: {e}")

        time.sleep(5)


if __name__ == "__main__":
    main()