from flask import render_template, request, redirect, url_for, flash, jsonify
from app import app, db
from models import Employee
from datetime import datetime
import logging

@app.route('/')
def index():
    """Display all employees"""
    try:
        employees = Employee.query.all()
        return render_template('index.html', employees=employees)
    except Exception as e:
        logging.error(f"Error fetching employees: {e}")
        flash('Error loading employees. Please try again.', 'error')
        return render_template('index.html', employees=[])

@app.route('/add', methods=['GET', 'POST'])
def add_employee():
    """Add a new employee"""
    if request.method == 'POST':
        try:
            # Get form data
            first_name = request.form.get('first_name', '').strip()
            last_name = request.form.get('last_name', '').strip()
            email = request.form.get('email', '').strip()
            phone = request.form.get('phone', '').strip()
            department = request.form.get('department', '').strip()
            position = request.form.get('position', '').strip()
            salary = request.form.get('salary', '').strip()
            hire_date = request.form.get('hire_date', '').strip()
            address = request.form.get('address', '').strip()
            notes = request.form.get('notes', '').strip()
            
            # Validate required fields
            if not all([first_name, last_name, email, department, position, salary]):
                flash('Please fill in all required fields.', 'error')
                return render_template('add_employee.html')
            
            # Check if email already exists
            existing_employee = Employee.query.filter_by(email=email).first()
            if existing_employee:
                flash('An employee with this email already exists.', 'error')
                return render_template('add_employee.html')
            
            # Validate salary
            try:
                salary = float(salary)
                if salary < 0:
                    flash('Salary must be a positive number.', 'error')
                    return render_template('add_employee.html')
            except ValueError:
                flash('Please enter a valid salary.', 'error')
                return render_template('add_employee.html')
            
            # Parse hire date
            hire_date_obj = datetime.utcnow()
            if hire_date:
                try:
                    hire_date_obj = datetime.strptime(hire_date, '%Y-%m-%d')
                except ValueError:
                    flash('Please enter a valid hire date.', 'error')
                    return render_template('add_employee.html')
            
            # Create new employee
            employee = Employee(
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone if phone else None,
                department=department,
                position=position,
                salary=salary,
                hire_date=hire_date_obj,
                address=address if address else None,
                notes=notes if notes else None
            )
            
            db.session.add(employee)
            db.session.commit()
            
            flash(f'Employee {employee.full_name} added successfully!', 'success')
            return redirect(url_for('index'))
            
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error adding employee: {e}")
            flash('Error adding employee. Please try again.', 'error')
            return render_template('add_employee.html')
    
    return render_template('add_employee.html')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_employee(id):
    """Edit an existing employee"""
    employee = Employee.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            # Get form data
            first_name = request.form.get('first_name', '').strip()
            last_name = request.form.get('last_name', '').strip()
            email = request.form.get('email', '').strip()
            phone = request.form.get('phone', '').strip()
            department = request.form.get('department', '').strip()
            position = request.form.get('position', '').strip()
            salary = request.form.get('salary', '').strip()
            hire_date = request.form.get('hire_date', '').strip()
            address = request.form.get('address', '').strip()
            notes = request.form.get('notes', '').strip()
            
            # Validate required fields
            if not all([first_name, last_name, email, department, position, salary]):
                flash('Please fill in all required fields.', 'error')
                return render_template('edit_employee.html', employee=employee)
            
            # Check if email already exists (excluding current employee)
            existing_employee = Employee.query.filter(
                Employee.email == email,
                Employee.id != id
            ).first()
            if existing_employee:
                flash('An employee with this email already exists.', 'error')
                return render_template('edit_employee.html', employee=employee)
            
            # Validate salary
            try:
                salary = float(salary)
                if salary < 0:
                    flash('Salary must be a positive number.', 'error')
                    return render_template('edit_employee.html', employee=employee)
            except ValueError:
                flash('Please enter a valid salary.', 'error')
                return render_template('edit_employee.html', employee=employee)
            
            # Parse hire date
            hire_date_obj = employee.hire_date
            if hire_date:
                try:
                    hire_date_obj = datetime.strptime(hire_date, '%Y-%m-%d')
                except ValueError:
                    flash('Please enter a valid hire date.', 'error')
                    return render_template('edit_employee.html', employee=employee)
            
            # Update employee
            employee.first_name = first_name
            employee.last_name = last_name
            employee.email = email
            employee.phone = phone if phone else None
            employee.department = department
            employee.position = position
            employee.salary = salary
            employee.hire_date = hire_date_obj
            employee.address = address if address else None
            employee.notes = notes if notes else None
            employee.updated_at = datetime.utcnow()
            
            db.session.commit()
            
            flash(f'Employee {employee.full_name} updated successfully!', 'success')
            return redirect(url_for('index'))
            
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error updating employee: {e}")
            flash('Error updating employee. Please try again.', 'error')
            return render_template('edit_employee.html', employee=employee)
    
    return render_template('edit_employee.html', employee=employee)

@app.route('/view/<int:id>')
def view_employee(id):
    """View employee details"""
    employee = Employee.query.get_or_404(id)
    return render_template('view_employee.html', employee=employee)

@app.route('/delete/<int:id>')
def delete_employee(id):
    """Delete an employee"""
    try:
        employee = Employee.query.get_or_404(id)
        employee_name = employee.full_name
        
        db.session.delete(employee)
        db.session.commit()
        
        flash(f'Employee {employee_name} deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error deleting employee: {e}")
        flash('Error deleting employee. Please try again.', 'error')
    
    return redirect(url_for('index'))

@app.route('/search')
def search_employees():
    """Search employees by name, email, or department"""
    query = request.args.get('q', '').strip()
    
    if not query:
        return redirect(url_for('index'))
    
    try:
        employees = Employee.query.filter(
            db.or_(
                Employee.first_name.ilike(f'%{query}%'),
                Employee.last_name.ilike(f'%{query}%'),
                Employee.email.ilike(f'%{query}%'),
                Employee.department.ilike(f'%{query}%'),
                Employee.position.ilike(f'%{query}%')
            )
        ).all()
        
        return render_template('index.html', employees=employees, search_query=query)
    except Exception as e:
        logging.error(f"Error searching employees: {e}")
        flash('Error searching employees. Please try again.', 'error')
        return redirect(url_for('index'))

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return render_template('base.html', error_message='Page not found'), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    db.session.rollback()
    return render_template('base.html', error_message='Internal server error'), 500
