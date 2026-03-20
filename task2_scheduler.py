import os
import time
from datetime import datetime

JOB_QUEUE_FILE = "job_queue.txt"
COMPLETED_FILE = "completed_jobs.txt"
LOG_FILE = "scheduler_log.txt"
TIME_QUANTUM = 5

def ensure_files():
    for filename in [JOB_QUEUE_FILE, COMPLETED_FILE, LOG_FILE]:
        if not os.path.exists(filename):
            open(filename, "w").close()

def log_event(student_id, job_name, scheduling_type, result):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] StudentID: {student_id} | Job: {job_name} | Type: {scheduling_type} | Result: {result}\n")

def load_jobs():
    ensure_files()
    jobs = []
    with open(JOB_QUEUE_FILE, "r") as f:
        for line in f:
            line = line.strip()
            if line:
                parts = line.split("|")
                if len(parts) == 4:
                    student_id, job_name, exec_time, priority = parts
                    jobs.append({
                        "student_id": student_id,
                        "job_name": job_name,
                        "exec_time": int(exec_time),
                        "priority": int(priority)
                    })
    return jobs

def save_jobs(jobs):
    with open(JOB_QUEUE_FILE, "w") as f:
        for job in jobs:
            f.write(f"{job['student_id']}|{job['job_name']}|{job['exec_time']}|{job['priority']}\n")

def append_completed(job, scheduling_type):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(COMPLETED_FILE, "a") as f:
        f.write(f"{job['student_id']}|{job['job_name']}|{job['priority']}|{scheduling_type}|{timestamp}\n")

def submit_job():
    student_id = input("Enter Student ID: ").strip()
    if not student_id:
        print("Student ID cannot be empty.\n")
        return

    job_name = input("Enter Job Name: ").strip()
    if not job_name:
        print("Job name cannot be empty.\n")
        return

    try:
        exec_time = int(input("Enter Estimated Execution Time (seconds): ").strip())
        if exec_time <= 0:
            print("Execution time must be greater than 0.\n")
            return
    except ValueError:
        print("Execution time must be a number.\n")
        return

    try:
        priority = int(input("Enter Priority (1-10, 1 = highest): ").strip())
        if priority < 1 or priority > 10:
            print("Priority must be between 1 and 10.\n")
            return
    except ValueError:
        print("Priority must be a number.\n")
        return

    with open(JOB_QUEUE_FILE, "a") as f:
        f.write(f"{student_id}|{job_name}|{exec_time}|{priority}\n")

    log_event(student_id, job_name, "SUBMIT", "Job added to queue")
    print("Job submitted successfully.\n")

def view_pending_jobs():
    jobs = load_jobs()
    if not jobs:
        print("No pending jobs.\n")
        return

    print("\nPending Jobs:")
    print(f"{'StudentID':<12}{'Job Name':<20}{'Exec Time':<12}{'Priority':<10}")
    for job in jobs:
        print(f"{job['student_id']:<12}{job['job_name']:<20}{job['exec_time']:<12}{job['priority']:<10}")
    print()

def view_completed_jobs():
    ensure_files()
    if os.path.getsize(COMPLETED_FILE) == 0:
        print("No completed jobs.\n")
        return

    print("\nCompleted Jobs:")
    with open(COMPLETED_FILE, "r") as f:
        for line in f:
            print(line.strip())
    print()

def process_round_robin():
    jobs = load_jobs()
    if not jobs:
        print("No pending jobs to process.\n")
        return

    print(f"\nProcessing jobs using Round Robin (Time Quantum = {TIME_QUANTUM} seconds)\n")

    while jobs:
        current_job = jobs.pop(0)

        run_time = min(current_job["exec_time"], TIME_QUANTUM)
        print(f"Running {current_job['job_name']} for {run_time} seconds "
              f"(Student: {current_job['student_id']}, Priority: {current_job['priority']})")

        time.sleep(1)
        current_job["exec_time"] -= run_time

        if current_job["exec_time"] > 0:
            print(f"{current_job['job_name']} not finished, remaining time: {current_job['exec_time']} seconds\n")
            jobs.append(current_job)
            log_event(current_job["student_id"], current_job["job_name"], "Round Robin", f"Partially executed, remaining {current_job['exec_time']}s")
        else:
            print(f"{current_job['job_name']} completed.\n")
            append_completed(current_job, "Round Robin")
            log_event(current_job["student_id"], current_job["job_name"], "Round Robin", "Completed")

        save_jobs(jobs)

def process_priority():
    jobs = load_jobs()
    if not jobs:
        print("No pending jobs to process.\n")
        return

    jobs.sort(key=lambda x: x["priority"])

    print("\nProcessing jobs using Priority Scheduling\n")

    remaining_jobs = []

    for job in jobs:
        print(f"Running {job['job_name']} "
              f"(Student: {job['student_id']}, Priority: {job['priority']}, Time: {job['exec_time']}s)")
        time.sleep(1)
        print(f"{job['job_name']} completed.\n")
        append_completed(job, "Priority")
        log_event(job["student_id"], job["job_name"], "Priority", "Completed")

    save_jobs(remaining_jobs)

def exit_program():
    confirm = input("Bye? Are you sure you want to exit? (Y/N): ").strip().lower()
    if confirm == "y":
        print("Goodbye.")
        return True
    elif confirm == "n":
        return False
    else:
        print("Invalid input.\n")
        return False

def menu():
    ensure_files()

    while True:
        print("===== HPC JOB SCHEDULER =====")
        print("1. View Pending Jobs")
        print("2. Submit Job Request")
        print("3. Process Queue - Round Robin")
        print("4. Process Queue - Priority Scheduling")
        print("5. View Completed Jobs")
        print("6. Exit")
        choice = input("Select option: ").strip()

        if choice == "1":
            view_pending_jobs()
        elif choice == "2":
            submit_job()
        elif choice == "3":
            process_round_robin()
        elif choice == "4":
            process_priority()
        elif choice == "5":
            view_completed_jobs()
        elif choice == "6":
            if exit_program():
                break
        else:
            print("Invalid option. Please try again.\n")

menu()
