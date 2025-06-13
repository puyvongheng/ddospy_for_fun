from flask import Flask, render_template_string, request, jsonify
import threading
import time
import requests
import random
from faker import Faker

app = Flask(__name__)
fake = Faker()

# API endpoints
BASE_URL = "https://staging-student-score-d7vi.encr.app"
API_ADD = f"{BASE_URL}/addtostudent"

faculties = ["IT", "Business", "Engineering", "Web develop", "Design"]
genders = [
    "Male", "Female", "Transgender Male", "Transgender Female",
    "Non-Binary", "Genderqueer", "Genderfluid", "Agender",
    "Bigender", "Two-Spirit", "Intersex", "Other", "Prefer not to say"
]

logs = []
logs_lock = threading.Lock()

def log(message):
    with logs_lock:
        logs.append(message)
        # Keep only last 200 logs to limit memory
        if len(logs) > 200:
            logs.pop(0)

success_count = 0
failure_count = 0

def add_student():
    global success_count, failure_count
    student = {
        "fullname": fake.name(),
        "gender": random.choice(genders),
        "dob": fake.date_of_birth(minimum_age=17, maximum_age=24).strftime("%Y/%m/%d"),
        "faculty": random.choice(faculties)
    }
    try:
        res = requests.post(API_ADD, json=student)
        if res.status_code == 200:
            success_count += 1
            log(f"✅ Added: {student['fullname']}  (cont ){success_count}  ")
        else:
            failure_count += 1
            log(f"❌ Failed: {res.status_code} - {res.text}")
    except Exception as e:
        failure_count += 1
        log(f"❌ Error: {e}")

def add_students(n):
    log(f"🚀 Starting to add {n} students...")
    for i in range(1, n+1):
        add_student()
        time.sleep(0.1)  # small delay to avoid burst
    log(f"✅ Finished adding {n} students. Success: {success_count}, Failures: {failure_count}")

@app.route("/", methods=["GET"])
def index():
    return render_template_string("""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<title>Student API Test Tool</title>
<style>
  body { font-family: monospace; background: #222; color: #eee; }
  #console { background: #000; padding: 10px; height: 400px; overflow-y: scroll; border: 2px solid #0f0; }
  input[type=number] { width: 80px; }
  button { font-size: 1rem; }
</style>
</head>
<body>
<h2>🎓 Student API Test Tool - Live Console</h2>

<form id="runForm">
  <label for="count">Add how many students?</label>
  <input type="number" id="count" name="count" min="1" max="1000" value="10" required />
  <button type="submit">Start Adding</button>
</form>

<div id="console"></div>

<script>
const consoleDiv = document.getElementById('console');
const runForm = document.getElementById('runForm');

function escapeHtml(text) {
  var div = document.createElement('div');
  div.innerText = text;
  return div.innerHTML;
}

async function fetchLogs() {
  try {
    const res = await fetch('/log');
    if (res.ok) {
      const data = await res.json();
      consoleDiv.innerHTML = data.logs.map(escapeHtml).join('<br>');
      consoleDiv.scrollTop = consoleDiv.scrollHeight;
    }
  } catch(e) {
    consoleDiv.innerHTML += `<br>❌ Error fetching logs: ${e}`;
  }
}

runForm.onsubmit = async (e) => {
  e.preventDefault();
  const count = document.getElementById('count').value;
  try {
    await fetch('/run', {
      method: 'POST',
      headers: {'Content-Type': 'application/x-www-form-urlencoded'},
      body: `count=${encodeURIComponent(count)}`
    });
  } catch (e) {
    alert('Failed to start adding students: ' + e);
  }
}

setInterval(fetchLogs, 1000);
fetchLogs();
</script>

</body>
</html>
    """)

@app.route("/run", methods=["POST"])
def run():
    count = int(request.form.get("count", 10))
    # Start background thread
    threading.Thread(target=add_students, args=(count,), daemon=True).start()
    return "", 204

@app.route("/log", methods=["GET"])
def get_log():
    with logs_lock:
        return jsonify(logs=logs)

if __name__ == "__main__":
    app.run(debug=True)
