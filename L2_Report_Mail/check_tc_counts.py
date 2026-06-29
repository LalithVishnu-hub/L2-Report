import pandas as pd
from pathlib import Path

# Find the ASEoD file
box_path = Path(r"C:\Users\LalithVishnu\Box\L1 Report Repository")
files = sorted(list(box_path.glob("*ASEoD*")), key=lambda p: p.stat().st_mtime, reverse=True)

if files:
    file_path = files[0]
    print(f"Checking file: {file_path.name}\n")
    
    # Read the Detailed TC Summary sheet
    try:
        xl = pd.ExcelFile(file_path)
        print(f"Sheet names: {xl.sheet_names}\n")
        
        # Find the correct sheet name
        tc_sheet = None
        for name in xl.sheet_names:
            if 'detailed tc summary' in name.strip().lower():
                tc_sheet = name
                break
        
        if tc_sheet:
            print(f"Found sheet: '{tc_sheet}'\n")
            df = pd.read_excel(file_path, sheet_name=tc_sheet, header=2)
            print(f"Shape: {df.shape}")
            print(f"\nColumns (first 10):")
            for i, col in enumerate(df.columns[:10]):
                print(f"  {i}: {repr(col)}")
            
            # Find Status column
            status_col = None
            for col in df.columns:
                if col.strip().lower() == 'status':
                    status_col = col
                    break
            
            if status_col:
                print(f"\n✓ Status column found: {repr(status_col)}\n")
                print("Status value counts from Excel:")
                counts = df[status_col].dropna().value_counts().sort_index()
                for status, count in counts.items():
                    print(f"  {status}: {count}")
                print(f"\nTotal rows with status: {df[status_col].notna().sum()}")
                print(f"Total TCs: {len(df)}")
            else:
                print("\n✗ Status column NOT found!")
                print(f"Available columns: {[str(c) for c in df.columns]}")
        else:
            print("✗ Detailed TC Summary sheet not found!")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
else:
    print("No ASEoD file found")
