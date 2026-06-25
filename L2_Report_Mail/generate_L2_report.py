"""
Generate L2 Report HTML - Enhanced Dashboard Format
- Extracts project info from Excel files
- Adds UFD # and Last Updated columns
- Deduplicates by project name (keeps latest file)
- Matches dashboard styling exactly
"""

import pandas as pd
from pathlib import Path
from datetime import datetime
import webbrowser
import re
import os
from urllib.parse import quote_plus
from html import escape

from dotenv import load_dotenv


SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
load_dotenv(PROJECT_ROOT / '.env', override=True)
L1_DASHBOARD_BASE_URL = os.getenv('L1_DASHBOARD_BASE_URL', 'http://localhost:5000').rstrip('/')
GITHUB_PAGES_BASE_URL = os.getenv('GITHUB_PAGES_BASE_URL', '').rstrip('/')
BOX_LOCAL_PATH = os.getenv('BOX_LOCAL_PATH', r'C:\Users\LalithVishnu\Box\L1 Report Repository')
EMAIL_GREETING = os.getenv('EMAIL_GREETING', 'Hi All,')
EMAIL_INTRO_MESSAGE = os.getenv('EMAIL_INTRO_MESSAGE', 'Please find below the L2 Project Dashboard for ETE Wireline Projects.')
EMAIL_FOOTER = os.getenv(
    'EMAIL_FOOTER',
    'This report is automatically generated and sent daily. For any questions or clarifications regarding the projects listed above, please reach out to the respective Test Lead or Test Manager.'
)
EMAIL_SIGNATURE = os.getenv('EMAIL_SIGNATURE', 'Thanks & Regards,\nLalith Vishnu. S')


def format_email_text(text):
    """Escape and preserve line breaks for configurable email text."""
    return '<br/>'.join(escape(str(text or '')).splitlines())

def extract_date_from_filename(filename):
    """Extract date from filename and convert to datetime object.
    Supports multiple date formats:
    - MM-DD format: 06-23, 12-25
    - DD-MM format: 23-06
    - YY.MM format: 26.06
    - Month Day format: June_23, June_24
    - YYYY-MM-DD format: 2026-06-23
    """
    # Try YYYY-MM-DD format first: 2026-06-23
    match = re.search(r'(\d{4})-(\d{1,2})-(\d{1,2})', filename)
    if match:
        try:
            return datetime(int(match.group(1)), int(match.group(2)), int(match.group(3)))
        except ValueError:
            pass
    
    # Try YY.MM format: 26.06 (year.month), then use day from nearby text
    match = re.search(r'_(\d{2})\.(\d{2})\s', filename)
    if match:
        year = int(match.group(1))
        month = int(match.group(2))
        # Extract day from nearby text (e.g., "June_23" or "as_of_June_23")
        day_match = re.search(r'(?:as_of_)?(?:as-of-)?[A-Za-z]*_?(\d{1,2})(?:\.xlsx|\.xls|$)', filename)
        if day_match:
            day = int(day_match.group(1))
            if 1 <= month <= 12 and 1 <= day <= 31:
                year_full = 2000 + year
                try:
                    return datetime(year_full, month, day)
                except ValueError:
                    pass
    
    # Try Month_DD format: June_23, Jan_01, December_25
    month_names = ['January', 'February', 'March', 'April', 'May', 'June',
                   'July', 'August', 'September', 'October', 'November', 'December']
    for i, month_name in enumerate(month_names, 1):
        match = re.search(rf'{month_name}[_\s-](\d{{1,2}})', filename, re.IGNORECASE)
        if match:
            day = int(match.group(1))
            # Try to extract year, default to current year
            year_match = re.search(r'(\d{4})', filename)
            year = int(year_match.group(1)) if year_match else datetime.now().year
            try:
                return datetime(year, i, day)
            except ValueError:
                pass
    
    # Try MM-DD or DD-MM format at end of filename: 06-23.xlsx, 12-25.xls
    match = re.search(r'[_\s](\d{1,2})-(\d{1,2})(?:\.xlsx|\.xls)$', filename)
    if match:
        num1 = int(match.group(1))
        num2 = int(match.group(2))
        year = datetime.now().year
        
        # Heuristic: assume MM-DD format (first number is month)
        if 1 <= num1 <= 12 and 1 <= num2 <= 31:
            try:
                return datetime(year, num1, num2)
            except ValueError:
                pass
        
        # If that fails, try DD-MM format
        if 1 <= num2 <= 12 and 1 <= num1 <= 31:
            try:
                return datetime(year, num2, num1)
            except ValueError:
                pass
    
    # If no date found, return None
    return None


def parse_project_info_from_filename(filename):
    """Extract Project ID, Project Name, and Date from filename.
    Supports multiple filename formats with flexible parsing."""
    
    project_id = None
    project_name = None
    
    # Try to match patterns with PID prefix (handles various spacing and separators)
    # Pattern: PID[space or nothing]ID[space or underscore]ProjectName
    patterns = [
        # PID_XXXXX_ProjectName_ETE_
        r'PID_?(\d+)[_\s]+(.+?)_(?:ETE|E2E)_',
        # PID XXXXX - ProjectName_E2E_ or _ETE_
        r'PID\s+(\d+).*?\s*-\s*(.+?)_(?:E2E|ETE)_',
        # PID XXXXX _ ProjectName _ETE_ or _E2E_
        r'PID\s+(\d+)\s*_\s*(.+?)\s*_(?:E2E|ETE)_',
    ]
    
    for pattern in patterns:
        match = re.match(pattern, filename, re.IGNORECASE)
        if match:
            project_id = match.group(1)
            project_name = match.group(2).strip()
            break
    
    # Fallback: Try to match without PID prefix (just ID_ProjectName_Status)
    if not project_id:
        match = re.match(r'^(\d+)[_\s]+(.+?)_(?:Status|ETE|E2E)', filename, re.IGNORECASE)
        if match:
            project_id = match.group(1)
            project_name = match.group(2).strip()
    
    # Extract date from filename
    file_date = extract_date_from_filename(filename)
    
    dashboard_route = '/ete'
    file_upper = filename.upper()
    if 'PVT' in file_upper:
        dashboard_route = '/pvt'
    elif 'BILLING' in file_upper:
        dashboard_route = '/ete-billing'

    return project_id, project_name, file_date, dashboard_route


def extract_tc_summary_compact(file_path):
    """Build compact TC summary from the 'TC Summary' sheet."""
    status_map = {}
    statuses = [
        'Completed',
        'Execution Complete/Uploaded for review',
        'Blocked',
        'Failed',
        'On Hold',
        'In Progress',
        'Not Started',
        'Deferred',
        'Descoped',
        'Total TCs'
    ]

    try:
        tc_df = pd.read_excel(file_path, sheet_name='TC Summary', header=None)
        for _, row in tc_df.iterrows():
            label = str(row.iloc[0]).strip() if len(row) > 0 and pd.notna(row.iloc[0]) else ''
            value = str(row.iloc[1]).strip() if len(row) > 1 and pd.notna(row.iloc[1]) else ''
            if label in statuses and value:
                status_map[label] = value
    except Exception:
        return 'N/A'

    total = status_map.get('Total TCs', '0')
    completed = status_map.get('Completed', '0')
    in_progress = status_map.get('In Progress', '0')
    blocked = status_map.get('Blocked', '0')
    failed = status_map.get('Failed', '0')

    return f"T:{total} | C:{completed} | IP:{in_progress} | B:{blocked} | F:{failed}"


def build_l1_detail_link(project_id, project_name, dashboard_route):
    """Build URL to GitHub Pages static L1 page (preferred) or local Flask fallback."""
    safe_id = str(project_id or '').strip()
    if GITHUB_PAGES_BASE_URL and safe_id:
        return f"{GITHUB_PAGES_BASE_URL}/html_reports/L1/PID_{safe_id}.html"
    # Fallback: local Flask dashboard
    if not L1_DASHBOARD_BASE_URL:
        return '#'
    route = dashboard_route or '/ete'
    encoded_name = quote_plus(str(project_name or ''))
    return f"{L1_DASHBOARD_BASE_URL}{route}?project_id={project_id}&project_name={encoded_name}"


def extract_tc_summary_full(file_path):
    """Read full TC Summary sheet into list of (label, value) pairs."""
    statuses = [
        'Total TCs', 'Completed', 'Execution Complete/Uploaded for review',
        'In Progress', 'Blocked', 'Failed', 'On Hold', 'Not Started',
        'Deferred', 'Descoped',
    ]
    rows = []
    try:
        tc_df = pd.read_excel(file_path, sheet_name='TC Summary', header=None)
        for _, row in tc_df.iterrows():
            label = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else ''
            value = str(row.iloc[1]).strip() if len(row) > 1 and pd.notna(row.iloc[1]) else ''
            if label in statuses:
                rows.append((label, value if value else '0'))
    except Exception:
        pass
    return rows


def generate_l1_static_page(project, file_path):
    """Generate a self-contained static HTML page for one L1 project."""
    tc_rows = extract_tc_summary_full(file_path)
    status = str(project.get('overall_status', 'N/A')).strip()
    status_lower = status.lower()
    if 'blocked' in status_lower:
        status_color = '#e74c3c'
    elif 'in progress' in status_lower or 'on schedule' in status_lower or 'ahead' in status_lower:
        status_color = '#27ae60'
    elif 'completed' in status_lower:
        status_color = '#3498db'
    elif 'behind' in status_lower:
        status_color = '#f39c12'
    else:
        status_color = '#7f8c8d'

    tc_rows_html = ''
    for label, value in tc_rows:
        tc_rows_html += f'<tr><td style="padding:8px 16px;border:1px solid #ddd;font-family:\'Times New Roman\',serif;">{escape(label)}</td><td style="padding:8px 16px;border:1px solid #ddd;text-align:center;font-weight:bold;font-family:\'Times New Roman\',serif;">{escape(value)}</td></tr>\n'

    if not tc_rows_html:
        tc_rows_html = '<tr><td colspan="2" style="padding:8px;text-align:center;color:#888;">No TC Summary data available</td></tr>'

    generated_at = datetime.now().strftime('%d %b %Y %I:%M %p')

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>L1 Report – {escape(str(project["project_name"]))}</title>
<style>
  body{{font-family:\'Times New Roman\',Times,serif;background:#f4f6f9;margin:0;padding:20px;}}
  .card{{background:#fff;max-width:860px;margin:0 auto;border-radius:10px;box-shadow:0 2px 12px rgba(0,0,0,.1);overflow:hidden;}}
  .header{{background:#4472C4;color:#fff;padding:24px 32px;}}
  .header h1{{margin:0;font-size:22px;}}
  .header p{{margin:4px 0 0;font-size:13px;opacity:.85;}}
  .body{{padding:28px 32px;}}
  .grid{{display:grid;grid-template-columns:1fr 1fr;gap:12px 32px;margin-bottom:24px;}}
  .field label{{font-size:11px;color:#888;text-transform:uppercase;letter-spacing:.5px;display:block;margin-bottom:2px;}}
  .field span{{font-size:14px;color:#222;}}
  .status-badge{{display:inline-block;padding:6px 18px;border-radius:20px;color:#fff;font-weight:bold;font-size:14px;background:{status_color};}}
  table{{width:100%;border-collapse:collapse;margin-top:8px;}}
  th{{background:#4472C4;color:#fff;padding:10px 16px;text-align:left;font-size:13px;}}
  th:last-child{{text-align:center;}}
  .footer{{font-size:11px;color:#aaa;text-align:right;margin-top:20px;}}
</style>
</head>
<body>
<div class="card">
  <div class="header">
    <h1>{escape(str(project["project_name"]))}</h1>
    <p>Project ID: {escape(str(project["project_id"]))} &nbsp;|&nbsp; UFD #: {escape(str(project["ufd_number"]))}</p>
  </div>
  <div class="body">
    <div class="grid">
      <div class="field"><label>Test Lead</label><span>{escape(str(project["test_lead"]))}</span></div>
      <div class="field"><label>Test Manager</label><span>{escape(str(project["test_manager"]))}</span></div>
      <div class="field"><label>Plan Start</label><span>{escape(str(project["plan_start"]))}</span></div>
      <div class="field"><label>Plan End</label><span>{escape(str(project["plan_end"]))}</span></div>
      <div class="field"><label>Planned %</label><span>{escape(str(project["planned_pct"]))}</span></div>
      <div class="field"><label>Passed %</label><span>{escape(str(project["passed_pct"]))}</span></div>
      <div class="field"><label>Last Updated</label><span>{escape(str(project["last_updated"]))}</span></div>
      <div class="field"><label>Overall Status</label><span class="status-badge">{escape(status)}</span></div>
    </div>
    <h3 style="margin:20px 0 10px;color:#4472C4;">TC Summary</h3>
    <table>
      <thead><tr><th>Status</th><th style="text-align:center;">Count</th></tr></thead>
      <tbody>{tc_rows_html}</tbody>
    </table>
    <div class="footer">Generated: {generated_at}</div>
  </div>
</div>
</body>
</html>
'''


def read_l2_project_data(file_path):
    """Extract project summary data from Excel file."""
    try:
        df_raw = pd.read_excel(file_path, sheet_name='Overall Project Status', header=None)
        
        # Extract project info from metadata rows (rows 3-11)
        test_lead = "N/A"
        test_manager = "N/A"
        ufd_number = "N/A"
        
        for i in range(3, 12):
            # Check column 0 for UFD Number
            if i < len(df_raw) and pd.notna(df_raw.iloc[i, 0]):
                key0 = str(df_raw.iloc[i, 0]).strip().lower()
                value0 = str(df_raw.iloc[i, 1]).strip() if pd.notna(df_raw.iloc[i, 1]) else 'N/A'
                
                if 'ufd number' in key0:
                    if value0 != 'N/A':
                        ufd_number = value0
            
            # Check column 3 for contact labels and column 4 for values
            if i < len(df_raw) and pd.notna(df_raw.iloc[i, 3]):
                key3 = str(df_raw.iloc[i, 3]).strip().lower()
                value3 = str(df_raw.iloc[i, 4]).strip() if pd.notna(df_raw.iloc[i, 4]) else 'N/A'
                
                if 'test lead' in key3:
                    if value3 != 'N/A':
                        test_lead = value3
                elif 'test manager' in key3:
                    if value3 != 'N/A':
                        test_manager = value3
        
        # Extract Overall Status table (rows 14-15)
        plan_start = "N/A"
        plan_end = "N/A"
        planned_pct = "N/A"
        passed_pct = "N/A"
        overall_status = "N/A"
        
        if len(df_raw) > 15:
            headers_row = df_raw.iloc[14, :].tolist()
            data_row = df_raw.iloc[15, :].tolist()
            
            # Find columns by header name
            for idx, header in enumerate(headers_row):
                if pd.isna(header):
                    continue
                    
                header_str = str(header).strip().lower()
                value = data_row[idx] if idx < len(data_row) and pd.notna(data_row[idx]) else None
                
                if 'plan start' in header_str:
                    if value:
                        if isinstance(value, str):
                            plan_start = value
                        else:
                            try:
                                plan_start = pd.Timestamp(value).strftime('%m/%d/%Y')
                            except:
                                plan_start = str(value)
                elif 'plan end' in header_str:
                    if value:
                        if isinstance(value, str):
                            plan_end = value
                        else:
                            try:
                                plan_end = pd.Timestamp(value).strftime('%m/%d/%Y')
                            except:
                                plan_end = str(value)
                elif 'planned %' in header_str or ('planned' in header_str and '%' in header_str):
                    if value:
                        try:
                            if isinstance(value, str):
                                planned_pct = value
                            else:
                                pct_val = float(value) * 100
                                planned_pct = f"{pct_val:.2f}%"
                        except:
                            planned_pct = str(value)
                elif 'passed %' in header_str or ('passed' in header_str and '%' in header_str):
                    if value:
                        try:
                            if isinstance(value, str):
                                passed_pct = value
                            else:
                                pct_val = float(value) * 100
                                passed_pct = f"{pct_val:.2f}%"
                        except:
                            passed_pct = str(value)
                elif 'overall status' in header_str:
                    if value:
                        overall_status = str(value).strip()
        
        # Get file modification time
        file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
        last_updated = file_mtime.strftime('%m/%d/%Y %I:%M %p')
        
        return {
            'test_lead': test_lead,
            'test_manager': test_manager,
            'ufd_number': ufd_number,
            'plan_start': plan_start,
            'plan_end': plan_end,
            'planned_pct': planned_pct,
            'passed_pct': passed_pct,
            'overall_status': overall_status,
            'tc_summary_compact': extract_tc_summary_compact(file_path),
            'last_updated': last_updated,
            'file_mtime': file_mtime
        }
    except Exception as e:
        print(f"Error reading {file_path.name}: {e}")
        import traceback
        traceback.print_exc()
        return None


def get_status_badge_html(status_text):
    """Return HTML for status badge matching dashboard styling."""
    status_lower = str(status_text).strip().lower()
    
    # Determine color and text
    if 'blocked' in status_lower:
        bg_color = '#e74c3c'  # Red
    elif 'in progress' in status_lower:
        bg_color = '#27ae60'  # Green
    elif 'completed' in status_lower:
        bg_color = '#3498db'  # Blue
    elif 'on schedule' in status_lower:
        bg_color = '#27ae60'  # Green
    elif 'behind' in status_lower:
        bg_color = '#f39c12'  # Orange/Yellow
    elif 'ahead' in status_lower:
        bg_color = '#27ae60'  # Green
    else:
        bg_color = '#7f8c8d'  # Gray
    
    return f'<span style="background: {bg_color}; color: white; padding: 6px 16px; border-radius: 20px; font-weight: bold; font-size: 13px; display: inline-block; font-family: Times New Roman, Times, serif; white-space: nowrap;">{status_text}</span>'


def deduplicate_by_project_name(projects_list):
    """Keep only latest file for each project name.
    Prioritizes filename date, falls back to modification time if date unavailable."""
    seen = {}
    for project in projects_list:
        name = project['project_name']
        if name not in seen:
            seen[name] = project
        else:
            current = seen[name]
            # First, compare by filename date if available
            if project['file_date'] and current['file_date']:
                if project['file_date'] > current['file_date']:
                    seen[name] = project
            elif project['file_date'] and not current['file_date']:
                # Prefer file with date over one without
                seen[name] = project
            elif not project['file_date'] and current['file_date']:
                # Keep the one with date
                pass
            else:
                # Both lack date, fall back to modification time
                if project['file_mtime'] > current['file_mtime']:
                    seen[name] = project
    
    return list(seen.values())


def generate_l2_report_html(projects_data):
    """Generate L2 report HTML with email format."""
    
    html = r'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>L2 Project Dashboard Report</title>
    <style>
        body {
            font-family: 'Times New Roman', Times, serif;
            background: #ffffff;
            margin: 0;
            padding: 0;
            font-size: 11pt;
        }
        .email-container {
            max-width: 1200px;
            margin: 0 auto;
            background: #ffffff;
            padding: 20px;
            font-family: 'Times New Roman', Times, serif;
            font-size: 11pt;
        }
        .greeting {
            font-size: 11pt;
            line-height: 1.6;
            color: #333333;
            margin-bottom: 15px;
            font-family: 'Times New Roman', Times, serif;
        }
        .greeting p {
            margin: 5px 0;
        }
        .table-section {
            margin-top: 20px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
            font-size: 11pt;
            font-family: 'Times New Roman', Times, serif;
        }
        th {
            background: #4472C4;
            color: #ffffff;
            font-weight: bold;
            padding: 10px;
            text-align: center;
            border: 1px solid #cccccc;
        }
        td {
            padding: 10px;
            text-align: center;
            border: 1px solid #cccccc;
            color: #333333;
        }
        tbody tr:nth-child(even) {
            background: #f0f0f0;
        }
        tbody tr:nth-child(odd) {
            background: #ffffff;
        }
        .footer {
            margin-top: 20px;
            font-size: 11pt;
            color: #666666;
            line-height: 1.6;
            font-family: 'Times New Roman', Times, serif;
        }
        .footer p {
            margin: 5px 0;
        }
    </style>
</head>
<body>
    <div class="email-container">
        <div class="greeting">
            <p>__EMAIL_GREETING__</p>
            <p>__EMAIL_INTRO_MESSAGE__</p>
        </div>

        <div class="table-section">
            <table>
                <thead>
                    <tr>
                        <th>Project ID</th>
                        <th>UFD #</th>
                        <th>Project Name</th>
                        <th>TC Summary</th>
                        <th>Plan Start</th>
                        <th>Plan End</th>
                        <th>Planned %</th>
                        <th>Passed %</th>
                        <th>Last Updated</th>
                        <th>Overall Status</th>
                        <th>L1 Report</th>
                    </tr>
                </thead>
                <tbody>
'''
    
    # Add project rows
    for idx, project in enumerate(projects_data):
        html += '                <tr>\n'
        html += f'                    <td>{project["project_id"]}</td>\n'
        html += f'                    <td>{project["ufd_number"]}</td>\n'
        html += f'                    <td>{project["project_name"]}</td>\n'
        html += f'                    <td>{project["tc_summary_compact"]}</td>\n'
        html += f'                    <td>{project["plan_start"]}</td>\n'
        html += f'                    <td>{project["plan_end"]}</td>\n'
        html += f'                    <td>{project["planned_pct"]}</td>\n'
        html += f'                    <td>{project["passed_pct"]}</td>\n'
        html += f'                    <td>{project["last_updated"]}</td>\n'
        html += f'                    <td>{project["status_html"]}</td>\n'
        html += f'                    <td><a href="{project["details_link"]}" target="_blank" rel="noopener noreferrer">Click here for more details</a></td>\n'
        html += '                </tr>\n'
    
    html += '''            </tbody>
            </table>
        </div>

        <div class="footer">
            <p>__EMAIL_FOOTER__</p>
            <p>__EMAIL_SIGNATURE__</p>
        </div>
    </div>
</body>
</html>
'''
    html = html.replace('__EMAIL_GREETING__', format_email_text(EMAIL_GREETING))
    html = html.replace('__EMAIL_INTRO_MESSAGE__', format_email_text(EMAIL_INTRO_MESSAGE))
    html = html.replace('__EMAIL_FOOTER__', format_email_text(EMAIL_FOOTER))
    html = html.replace('__EMAIL_SIGNATURE__', format_email_text(EMAIL_SIGNATURE))
    return html


def main():
    """Main execution."""
    print("=" * 70)
    print("L2 Report - Enhanced Dashboard Style with Deduplication")
    print("=" * 70)
    print()
    
    excel_dir = Path(BOX_LOCAL_PATH)
    
    if not excel_dir.exists():
        print(f"✗ Directory not found: {excel_dir}")
        return
    
    # Get all Excel files (including .xlsm)
    excel_files = sorted(
        list(excel_dir.glob("*.xlsx")) + list(excel_dir.glob("*.xls")) + list(excel_dir.glob("*.xlsm")),
        key=lambda p: p.stat().st_mtime,
        reverse=True
    )
    
    if not excel_files:
        print(f"✗ No Excel files found")
        return
    
    print(f"Found {len(excel_files)} Excel file(s):")
    for f in excel_files:
        print(f"  - {f.name}")
    print()
    
    # Extract project data
    projects_data = []
    for file_path in excel_files:
        print(f"Reading: {file_path.name}...")
        
        # Get project info from filename
        project_id, project_name, file_date, dashboard_route = parse_project_info_from_filename(file_path.name)
        
        if not project_id:
            print(f"  ⚠ Could not parse project ID from filename")
            continue
        
        # Get status data from Excel
        data = read_l2_project_data(file_path)
        if not data:
            print(f"  ⚠ Could not read data from Excel")
            continue
        
        # Build project record
        project_record = {
            'project_id': project_id,
            'project_name': project_name,
            'test_lead': data['test_lead'],
            'test_manager': data['test_manager'],
            'plan_start': data['plan_start'],
            'plan_end': data['plan_end'],
            'planned_pct': data['planned_pct'],
            'passed_pct': data['passed_pct'],
            'tc_summary_compact': data['tc_summary_compact'],
            'ufd_number': data['ufd_number'],
            'overall_status': data['overall_status'],
            'last_updated': data['last_updated'],
            'file_mtime': data['file_mtime'],
            'file_date': file_date,
            'dashboard_route': dashboard_route,
            'details_link': build_l1_detail_link(project_id, project_name, dashboard_route),
            'status_html': get_status_badge_html(data['overall_status'])
        }
        
        projects_data.append(project_record)
        # Store original file_path on record so static pages can be generated later
        project_record['_file_path'] = file_path
        print(f"  ✓ Project: {project_name}")
        print(f"      Test Lead: {data['test_lead']} | Test Manager: {data['test_manager']}")
        print(f"      UFD: {data['ufd_number']} | Updated: {data['last_updated']}")
        if file_date:
            print(f"      File Date: {file_date.strftime('%Y-%m-%d')}")
        else:
            print(f"      File Date: Could not parse from filename")
    
    print()
    
    if not projects_data:
        print("✗ No projects found")
        return
    
    # Deduplicate by project name
    print(f"Total projects before deduplication: {len(projects_data)}")
    projects_data = deduplicate_by_project_name(projects_data)
    print(f"Total projects after deduplication: {len(projects_data)}")
    print()
    
    # Sort by project ID for consistent display
    projects_data.sort(key=lambda p: p['project_id'])
    
    # Generate HTML
    print("Generating HTML...")
    html = generate_l2_report_html(projects_data)
    
    # Save to file in html_reports folder (in parent directory)
    output_dir = Path(__file__).parent.parent / 'html_reports'
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / 'L2_Report.html'
    output_file.write_text(html, encoding='utf-8')
    print(f"✓ HTML saved: {output_file}")
    print(f"  File size: {output_file.stat().st_size:,} bytes")
    print(f"  Projects: {len(projects_data)}")
    print()

    # Generate per-project static L1 pages for GitHub Pages
    if GITHUB_PAGES_BASE_URL:
        l1_dir = output_dir / 'L1'
        l1_dir.mkdir(exist_ok=True)
        print("Generating static L1 project pages for GitHub Pages...")
        for project in projects_data:
            fp = project.get('_file_path')
            if not fp:
                continue
            safe_id = str(project['project_id']).strip()
            page_html = generate_l1_static_page(project, fp)
            page_file = l1_dir / f'PID_{safe_id}.html'
            page_file.write_text(page_html, encoding='utf-8')
            print(f"  ✓ {page_file.name}")
        print(f"✓ L1 static pages saved to: {l1_dir}")
        print()

    # Open in browser
    print("Opening in browser...")
    webbrowser.open(f'file:///{output_file}')


if __name__ == '__main__':
    main()
