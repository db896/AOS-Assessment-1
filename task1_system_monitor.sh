#!/bin/bash

LOG_FILE="system_monitor_log.txt"
ARCHIVE_DIR="ArchiveLogs"

LOG_SIZE_THRESHOLD=$((50 * 1024 * 1024))
ARCHIVE_WARN_THRESHOLD=$((1024 * 1024 * 1024))

RED="\e[31m"
GREEN="\e[32m"
YELLOW="\e[33m"
BLUE="\e[34m"
CYAN="\e[36m"
NC="\e[0m"

CRITICAL_PROCESSES=("systemd" "init" "kthreadd" "sshd" "bash" "login" "NetworkManager")

log_action() {
    local action="$1"
    local status="$2"
    local timestamp
    timestamp=$(date "+%Y-%m-%d %H:%M:%S")
    echo "[$timestamp] ACTION: $action | STATUS: $status" >> "$LOG_FILE"
}

print_header() {
    clear
    echo -e "${CYAN}===== UNIVERSITY DATA CENTRE SYSTEM =====${NC}"
}

pause_screen() {
    echo
    read -rp "Press Enter to continue..."
}

show_cpu_memory_usage() {
    echo -e "${BLUE}Current CPU and Memory Usage${NC}"
    echo
    echo "----- Uptime / Load -----"
    uptime
    echo
    echo "----- Memory Usage -----"
    free -h
    echo
    echo "----- CPU Snapshot -----"
    top -bn1 | head -n 5
    log_action "Displayed CPU and memory usage" "SUCCESS"
}

show_top_processes() {
    echo -e "${BLUE}Top 10 Memory Consuming Processes${NC}"
    echo
    printf "%-10s %-15s %-10s %-10s %-20s\n" "PID" "USER" "CPU(%)" "MEM(%)" "COMMAND"
    ps -eo pid,user,%cpu,%mem,comm --sort=-%mem | head -n 11
    log_action "Displayed top 10 memory-consuming processes" "SUCCESS"
}

is_critical_process() {
    local pname="$1"
    for proc in "${CRITICAL_PROCESSES[@]}"; do
        if [[ "$pname" == "$proc" ]]; then
            return 0
        fi
    done
    return 1
}

terminate_process() {
    read -rp "Enter PID to terminate: " pid

    if ! [[ "$pid" =~ ^[0-9]+$ ]]; then
        echo -e "${RED}Invalid PID.${NC}"
        log_action "Attempted process termination with invalid PID: $pid" "FAILED"
        return
    fi

    if ! ps -p "$pid" > /dev/null 2>&1; then
        echo -e "${RED}PID $pid does not exist.${NC}"
        log_action "Attempted to terminate non-existent PID: $pid" "FAILED"
        return
    fi

    pname=$(ps -p "$pid" -o comm= | awk '{print $1}')
    puser=$(ps -p "$pid" -o user= | awk '{print $1}')

    if is_critical_process "$pname"; then
        echo -e "${RED}Termination blocked. '$pname' is a critical system process.${NC}"
        log_action "Blocked termination of critical process $pname (PID $pid)" "FAILED"
        return
    fi

    echo "Selected Process:"
    echo "PID: $pid | USER: $puser | NAME: $pname"
    read -rp "Are you sure you want to terminate this process? (Y/N): " confirm

    case "$confirm" in
        Y|y)
            kill "$pid" 2>/dev/null
            if [[ $? -eq 0 ]]; then
                echo -e "${GREEN}Process $pid terminated successfully.${NC}"
                log_action "Terminated process $pname (PID $pid)" "SUCCESS"
            else
                echo -e "${RED}Failed to terminate process $pid.${NC}"
                log_action "Failed to terminate process $pname (PID $pid)" "FAILED"
            fi
            ;;
        N|n)
            echo -e "${YELLOW}Termination cancelled.${NC}"
            log_action "Cancelled process termination for PID $pid" "CANCELLED"
            ;;
        *)
            echo -e "${RED}Invalid choice. Termination cancelled.${NC}"
            log_action "Invalid confirmation while terminating PID $pid" "FAILED"
            ;;
    esac
}

inspect_directory_usage() {
    read -rp "Enter directory path to inspect: " dir

    if [[ ! -d "$dir" ]]; then
        echo -e "${RED}Directory does not exist.${NC}"
        log_action "Directory inspection failed for '$dir'" "FAILED"
        return
    fi

    echo -e "${BLUE}Disk Usage for: $dir${NC}"
    du -sh "$dir"
    echo
    echo -e "${BLUE}Largest 10 items inside directory:${NC}"
    du -ah "$dir" 2>/dev/null | sort -rh | head -n 10

    log_action "Inspected disk usage for directory '$dir'" "SUCCESS"
}

archive_large_logs() {
    read -rp "Enter directory path to scan for .log files: " dir

    if [[ ! -d "$dir" ]]; then
        echo -e "${RED}Directory does not exist.${NC}"
        log_action "Log archive scan failed for '$dir'" "FAILED"
        return
    fi

    mkdir -p "$ARCHIVE_DIR"

    found_any=false
    archived_count=0

    while IFS= read -r -d '' logfile; do
        found_any=true
        size=$(stat -c%s "$logfile" 2>/dev/null)

        if [[ "$size" -gt "$LOG_SIZE_THRESHOLD" ]]; then
            base=$(basename "$logfile")
            timestamp=$(date "+%Y%m%d_%H%M%S")
            archive_name="${ARCHIVE_DIR}/${base}_${timestamp}.gz"

            gzip -c "$logfile" > "$archive_name"

            if [[ $? -eq 0 ]]; then
                echo -e "${GREEN}Archived:${NC} $logfile -> $archive_name"
                log_action "Archived large log file '$logfile' to '$archive_name'" "SUCCESS"
                ((archived_count++))
            else
                echo -e "${RED}Failed to archive:${NC} $logfile"
                log_action "Failed to archive log file '$logfile'" "FAILED"
            fi
        fi
    done < <(find "$dir" -type f -name "*.log" -print0 2>/dev/null)

    if [[ "$found_any" = false ]]; then
        echo -e "${YELLOW}No .log files found in the specified directory.${NC}"
        log_action "No log files found in '$dir'" "INFO"
    fi

    archive_size=$(du -sb "$ARCHIVE_DIR" 2>/dev/null | awk '{print $1}')
    echo
    echo "Archived files created in this run: $archived_count"

    if [[ -n "$archive_size" && "$archive_size" -gt "$ARCHIVE_WARN_THRESHOLD" ]]; then
        echo -e "${RED}Warning: ArchiveLogs exceeds 1GB.${NC}"
        log_action "ArchiveLogs exceeded 1GB" "WARNING"
    else
        echo -e "${GREEN}ArchiveLogs size is within safe limit.${NC}"
        log_action "Checked ArchiveLogs size" "SUCCESS"
    fi
}

view_log_summary() {
    echo -e "${BLUE}System Monitor Log Summary${NC}"
    if [[ ! -f "$LOG_FILE" ]]; then
        echo -e "${YELLOW}No log file exists yet.${NC}"
        return
    fi

    echo "Total log entries: $(wc -l < "$LOG_FILE")"
    echo
    tail -n 10 "$LOG_FILE"
    log_action "Viewed log summary" "SUCCESS"
}

exit_program() {
    read -rp "Bye? Are you sure you want to exit? (Y/N): " confirm
    case "$confirm" in
        Y|y)
            echo -e "${GREEN}Goodbye.${NC}"
            log_action "Exited system monitor program" "SUCCESS"
            exit 0
            ;;
        N|n)
            echo -e "${YELLOW}Exit cancelled.${NC}"
            log_action "Cancelled exit request" "CANCELLED"
            ;;
        *)
            echo -e "${RED}Invalid choice. Returning to menu.${NC}"
            log_action "Invalid exit confirmation input" "FAILED"
            ;;
    esac
}

while true; do
    print_header
    echo "1. Display CPU and Memory Usage"
    echo "2. Show Top 10 Memory Processes"
    echo "3. Terminate Process"
    echo "4. Inspect Disk Usage"
    echo "5. Archive Large Log Files"
    echo "6. View Log Summary"
    echo "7. Bye"
    echo
    read -rp "Select option: " choice

    case "$choice" in
        1) print_header; show_cpu_memory_usage; pause_screen ;;
        2) print_header; show_top_processes; pause_screen ;;
        3) print_header; terminate_process; pause_screen ;;
        4) print_header; inspect_directory_usage; pause_screen ;;
        5) print_header; archive_large_logs; pause_screen ;;
        6) print_header; view_log_summary; pause_screen ;;
        7) print_header; exit_program; pause_screen ;;
        *)
            echo -e "${RED}Invalid option. Please try again.${NC}"
            log_action "Invalid menu option selected: $choice" "FAILED"
            sleep 1
            ;;
    esac
done
       
