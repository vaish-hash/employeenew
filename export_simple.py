import pandas as pd
from io import BytesIO
from flask import make_response
from app import Employee, Project, WeeklyHours, Assignment

def create_simple_export(export_type):
    """Create a simple Excel export without complex dependencies"""
    try:
        data = []
        
        if export_type == 'employees':
            employees = Employee.query.all()
            data = [{'Name': emp.name, 'Email': emp.email, 'Role': emp.role} for emp in employees]
            if not data:
                data = [{'Name': 'No employees found', 'Email': '', 'Role': ''}]
                
        elif export_type == 'projects':
            projects = Project.query.all()
            data = [{
                'Project Name': proj.name,
                'Duration (Months)': proj.duration_months,
                'Start Month': proj.start_month,
                'Start Year': proj.start_year,
                'End Month': proj.end_month,
                'End Year': proj.end_year
            } for proj in projects]
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
                            'Emp Name': employee.name,
                            'Project Name': project.name,
                            'Function': wh.function_name or 'General',
                            'Week Days': str(wh.week_start_date) if wh.week_start_date else 'N/A',
                            'Hours': wh.hours_worked
                        })
            if not data:
                data = [{'Emp Name': 'No weekly hours found', 'Project Name': '', 'Function': '', 'Week Days': '', 'Hours': ''}]
        
        # Create simple CSV-like Excel
        df = pd.DataFrame(data)
        output = BytesIO()
        
        # Use simple Excel writer
        df.to_excel(output, index=False, engine='openpyxl')
        output.seek(0)
        
        return output.getvalue()
        
    except Exception as e:
        # Fallback to CSV if Excel fails
        df = pd.DataFrame(data)
        output = BytesIO()
        csv_data = df.to_csv(index=False)
        output.write(csv_data.encode('utf-8'))
        output.seek(0)
        return output.getvalue()