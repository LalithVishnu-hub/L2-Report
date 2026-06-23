"""
Validation script for L2 Report Automation setup.
Checks all prerequisites and configuration before automation is enabled.
"""

import os
import sys
import logging
from pathlib import Path
from datetime import datetime
import smtplib

# Setup logging
log_dir = Path(__file__).parent / 'logs'
log_dir.mkdir(exist_ok=True)
log_file = log_dir / f"validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class ValidationChecker:
    """Validates L2 Report Automation setup."""

    def __init__(self):
        """Initialize checker."""
        self.checks_passed = 0
        self.checks_failed = 0
        self.warnings = []
        self.script_dir = Path(__file__).parent

    def log_check(self, name: str, result: bool, message: str = ""):
        """Log a check result."""
        if result:
            self.checks_passed += 1
            logger.info(f"✓ {name}")
            if message:
                logger.info(f"  → {message}")
        else:
            self.checks_failed += 1
            logger.error(f"✗ {name}")
            if message:
                logger.error(f"  → {message}")

    def log_warning(self, message: str):
        """Log a warning."""
        self.warnings.append(message)
        logger.warning(f"⚠ {message}")

    def check_python_version(self) -> bool:
        """Check Python version."""
        version = sys.version_info
        required = (3, 8)
        result = version >= required
        message = f"Python {version.major}.{version.minor}.{version.micro}"
        self.log_check("Python Version", result, message)
        return result

    def check_required_files(self) -> bool:
        """Check if all required files exist."""
        required_files = [
            'email_utils.py',
            'report_generator.py',
            'report_scheduler.py',
            'send_reports.py',
            'setup_task_scheduler.py',
            'test_email_format.html',
        ]

        all_exist = True
        for filename in required_files:
            file_path = self.script_dir / filename
            exists = file_path.exists()
            self.log_check(f"File: {filename}", exists, str(file_path) if exists else "NOT FOUND")
            all_exist = all_exist and exists

        return all_exist

    def check_env_configuration(self) -> bool:
        """Check .env file configuration."""
        from dotenv import load_dotenv
        
        env_file = self.script_dir / '.env'
        if not env_file.exists():
            self.log_check(".env File", False, "File not found")
            return False

        self.log_check(".env File", True, "File found")

        # Load environment
        load_dotenv(env_file)

        # Check required variables
        all_configured = True

        # SMTP Configuration
        smtp_server = os.environ.get('SMTP_SERVER')
        self.log_check("SMTP_SERVER configured", smtp_server is not None, smtp_server or "NOT SET")
        all_configured = all_configured and smtp_server is not None

        smtp_port = os.environ.get('SMTP_PORT')
        self.log_check("SMTP_PORT configured", smtp_port is not None, smtp_port or "NOT SET")
        all_configured = all_configured and smtp_port is not None

        smtp_from = os.environ.get('SMTP_FROM_EMAIL')
        self.log_check("SMTP_FROM_EMAIL configured", smtp_from is not None, smtp_from or "NOT SET")
        all_configured = all_configured and smtp_from is not None

        # Email Recipients
        recipients = os.environ.get('EMAIL_RECIPIENTS')
        if recipients:
            self.log_check("EMAIL_RECIPIENTS configured", True, recipients)
        else:
            self.log_check("EMAIL_RECIPIENTS configured", False, "NOT SET - Required for automation")
            all_configured = False

        # Excel folder
        excel_folder = os.environ.get('BOX_LOCAL_PATH')
        if excel_folder:
            folder_exists = Path(excel_folder).exists()
            self.log_check("BOX_LOCAL_PATH exists", folder_exists, excel_folder if folder_exists else f"Path not found: {excel_folder}")
            if folder_exists:
                # Check for Excel files
                excel_files = list(Path(excel_folder).glob('*.xlsx')) + list(Path(excel_folder).glob('*.xls'))
                self.log_check("Excel files in BOX_LOCAL_PATH", len(excel_files) > 0, f"Found {len(excel_files)} file(s)")
            else:
                all_configured = False
        else:
            self.log_warning("BOX_LOCAL_PATH not configured - will use default")

        return all_configured

    def check_dependencies(self) -> bool:
        """Check if all required Python packages are installed."""
        required_packages = {
            'flask': 'Flask',
            'pandas': 'Pandas',
            'openpyxl': 'OpenPyXL',
            'dotenv': 'python-dotenv',
            'requests': 'Requests',
            'watchdog': 'Watchdog',
            'apscheduler': 'APScheduler',
            'pytz': 'pytz',
        }

        all_installed = True
        for import_name, package_name in required_packages.items():
            try:
                __import__(import_name)
                self.log_check(f"Package: {package_name}", True)
            except ImportError:
                self.log_check(f"Package: {package_name}", False, f"Install with: pip install {package_name}")
                all_installed = False

        return all_installed

    def check_smtp_connection(self) -> bool:
        """Test SMTP connection."""
        try:
            smtp_server = os.environ.get('SMTP_SERVER', 'mail.company.com')
            smtp_port = int(os.environ.get('SMTP_PORT', 25))
            use_tls = os.environ.get('SMTP_USE_TLS', 'false').lower() == 'true'

            logger.info(f"Testing SMTP connection to {smtp_server}:{smtp_port}...")

            try:
                server = smtplib.SMTP(smtp_server, smtp_port, timeout=5)
                if use_tls:
                    server.starttls()
                server.quit()
                self.log_check("SMTP Connection", True, f"{smtp_server}:{smtp_port}")
                return True
            except smtplib.SMTPException as e:
                self.log_check("SMTP Connection", False, f"SMTP Error: {e}")
                return False
            except Exception as e:
                self.log_check("SMTP Connection", False, f"Connection Error: {e}")
                return False

        except Exception as e:
            self.log_check("SMTP Connection", False, str(e))
            return False

    def check_report_generation(self) -> bool:
        """Test report generation."""
        try:
            from report_generator import get_report_generator

            generator = get_report_generator()
            html = generator.generate_email_html(subject="Validation Test")

            if html and len(html) > 100:
                self.log_check("Report Generation", True, f"Generated {len(html)} bytes")
                return True
            else:
                self.log_check("Report Generation", False, "Generated invalid HTML")
                return False

        except Exception as e:
            self.log_check("Report Generation", False, str(e))
            return False

    def check_excel_reading(self) -> bool:
        """Test Excel file reading."""
        try:
            from report_generator import get_report_generator

            generator = get_report_generator()
            latest_files = generator.get_latest_excel_files(limit=1)

            if not latest_files:
                self.log_warning("No Excel files found - using default folder path")
                return False

            file = latest_files[0]
            columns, rows = generator.read_excel_data(file)

            if columns and rows:
                self.log_check("Excel File Reading", True, f"{file.name}: {len(columns)} columns, {len(rows)} rows")
                return True
            else:
                self.log_check("Excel File Reading", False, f"Could not read: {file.name}")
                return False

        except Exception as e:
            self.log_check("Excel File Reading", False, str(e))
            return False

    def check_logs_directory(self) -> bool:
        """Check and create logs directory."""
        logs_dir = self.script_dir / 'logs'
        if logs_dir.exists():
            self.log_check("Logs Directory", True, str(logs_dir))
            return True
        else:
            try:
                logs_dir.mkdir()
                self.log_check("Logs Directory", True, f"Created: {logs_dir}")
                return True
            except Exception as e:
                self.log_check("Logs Directory", False, str(e))
                return False

    def check_flask_routes(self) -> bool:
        """Check if Flask routes are available."""
        try:
            import app
            
            # Check if key routes are defined
            routes_to_check = [
                '/email/test-format',
                '/email/generate-report',
                '/email/send-test',
                '/scheduler/info',
            ]

            # Get all routes from app
            app_routes = [str(rule) for rule in app.app.url_map.iter_rules()]
            
            missing_routes = []
            for route in routes_to_check:
                if not any(route in str(r) for r in app_routes):
                    missing_routes.append(route)

            if missing_routes:
                self.log_warning(f"Missing Flask routes: {missing_routes}")
                return False
            else:
                self.log_check("Flask Email Routes", True, "All routes available")
                return True

        except Exception as e:
            self.log_warning(f"Could not verify Flask routes: {e}")
            return False

    def run_all_checks(self) -> bool:
        """Run all validation checks."""
        logger.info("=" * 70)
        logger.info("L2 Report Automation - Setup Validation")
        logger.info("=" * 70)
        logger.info("")

        # Run all checks
        logger.info("ENVIRONMENT CHECKS:")
        logger.info("-" * 70)
        self.check_python_version()
        self.check_required_files()
        self.check_logs_directory()

        logger.info("")
        logger.info("CONFIGURATION CHECKS:")
        logger.info("-" * 70)
        self.check_env_configuration()
        self.check_dependencies()

        logger.info("")
        logger.info("FUNCTIONALITY CHECKS:")
        logger.info("-" * 70)
        self.check_smtp_connection()
        self.check_report_generation()
        self.check_excel_reading()
        self.check_flask_routes()

        logger.info("")
        logger.info("=" * 70)
        logger.info("VALIDATION SUMMARY")
        logger.info("=" * 70)
        logger.info(f"Passed: {self.checks_passed}")
        logger.info(f"Failed: {self.checks_failed}")
        logger.info(f"Warnings: {len(self.warnings)}")
        logger.info("")

        if self.warnings:
            logger.info("WARNINGS:")
            for warning in self.warnings:
                logger.warning(f"  • {warning}")
            logger.info("")

        if self.checks_failed == 0:
            logger.info("✓ All checks passed! Ready for automation setup.")
            logger.info("=" * 70)
            logger.info("NEXT STEPS:")
            logger.info("-" * 70)
            logger.info("1. Update .env with EMAIL_RECIPIENTS if not already set")
            logger.info("2. Test email sending: python send_reports.py --mode test")
            logger.info("3. Preview report format: http://localhost:5000/email/test-format")
            logger.info("4. Setup automation: python setup_task_scheduler.py")
            logger.info("   (Requires Administrator privileges)")
            logger.info("=" * 70)
            return True
        else:
            logger.error("✗ Some checks failed. See above for details.")
            logger.info("=" * 70)
            logger.info("FIX FAILURES BEFORE SETTING UP AUTOMATION")
            logger.info("=" * 70)
            return False


def main():
    """Main function."""
    checker = ValidationChecker()
    success = checker.run_all_checks()

    logger.info(f"Validation log: {log_file}")
    logger.info("")

    return success


if __name__ == '__main__':
    from dotenv import load_dotenv
    
    load_dotenv()
    
    success = main()
    sys.exit(0 if success else 1)
