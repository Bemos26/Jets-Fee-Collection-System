import os

file_path = r"c:\My-projects\Jets Fee Collection System\templates\students\student_list.html"
if not os.path.exists(file_path):
    print(f"File not found: {file_path}")
else:
    print(f"Reading {file_path}")
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        for idx, line in enumerate(lines):
            if 10 <= idx <= 30:
                 print(f"Line {idx+1}: {line.strip()}")
