import pandas as pd
from pathlib import Path

# Read the generated HTML file
html_file = Path(r"C:\Users\LalithVishnu\Desktop\Project Dashboard-L2 SQL DB\html_reports\L1\PID_437332_ASEoD_Deprecation_Phase_2B.html")

if html_file.exists():
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract TC Summary section
    import re
    
    # Find TC Summary table
    tc_summary_match = re.search(r'<h3[^>]*>TC Summary</h3>.*?</table>', content, re.DOTALL)
    
    if tc_summary_match:
        tc_table = tc_summary_match.group()
        # Extract all rows
        rows = re.findall(r'<tr[^>]*>.*?<td[^>]*>([^<]+)</td>\s*<td[^>]*>(\d+)</td>', tc_table)
        
        print("=" * 60)
        print("GENERATED HTML - TC SUMMARY (ASEoD Deprecation Phase 2B)")
        print("=" * 60)
        for status, count in rows:
            status = status.strip()
            print(f"  {status}: {count}")
        
        print("\n" + "=" * 60)
        print("EXPECTED DATA FROM EXCEL")
        print("=" * 60)
        print("  Completed: 11")
        print("  Execution Completed: 7")
        print("  In Progress: 6")
        print("  Blocked: 6")
        print("  Failed: 0")
        print("  On Hold: 3")
        print("  Not Started: 9")
        print("  Deferred: 0")
        print("  Descoped: 2")
        print("  Total TCs: 44")
        
        print("\n" + "=" * 60)
        print("VALIDATION")
        print("=" * 60)
        
        expected = {
            'Completed': 11,
            'Execution Completed': 7,
            'In Progress': 6,
            'Blocked': 6,
            'Failed': 0,
            'On Hold': 3,
            'Not Started': 9,
            'Deferred': 0,
            'Descoped': 2,
            'Total TCs': 44
        }
        
        all_match = True
        for status, count in rows:
            status = status.strip()
            count = int(count)
            if status in expected:
                if count == expected[status]:
                    print(f"  ✓ {status}: {count} (CORRECT)")
                else:
                    print(f"  ✗ {status}: {count} (Expected {expected[status]})")
                    all_match = False
        
        if all_match:
            print("\n✓ ALL TC COUNTS MATCH!")
        else:
            print("\n✗ SOME COUNTS DO NOT MATCH")
    else:
        print("TC Summary table not found in HTML")
else:
    print(f"File not found: {html_file}")
