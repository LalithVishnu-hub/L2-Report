import pandas as pd
from pathlib import Path
import re

# Get all L1 HTML files
l1_dir = Path(r"C:\Users\LalithVishnu\Desktop\Project Dashboard-L2 SQL DB\html_reports\L1")
html_files = sorted(l1_dir.glob("PID_*.html"))

print(f"Validating {len(html_files)} projects...\n")
print("=" * 80)

all_valid = True
validation_results = []

for html_file in html_files:
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract project name from HTML title
    title_match = re.search(r'<title>L1 Report – ([^<]+)</title>', content)
    project_name = title_match.group(1) if title_match else "Unknown"
    
    # Extract TC Summary table
    tc_summary_match = re.search(r'<h3[^>]*>TC Summary</h3>.*?</table>', content, re.DOTALL)
    
    if tc_summary_match:
        tc_table = tc_summary_match.group()
        rows = re.findall(r'<tr[^>]*>.*?<td[^>]*>([^<]+)</td>\s*<td[^>]*>(\d+)</td>', tc_table)
        
        # Get the Total TCs count
        total_tc = None
        for status, count in rows:
            if 'Total TCs' in status:
                total_tc = int(count)
                break
        
        # Check if all rows have valid data (non-empty, numeric)
        is_valid = all(count.isdigit() and int(count) >= 0 for _, count in rows) and total_tc is not None
        
        status_icon = "[OK]" if is_valid else "[ERR]"
        print(f"{status_icon} {project_name}")
        print(f"     Total TCs: {total_tc}, Statuses: {len(rows) - 1}")  # -1 for Total row
        
        if not is_valid:
            print(f"     WARNING: Invalid TC data detected")
            all_valid = False
        
        validation_results.append((project_name, is_valid, total_tc))
    else:
        print(f"[ERR] {project_name}")
        print(f"     TC Summary table not found")
        validation_results.append((project_name, False, 0))
        all_valid = False

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)

valid_count = sum(1 for _, valid, _ in validation_results if valid)
print(f"Valid projects: {valid_count}/{len(validation_results)}")

if all_valid:
    print("\n✓ ALL PROJECTS HAVE VALID TC SUMMARY DATA!")
else:
    print("\n✗ Some projects have issues:")
    for name, valid, total in validation_results:
        if not valid:
            print(f"   - {name} (Total TCs: {total})")
