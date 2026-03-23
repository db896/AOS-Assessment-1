# AOS-Assessment-1
Advanced Operating Systems Assessment 1

**Module:** Advanced Operating Systems (U14553)  
**Student ID:** 100073431

---

## Repository Contents

| File | Description |
|---|---|
| `task1_system_monitor.sh` | University Data Centre Process and Resource Management System (Bash) |
| `task2_scheduler.py` | University High Performance Computing Job Scheduler (Python) |
| `task3_secure_submission.sh` | Secure Examination Submission and Access Control System (Bash front-end) |
| `task3_backend.py` | Secure Examination Submission and Access Control System (Python back-end) |

---

## Prerequisites

- Linux environment (tested on Kali Linux)
- Python 3
- Standard GNU coreutils (`ps`, `top`, `free`, `du`, `find`, `gzip`)

---

## How to Execute

### Task 1 – System Monitor

```bash
chmod +x task1_system_monitor.sh
./task1_system_monitor.sh
```

The interactive menu allows you to monitor CPU and memory usage, view top processes, terminate a process safely, inspect disk usage, archive large log files, and view the log summary. Select option 7 (Bye) to exit.

### Task 2 – Job Scheduler

```bash
python3 task2_scheduler.py
```

Submit jobs with a student ID, job name, execution time, and priority (1–10). Process the queue using Round Robin (5-second time quantum) or Priority Scheduling. Completed jobs and logs are saved to `completed_jobs.txt` and `scheduler_log.txt`.

### Task 3 – Secure Submission System

```bash
chmod +x task3_secure_submission.sh
./task3_secure_submission.sh
```

Both `task3_secure_submission.sh` and `task3_backend.py` must be in the same directory. The system validates file submissions (.pdf and .docx only, max 5 MB), detects duplicates using SHA-256 hashing, and monitors login attempts with account lockout after three failures within 60 seconds.

**Test credentials for login simulation:**

| Username | Password |
|---|---|
| student1 | pass123 |
| admin | admin123 |
| dev | dev123 |

---

## Output Files

| File | Created by |
|---|---|
| `system_monitor_log.txt` | Task 1 |
| `job_queue.txt` | Task 2 |
| `completed_jobs.txt` | Task 2 |
| `scheduler_log.txt` | Task 2 |
| `submission_log.txt` | Task 3 |
| `locked_accounts.txt` | Task 3 |
| `submissions/` | Task 3 (stored files) |
