import pandas as pd
from pathlib import Path
import sys
sys.path.insert(0, '.')

# Import the extraction functions
from generate_L2_report import _count_tc_statuses, extract_tc_summary_full

# Find the ASEoD file
box_path = Path(r"C:\Users\LalithVishnu\Box\L1 Report Repository")
files = sorted(list(box_path.glob("*ASEoD*")), key=lambda p: p.stat().st_mtime, reverse=True)

if files:
    file_path = files[0]
    print(f"File: {file_path.name}\n")
    
    # Test the extraction function
    print("=" * 60)
    print("ACTUAL EXCEL DATA (from previous check):")
    print("=" * 60)
    print("  Blocked: 6")
    print("  Completed: 11")
    print("  Descoped: 2")
    print("  Execution Completed: 7")
    print("  In Progress: 6")
    print("  Not Started: 9")
    print("  On Hold: 3")
    print("  Total: 44\n")
    
    print("=" * 60)
    print("EXTRACTED DATA (from our function):")
    print("=" * 60)
    
    counts = _count_tc_statuses(file_path)
    print("Raw counts:", counts)
    print()
    
    tc_summary = extract_tc_summary_full(file_path)
    for label, count in tc_summary:
        print(f"  {label}: {count}")
    
else:
    print("File not found")
