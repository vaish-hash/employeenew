import os
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_file, make_response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from datetime import datetime, date, timedelta
from calendar import monthrange
import io
import pandas as pd
import re
import sys
# from db_seeder import seed_all_data # Ensure db_seeder.py exists in the same directory


# Get the absolute path of the directory containing this app.py file
current_app_dir = os.path.abspath(os.path.dirname(__file__))

# Initialize the Flask application, explicitly setting template and static folders
app = Flask(
    __name__,
    template_folder=os.path.join(current_app_dir, 'templates'),
    static_folder=os.path.join(current_app_dir, 'static')
)
# --- NEW: CONFIGURATION FOR YOUR APP'S STOP DATE ---
# IMPORTANT:
# 1. Set this date to a few days from now (e.g., if today is July 3, 2025, set it to "2025-07-06").
#    This allows your app to run for a few days, then stop.
# 2. To test immediately, you can set it to a date in the past (e.g., "2025-06-25").
#    This will make the app stop as soon as you run it.
APP_HARD_STOP_DATE_STR = "2025-08-16" # Year-Month-Day format (e.g., 2025-07-03 for July 3rd, 2025)
# ---------------------------------------------------
# --- NEW: Function to check if the app should stop ---
def check_app_for_hard_stop():
    """
    This function contains the logic to determine if the application
    should stop based on a pre-defined date.
    If the current date is on or after the APP_HARD_STOP_DATE_STR,
    the application will be prevented from running further.
    """
    try:
        # Convert the configured stop date string into a date object
        stop_date = datetime.strptime(APP_HARD_STOP_DATE_STR, "%Y-%m-%d").date() # Removed the extra '.datetime'
        # Get today's current date
        current_date = date.today() # Just use 'date' directly since it's imported

        if current_date >= stop_date:
            # --- THIS IS THE "STOP SWITCH" PART ---
            print("\n" + "="*60)
            print("!!! APPLICATION STOPPED - LICENCE/TRIAL EXPIRED !!!".center(60))
            print(f"This application was configured to stop on: {APP_HARD_STOP_DATE_STR}".center(60))
            print(f"Today's date is: {current_date}".center(60))
            print("The application will not function until rectified in the code.".center(60))
            print("================================================" + "\n")
            return False # Indicate that the app should NOT proceed
        else:
            # If the stop date is not yet reached, print a message and allow the app to continue
            days_remaining = (stop_date - current_date).days
            print(f"App is active. Will stop in {days_remaining} day(s) on {APP_HARD_STOP_DATE_STR}.")
            return True # Indicates that the app can proceed

    except ValueError:
        # This catches errors if APP_HARD_STOP_DATE_STR is in the wrong format
        print("\n" + "="*60)
        print("!!! CONFIGURATION ERROR: INVALID DATE FORMAT !!!".center(60))
        print("Please check APP_HARD_STOP_DATE_STR. It must be YYYY-MM-DD.".center(60))
        print("="*60 + "\n")
        return False # Indicate that the app should NOT proceed due to config error
    except Exception as e:
        # Catches any other unexpected errors during the check itself
        print(f"\nAn unexpected error occurred during the stop check: {e}")
        return False # Indicate that the app should NOT proceed due to error
# --- SQLAlchemy Configuration ---
instance_path = os.path.join(current_app_dir, 'instance')
if not os.path.exists(instance_path):
    os.makedirs(instance_path)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
# Flask-Migrate is useful for schema changes, but not strictly required if you use flask init-db
# from flask_migrate import Migrate
# migrate = Migrate(app, db)


# --- Database Models ---

class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    role = db.Column(db.String(80), nullable=False)

    assignments = db.relationship('Assignment', backref='employee', lazy=True)

    def __repr__(self):
        return f'<Employee {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'role': self.role
        }

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    duration_months = db.Column(db.Integer, nullable=False)
    start_month = db.Column(db.String(20), nullable=False)
    start_year = db.Column(db.Integer, nullable=False)
    end_month = db.Column(db.String(20), nullable=False)
    end_year = db.Column(db.Integer, nullable=False)

    assignments = db.relationship('Assignment', backref='project', lazy=True)

    def __repr__(self):
        return f'<Project {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'duration_months': self.duration_months,
            'start_month': self.start_month,
            'start_year': self.start_year,
            'end_month': self.end_month,
            'end_year': self.end_year
        }

class Assignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    assigned_hours_per_week = db.Column(db.Integer, nullable=False)
    assigned_start_month = db.Column(db.String(20), nullable=False)
    assigned_start_year = db.Column(db.Integer, nullable=False)
    assigned_end_month = db.Column(db.String(20), nullable=False)
    assigned_end_year = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'<Assignment {self.employee_id} to {self.project_id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'project_id': self.project_id,
            'assigned_hours_per_week': self.assigned_hours_per_week,
            'assigned_start_month': self.assigned_start_month,
            'assigned_start_year': self.assigned_start_year,
            'assigned_end_month': self.assigned_end_month,
            'assigned_end_year': self.assigned_end_year,
        }

class WeeklyHours(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignment.id'), nullable=False)
    week_start_date = db.Column(db.Date, nullable=False)
    hours_worked = db.Column(db.Integer, nullable=False)
    function_name = db.Column(db.String(80), nullable=True) 

    assignment = db.relationship('Assignment', backref=db.backref('weekly_hours', lazy=True))

    __table_args__ = (db.UniqueConstraint('assignment_id', 'week_start_date', 'function_name', name='_assignment_week_function_uc'),)

    def __repr__(self):
        return f"<WeeklyHours AssignmentID: {self.assignment_id}, Week: {self.week_start_date}, Hours: {self.hours_worked}, Function: {self.function_name}>"

    @property
    def percentage(self):
        if self.hours_worked is None:
            return 0
        return (self.hours_worked / 40.0) * 100

    @property
    def status(self):
        if self.hours_worked > 40:
            return 'Overloaded'
        elif self.hours_worked < 40:
            return 'Free'
        else:
            return 'Normal'
        # --- NEW: Custom Error Page Route for Expired App ---
@app.route('/app_stopped')
def app_stopped():
    # This will render a new HTML template we'll create later
    return render_template('app_stopped.html', stop_date=APP_HARD_STOP_DATE_STR)
# Disabled the hard stop check to prevent timeout issues
# @app.before_request
# def check_app_status_before_request():
#     if request.path != url_for('app_stopped') and not request.path.startswith('/static/'):
#         if not check_app_for_hard_stop():
#             return redirect(url_for('app_stopped'))
# ---------------------------------------------------

# --- IMPORTANT: Configure a secret key for session management ---
app.config['SECRET_KEY'] = os.urandom(24)

# --- Flask CLI Commands ---
@app.cli.command("init-db")
def init_db_command():
    """Clear existing data and create new tables."""
    with app.app_context():
        db.drop_all()
        db.create_all()
    print("Database tables initialized!")

# @app.cli.command("seed-data")
# def seed_data_command():
#     """Seed the database with initial data."""
#     print("Starting database seeding process...")
#     with app.app_context():
#         seed_all_data()
#     print("Database seeding complete!")


# --- Routes ---

@app.route('/')
def home():
    if 'logged_in' in session and session['logged_in']:
        return redirect(url_for('index'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
            username = data.get('username')
            password = data.get('password')
        else:
            username = request.form.get('username')
            password = request.form.get('password')

        if username == 'admin' and password == 'password':
            session['logged_in'] = True
            session['username'] = username
            flash('Logged in successfully!', 'success')
            return jsonify({'success': True, 'redirect_url': url_for('index')})
        else:
            flash('Invalid Credentials. Please try again.', 'error')
            return jsonify({'success': False, 'message': 'Invalid Credentials.'}), 401
    return render_template('login.html')


@app.route('/index')
def index():
    if 'logged_in' in session and session['logged_in']:
        return render_template('index.html', username=session.get('username', 'Guest'))
    else:
        flash('Please log in to access this page.', 'warning')
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

# --- Dashboard Pages Routes ---

@app.route('/actual_hours')
def get_actual_hours_page():
    if 'logged_in' in session and session['logged_in']:
        return render_template('actual_hours.html')
    flash('Please log in to access this page.', 'warning')
    return redirect(url_for('login'))

@app.route('/import_data')
def get_import_data_page():
    """Renders the import data page."""
    if 'logged_in' in session and session['logged_in']:
        return render_template('import_data.html')
    flash('Please log in to access this page.', 'warning')
    return redirect(url_for('login'))

@app.route('/members')
def get_employees_page():
    if 'logged_in' in session and session['logged_in']:
        return render_template('members.html')
    flash('Please log in to access this page.', 'warning')
    return redirect(url_for('login'))

# --- START OF API ENDPOINTS ---

@app.route('/api/import_data', methods=['POST'])
def api_import_data():
    """Handles Excel file upload and imports data into the database."""
    if not (session.get('logged_in') and session['logged_in']):
        return jsonify({"error": "Unauthorized"}), 401

    if 'excel_file' not in request.files:
        return jsonify({"message": "No file part"}), 400

    file = request.files['excel_file']
    data_type = request.form.get('data_type')

    if file.filename == '':
        return jsonify({"message": "No selected file"}), 400

    if not data_type:
        return jsonify({"message": "No data type selected for import"}), 400

    if file and (file.filename.endswith('.xlsx') or file.filename.endswith('.xls')):
        try:
            df = pd.read_excel(file)
            imported_count = 0
            skipped_count = 0
            errors = []
            
            # Debug: Log the actual column names found
            app.logger.info(f"Excel columns found: {list(df.columns)}")
            app.logger.info(f"Data type selected: {data_type}")
            app.logger.info(f"DataFrame shape: {df.shape}")
            
            # Auto-detect and fix column headers
            original_columns = list(df.columns)
            
            # If columns are unnamed or numeric, try to find headers in data
            if any(col.startswith('Unnamed:') or str(col).isdigit() for col in df.columns):
                app.logger.warning("Excel file appears to have no proper column headers")
                
                # Search first few rows for potential headers
                header_row_index = None
                for i in range(min(5, len(df))):
                    row = df.iloc[i]
                    # Check if row contains mostly text (potential headers)
                    text_count = sum(1 for val in row if isinstance(val, str) and len(str(val).strip()) > 0)
                    if text_count >= len(row) * 0.6:  # 60% of columns have text
                        header_row_index = i
                        break
                
                if header_row_index is not None:
                    # Use this row as headers
                    df.columns = [str(val).strip() if pd.notna(val) else f"Column_{i}" for i, val in enumerate(df.iloc[header_row_index])]
                    df = df.drop(df.index[header_row_index]).reset_index(drop=True)
                    app.logger.info(f"Used row {header_row_index} as headers: {list(df.columns)}")
                else:
                    # Create generic column names based on data analysis
                    df.columns = [f"Column_{i}" for i in range(len(df.columns))]
                    app.logger.info("Created generic column names")

            if data_type == 'employees':
                # Expected columns: 'Name', 'Email', 'Position'
                for index, row in df.iterrows():
                    name = row.get('Name')
                    email = row.get('Email')
                    role = row.get('Position')

                    if not all([name, email, role]):
                        errors.append(f"Row {index + 2} (Employee): Missing Name, Email, or Position. Skipped.")
                        skipped_count += 1
                        continue
                    if not isinstance(email, str) or "@" not in email or "." not in email:
                        errors.append(f"Row {index + 2} (Employee): Invalid email format for '{email}'. Skipped.")
                        skipped_count += 1
                        continue

                    try:
                        existing_employee = Employee.query.filter_by(email=email).first()
                        if existing_employee:
                            errors.append(f"Row {index + 2} (Employee): Employee with email '{email}' already exists, skipped.")
                            skipped_count += 1
                            continue

                        new_employee = Employee(name=name, email=email, role=role)
                        db.session.add(new_employee)
                        db.session.commit()
                        imported_count += 1
                    except IntegrityError:
                        db.session.rollback()
                        errors.append(f"Row {index + 2} (Employee): Database integrity error for employee '{name}' ({email}). Possible duplicate. Skipped.")
                        skipped_count += 1
                    except Exception as e:
                        db.session.rollback()
                        errors.append(f"Row {index + 2} (Employee): Error importing employee '{name}' ({email}): {str(e)}. Skipped.")
                        skipped_count += 1
                message = f"Employees import complete. Imported: {imported_count}, Skipped: {skipped_count}."
                if errors:
                    message += " Errors encountered."

            elif data_type == 'projects':
                # Expected columns: 'Project Name', 'Duration (Months)', 'Start Month', 'Start Year', 'End Month', 'End Year'
                for index, row in df.iterrows():
                    name = row.get('Project Name')
                    duration_months = row.get('Duration (Months)')
                    start_month_str = row.get('Start Month')
                    start_year = row.get('Start Year')
                    end_month_str = row.get('End Month')
                    end_year = row.get('End Year')

                    if not all([name, duration_months, start_month_str, start_year, end_month_str, end_year]):
                        errors.append(f"Row {index + 2} (Project): Missing project data. Skipped.")
                        skipped_count += 1
                        continue

                    try:
                        existing_project = Project.query.filter_by(name=name).first()
                        if existing_project:
                            errors.append(f"Row {index + 2} (Project): Project with name '{name}' already exists, skipped.")
                            skipped_count += 1
                            continue

                        month_names = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
                        if start_month_str not in month_names or end_month_str not in month_names:
                            errors.append(f"Row {index + 2} (Project): Invalid month name for project '{name}'. Skipped.")
                            skipped_count += 1
                            continue

                        new_project = Project(
                            name=name,
                            duration_months=int(duration_months),
                            start_month=start_month_str,
                            start_year=int(start_year),
                            end_month=end_month_str,
                            end_year=int(end_year)
                        )
                        db.session.add(new_project)
                        db.session.commit()
                        imported_count += 1
                    except IntegrityError:
                        db.session.rollback()
                        errors.append(f"Row {index + 2} (Project): Database integrity error for project '{name}'. Possible duplicate. Skipped.")
                        skipped_count += 1
                    except ValueError:
                        db.session.rollback()
                        errors.append(f"Row {index + 2} (Project): Invalid number format for project '{name}' duration/year. Skipped.")
                        skipped_count += 1
                    except Exception as e:
                        db.session.rollback()
                        errors.append(f"Row {index + 2} (Project): Error importing project '{name}': {str(e)}. Skipped.")
                        skipped_count += 1
                message = f"Projects import complete. Imported: {imported_count}, Skipped: {skipped_count}."
                if errors:
                    message += " Errors encountered."

            elif data_type == 'actual_hours_bulk':
                # This section is designed to handle your raw, unorganized Excel data with
                # 'Emp Name', 'Project Name', 'Function', 'Week Days', and 'Hours' columns.
                
                # Smart data mapping - analyze data content to identify columns
                def smart_column_mapping(df):
                    mapping = {}
                    df_columns = [str(col).strip() for col in df.columns]
                    
                    # Analyze each column's data to identify its type
                    for col in df_columns:
                        col_data = df[col].dropna().head(10)  # Sample first 10 non-null values
                        col_lower = col.lower()
                        
                        # Employee name detection
                        if not mapping.get('emp_name'):
                            if any(keyword in col_lower for keyword in ['emp', 'employee', 'name', 'person', 'staff']) and col_lower not in ['project name', 'proj name']:
                                mapping['emp_name'] = col
                                continue
                            # Check if column contains name-like data
                            if col_data.apply(lambda x: isinstance(x, str) and len(str(x).split()) >= 2).sum() >= len(col_data) * 0.5:
                                mapping['emp_name'] = col
                                continue
                        
                        # Project name detection
                        if not mapping.get('project_name'):
                            if any(keyword in col_lower for keyword in ['project', 'proj', 'job', 'task', 'work']):
                                mapping['project_name'] = col
                                continue
                        
                        # Function detection
                        if not mapping.get('function_name'):
                            if any(keyword in col_lower for keyword in ['function', 'role', 'position', 'job', 'title', 'dept', 'department']):
                                mapping['function_name'] = col
                                continue
                        
                        # Date/week detection
                        if not mapping.get('week_days'):
                            if any(keyword in col_lower for keyword in ['week', 'date', 'day', 'time', 'period']):
                                mapping['week_days'] = col
                                continue
                            # Check if column contains date-like data
                            try:
                                date_count = col_data.apply(lambda x: pd.to_datetime(x, errors='coerce')).notna().sum()
                                if date_count >= len(col_data) * 0.5:
                                    mapping['week_days'] = col
                                    continue
                            except:
                                pass
                        
                        # Hours detection
                        if not mapping.get('hours'):
                            if any(keyword in col_lower for keyword in ['hour', 'hrs', 'time', 'duration']):
                                mapping['hours'] = col
                                continue
                            # Check if column contains numeric data
                            try:
                                numeric_count = pd.to_numeric(col_data, errors='coerce').notna().sum()
                                if numeric_count >= len(col_data) * 0.7:
                                    mapping['hours'] = col
                                    continue
                            except:
                                pass
                    
                    return mapping
                
                # Auto-assign missing fields based on column position if smart mapping fails
                def fallback_mapping(df, current_mapping):
                    df_columns = list(df.columns)
                    required_fields = ['emp_name', 'project_name', 'function_name', 'week_days', 'hours']
                    
                    # If we have at least 5 columns, assume standard order
                    if len(df_columns) >= 5:
                        fallback_map = {
                            'emp_name': df_columns[0],
                            'project_name': df_columns[1], 
                            'function_name': df_columns[2],
                            'week_days': df_columns[3],
                            'hours': df_columns[4]
                        }
                        
                        # Use fallback only for missing fields
                        for field in required_fields:
                            if field not in current_mapping:
                                current_mapping[field] = fallback_map[field]
                    
                    return current_mapping
                
                # Apply smart mapping
                column_mapping = smart_column_mapping(df)
                app.logger.info(f"Smart column mapping: {column_mapping}")
                
                # Apply fallback mapping if needed
                column_mapping = fallback_mapping(df, column_mapping)
                app.logger.info(f"Final column mapping: {column_mapping}")
                
                # Ensure all required fields are mapped
                required_fields = ['emp_name', 'project_name', 'function_name', 'week_days', 'hours']
                if not all(field in column_mapping for field in required_fields):
                    # Last resort: use first 5 columns
                    df_columns = list(df.columns)
                    for i, field in enumerate(required_fields):
                        if field not in column_mapping and i < len(df_columns):
                            column_mapping[field] = df_columns[i]
                    
                    app.logger.info(f"Applied last resort mapping: {column_mapping}")
                
                employee_cache = {} # name -> Employee object
                project_cache = {}  # name -> Project object
                assignment_cache = {} # (employee_id, project_id) -> Assignment object
                
                # Filter out rows where essential columns are completely empty (e.g., blank rows at end)
                df = df.dropna(subset=['Emp Name', 'Project Name', 'Function', 'Week Days', 'Hours'], how='all')
                
                # Use a dictionary to aggregate hours for unique (employee, project, function, week_start_date) combinations
                # This handles multiple entries for the same week/task by summing hours.
                aggregated_weekly_hours = {} # (emp_name, proj_name, func_name, week_start_date_obj) -> total_hours

                for index, row in df.iterrows():
                    try:
                        # Safely extract data with fallback values
                        emp_name = str(row.get(column_mapping.get('emp_name', ''), 'Unknown Employee')).strip()
                        project_name = str(row.get(column_mapping.get('project_name', ''), 'Unknown Project')).strip()
                        function_name = str(row.get(column_mapping.get('function_name', ''), 'General')).strip()
                        week_days_raw = row.get(column_mapping.get('week_days', ''))
                        hours_raw = row.get(column_mapping.get('hours', ''))

                        # Clean up 'nan' strings and None values
                        if emp_name.lower() in ['nan', 'none', ''] or pd.isna(emp_name):
                            emp_name = f"Employee_{index + 1}"
                        if project_name.lower() in ['nan', 'none', ''] or pd.isna(project_name):
                            project_name = f"Project_{index + 1}"
                        if function_name.lower() in ['nan', 'none', ''] or pd.isna(function_name):
                            function_name = "General"

                        # Skip completely empty rows
                        if all(pd.isna(val) or str(val).strip() == '' for val in [emp_name, project_name, week_days_raw, hours_raw]):
                            continue

                    except Exception as e:
                        errors.append(f"Row {index + 2}: Error extracting data - {str(e)}. Using defaults.")
                        emp_name = f"Employee_{index + 1}"
                        project_name = f"Project_{index + 1}"
                        function_name = "General"
                        week_days_raw = None
                        hours_raw = 0

                    try:
                        # Smart date parsing with multiple fallbacks
                        week_start_date = None
                        
                        if pd.isna(week_days_raw) or week_days_raw == '':
                            # Use current week if no date provided
                            week_start_date = datetime.now().date()
                        elif isinstance(week_days_raw, (datetime, date)):
                            week_start_date = week_days_raw.date() if isinstance(week_days_raw, datetime) else week_days_raw
                        else:
                            # Try multiple parsing methods
                            try:
                                # Use pandas to_datetime which handles many formats
                                week_start_date = pd.to_datetime(week_days_raw, errors='coerce')
                                if pd.isna(week_start_date):
                                    raise ValueError("Could not parse date")
                                week_start_date = week_start_date.date()
                            except:
                                try:
                                    # Try Excel numeric date
                                    if isinstance(week_days_raw, (int, float)):
                                        week_start_date = pd.to_datetime(week_days_raw, unit='D', origin='1899-12-30').date()
                                    else:
                                        # Try common date formats
                                        week_days_str = str(week_days_raw).strip()
                                        for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%b %d, %Y', '%B %d, %Y', '%d-%m-%Y', '%m-%d-%Y']:
                                            try:
                                                week_start_date = datetime.strptime(week_days_str, fmt).date()
                                                break
                                            except ValueError:
                                                continue
                                        
                                        if not week_start_date:
                                            # Last resort: use current date
                                            week_start_date = datetime.now().date()
                                            errors.append(f"Row {index + 2}: Could not parse date '{week_days_raw}', using current date")
                                except:
                                    # Ultimate fallback
                                    week_start_date = datetime.now().date()
                                    errors.append(f"Row {index + 2}: Date parsing failed, using current date")

                        if not week_start_date:
                            raise ValueError(f"Week start date could not be parsed from '{week_days_raw}'")

                        # Smart hours parsing with fallbacks
                        hours_to_add = 0
                        if pd.isna(hours_raw) or str(hours_raw).strip() == '':
                            hours_to_add = 0
                        else:
                            try:
                                # Handle various hour formats
                                hours_str = str(hours_raw).strip().lower()
                                
                                # Remove common text that might be in hours field
                                hours_str = hours_str.replace('hours', '').replace('hrs', '').replace('h', '').strip()
                                
                                # Handle fractions and decimals
                                if '/' in hours_str:  # Handle fractions like "7.5" or "7/2"
                                    if '.' in hours_str:
                                        hours_to_add = float(hours_str)
                                    else:
                                        parts = hours_str.split('/')
                                        if len(parts) == 2:
                                            hours_to_add = float(parts[0]) / float(parts[1])
                                else:
                                    hours_to_add = float(hours_str)
                                
                                # Ensure reasonable bounds (0-168 hours per week)
                                hours_to_add = max(0, min(168, hours_to_add))
                                hours_to_add = int(hours_to_add)  # Convert to integer
                                
                            except (ValueError, ZeroDivisionError):
                                # If all parsing fails, default to 8 hours
                                hours_to_add = 8
                                errors.append(f"Row {index + 2}: Could not parse hours '{hours_raw}', using default 8 hours")
                        
                        # Aggregate hours for the unique key
                        key = (emp_name, project_name, function_name, week_start_date)
                        aggregated_weekly_hours[key] = aggregated_weekly_hours.get(key, 0) + hours_to_add

                    except ValueError as ve:
                        errors.append(f"Row {index + 2}: Data format error ({ve}). Skipped this entry.")
                        skipped_count += 1
                    except Exception as e:
                        errors.append(f"Row {index + 2}: General error during row parsing ({str(e)}). Skipped this entry.")
                        skipped_count += 1
                
                # Now, iterate through the aggregated data and save/update in the database
                for (emp_name, project_name, function_name, week_start_date), hours_to_record in aggregated_weekly_hours.items():
                    try:
                        # 1. Get or Create Employee
                        employee = employee_cache.get(emp_name)
                        if not employee:
                            employee = db.session.query(Employee).filter_by(name=emp_name).first()
                            if not employee:
                                temp_email_base = emp_name.lower().replace(' ', '.')
                                temp_email = f"{temp_email_base}.temp@example.com"
                                count = 0
                                # Ensure temp email is unique
                                while db.session.query(Employee).filter_by(email=temp_email).first():
                                    count += 1
                                    temp_email = f"{temp_email_base}{count}.temp@example.com"

                                employee = Employee(name=emp_name, email=temp_email, role="Imported")
                                db.session.add(employee)
                                db.session.flush() # Get ID before commit
                                errors.append(f"Created new employee '{emp_name}' (temp email: {employee.email}).")
                            employee_cache[emp_name] = employee

                        # 2. Get or Create Project
                        project = project_cache.get(project_name)
                        if not project:
                            project = db.session.query(Project).filter_by(name=project_name).first()
                            if not project:
                                current_year = datetime.now().year
                                project = Project(
                                    name=project_name,
                                    duration_months=12,
                                    start_month="January",
                                    start_year=current_year,
                                    end_month="December",
                                    end_year=current_year + 1
                                )
                                db.session.add(project)
                                db.session.flush() # Get ID before commit
                                errors.append(f"Created new project '{project_name}'.")
                            project_cache[project_name] = project

                        # 3. Get or Create Assignment
                        assignment_key = (employee.id, project.id)
                        assignment = assignment_cache.get(assignment_key)
                        if not assignment:
                            assignment = db.session.query(Assignment).filter_by(employee_id=employee.id, project_id=project.id).first()
                            if not assignment:
                                assignment = Assignment(
                                    employee_id=employee.id,
                                    project_id=project.id,
                                    assigned_hours_per_week=40, # Default assigned hours for auto-created
                                    assigned_start_month="January",
                                    assigned_start_year=datetime.now().year,
                                    assigned_end_month="December",
                                    assigned_end_year=datetime.now().year + 1
                                )
                                db.session.add(assignment)
                                db.session.flush() # Get ID before commit
                                errors.append(f"Created new assignment for '{employee.name}' on '{project.name}'.")
                            assignment_cache[assignment_key] = assignment

                        # 4. Save or Update Weekly Hours for the aggregated total
                        existing_weekly_hours = db.session.query(WeeklyHours).filter_by(
                            assignment_id=assignment.id,
                            week_start_date=week_start_date,
                            function_name=function_name
                        ).first()

                        if existing_weekly_hours:
                            if existing_weekly_hours.hours_worked != hours_to_record:
                                existing_weekly_hours.hours_worked = hours_to_record
                                db.session.commit()
                                imported_count += 1
                        else:
                            new_weekly_hours = WeeklyHours(
                                assignment_id=assignment.id,
                                week_start_date=week_start_date,
                                hours_worked=hours_to_record,
                                function_name=function_name
                            )
                            db.session.add(new_weekly_hours)
                            db.session.commit()
                            imported_count += 1
                    
                    except IntegrityError:
                        db.session.rollback()
                        errors.append(f"DB Integrity conflict for ({emp_name}, {project_name}, {function_name}, {week_start_date}). Record may already exist.")
                        # Don't increment skipped_count - this is expected behavior
                    except Exception as e:
                        db.session.rollback()
                        errors.append(f"Error during DB save for ({emp_name}, {project_name}, {function_name}, {week_start_date}): {str(e)}. Continuing with next record.")
                        # Don't increment skipped_count - keep processing
                
                message = f"✅ Excel import successful! Processed {len(aggregated_weekly_hours)} unique entries. Successfully imported/updated {imported_count} records."
                if errors:
                    message += f" Found {len(errors)} data adjustments and processing notes (details below)."

            else:
                return jsonify({"message": "Invalid data type specified for import"}), 400

            if errors:
                return jsonify({"success": True, "message": message, "errors": errors}), 200
            return jsonify({"success": True, "message": message}), 200

        except Exception as e:
            error_message = f"🔧 Excel processing encountered an issue but we've handled it gracefully: {str(e)}"
            app.logger.error(f"Excel processing failed: {e}")
            
            # Provide helpful feedback even on failure
            try:
                if 'df' in locals() and not df.empty:
                    basic_stats = f"Your Excel file has {len(df)} rows and {len(df.columns)} columns. "
                    basic_stats += f"Columns found: {', '.join(df.columns[:5])}{'...' if len(df.columns) > 5 else ''}"
                    error_message += f" {basic_stats}"
            except:
                pass
            
            return jsonify({
                "message": error_message,
                "success": False,
                "columns_found": list(df.columns) if 'df' in locals() else [],
                "errors": errors if 'errors' in locals() else []
            }), 200  # Return 200 to avoid browser errors
    else:
        return jsonify({"message": "Invalid file type. Please upload an Excel file (.xlsx or .xls)."}), 400


@app.route('/api/employees', methods=['GET', 'POST'])
def api_employees():
    if not (session.get('logged_in') and session['logged_in']):
        return jsonify({"error": "Unauthorized"}), 401

    if request.method == 'GET':
        search_term = request.args.get('q', '').strip()
        employees_query = db.session.query(Employee)

        if search_term:
            employees_query = employees_query.filter(
                (Employee.name.ilike(f'%{search_term}%')) |
                (Employee.email.ilike(f'%{search_term}%')) |
                (Employee.role.ilike(f'%{search_term}%'))
            )
        employees = employees_query.all()
        return jsonify([emp.to_dict() for emp in employees])
    
    elif request.method == 'POST':
        data = request.get_json()
        name = data.get('name')
        email = data.get('email')
        role = data.get('role')

        if not all([name, email, role]):
            return jsonify({"message": "Missing employee data"}), 400

        if not "@" in email or "." not in email:
            return jsonify({"message": "Invalid email format"}), 400

        try:
            new_employee = Employee(name=name, email=email, role=role)
            db.session.add(new_employee)
            db.session.commit()
            return jsonify({"message": "Employee added successfully!", "employee": new_employee.to_dict()}), 201
        except IntegrityError:
            db.session.rollback()
            return jsonify({"message": "Employee with this email already exists."}), 409
        except Exception as e:
            db.session.rollback()
            return jsonify({"message": f"Error adding employee: {str(e)}"}), 500


@app.route('/projects')
def get_projects_page():
    if 'logged_in' in session and session['logged_in']:
        return render_template('projects.html')
    flash('Please log in to access this page.', 'warning')
    return redirect(url_for('login'))

@app.route('/api/projects', methods=['GET', 'POST'])
def api_projects():
    if not (session.get('logged_in') and session['logged_in']):
        return jsonify({"error": "Unauthorized"}), 401

    if request.method == 'GET':
        search_term = request.args.get('q', '').strip()
        projects_query = db.session.query(Project)

        if search_term:
            projects_query = projects_query.filter(
                Project.name.ilike(f'%{search_term}%')
            )
        
        projects = projects_query.all()

        projects_data = []
        for project in projects:
            project_dict = project.to_dict()
            assignments = db.session.query(Assignment).filter_by(project_id=project.id).all()
            project_assignments = []
            for assignment in assignments:
                employee = db.session.query(Employee).get(assignment.employee_id)
                if employee:
                    project_assignments.append({
                        "employee_id": employee.id,
                        "employee_name": employee.name,
                        "position": employee.role,
                        "assigned_hours_per_week": assignment.assigned_hours_per_week,
                        "assigned_start_month": assignment.assigned_start_month,
                        "assigned_start_year": assignment.assigned_start_year,
                        "assigned_end_month": assignment.assigned_end_month,
                        "assigned_end_year": assignment.assigned_end_year
                    })
            project_dict["assignments"] = project_assignments
            projects_data.append(project_dict)
        return jsonify(projects_data)

    elif request.method == 'POST':
        data = request.get_json()
        name = data.get('name')
        start_month_num = data.get('start_month')
        start_year = data.get('start_year')
        end_month_num = data.get('end_month')
        end_year = data.get('end_year')

        if not all([name, start_month_num, start_year, end_month_num, end_year]):
            return jsonify({"message": "Missing project details. Name, start/end month/year are required."}), 400

        month_names_full = [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]
        try:
            start_month_name = month_names_full[int(start_month_num) - 1]
            end_month_name = month_names_full[int(end_month_num) - 1]
        except (ValueError, IndexError):
            return jsonify({"message": "Invalid month number provided."}), 400

        try:
            start_date_obj = date(int(start_year), int(start_month_num), 1)
            last_day_of_end_month = monthrange(int(end_year), int(end_month_num))[1]
            end_date_obj = date(int(end_year), int(end_month_num), last_day_of_end_month)

            duration_months = (end_date_obj.year - start_date_obj.year) * 12 + \
                              (end_date_obj.month - start_date_obj.month) + 1
            if duration_months <= 0:
                return jsonify({"message": "End date must be after start date."}), 400

        except (ValueError, TypeError) as e:
            return jsonify({"message": f"Invalid date components for duration calculation: {e}"}), 400


        try:
            new_project = Project(
                name=name,
                duration_months=duration_months,
                start_month=start_month_name,
                start_year=start_year,
                end_month=end_month_name,
                end_year=end_year
            )
            db.session.add(new_project)
            db.session.commit()
            return jsonify({"message": "Project created successfully!", "project_id": new_project.id}), 201
        except IntegrityError:
            db.session.rollback()
            return jsonify({"message": "Project with this name already exists."}), 409
        except Exception as e:
            db.session.rollback()
            return jsonify({"message": f"Error creating project: {str(e)}"}), 500


@app.route('/assignments')
def get_assignments_page():
    if 'logged_in' in session and session['logged_in']:
        return render_template('assign_employee.html')
    flash('Please log in to access this page.', 'warning')
    return redirect(url_for('login'))

@app.route('/workload_current')
def get_current_workload_page():
    if 'logged_in' in session and session['logged_in']:
        return render_template('workload_current.html')
    flash('Please log in to access this page.', 'warning')
    return redirect(url_for('login'))

@app.route('/export_data')
def export_data_page():
    if 'logged_in' in session and session['logged_in']:
        return render_template('export_data.html')
    flash('Please log in to access this page.', 'warning')
    return redirect(url_for('login'))

@app.route('/monthly_workload')
def get_monthly_workload_page():
    if 'logged_in' in session and session['logged_in']:
        return render_template('workload_monthly.html')
    flash('Please log in to access this page.', 'warning')
    return redirect(url_for('login'))


@app.route('/api/assign_employee', methods=['POST'])
def api_assign_employee():
    if not (session.get('logged_in') and session['logged_in']):
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    employee_id = data.get('employee_id')
    project_id = data.get('project_id')
    assigned_hours_per_week = data.get('assigned_hours_per_week')
    assigned_start_month = data.get('assigned_start_month')
    assigned_start_year = data.get('assigned_start_year')
    assigned_end_month = data.get('assigned_end_month')
    assigned_end_year = data.get('assigned_end_year')

    if not all([employee_id, project_id, assigned_hours_per_week,
                assigned_start_month, assigned_start_year,
                assigned_end_month, assigned_end_year]):
        return jsonify({"message": "Missing assignment data. All fields are required."}), 400

    try:
        month_names = [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]
        start_month_int = int(assigned_start_month)
        end_month_int = int(assigned_end_month)

        if not (1 <= start_month_int <= 12 and 1 <= end_month_int <= 12):
            return jsonify({"message": "Invalid month number provided."}), 400

        start_month_name = month_names[start_month_int - 1]
        end_month_name = month_names[end_month_int - 1]

        new_assignment = Assignment(
            employee_id=employee_id,
            project_id=project_id,
            assigned_hours_per_week=assigned_hours_per_week,
            assigned_start_month=start_month_name,
            assigned_start_year=assigned_start_year,
            assigned_end_month=end_month_name,
            assigned_end_year=assigned_end_year
        )
        db.session.add(new_assignment)
        db.session.commit()
        return jsonify({"message": "Employee assigned to project successfully!", "assignment": new_assignment.to_dict()}), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({"message": "Assignment already exists or another database conflict."}), 409
    except ValueError:
        db.session.rollback()
        return jsonify({"message": "Invalid data format for month or year."}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error assigning employee: {str(e)}"}), 500
    
@app.route('/api/record_actual_hours', methods=['POST'])
def api_record_actual_hours():
    if not (session.get('logged_in') and session['logged_in']):
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    employee_id = data.get('employee_id')
    project_id = data.get('project_id')
    week_start_date_str = data.get('week_start_date')
    hours_worked_raw = data.get('hours_worked')
    function_name = data.get('function_name')

    if not all([employee_id, project_id, week_start_date_str, hours_worked_raw is not None, function_name]):
        return jsonify({"message": "Missing actual hours data. All fields are required."}), 400

    try:
        hours_worked = int(hours_worked_raw)
    except (ValueError, TypeError):
        return jsonify({"message": "Invalid format for hours worked. Hours must be a valid number."}), 400
    
    try:
        assignment = db.session.query(Assignment).filter_by(
            employee_id=employee_id,
            project_id=project_id
        ).first()

        if not assignment:
            current_date = date.today()
            default_start_month = current_date.strftime('%B')
            default_start_year = current_date.year
            
            default_end_date = current_date.replace(year=current_date.year + 1)
            default_end_month = default_end_date.strftime('%B')
            default_end_year = default_end_date.year

            employee = db.session.query(Employee).get(employee_id)
            project = db.session.query(Project).get(project_id)
            if not employee or not project:
                return jsonify({"message": "Employee or Project not found for on-the-fly assignment."}), 404

            new_assignment = Assignment(
                employee_id=employee_id,
                project_id=project.id,
                assigned_hours_per_week=40,
                assigned_start_month=default_start_month,
                assigned_start_year=default_start_year,
                assigned_end_month=default_end_month,
                assigned_end_year=default_end_year
            )
            db.session.add(new_assignment)
            db.session.commit()
            assignment = new_assignment

        week_start_date = datetime.strptime(week_start_date_str, '%Y-%m-%d').date()

        existing_record = db.session.query(WeeklyHours).filter_by(
            assignment_id=assignment.id,
            week_start_date=week_start_date,
            function_name=function_name
        ).first()

        if existing_record:
            existing_record.hours_worked = hours_worked
            db.session.commit()
            return jsonify({"message": "Actual hours updated successfully!", "record": existing_record.hours_worked}), 200
        else:
            new_weekly_hours = WeeklyHours(
                assignment_id=assignment.id,
                week_start_date=week_start_date,
                hours_worked=hours_worked,
                function_name=function_name
            )
            db.session.add(new_weekly_hours)
            db.session.commit()
            return jsonify({"message": "Actual hours recorded successfully!", "record": new_weekly_hours.hours_worked}), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({"message": "Duplicate entry: Actual hours for this employee, project, function, and week already exist."}), 409
    except ValueError:
        return jsonify({"message": "Invalid date format for week_start_date. UseYYYY-MM-DD."}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error recording actual hours: {str(e)}"}), 500

@app.route('/api/export_data', methods=['GET'])
def api_export_data():
    """Simple, bulletproof export endpoint"""
    if not (session.get('logged_in') and session['logged_in']):
        return redirect(url_for('login'))

    try:
        export_type = request.args.get('type', 'weekly_hours')
        
        # Create simple data structure
        data = []
        filename = f'{export_type}_export.xlsx'
        
        if export_type == 'employees':
            employees = Employee.query.all()
            for emp in employees:
                data.append({
                    'Name': emp.name or '',
                    'Email': emp.email or '', 
                    'Role': emp.role or ''
                })
            if not data:
                data = [{'Name': 'No employees found', 'Email': '', 'Role': ''}]
                
        elif export_type == 'projects':
            projects = Project.query.all()
            for proj in projects:
                data.append({
                    'Project Name': proj.name or '',
                    'Duration (Months)': proj.duration_months or 0,
                    'Start Month': proj.start_month or '',
                    'Start Year': proj.start_year or 0,
                    'End Month': proj.end_month or '',
                    'End Year': proj.end_year or 0
                })
            if not data:
                data = [{'Project Name': 'No projects found', 'Duration (Months)': '', 'Start Month': '', 'Start Year': '', 'End Month': '', 'End Year': ''}]
                
        elif export_type == 'weekly_hours':
            weekly_hours = WeeklyHours.query.all()
            for wh in weekly_hours:
                assignment = Assignment.query.get(wh.assignment_id)
                if assignment:
                    employee = Employee.query.get(assignment.employee_id) 
                    project = Project.query.get(assignment.project_id)
                    if employee and project:
                        data.append({
                            'Emp Name': employee.name or '',
                            'Project Name': project.name or '',
                            'Function': wh.function_name or 'General',
                            'Week Days': str(wh.week_start_date) if wh.week_start_date else '',
                            'Hours': wh.hours_worked or 0
                        })
            if not data:
                data = [{'Emp Name': 'No weekly hours found', 'Project Name': '', 'Function': '', 'Week Days': '', 'Hours': ''}]
        
        # Simple Excel creation
        df = pd.DataFrame(data)
        output = io.BytesIO()
        df.to_excel(output, index=False, engine='openpyxl')
        output.seek(0)
        
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        response.headers['Content-Disposition'] = f'attachment; filename={filename}'
        response.headers['Cache-Control'] = 'no-cache'
        
        return response
        
    except Exception as e:
        # Return plain text error instead of JSON to avoid parsing issues
        error_response = make_response(f"Export Error: {str(e)}")
        error_response.headers['Content-Type'] = 'text/plain'
        return error_response

# Delete endpoints
@app.route('/api/employees/<int:employee_id>', methods=['DELETE'])
def delete_employee(employee_id):
    """Delete a specific employee"""
    if not (session.get('logged_in') and session['logged_in']):
        return jsonify({"error": "Unauthorized"}), 401
    
    try:
        employee = Employee.query.get(employee_id)
        if not employee:
            return jsonify({"message": "Employee not found"}), 404
        
        # Check for existing assignments
        assignments = Assignment.query.filter_by(employee_id=employee_id).all()
        if assignments:
            return jsonify({"message": f"Cannot delete employee. They have {len(assignments)} active assignment(s). Delete assignments first."}), 400
        
        db.session.delete(employee)
        db.session.commit()
        return jsonify({"message": f"Employee '{employee.name}' deleted successfully"}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error deleting employee: {str(e)}"}), 500

@app.route('/api/projects/<int:project_id>', methods=['DELETE'])
def delete_project(project_id):
    """Delete a specific project"""
    if not (session.get('logged_in') and session['logged_in']):
        return jsonify({"error": "Unauthorized"}), 401
    
    try:
        project = Project.query.get(project_id)
        if not project:
            return jsonify({"message": "Project not found"}), 404
        
        # Check for existing assignments
        assignments = Assignment.query.filter_by(project_id=project_id).all()
        if assignments:
            return jsonify({"message": f"Cannot delete project. It has {len(assignments)} active assignment(s). Delete assignments first."}), 400
        
        db.session.delete(project)
        db.session.commit()
        return jsonify({"message": f"Project '{project.name}' deleted successfully"}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error deleting project: {str(e)}"}), 500

@app.route('/api/assignments/<int:assignment_id>', methods=['DELETE'])
def delete_assignment(assignment_id):
    """Delete a specific assignment"""
    if not (session.get('logged_in') and session['logged_in']):
        return jsonify({"error": "Unauthorized"}), 401
    
    try:
        assignment = Assignment.query.get(assignment_id)
        if not assignment:
            return jsonify({"message": "Assignment not found"}), 404
        
        # Check for existing weekly hours
        weekly_hours = WeeklyHours.query.filter_by(assignment_id=assignment_id).all()
        if weekly_hours:
            return jsonify({"message": f"Cannot delete assignment. It has {len(weekly_hours)} weekly hour record(s). Delete weekly hours first."}), 400
        
        employee_name = assignment.employee.name
        project_name = assignment.project.name
        
        db.session.delete(assignment)
        db.session.commit()
        return jsonify({"message": f"Assignment for '{employee_name}' on '{project_name}' deleted successfully"}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error deleting assignment: {str(e)}"}), 500

@app.route('/api/weekly_hours/<int:weekly_hours_id>', methods=['DELETE'])
def delete_weekly_hours(weekly_hours_id):
    """Delete a specific weekly hours record"""
    if not (session.get('logged_in') and session['logged_in']):
        return jsonify({"error": "Unauthorized"}), 401
    
    try:
        weekly_hours = WeeklyHours.query.get(weekly_hours_id)
        if not weekly_hours:
            return jsonify({"message": "Weekly hours record not found"}), 404
        
        assignment = weekly_hours.assignment
        employee_name = assignment.employee.name if assignment and assignment.employee else "Unknown"
        project_name = assignment.project.name if assignment and assignment.project else "Unknown"
        
        db.session.delete(weekly_hours)
        db.session.commit()
        return jsonify({"message": f"Weekly hours record for '{employee_name}' on '{project_name}' deleted successfully"}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error deleting weekly hours: {str(e)}"}), 500

@app.route('/api/export_workload_excel', methods=['GET'])
def api_export_workload_excel():
    if not (session.get('logged_in') and session['logged_in']):
        return jsonify({"error": "Unauthorized"}), 401

    try:
        weekly_hours_records = db.session.query(WeeklyHours).join(Assignment).join(Employee).join(Project).all()

        if not weekly_hours_records:
            return jsonify({"message": "No data available to export."}), 404

        grouped_by_employee = {}
        all_week_start_dates = set()
        normal_hours_per_week = 40

        for entry in weekly_hours_records:
            employee_name = entry.assignment.employee.name
            week_start_date = entry.week_start_date.isoformat()
            hours_worked = entry.hours_worked
            
            all_week_start_dates.add(week_start_date)

            if employee_name not in grouped_by_employee:
                grouped_by_employee[employee_name] = {
                    'weekly_totals': {},
                    'weekly_total_status': {},
                }
            
            emp_data = grouped_by_employee[employee_name]
            current_total_hours = emp_data['weekly_totals'].get(week_start_date, 0) + hours_worked
            emp_data['weekly_totals'][week_start_date] = current_total_hours
            emp_data['weekly_total_status'][week_start_date] = 'Overloaded' if current_total_hours > normal_hours_per_week else ('Free' if current_total_hours < normal_hours_per_week else 'Normal')


        sorted_week_start_dates = sorted(list(all_week_start_dates))

        excel_data = []
        s_no = 1

        def get_iso_week_number(dt):
            return dt.isocalendar()[1]

        dynamic_week_columns_headers = []
        for week_date_str in sorted_week_start_dates:
            start_dt = datetime.strptime(week_date_str, '%Y-%m-%d').date()
            end_dt = start_dt + timedelta(days=6)
            week_num = get_iso_week_number(start_dt)
            base_header = f"WK{week_num} ({start_dt.strftime('%b %d')} - {end_dt.strftime('%b %d')})"
            dynamic_week_columns_headers.append(f"{base_header} - Working Hours")
            dynamic_week_columns_headers.append(f"{base_header} - Status")


        fixed_report_columns = ['S.No.', 'Employee Name']
        final_excel_columns_order = fixed_report_columns + dynamic_week_columns_headers

        for employee_name in sorted(grouped_by_employee.keys()):
            emp_data = grouped_by_employee[employee_name]

            summary_row = {
                'S.No.': s_no,
                'Employee Name': employee_name,
            }
            for week_date in sorted_week_start_dates:
                total_hours = emp_data['weekly_totals'].get(week_date, '')
                total_status = emp_data['weekly_total_status'].get(week_date, '')
                
                start_dt_for_header = datetime.strptime(week_date, '%Y-%m-%d').date()
                week_num_for_header = get_iso_week_number(start_dt_for_header)
                end_dt_for_header = start_dt_for_header + timedelta(days=6)
                base_header = f"WK{week_num_for_header} ({start_dt_for_header.strftime('%b %d')} - {end_dt_for_header.strftime('%b %d')})"
                
                summary_row[f"{base_header} - Working Hours"] = total_hours
                summary_row[f"{base_header} - Status"] = total_status

            excel_data.append(summary_row)
            
            s_no += 1
            
        df_report = pd.DataFrame(excel_data, columns=final_excel_columns_order)
        df_report = df_report.fillna('')


        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df_report.to_excel(writer, sheet_name='Actual Hours Report', index=False) 

            workbook = writer.book
            worksheet = writer.sheets['Actual Hours Report']

            header_format = workbook.add_format({'bold': True, 'font_color': 'white', 'bg_color': '#4F81BD', 'align': 'center', 'valign': 'vcenter'})
            sub_header_format = workbook.add_format({'bold': True, 'align': 'center'})

            bold_text_format = workbook.add_format({'bold': True})

            red_fill_bold = workbook.add_format({'bold': True, 'bg_color': '#FFC7CE', 'font_color': '#9C0006'})
            green_fill_bold = workbook.add_format({'bold': True, 'bg_color': '#C6EFCE', 'font_color': '#006100'})
            orange_fill_bold = workbook.add_format({'bold': True, 'bg_color': '#FFEB9C', 'font_color': '#9C6500'})
            grey_fill_bold = workbook.add_format({'bold': True, 'bg_color': '#F2F2F2', 'font_color': '#666666'})

            
            current_col = 0
            for col_name in fixed_report_columns:
                worksheet.write(0, current_col, col_name, header_format)
                current_col += 1
            
            for week_date_str in sorted_week_start_dates:
                start_dt = datetime.strptime(week_date_str, '%Y-%m-%d').date()
                end_dt = start_dt + timedelta(days=6)
                week_num = get_iso_week_number(start_dt)
                base_header = f"WK{week_num} ({start_dt.strftime('%b %d')} - {end_dt.strftime('%b %d')})"
                
                merge_start_col = current_col
                merge_end_col = current_col + 1
                worksheet.merge_range(0, merge_start_col, 0, merge_end_col, base_header, header_format)
            
                worksheet.write(1, current_col, "Working Hours", sub_header_format)
                worksheet.write(1, current_col + 1, "Status", sub_header_format)
                current_col += 2


            for r_idx, row_data_dict in enumerate(excel_data):
                excel_row_idx = r_idx + 2

                current_col_excel = 0
                
                worksheet.write(excel_row_idx, current_col_excel, row_data_dict['S.No.'], bold_text_format)
                current_col_excel += 1
                worksheet.write(excel_row_idx, current_col_excel, row_data_dict['Employee Name'], bold_text_format)
                current_col_excel += 1
                
                for week_date_str in sorted_week_start_dates:
                    start_dt_for_header = datetime.strptime(week_date_str, '%Y-%m-%d').date()
                    week_num_for_header = get_iso_week_number(start_dt_for_header)
                    end_dt_for_header = start_dt_for_header + timedelta(days=6)
                    base_header = f"WK{week_num_for_header} ({start_dt_for_header.strftime('%b %d')} - {end_dt_for_header.strftime('%b %d')})"
                    
                    hours_col_name = f"{base_header} - Working Hours"
                    status_col_name = f"{base_header} - Status"

                    hours_value = df_report.iloc[r_idx, df_report.columns.get_loc(hours_col_name)]
                    status_value = df_report.iloc[r_idx, df_report.columns.get_loc(status_col_name)]

                    hours_cell_format_to_apply = bold_text_format
                    
                    numeric_hours_value = None
                    try:
                        float_hours_value = float(hours_value)
                        if float_hours_value == int(float_hours_value):
                            numeric_hours_value = int(float_hours_value)
                        else:
                            numeric_hours_value = float_hours_value
                    except (ValueError, TypeError):
                        pass

                    if numeric_hours_value is not None:
                        if status_value == 'Overloaded':
                            hours_cell_format_to_apply = red_fill_bold
                        elif status_value == 'Free' and numeric_hours_value > 0:
                            hours_cell_format_to_apply = orange_fill_bold
                        elif status_value == 'Normal' and numeric_hours_value == normal_hours_per_week:
                            hours_cell_format_to_apply = green_fill_bold
                        elif numeric_hours_value == 0:
                            hours_cell_format_to_apply = grey_fill_bold
                    elif hours_value == '':
                        hours_cell_format_to_apply = grey_fill_bold
                    
                    worksheet.write(excel_row_idx, current_col_excel, hours_value, hours_cell_format_to_apply)
                    current_col_excel += 1

                    worksheet.write(excel_row_idx, current_col_excel, status_value, bold_text_format)
                    current_col_excel += 1


            for i, col_name in enumerate(final_excel_columns_order):
                header1_len = 0
                header2_len = 0

                if i < len(fixed_report_columns):
                    header1_len = len(fixed_report_columns[i])
                else:
                    current_dynamic_idx = (i - len(fixed_report_columns)) // 2
                    if current_dynamic_idx < len(sorted_week_start_dates):
                        week_date_str = sorted_week_start_dates[current_dynamic_idx]
                        start_dt = datetime.strptime(week_date_str, '%Y-%m-%d').date()
                        end_dt = start_dt + timedelta(days=6)
                        week_num = get_iso_week_number(start_dt)
                        header1_text = f"WK{week_num} ({start_dt.strftime('%b %d')} - {end_dt.strftime('%b %d')})"
                        header1_len = len(header1_text)

                    sub_header_position = (i - len(fixed_report_columns)) % 2
                    if sub_header_position == 0:
                        header2_len = len("Working Hours")
                    elif sub_header_position == 1:
                        header2_len = len("Status")
                
                max_content_len = 0
                max_content_len = df_report[col_name].astype(str).map(len).max() if not df_report.empty else 0


                max_len = max(header1_len, header2_len, max_content_len)
                worksheet.set_column(i, i, max_len + 2)

            worksheet.freeze_panes(2, len(fixed_report_columns))


        output.seek(0)
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            download_name='Detailed_Actual_Hours_Report.xlsx',
            as_attachment=True
        )
    except Exception as e:
        app.logger.error(f"Error exporting processed imported data: {e}")
        return jsonify({"error": f"Failed to generate export file: {str(e)}"}), 500


@app.route('/api/employee_project_assignments', methods=['GET'])
def api_employee_project_assignments():
    if not (session.get('logged_in') and session['logged_in']):
        return jsonify({"error": "Unauthorized"}), 401

    search_term = request.args.get('q', '').strip()
    assignments_data = {}

    assignments_query = db.session.query(Assignment).all()

    for assignment in assignments_query:
        employee = db.session.query(Employee).get(assignment.employee_id)
        project = db.session.query(Project).get(assignment.project_id)

        if employee and project:
            employee_name = employee.name
            project_name = project.name
            
            if search_term and \
               not (search_term.lower() in employee_name.lower() or \
                    search_term.lower() in project_name.lower() or \
                    search_term.lower() in employee.role.lower()):
                continue

            if employee.id not in assignments_data:
                assignments_data[employee.id] = {
                    'employee': employee.to_dict(),
                    'projects': []
                }
            
            assignments_data[employee.id]['projects'].append({
                'assignment_id': assignment.id,
                'project_id': project.id,
                'project_name': project.name,
                'hours_per_week': assignment.assigned_hours_per_week,
                'assigned_start': f"{assignment.assigned_start_month} {assignment.assigned_start_year}",
                'assigned_end': f"{assignment.assigned_end_month} {assignment.assigned_end_year}"
            })
    
    return jsonify(list(assignments_data.values()))


@app.route('/api/weekly_hours', methods=['GET'])
def api_weekly_hours():
    if not (session.get('logged_in') and session['logged_in']):
        return jsonify({"error": "Unauthorized"}), 401

    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    search_term = request.args.get('q', '').strip()

    weekly_hours_query = db.session.query(WeeklyHours).join(Assignment).join(Employee).join(Project)

    if start_date_str and end_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            weekly_hours_query = weekly_hours_query.filter(
                (WeeklyHours.week_start_date >= start_date) & (WeeklyHours.week_start_date <= end_date)
            )
        except ValueError:
            return jsonify({"message": "Invalid date format for start_date or end_date. UseYYYY-MM-DD."}), 400

    if search_term:
        weekly_hours_query = weekly_hours_query.filter(
            (Employee.name.ilike(f'%{search_term}%')) |
            (Project.name.ilike(f'%{search_term}%')) |
            (WeeklyHours.function_name.ilike(f'%{search_term}%'))
        )
    
    weekly_hours_records = weekly_hours_query.all()
    
    weekly_hours_data = []
    for wh in weekly_hours_records:
        employee = wh.assignment.employee if wh.assignment else None
        project = wh.assignment.project if wh.assignment else None

        if employee and project:
            weekly_hours_data.append({
                'id': wh.id,
                'assignment_id': wh.assignment_id,
                'employee_id': employee.id,
                'employee_name': employee.name,
                'project_id': project.id,
                'project_name': project.name,
                'week_start_date': wh.week_start_date.isoformat(),
                'hours_worked': wh.hours_worked,
                'function_name': wh.function_name,
                'percentage': wh.percentage,
                'status': wh.status
            })
    
    return jsonify(weekly_hours_data)


@app.route('/api/monthly_workload', methods=['GET'])
def api_monthly_workload():
    if not (session.get('logged_in') and session['logged_in']):
        return jsonify({"error": "Unauthorized"}), 401

    start_month_num = int(request.args.get('start_month', datetime.now().month))
    start_year = int(request.args.get('start_year', datetime.now().year))
    num_months = int(request.args.get('num_months', 6))
    search_term = request.args.get('q', '').strip()

    normal_weekly_hours = 40
    hours_per_month_approx = normal_weekly_hours * 4

    employee_monthly_load = []
    
    all_employees = db.session.query(Employee).all()
    all_projects = db.session.query(Project).all()
    all_assignments = db.session.query(Assignment).all()
    all_weekly_hours = db.session.query(WeeklyHours).all()

    projects_by_id = {p.id: p for p in all_projects}
    employees_by_id = {e.id: e for e in all_employees}
    assignments_by_id = {a.id: a for a in all_assignments}

    for employee in all_employees:
        employee_data = {
            'employee': employee.to_dict(),
            'monthly_loads': []
        }
        
        if search_term and not (search_term.lower() in employee.name.lower() or \
                                search_term.lower() in employee.role.lower() or \
                                search_term.lower() in employee.email.lower()):
            continue

        current_month_date = datetime(start_year, start_month_num, 1)

        for i in range(num_months):
            month_start = datetime(current_month_date.year, current_month_date.month, 1).date()
            month_end = datetime(current_month_date.year, current_month_date.month, monthrange(current_month_date.year, current_month_date.month)[1]).date()

            total_assigned_hours_for_month = 0
            total_actual_hours_for_month = 0

            relevant_assignments = [
                a for a in all_assignments
                if a.employee_id == employee.id and
                   (datetime(a.assigned_start_year, datetime.strptime(a.assigned_start_month, '%B').month, 1).date() <= month_end) and
                   (datetime(a.assigned_end_year, datetime.strptime(a.assigned_end_month, '%B').month, monthrange(a.assigned_end_year, datetime.strptime(a.assigned_end_month, '%B').month)[1]).date() >= month_start)
            ]
            
            for assignment in relevant_assignments:
                total_assigned_hours_for_month += assignment.assigned_hours_per_week * 4

                actual_hours_in_month = [
                    wh.hours_worked for wh in all_weekly_hours
                    if wh.assignment_id == assignment.id and
                       wh.week_start_date >= month_start and
                       wh.week_start_date <= month_end
                ]
                total_actual_hours_for_month += sum(actual_hours_in_month)

            load = total_actual_hours_for_month if total_actual_hours_for_month > 0 else total_assigned_hours_for_month
            
            load_percentage = (load / hours_per_month_approx) * 100 if hours_per_month_approx > 0 else 0

            employee_data['monthly_loads'].append({
                'month_year': current_month_date.strftime('%b %Y'),
                'load': load,
                'load_percentage': load_percentage
            })

            if current_month_date.month == 12:
                current_month_date = datetime(current_month_date.year + 1, 1, 1)
            else:
                current_month_date = datetime(current_month_date.year, current_month_date.month + 1, 1)
        
        employee_monthly_load.append(employee_data)

    months_labels = []
    temp_date = datetime(start_year, start_month_num, 1)
    for _ in range(num_months):
        months_labels.append(temp_date.strftime('%b %Y'))
        if temp_date.month == 12:
            temp_date = datetime(temp_date.year + 1, 1, 1)
        else:
            temp_date = datetime(temp_date.year, temp_date.month + 1, 1)

    return jsonify({
        'employee_monthly_load': employee_monthly_load,
        'months': months_labels,
        'normal_hours': normal_weekly_hours
    })


# --- Run the application ---
if __name__ == '__main__':
    app.run(debug=False)
