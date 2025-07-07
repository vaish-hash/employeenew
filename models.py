from app import db
from datetime import datetime
from sqlalchemy import String, Integer, Float, DateTime, Text

class Employee(db.Model):
    """Employee model for storing employee information"""
    __tablename__ = 'employees'
    
    id = db.Column(Integer, primary_key=True)
    first_name = db.Column(String(50), nullable=False)
    last_name = db.Column(String(50), nullable=False)
    email = db.Column(String(120), unique=True, nullable=False)
    phone = db.Column(String(20), nullable=True)
    department = db.Column(String(100), nullable=False)
    position = db.Column(String(100), nullable=False)
    salary = db.Column(Float, nullable=False)
    hire_date = db.Column(DateTime, nullable=False, default=datetime.utcnow)
    address = db.Column(Text, nullable=True)
    notes = db.Column(Text, nullable=True)
    created_at = db.Column(DateTime, default=datetime.utcnow)
    updated_at = db.Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Employee {self.first_name} {self.last_name}>'
    
    def to_dict(self):
        """Convert employee object to dictionary"""
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'phone': self.phone,
            'department': self.department,
            'position': self.position,
            'salary': self.salary,
            'hire_date': self.hire_date.strftime('%Y-%m-%d') if self.hire_date else None,
            'address': self.address,
            'notes': self.notes,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }
    
    @property
    def full_name(self):
        """Return full name of employee"""
        return f"{self.first_name} {self.last_name}"
