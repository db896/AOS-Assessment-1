import os
import sys
import json
import time
import shutil
import hashlib
from datetime import datetime

SUBMISSIONS_DIR = "submissions"
LOG_FILE = "submission_log.txt"
LOCKED_FILE = "locked_accounts.txt"
ATTEMPTS_FILE = "login_attempts.json"
INDEX_FILE = "submission_index.json"

MAX_FILE_SIZE = 5 * 1024 * 1024
ALLOWED_EXTENSIONS = [".pdf", ".docx"]

VALID_USERS = {
    "student1": "pass123",
    "admin": "admin123",
    "dev": "dev123"
}

def ensure_files():
    os.makedirs(SUBMISSIONS_DIR, exist_ok=True)

    for file_name, default_content in [
        (LOG_FILE, ""),
        (LOCKED_FILE, ""),
        (ATTEMPTS_FILE, "{}"),
        (INDEX_FILE, "[]")
    ]:
        if not os.path.exists(file_name):
            with open(file_name, "w") as f:
                f.write(default_content)

def log_event(student_id, filename, status):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] StudentID/User: {student_id} | File: {filename} | Status: {status}\n")

def load_json(path, default):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except:
        return default

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

def sha256_file(filepath):
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while True:
            chunk = f.read(4096)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()

def submit_assignment(student_id, filepath):
    ensure_files()

    if not os.path.isfile(filepath):
        print("File does not exist.")
        log_event(student_id, filepath, "FAILED - File not found")
        return

    _, ext = os.path.splitext(filepath)
    ext = ext.lower()

    if ext not in ALLOWED_EXTENSIONS:
        print("Invalid file type. Only .pdf and .docx allowed.")
        log_event(student_id, os.path.basename(filepath), "FAILED - Invalid file type")
        return

    size = os.path.getsize(filepath)
    if size > MAX_FILE_SIZE:
        print("File rejected. Size exceeds 5MB.")
        log_event(student_id, os.path.basename(filepath), "FAILED - File too large")
        return

    file_hash = sha256_file(filepath)
    filename = os.path.basename(filepath)

    index = load_json(INDEX_FILE, [])

    for record in index:
        if record["filename"] == filename and record["hash"] == file_hash:
            print("Duplicate submission detected: identical filename and content.")
            log_event(student_id, filename, "FAILED - Duplicate filename and content")
            return

    destination_name = f"{student_id}_{filename}"
    destination_path = os.path.join(SUBMISSIONS_DIR, destination_name)
    shutil.copy2(filepath, destination_path)

    index.append({
        "student_id": student_id,
        "filename": filename,
        "stored_as": destination_name,
        "hash": file_hash,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    save_json(INDEX_FILE, index)

    print("Submission accepted successfully.")
    log_event(student_id, filename, "SUCCESS - Submission accepted")

def check_duplicate(filepath):
    ensure_files()

    if not os.path.isfile(filepath):
        print("File does not exist.")
        return

    filename = os.path.basename(filepath)
    file_hash = sha256_file(filepath)

    index = load_json(INDEX_FILE, [])

    for record in index:
        if record["filename"] == filename and record["hash"] == file_hash:
            print("Yes - file has already been submitted.")
            return

    print("No - file has not been submitted before.")

def list_submissions():
    ensure_files()

    files = sorted(os.listdir(SUBMISSIONS_DIR))
    if not files:
        print("No submitted assignments found.")
        return

    print("Submitted assignments:")
    for file in files:
        print(f"- {file}")

def read_locked_accounts():
    ensure_files()
    with open(LOCKED_FILE, "r") as f:
        return set(line.strip() for line in f if line.strip())

def lock_account(username):
    locked = read_locked_accounts()
    if username not in locked:
        with open(LOCKED_FILE, "a") as f:
            f.write(username + "\n")

def simulate_login(username, password):
    ensure_files()

    locked_accounts = read_locked_accounts()
    if username in locked_accounts:
        print("Account is locked.")
        log_event(username, "LOGIN", "FAILED - Account locked")
        return

    attempts = load_json(ATTEMPTS_FILE, {})
    now = time.time()

    if username not in attempts:
        attempts[username] = []

    attempts[username] = [t for t in attempts[username] if now - t <= 60]

    if username not in VALID_USERS or VALID_USERS[username] != password:
        attempts[username].append(now)
        save_json(ATTEMPTS_FILE, attempts)

        if len(attempts[username]) >= 3:
            lock_account(username)
            print("Account locked after three failed attempts.")
            log_event(username, "LOGIN", "FAILED - Locked after 3 attempts")
            return

        if len(attempts[username]) >= 2:
            print("Suspicious activity detected: repeated failed login attempts within 60 seconds.")
            log_event(username, "LOGIN", "WARNING - Suspicious repeated login attempts")

        print("Login failed.")
        log_event(username, "LOGIN", "FAILED - Invalid credentials")
        return

    attempts[username] = []
    save_json(ATTEMPTS_FILE, attempts)
    print("Login successful.")
    log_event(username, "LOGIN", "SUCCESS - Login successful")

def main():
    if len(sys.argv) < 2:
        print("Usage error.")
        return

    command = sys.argv[1]

    if command == "submit" and len(sys.argv) == 4:
        submit_assignment(sys.argv[2], sys.argv[3])
    elif command == "check" and len(sys.argv) == 3:
        check_duplicate(sys.argv[2])
    elif command == "list":
        list_submissions()
    elif command == "login" and len(sys.argv) == 4:
        simulate_login(sys.argv[2], sys.argv[3])
    else:
        print("Invalid command.")

if __name__ == "__main__":
    main()
