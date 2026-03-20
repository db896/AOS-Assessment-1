#!/bin/bash

while true; do
    clear
    echo "===== SECURE SUBMISSION SYSTEM ====="
    echo "1. Submit Assignment"
    echo "2. Check Duplicate Submission"
    echo "3. List Submitted Assignments"
    echo "4. Simulate Login Attempt"
    echo "5. Exit"
    echo
    read -rp "Select option: " choice

    case "$choice" in
        1)
            read -rp "Enter Student ID: " sid
            read -rp "Enter file path: " filepath
            python3 task3_backend.py submit "$sid" "$filepath"
            read -rp "Press Enter to continue..."
            ;;
        2)
            read -rp "Enter file path to check: " filepath
            python3 task3_backend.py check "$filepath"
            read -rp "Press Enter to continue..."
            ;;
        3)
            python3 task3_backend.py list
            read -rp "Press Enter to continue..."
            ;;
        4)
            read -rp "Enter Username: " username
            read -rp "Enter Password: " password
            python3 task3_backend.py login "$username" "$password"
            read -rp "Press Enter to continue..."
            ;;
        5)
            read -rp "Bye? Are you sure you want to exit? (Y/N): " confirm
            case "$confirm" in
                Y|y)
                    echo "Goodbye."
                    exit 0
                    ;;
                N|n)
                    ;;
                *)
                    echo "Invalid input."
                    sleep 1
                    ;;
            esac
            ;;
        *)
            echo "Invalid option."
            sleep 1
            ;;
    esac
done
