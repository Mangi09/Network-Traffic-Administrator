# agent.py (User PC)

import os
import time
from datetime import datetime

# Shared folder path (Admin PC)
shared_folder = r"\\192.168.1.100\LabShare"

# Get unique PC name
pc_name = os.environ.get('COMPUTERNAME', 'PC_UNKNOWN')

# File paths
task_file = os.path.join(shared_folder, "task.txt")
log_file = os.path.join(shared_folder, f"log_{pc_name}.txt")
result_file = os.path.join(shared_folder, f"result_{pc_name}.txt")


def write_log(message):
    """Write logs to shared folder"""
    with open(log_file, "a") as f:
        f.write(f"[{datetime.now()}] {message}\n")


def execute_task(task):
    """Execute task based on command"""
    try:
        parts = task.strip().split()

        if parts[0] == "SUM":
            start = int(parts[1])
            end = int(parts[2])

            result = sum(range(start, end + 1))
            return f"SUM {start}-{end} = {result}"

        else:
            return "Unknown Task"

    except Exception as e:
        return f"Error: {str(e)}"


def main():
    write_log("Agent started and running...")

    while True:
        try:
            # Check if task exists
            if os.path.exists(task_file):

                write_log("Task detected")

                with open(task_file, "r") as f:
                    task = f.read()

                write_log(f"Task received: {task}")

                # Execute task
                result = execute_task(task)

                # Save result
                with open(result_file, "w") as f:
                    f.write(result)

                write_log(f"Task completed. Result: {result}")

                # Optional: delete task after execution
                # os.remove(task_file)

                time.sleep(5)

            else:
                write_log("No task found. Waiting...")

        except Exception as e:
            write_log(f"Error occurred: {str(e)}")

        time.sleep(10)


if __name__ == "__main__":
    main()