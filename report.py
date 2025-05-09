import os
import glob

def report_write():
    # Get all log files in results directory
    log_files = glob.glob('results/*.log')
    
    for file_path in log_files:
        print(f"\nFile: {file_path}")
        print("-" * 50)
        
        try:
            with open(file_path, 'r') as f:
                # Read all lines and get last 5
                lines = f.readlines()
                last_5_lines = lines[-5:] if len(lines) >= 5 else lines
                
                # Print last 5 lines
                for line in last_5_lines:
                    print(line.rstrip())
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
