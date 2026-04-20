import requests
import time
import os
import json
import subprocess
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

# ---------------- PATHS ----------------

BASE = r"C:\AI-Dev-Swarm"

TASKS_FILE = os.path.join(BASE, "tasks.txt")
RULES_FILE = os.path.join(BASE, "system_rules.txt")

WORKSPACE = os.path.join(BASE, "workspace")
PR_DIR = os.path.join(BASE, "pr")
STATE_FILE = os.path.join(BASE, "state", "state.json")
LOG_FILE = os.path.join(BASE, "logs", "log.txt")

os.makedirs(WORKSPACE, exist_ok=True)
os.makedirs(PR_DIR, exist_ok=True)
os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

OLLAMA = "http://localhost:11434/api/chat"


# ---------------- LOGGING ----------------

def log(msg):
    line = f"[{datetime.now()}] {msg}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


# ---------------- STATE ----------------

def load_state():
    if not os.path.exists(STATE_FILE):
        return {"completed_tasks": [], "metrics": {}}
    return json.load(open(STATE_FILE, "r", encoding="utf-8"))


def save_state(state):
    json.dump(state, open(STATE_FILE, "w", encoding="utf-8"), indent=2)


# ---------------- TASKS ----------------

def load_tasks():
    if not os.path.exists(TASKS_FILE):
        return []
    return [t.strip() for t in open(TASKS_FILE, encoding="utf-8") if t.strip()]


def load_rules():
    if not os.path.exists(RULES_FILE):
        return ""
    return open(RULES_FILE, encoding="utf-8").read()


# ---------------- OLLAMA ----------------

def call(model, prompt):
    r = requests.post(OLLAMA, json={
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False
    })
    return r.json()["message"]["content"]


# ---------------- AGENTS ----------------

def planner(task, rules):
    return call("qwen2.5-coder:14b", f"""
SYSTEM RULES:
{rules}

You are the ARCHITECT.

Break into steps and file structure:

TASK:
{task}
""")


def executor(plan):
    return call("deepseek-coder:6.7b", f"""
You are a SENIOR ENGINEER.

Implement exactly:

{plan}
""")


def reviewer(code):
    return call("qwen2.5-coder:14b", f"""
You are QA ENGINEER.

Find bugs, issues, improvements:

{code}
""")


# ---------------- PR SYSTEM ----------------

def create_pr(task, plan, code, review):
    name = "pr_" + str(abs(hash(task)))
    path = os.path.join(PR_DIR, name)
    os.makedirs(path, exist_ok=True)

    open(os.path.join(path, "plan.txt"), "w", encoding="utf-8").write(plan)
    open(os.path.join(path, "code.txt"), "w", encoding="utf-8").write(code)
    open(os.path.join(path, "review.txt"), "w", encoding="utf-8").write(review)

    return path


# ---------------- WORKER ----------------

def process_task(task, state, rules):

    log(f"🧠 TASK START: {task}")

    plan = planner(task, rules)
    code = executor(plan)
    review = reviewer(code)

    fix_cycles = 0

    while any(x in review.lower() for x in ["bug", "error", "issue"]):
        log("🔁 Fix cycle triggered")
        code = executor(plan + "\nFix issues:\n" + review)
        review = reviewer(code)
        fix_cycles += 1

    pr = create_pr(task, plan, code, review)

    state["completed_tasks"].append(task)
    state["metrics"]["tasks_done"] = state["metrics"].get("tasks_done", 0) + 1
    state["metrics"]["fix_cycles"] = state["metrics"].get("fix_cycles", 0) + fix_cycles

    save_state(state)

    log(f"✅ PR CREATED: {pr}")


# ---------------- SWARM ENGINE ----------------

def main():

    log("🏢 AI SOFTWARE COMPANY OS STARTED")

    while True:

        tasks = load_tasks()
        rules = load_rules()
        state = load_state()

        pending = [t for t in tasks if t not in state["completed_tasks"]]

        if not pending:
            time.sleep(3)
            continue

        # 🔥 PARALLEL SWARM
        with ThreadPoolExecutor(max_workers=3) as pool:
            for task in pending:
                pool.submit(process_task, task, state, rules)

        time.sleep(5)


if __name__ == "__main__":
    main()