import subprocess
import sys

# 📦 Automatically install required libraries if missing
def install_if_missing(package, import_name=None):
    try:
        __import__(import_name if import_name else package)
    except ImportError:
        print(f"📦 Installing missing package: {package}")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Auto-install required packages
install_if_missing("requests")
install_if_missing("faker", "faker")

# Now safe to import
import requests
import random
from faker import Faker
import time
import threading

fake = Faker()

# API endpoints
BASE_URL = "https://staging-student-score-d7vi.encr.app"
API_ADD = f"{BASE_URL}/addtostudent"
API_ALL = f"{BASE_URL}/allstudents"
API_DELETE = f"{BASE_URL}/deletestudent"

# Faculties and Genders
faculties = ["IT", "Business", "Engineering", "Web develop", "Design"]
genders = [
    "Male", "Female", "Transgender Male", "Transgender Female",
    "Non-Binary", "Genderqueer", "Genderfluid", "Agender",
    "Bigender", "Two-Spirit", "Intersex", "Other", "Prefer not to say"
]

# Thread-safe counters
lock = threading.Lock()
success_count = 0
failure_count = 0

# ✅ Add one student
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
            with lock:
                success_count += 1
            print(f"✅ Added: {student['fullname']}")
        else:
            with lock:
                failure_count += 1
            print(f"❌ Failed: {res.status_code} - {res.text}")
    except Exception as e:
        with lock:
            failure_count += 1
        print(f"❌ Error: {e}")

# ✅ Fetch all students
def fetch_all_students():
    try:
        res = requests.get(API_ALL)
        if res.status_code == 200:
            return res.json().get("items", [])
        else:
            print(f"❌ Fetch error: {res.status_code}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    return []

# ✅ Delete student by ID
def delete_student_by_id(student_id):
    try:
        res = requests.delete(f"{API_DELETE}/{student_id}")
        if res.status_code == 200:
            print(f"🗑️ Deleted ID: {student_id}")
        else:
            print(f"❌ Delete {student_id} failed — {res.status_code}: {res.text}")
    except Exception as e:
        print(f"❌ Exception while deleting {student_id}: {e}")

# ✅ Delete ALL students
def delete_all_students():
    students = fetch_all_students()
    print(f"⚠️ Deleting {len(students)} students...")
    for s in students:
        delete_student_by_id(s['id'])
        time.sleep(0.01)

# ✅ Delete N students
def delete_n_students(n=10):
    students = fetch_all_students()
    print(f"⚠️ Deleting first {n} students...")
    for s in students[:n]:
        delete_student_by_id(s['id'])
        time.sleep(0.01)

# ✅ Add students (single thread)
def add_100_students(n=100):
    for i in range(1, n + 1):
        add_student()

# ✅ Add n students using threads
def add_student_threaded(n=5):
    threads = []
    for _ in range(n):
        t = threading.Thread(target=add_student)
        threads.append(t)
        t.start()
        time.sleep(0.001)
    for t in threads:
        t.join()

# ✅ Add students with retry logic
def run_dynamic_add_students(target=50):
    global success_count, failure_count
    current = 0

    print(f"🚀 Starting dynamic thread add: Target {target}")
    while current < target:
        prev_success = success_count
        prev_fail = failure_count

        print(f"\n➡️ Loop {current + 1} | ✅ Success: {success_count} ❌ Fail: {failure_count}")
        add_student_threaded(n=1)

        if success_count > prev_success:
            current += 1
        elif failure_count > prev_fail:
            current = max(current - 1, 0)

        time.sleep(0.05)

# ✅ Dynamic threaded loop
def run_dynamic_add_students_threaded(target=50, threads_per_loop=5):
    global success_count, failure_count
    current = 0
    loop = 0

    print(f"🚀 Starting threaded dynamic add: Target {target} students")

    while current < target:
        prev_success = success_count
        prev_failure = failure_count

        loop += 1
        print(f"\n➡️ Loop {loop} | Current count: {current}/{target} | ✅ Success: {success_count} ❌ Fail: {failure_count}")

        threads = []
        for _ in range(threads_per_loop):
            t = threading.Thread(target=add_student)
            threads.append(t)
            t.start()
            time.sleep(0.001)

        for t in threads:
            t.join()

        new_success = success_count - prev_success
        new_fail = failure_count - prev_failure

        current += new_success
        current -= new_fail
        current = max(current, 0)

        time.sleep(0.05)

    print(f"\n✅ Finished! Total success: {success_count}, Total fail: {failure_count}")

# ✅ Static 5-thread loop x 50
def run_50_loops_each_5_threads():
    total = 50
    for i in range(total):
        print(f"\n➡️ Batch {i + 1}/{total}")
        add_student_threaded(n=5)
        time.sleep(0.05)

# ✅ CLI Menu
def main():
    print("\n🎓 STUDENT API TEST TOOL 🎓")
    print("1. ➕ Add 100 students")
    print("2. 🗑️ Delete ALL students")
    print("3. 🧹 Delete 10 students")
    print("4. 🚀 Dynamic add students (retry on fail)")
    print("5. 🧵 Add 5 threads x 50 loops")
    print("0. ❌ Exit")

    choice = input("Choose option: ")

    if choice == "1":
        add_100_students(1000000)
    elif choice == "2":
        delete_all_students()
    elif choice == "3":
        delete_n_students(10)
    elif choice == "4":
        run_dynamic_add_students_threaded(target=50, threads_per_loop=5)
    elif choice == "5":
        run_50_loops_each_5_threads()
    elif choice == "0":
        print("👋 Exit")
    else:
        print("❌ Invalid option")

if __name__ == "__main__":
    main()
