import os
from sqlalchemy.exc import IntegrityError
from flask import current_app
from datetime import date, timedelta # NEW: Import timedelta for easier date math

def seed_all_data():
    from app import db, Employee, Project, Assignment, WeeklyHours # Ensure all models are imported

    print("Checking for existing data...")
    if Employee.query.first() or Project.query.first() or Assignment.query.first() or WeeklyHours.query.first():
        print("Database already contains data. Skipping seeding. If you want to re-seed, run 'flask init-db' first to clear.")
        return

    print("Inserting Projects...")
    project_data = [
        ("ER - TCAS", 6, "May", "October", 2024, 2024),
        ("CR Nagpur", 17, "January", "May", 2023, 2024),
        ("Railtel 5", 10, "March", "December", 2024, 2024),
        ("TATA Hot Metal", 14, "February", "March", 2024, 2025),
        ("TATA 8MTPA", 14, "April", "May", 2024, 2025),
        ("NCR Naini", 17, "June", "October", 2023, 2024),
        ("DFCC", 17, "July", "November", 2023, 2024),
        ("ECR-Dhanbad and Samastipur", 17, "August", "December", 2023, 2024),
        ("NWR Jaipur - Present L1", 17, "September", "January", 2023, 2025),
        ("WCR Bhopal - Present L1", 17, "October", "February", 2023, 2025),
        ("NCR-SandT-EPC-ABSGMC-VGLJ / Consortium-Param - Expected", 17, "November", "March", 2023, 2025),
        ("NCR-SnT-EPCKavach-MTJ-AGC/ Consortium-GG Tronics - Expected", 17, "December", "April", 2023, 2025),
        ("PowerMac Project1 –Expected", 17, "January", "May", 2024, 2025),
        ("PowerMac Project2 –Expected", 17, "February", "June", 2024, 2025),
        ("Commercial Lead", 17, "March", "July", 2024, 2025),
        ("SR - EPC_ABS23_JTJ-ED / Param", 17, "April", "August", 2024, 2025),
        ("SR - ABS_ERS-VTK_EPC / SS Rail", 17, "May", "September", 2024, 2025),
        ("NCR-SandT-EPC-ABSDHOGWL02/ Consortium-Param", 17, "June", "October", 2024, 2025),
        ("NCR - SIG-WS-CONTRACT-571/ Direct", 11, "July", "May", 2024, 2025),
        ("CR Project Closure", 8, "August", "March", 2024, 2025),
        ("Panoli", 8, "September", "April", 2024, 2025),
        ("SR 235DP", 8, "October", "May", 2024, 2025),
        ("SR KBT-AJJ Project", 8, "November", "June", 2024, 2025),
        ("WR Ratlam", 17, "December", "July", 2024, 2025),
        ("WR 537DP", 17, "January", "August", 2024, 2025),
        ("Pune Daund & Miraj", 17, "February", "September", 2024, 2025),
        ("Product Management-EoTT", 17, "March", "October", 2024, 2025),
        ("Product Management", 17, "April", "November", 2024, 2025),
        ("Product Management-AFTC", 17, "May", "December", 2024, 2025),
        ("Product Management-MSDAC", 17, "June", "January", 2024, 2025),
        ("Product Management-Point Machine", 17, "July", "February", 2024, 2025),
        ("Bid/ Sales Support", 17, "August", "March", 2024, 2025),
        ("Product Delivery Support", 17, "September", "April", 2024, 2025),
        ("RRI Altration and New Work", 17, "October", "May", 2024, 2025),
        ("MSDAC Region North,East,Central,East,West,South,West", 17, "November", "June", 2024, 2025),
        ("MSDAC Region North", 17, "December", "July", 2024, 2025),
        ("MSDAC Region Central", 17, "January", "August", 2024, 2025),
        ("MSDAC Support West", 17, "February", "September", 2024, 2025),
        ("MSDAC Support South", 17, "March", "October", 2024, 2025),
        ("MSDAC Support East", 17, "April", "November", 2024, 2025),
        ("PR Projects CPM", 17, "May", "December", 2024, 2025),
        ("SRAPL", 17, "June", "January", 2024, 2025),
        ("NR Ambala", 17, "July", "February", 2024, 2025)
    ]

    projects_dict = {}
    for name, duration, start_m, end_m, start_y, end_y in project_data:
        try:
            project = Project(
                name=name,
                duration_months=duration,
                start_month=start_m,
                end_month=end_m,
                start_year=start_y,
                end_year=end_y
            )
            db.session.add(project)
            db.session.flush() # Flush to get ID, but don't commit yet
            projects_dict[name] = project # Store project object for easy lookup
            print(f"  Added Project: {project.name}")
        except IntegrityError:
            db.session.rollback()
            existing_project = Project.query.filter_by(name=name).first()
            if existing_project:
                projects_dict[name] = existing_project # Store existing project
            print(f"  Project '{name}' already exists, skipping.")
        except Exception as e:
            db.session.rollback()
            print(f"  Error adding project {name}: {e}")
    db.session.commit()


    print("Inserting Employees...")
    consolidated_employee_data = {
        "sufiyashaikh.siemens@gmail.com": {"name": "Sufiya Shaikh", "role": "Project Manager", "projects": ["CR Nagpur", "TATA Hot Metal", "TATA 8MTPA"]},
        "vivekkapil.siemens@gmail.com": {"name": "Vivek Kapil", "role": "System Engineer", "projects": ["CR Nagpur", "DFCC", "WCR Bhopal - Present L1"]},
        "aritramanna.siemens@gmail.com": {"name": "Aritra Manna", "role": "Project Engineer", "projects": ["CR Nagpur", "Panoli", "Pune Daund & Miraj"]},
        "mandardhuru.siemens@gmail.com": {"name": "Mandar Dhuru", "role": "Commercial Project Manager", "projects": ["CR Nagpur", "NWR Jaipur - Present L1", "PowerMac Project1 –Expected", "WR Ratlam"]},
        "sriramabburi.siemens@gmail.com": {"name": "Sriram Abburi", "role": "Project Manager", "projects": ["ER - TCAS", "NCR Naini"]},
        "amanrawat.siemens@gmail.com": {"name": "Aman Rawat", "role": "Scheduler", "projects": ["ER - TCAS", "TATA Hot Metal", "TATA 8MTPA", "NCR Naini", "WCR Bhopal - Present L1", "NCR-SandT-EPC-ABSGMC-VGLJ / Consortium-Param - Expected", "NCR-SnT-EPCKavach-MTJ-AGC/ Consortium-GG Tronics - Expected", "PowerMac Project2 –Expected", "SR - EPC_ABS23_JTJ-ED / Param", "SR - ABS_ERS-VTK_EPC / SS Rail", "NCR-SandT-EPC-ABSDHOGWL02/ Consortium-Param", "NCR - SIG-WS-CONTRACT-571/ Direct", "WR Ratlam", "WR 537DP", "Pune Daund & Miraj"]},
        "suruchipatel.siemens@gmail.com": {"name": "Suruchi Patel", "role": "Commercial Project Manager", "projects": ["ER - TCAS", "DFCC", "WCR Bhopal - Present L1"]},
        "qmip.siemens@gmail.com": {"name": "QMiP-1", "role": "QMiP", "projects": ["ER - TCAS", "TATA Hot Metal", "TATA 8MTPA", "NCR Naini", "NWR Jaipur - Present L1", "WCR Bhopal - Present L1", "NCR-SandT-EPC-ABSGMC-VGLJ / Consortium-Param - Expected", "NCR-SnT-EPCKavach-MTJ-AGC/ Consortium-GG Tronics - Expected", "PowerMac Project1 –Expected", "PowerMac Project2 –Expected", "SR - EPC_ABS23_JTJ-ED / Param", "SR - ABS_ERS-VTK_EPC / SS Rail", "NCR-SandT-EPC-ABSDHOGWL02/ Consortium-Param", "NCR - SIG-WS-CONTRACT-571/ Direct", "WR Ratlam", "WR 537DP"]},
        "saranchandvajjala.siemens@gmail.com": {"name": "Saran Chand Vajjala", "role": "Project Manager", "projects": ["Railtel 5", "NCR-SnT-EPCKavach-MTJ-AGC/ Consortium-GG Tronics - Expected", "SR 235DP"]},
        "harshmourya.siemens@gmail.com": {"name": "Harsh Mourya", "role": "Project Engineer", "projects": ["Railtel 5", "NCR Naini", "NCR-SandT-EPC-ABSGMC-VGLJ / Consortium-Param - Expected"]},
        "bhushanbabar.siemens@gmail.com": {"name": "Bhushan Babar", "role": "Commercial Project Manager", "projects": ["Railtel 5", "ECR-Dhanbad and Samastipur", "NCR-SandT-EPC-ABSGMC-VGLJ / Consortium-Param - Expected", "NCR-SnT-EPCKavach-MTJ-AGC/ Consortium-GG Tronics - Expected", "Panoli"]},
        "satyaranjanmishra.siemens@gmail.com": {"name": "Satya Ranjan Mishra", "role": "Site Manager", "projects": ["TATA Hot Metal", "TATA 8MTPA"]},
        "abhijeethannamshetty.siemens@gmail.com": {"name": "Abhijeet Hannamshetty", "role": "Requirement Engineer", "projects": ["TATA Hot Metal", "NCR Naini", "TATA 8MTPA", "WCR Bhopal - Present L1", "NCR-SandT-EPC-ABSGMC-VGLJ / Consortium-Param - Expected", "NCR-SnT-EPCKavach-MTJ-AGC/ Consortium-GG Tronics - Expected", "PowerMac Project2 –Expected", "SR - EPC_ABS23_JTJ-ED / Param", "SR - ABS_ERS-VTK_EPC / SS Rail", "NCR-SandT-EPC-ABSDHOGWL02/ Consortium-Param", "NCR - SIG-WS-CONTRACT-571/ Direct", "WR Ratlam", "WR 537DP"]},
        "ehs-4.siemens@gmail.com": {"name": "EHS-4", "role": "EHS", "projects": ["NCR-SnT-EPCKavach-MTJ-AGC/ Consortium-GG Tronics - Expected"]},
        "sudhaajaykumar.siemens@gmail.com": {"name": "Sudha Ajaykumar", "role": "Commercial Project Manager", "projects": ["TATA Hot Metal", "TATA 8MTPA", "NCR Naini"]},
        "atulkumarshukla.siemens@gmail.com": {"name": "Atul Kumar Shukla", "role": "Engineer", "projects": ["NCR Naini", "NWR Jaipur - Present L1", "PowerMac Project1 –Expected", "PowerMac Project2 –Expected", "WR Ratlam", "Bid/ Sales Support"]},
        "rajneeshkumar.siemens@gmail.com": {"name": "Rajneesh Kumar", "role": "Site Manager", "projects": ["NCR Naini"]},
        "ankanghosh.siemens@gmail.com": {"name": "Ankan Ghosh", "role": "System manager", "projects": ["NCR Naini", "TATA 8MTPA", "PowerMac Project1 –Expected"]},
        "ehs-2.siemens@gmail.com": {"name": "EHS-2", "role": "EHS", "projects": ["NCR Naini"]},
        "atulpande.siemens@gmail.com": {"name": "Atul Pande", "role": "Project Director", "projects": ["DFCC"]},
        "sanjibmandal.siemens@gmail.com": {"name": "Sanjib Mandal", "role": "Sr. Project Manager ", "projects": ["DFCC"]},
        "ajazulhaque.siemens@gmail.com": {"name": "Ajazul Haque", "role": "Site Manager", "projects": ["DFCC"]},
        "yogeshdeshmukh.siemens@gmail.com": {"name": "Yogesh Deshmukh", "role": "System Engineer", "projects": ["DFCC", "NWR Jaipur - Present L1"]},
        "badriraja.siemens@gmail.com": {"name": "Badri Raja", "role": "Site Manager", "projects": ["ECR-Dhanbad and Samastipur"]},
        "virendrasaini.siemens@gmail.com": {"name": "Virendra Saini", "role": "Project Manager ", "projects": ["NWR Jaipur - Present L1", "NCR-SandT-EPC-ABSGMC-VGLJ / Consortium-Param - Expected", "PowerMac Project2 –Expected"]},
        "prashantwagh.siemens@gmail.com": {"name": "Prashant Wagh", "role": "Project Engineer", "projects": ["NWR Jaipur - Present L1", "PowerMac Project1 –Expected"]},
        "sm-1.siemens@gmail.com": {"name": "SM-1", "role": "Site Manager", "projects": ["NWR Jaipur - Present L1"]},
        "rm-1.siemens@gmail.com": {"name": "RM-1", "role": "Requirement Manager", "projects": ["NWR Jaipur - Present L1", "PowerMac Project1 –Expected"]},
        "sch-1.siemens@gmail.com": {"name": "Sch-1", "role": "Scheduler", "projects": ["NWR Jaipur - Present L1", "PowerMac Project1 –Expected"]},
        "ehs-3.siemens@gmail.com": {"name": "EHS-3", "role": "EHS", "projects": ["NWR Jaipur - Present L1"]},
        "ganeshpatil.siemens@gmail.com": {"name": "Ganesh Patil", "role": "Project Manager ", "projects": ["WCR Bhopal - Present L1", "PowerMac Project1 –Expected", "WR Ratlam"]},
        "pe-1.siemens@gmail.com": {"name": "PE-1", "role": "Project Engineer", "projects": ["WCR Bhopal - Present L1", "NCR-SnT-EPCKavach-MTJ-AGC/ Consortium-GG Tronics - Expected"]},
        "engg-1.siemens@gmail.com": {"name": "Engg-1", "role": "Engineering", "projects": ["WCR Bhopal - Present L1", "NCR-SandT-EPC-ABSGMC-VGLJ / Consortium-Param - Expected"]},
        "sm-3.siemens@gmail.com": {"name": "SM-3", "role": "Site Manager", "projects": ["NCR-SandT-EPC-ABSGMC-VGLJ / Consortium-Param - Expected"]},
        "rajatshukla.siemens@gmail.com": {"name": "Rajat Shukla", "role": "System Engineer", "projects": ["NCR-SandT-EPC-ABSGMC-VGLJ / Consortium-Param - Expected", "NCR-SnT-EPCKavach-MTJ-AGC/ Consortium-GG Tronics - Expected", "MSDAC Region North"]},
        "ehs-1.siemens@gmail.com": {"name": "EHS-1", "role": "EHS", "projects": ["TATA Hot Metal"]},
        "engg-2.siemens@gmail.com": {"name": "Engg-2", "role": "Engineering", "projects": ["NCR-SnT-EPCKavach-MTJ-AGC/ Consortium-GG Tronics - Expected", "SR - EPC_ABS23_JTJ-ED / Param", "SR - ABS_ERS-VTK_EPC / SS Rail"]},
        "sm-4.siemens@gmail.com": {"name": "SM-4", "role": "Site Manager", "projects": ["NCR-SnT-EPCKavach-MTJ-AGC/ Consortium-GG Tronics - Expected"]},
        "ehs-5.siemens@gmail.com": {"name": "EHS-5", "role": "EHS", "projects": ["PowerMac Project1 –Expected", "PowerMac Project2 –Expected"]},
        "sm-5.siemens@gmail.com": {"name": "SM-5", "role": "Site Manager", "projects": ["PowerMac Project1 –Expected"]},
        "se-2.siemens@gmail.com": {"name": "SE-2", "role": "System Engineer", "projects": ["PowerMac Project2 –Expected", "SR - EPC_ABS23_JTJ-ED / Param", "SR - ABS_ERS-VTK_EPC / SS Rail", "NCR - SIG-WS-CONTRACT-571/ Direct", "NCR-SandT-EPC-ABSDHOGWL02/ Consortium-Param", "MSDAC Support East"]},
        "sm-6.siemens@gmail.com": {"name": "SM-6", "role": "System Engineer", "projects": ["PowerMac Project2 –Expected", "SR - EPC_ABS23_JTJ-ED / Param"]},
        "pe-2.siemens@gmail.com": {"name": "PE-2", "role": "Project Engineer", "projects": ["PowerMac Project2 –Expected", "SR - EPC_ABS23_JTJ-ED / Param", "SR - ABS_ERS-VTK_EPC / SS Rail"]},
        "cpmtl.siemens@gmail.com": {"name": "CPM TL", "role": "CPM Team Lead", "projects": ["Commercial Lead"]},
        "kishorikumari.siemens@gmail.com": {"name": "Kishori Kumari", "role": "Project Manager ", "projects": ["SR - EPC_ABS23_JTJ-ED / Param"]},
        "ehs-6.siemens@gmail.com": {"name": "EHS-6", "role": "EHS", "projects": ["SR - EPC_ABS23_JTJ-ED / Param", "SR - ABS_ERS-VTK_EPC / SS Rail"]},
        "cpm-1.siemens@gmail.com": {"name": "CPM-1", "role": "CPM", "projects": ["SR - EPC_ABS23_JTJ-ED / Param", "PowerMac Project2 –Expected"]},
        "pm-1.siemens@gmail.com": {"name": "PM-1", "role": "Project Manager ", "projects": ["SR - ABS_ERS-VTK_EPC / SS Rail"]},
        "cpm-2.siemens@gmail.com": {"name": "CPM-2", "role": "Commercial Project Manager", "projects": ["SR - ABS_ERS-VTK_EPC / SS Rail"]},
        "satyashahi.siemens@gmail.com": {"name": "Satya Shahi", "role": "Project Manager ", "projects": ["NCR-SandT-EPC-ABSDHOGWL02/ Consortium-Param", "NCR - SIG-WS-CONTRACT-571/ Direct"]},
        "pe-3.siemens@gmail.com": {"name": "PE-3", "role": "Project Engineer", "projects": ["NCR-SandT-EPC-ABSDHOGWL02/ Consortium-Param", "NCR - SIG-WS-CONTRACT-571/ Direct"]},
        "engg-3.siemens@gmail.com": {"name": "Engg-3", "role": "Engineering", "projects": ["NCR-SandT-EPC-ABSDHOGWL02/ Consortium-Param", "NCR - SIG-WS-CONTRACT-571/ Direct"]},
        "sm-7.siemens@gmail.com": {"name": "SM-7", "role": "Site Manager", "projects": ["NCR-SandT-EPC-ABSDHOGWL02/ Consortium-Param"]},
        "sm-8.siemens@gmail.com": {"name": "SM-8", "role": "Site Manager", "projects": ["NCR - SIG-WS-CONTRACT-571/ Direct"]},
        "ehs-7.siemens@gmail.com": {"name": "EHS-7", "role": "EHS", "projects": ["NCR - SIG-WS-CONTRACT-571/ Direct"]},
        "saubhagyashreemahi.siemens@gmail.com": {"name": "Saubhagyashree Mahi", "role": "Commercial Project Manager", "projects": ["NCR - SIG-WS-CONTRACT-571/ Direct"]},
        "raghunathnemlekar.siemens@gmail.com": {"name": "Raghunath Nemlekar", "role": "Project Engineer", "projects": ["CR Project Closure", "Bid/ Sales Support"]},
        "varshajagtap.siemens@gmail.com": {"name": "Varsha Jagtap", "role": "Commercial Project manager", "projects": ["CR Project Closure", "NR Ambala", "SR 235DP", "SR KBT-AJJ Project", "WR 537DP", "Pune Daund & Miraj"]},
        "manojkatira.siemens@gmail.com": {"name": "Manoj Katira", "role": "Project Engineer", "projects": ["NR Ambala", "SR KBT-AJJ Project", "WR Ratlam"]},
        "sm-9.siemens@gmail.com": {"name": "SM-9", "role": "Site Manager", "projects": ["WR Ratlam"]},
        "mohdjunaid.siemens@gmail.com": {"name": "Mohd Junaid", "role": "System Engineer", "projects": ["WR Ratlam", "WR 537DP", "Pune Daund & Miraj", "MSDAC Region Central"]},
        "dhirajkumar.siemens@gmail.com": {"name": "Dhiraj Kumar", "role": "EHS", "projects": ["WR Ratlam"]},
        "amardeepsaini.siemens@gmail.com": {"name": "Amardeep Saini", "role": "Project Manager", "projects": ["WR 537DP"]},
        "ashishsurve.siemens@gmail.com": {"name": "Ashish Surve", "role": "System Engineer", "projects": ["WR 537DP", "Product Management-AFTC"]},
        "aneekagrawal.siemens@gmail.com": {"name": "Aneek Agrawal", "role": "Project Engineer", "projects": ["Pune Daund & Miraj", "Bid/ Sales Support"]},
        "anandamaity.siemens@gmail.com": {"name": "Ananda Maity", "role": "Product Manager", "projects": ["Product Management-EoTT"]},
        "venkatanaik.siemens@gmail.com": {"name": "Venkata Naik", "role": "Component Engineer", "projects": ["Product Management"]},
        "krishnakanthrokkedi.siemens@gmail.com": {"name": "Krishnakanth Rokkedi", "role": "Product Manager", "projects": ["Product Management-MSDAC"]},
        "tusharchiplunkar.siemens@gmail.com": {"name": "Tushar Chiplunkar", "role": "Product Manager", "projects": ["Product Management-Point Machine"]},
        "gunjanjha.siemens@gmail.com": {"name": "Gunjan Jha", "role": "System Engineer", "projects": ["Bid/ Sales Support", "MSDAC Support West"]},
        "rohinipatwardhan.siemens@gmail.com": {"name": "Rohini Patwardhan", "role": "Sales ProfessionaL", "projects": ["Bid/ Sales Support"]},
        "rishishukla.siemens@gmail.com": {"name": "Rishi Shukla", "role": "Sales ProfessionaL", "projects": ["Bid/ Sales Support"]},
        "sampurnaambole.siemens@gmail.com": {"name": "Sampurna Ambole", "role": "Sales Professional", "projects": ["Bid/ Sales Support"]},
        "harshaligade.siemens@gmail.com": {"name": "Harshali Gade", "role": "Sales Professional", "projects": ["Bid/ Sales Support"]},
        "sridharkopanathi.siemens@gmail.com": {"name": "Sridhar Kopanathi", "role": "Sales Professional", "projects": ["Bid/ Sales Support"]},
        "aritrasiddharthabasu.siemens@gmail.com": {"name": "Aritra Siddhartha Basu", "role": "Sales Professional", "projects": ["Bid/ Sales Support"]},
        "prashantrode.siemens@gmail.com": {"name": "Prashant Rode", "role": "Engineering", "projects": ["Bid/ Sales Support"]},
        "goutambhaiya.siemens@gmail.com": {"name": "Goutam Bhaiya", "role": "Project Engineer", "projects": ["Product Delivery Support"]},
        "shravanibhave.siemens@gmail.com": {"name": "Shravani Bhave", "role": "Project Engineer", "projects": ["Product Delivery Support"]},
        "anupamaraj.siemens@gmail.com": {"name": "Anupama Raj", "role": "Project Engineer", "projects": ["Product Delivery Support"]},
        "kiranvarde.siemens@gmail.com": {"name": "Kiran Varde", "role": "Project Engineer", "projects": ["RRI Altration and New Work"]},
        "sachindeshmukh.siemens@gmail.com": {"name": "Sachin Deshmukh", "role": "Project Engineer", "projects": ["RRI Altration and New Work"]},
        "se-1.siemens@gmail.com": {"name": "SE-1", "role": "System Engineer", "projects": ["MSDAC Support West"]},
        "gopikrishnaalla.siemens@gmail.com": {"name": "Gopikrishna Alla", "role": "System Engineer", "projects": ["MSDAC Support South"]},
        "amitpandit.siemens@gmail.com": {"name": "Amit Pandit", "role": "Srystem Engineer", "projects": ["MSDAC Support East"]},
        "ritukalaparambil.siemens@gmail.com": {"name": "Ritu Kalaparambil", "role": "Commercial Project Manager", "projects": ["PR Projects CPM"]},
        "karunagandharva.siemens@gmail.com": {"name": "Karuna Gandharva", "role": "Commercial Project Manager", "projects": ["PR Projects CPM"]}
    }

    employees_dict = {}
    for email, data in consolidated_employee_data.items():
        try:
            employee = Employee(name=data['name'], email=email, role=data['role'])
            db.session.add(employee)
            db.session.flush() # Flush to get ID for assignments_dict before commit
            employees_dict[email] = employee
            print(f"  Added Employee: {employee.name}")
        except IntegrityError:
            db.session.rollback()
            existing_employee = Employee.query.filter_by(email=email).first()
            if existing_employee:
                employees_dict[email] = existing_employee # Store existing employee
            print(f"  Employee '{email}' already exists, skipping.")
        except Exception as e:
            db.session.rollback()
            print(f"  Error adding employee {data['name']} ({email}): {e}")
    db.session.commit()

    print("Creating Assignments...")
    assignments_dict = {} # This will store assignment objects keyed by (employee_id, project_id)
    for email, data in consolidated_employee_data.items():
        employee = employees_dict.get(email)
        if not employee:
            print(f"  Skipping assignments for '{data['name']}' as employee not found.")
            continue

        for project_name in data['projects']:
            project = projects_dict.get(project_name)
            if not project:
                print(f"  Project '{project_name}' not found for employee {employee.name}, skipping assignment.")
                continue

            try:
                existing_assignment = Assignment.query.filter_by(
                    employee_id=employee.id,
                    project_id=project.id
                ).first()

                if not existing_assignment:
                    assignment = Assignment(
                        employee_id=employee.id,
                        project_id=project.id,
                        assigned_hours_per_week=40,
                        assigned_start_month="January",
                        assigned_start_year=2024,
                        assigned_end_month="December",
                        assigned_end_year=2024
                    )
                    db.session.add(assignment)
                    db.session.flush() # Flush to get ID for assignments_dict before commit
                    assignments_dict[(employee.id, project.id)] = assignment
                    print(f"  Assigned {employee.name} to {project.name}")
                else:
                    assignments_dict[(employee.id, project.id)] = existing_assignment
                    print(f"  Assignment for {employee.name} on {project.name} already exists, skipping creation.")

            except IntegrityError:
                db.session.rollback()
                print(f"  Assignment for {employee.name} on {project.name} already exists or invalid foreign key, skipping.")
            except Exception as e:
                db.session.rollback()
                print(f"  Error assigning {employee.name} to {project.name}: {e}")
    db.session.commit()

    print("Inserting WeeklyHours data...")
    # These functions need to match the PREDEFINED_POSITIONS list in app.py
    # This list is used only for seeding and should be consistent with app.py
    PREDEFINED_POSITIONS_FOR_SEEDING = [
        "Site Management", "Quality Management", "Engineering", "Scheduling Management",
        "EHS Management", "Sales", "System Engineer", "Project Engineer",
        "Document Management", "Requirement Management", "Commercial",
        "Product Management", "Other"
    ]

    weekly_hours_entries = []

    # --- Aman Rawat ---
    aman_rawat = employees_dict.get("amanrawat.siemens@gmail.com")
    ncr_naini = projects_dict.get("NCR Naini")
    if aman_rawat and ncr_naini:
        aman_naini_assignment = assignments_dict.get((aman_rawat.id, ncr_naini.id))
        if aman_naini_assignment:
            # Aman Rawat on NCR Naini - multiple functions in same week
            weekly_hours_entries.extend([
                WeeklyHours(assignment_id=aman_naini_assignment.id, week_start_date=date(2024, 6, 17), hours_worked=32, function_name="Scheduling Management"),
                WeeklyHours(assignment_id=aman_naini_assignment.id, week_start_date=date(2024, 6, 17), hours_worked=24, function_name="Requirement Management"),
                # Next week
                WeeklyHours(assignment_id=aman_naini_assignment.id, week_start_date=date(2024, 6, 24), hours_worked=24, function_name="Scheduling Management"),
                WeeklyHours(assignment_id=aman_naini_assignment.id, week_start_date=date(2024, 6, 24), hours_worked=16, function_name="Requirement Management"),
                # Next week
                WeeklyHours(assignment_id=aman_naini_assignment.id, week_start_date=date(2024, 7, 1), hours_worked=16, function_name="Scheduling Management"),
                WeeklyHours(assignment_id=aman_naini_assignment.id, week_start_date=date(2024, 7, 1), hours_worked=16, function_name="Requirement Management"),
            ])
        else:
            print(f"  Assignment not found for Aman Rawat on NCR Naini, skipping WeeklyHours.")

    # --- Ganesh Patil ---
    ganesh_patil = employees_dict.get("ganeshpatil.siemens@gmail.com")
    nwr_jaipur = projects_dict.get("NWR Jaipur - Present L1") # Using the exact project name
    nwr_udhna = projects_dict.get("NWR Udhana") # Assuming this project exists or will be added
    new_project_alpha = Project.query.filter_by(name='New Project Alpha').first() # Ensure this project exists

    if ganesh_patil and nwr_jaipur:
        ganesh_jaipur_assignment = assignments_dict.get((ganesh_patil.id, nwr_jaipur.id))
        if ganesh_jaipur_assignment:
            weekly_hours_entries.extend([
                WeeklyHours(assignment_id=ganesh_jaipur_assignment.id, week_start_date=date(2024, 6, 17), hours_worked=8, function_name="Document Management"),
                WeeklyHours(assignment_id=ganesh_jaipur_assignment.id, week_start_date=date(2024, 6, 24), hours_worked=8, function_name="Document Management"),
                WeeklyHours(assignment_id=ganesh_jaipur_assignment.id, week_start_date=date(2024, 7, 1), hours_worked=8, function_name="Document Management"),
            ])
        else:
            print(f"  Assignment not found for Ganesh Patil on NWR Jaipur, skipping WeeklyHours.")

    if ganesh_patil and nwr_udhna:
        ganesh_udhna_assignment = assignments_dict.get((ganesh_patil.id, nwr_udhna.id))
        if ganesh_udhna_assignment:
            weekly_hours_entries.extend([
                WeeklyHours(assignment_id=ganesh_udhna_assignment.id, week_start_date=date(2024, 6, 17), hours_worked=8, function_name="Scheduling Management"),
                WeeklyHours(assignment_id=ganesh_udhna_assignment.id, week_start_date=date(2024, 6, 24), hours_worked=8, function_name="Scheduling Management"),
                WeeklyHours(assignment_id=ganesh_udhna_assignment.id, week_start_date=date(2024, 7, 1), hours_worked=8, function_name="Scheduling Management"),
            ])
        else:
            print(f"  Assignment not found for Ganesh Patil on NWR Udhana, skipping WeeklyHours.")

    if ganesh_patil and new_project_alpha:
        # Manually create assignment if it's not in consolidated_employee_data projects for Ganesh
        ganesh_alpha_assignment = assignments_dict.get((ganesh_patil.id, new_project_alpha.id))
        if not ganesh_alpha_assignment:
            try:
                new_assign = Assignment(
                    employee_id=ganesh_patil.id,
                    project_id=new_project_alpha.id,
                    assigned_hours_per_week=20, # Example hours
                    assigned_start_month="July", assigned_start_year=2024,
                    assigned_end_month="December", assigned_end_year=2024
                )
                db.session.add(new_assign)
                db.session.flush()
                ganesh_alpha_assignment = new_assign
                assignments_dict[(ganesh_patil.id, new_project_alpha.id)] = new_assign
                print(f"  Created missing assignment for Ganesh Patil on {new_project_alpha.name} for seeding.")
            except IntegrityError:
                db.session.rollback()
                ganesh_alpha_assignment = Assignment.query.filter_by(employee_id=ganesh_patil.id, project_id=new_project_alpha.id).first()
                assignments_dict[(ganesh_patil.id, new_project_alpha.id)] = ganesh_alpha_assignment
                print(f"  Assignment for Ganesh Patil on {new_project_alpha.name} already exists.")
            except Exception as e:
                db.session.rollback()
                print(f"  Error creating assignment for Ganesh Patil on {new_project_alpha.name}: {e}")

        if ganesh_alpha_assignment:
            # Ganesh Patil on New Project Alpha - starting from week 27
            weekly_hours_entries.extend([
                WeeklyHours(assignment_id=ganesh_alpha_assignment.id, week_start_date=date(2024, 7, 1), hours_worked=16, function_name="Site Management"),
                WeeklyHours(assignment_id=ganesh_alpha_assignment.id, week_start_date=date(2024, 7, 8), hours_worked=16, function_name="Site Management"),
            ])
        else:
            print(f"  Assignment still not found for Ganesh Patil on New Project Alpha, skipping WeeklyHours.")


    # --- Priyanka Sharma ---
    # Need to find Priyanka Sharma and a project she's assigned to in your consolidated_employee_data.
    # Let's use 'QMiP-1' and 'ER - TCAS' for simplicity as they are in your existing data
    priyanka_sharma = employees_dict.get("qmip.siemens@gmail.com") # Using QMiP-1 as an example for Priyanka
    old_project_beta = projects_dict.get("ER - TCAS") # Using ER - TCAS as example project

    if priyanka_sharma and old_project_beta:
        priyanka_beta_assignment = assignments_dict.get((priyanka_sharma.id, old_project_beta.id))
        if priyanka_beta_assignment:
            weekly_hours_entries.extend([
                WeeklyHours(assignment_id=priyanka_beta_assignment.id, week_start_date=date(2024, 6, 17), hours_worked=40, function_name="Quality Management"),
                WeeklyHours(assignment_id=priyanka_beta_assignment.id, week_start_date=date(2024, 6, 24), hours_worked=40, function_name="Quality Management"),
                WeeklyHours(assignment_id=priyanka_beta_assignment.id, week_start_date=date(2024, 7, 1), hours_worked=40, function_name="Quality Management"),
            ])
        else:
            print(f"  Assignment not found for Priyanka Sharma (QMiP-1) on ER - TCAS, skipping WeeklyHours.")


    # Add these to the session, handling potential duplicates if running multiple times
    for wh_entry in weekly_hours_entries:
        try:
            existing_wh = WeeklyHours.query.filter_by(
                assignment_id=wh_entry.assignment_id,
                week_start_date=wh_entry.week_start_date,
                function_name=wh_entry.function_name # Include function_name in lookup for uniqueness
            ).first()
            if not existing_wh:
                db.session.add(wh_entry)
                print(f"  Added WeeklyHours for Assignment ID {wh_entry.assignment_id}, Week: {wh_entry.week_start_date}, Function: {wh_entry.function_name}, Hours: {wh_entry.hours_worked}")
            else:
                print(f"  WeeklyHours for Assignment ID {wh_entry.assignment_id}, Week: {wh_entry.week_start_date}, Function: {wh_entry.function_name} already exists, skipping.")
            db.session.commit() # Commit each weekly hour entry
        except IntegrityError:
            db.session.rollback()
            print(f"  Integrity error on WeeklyHours for Assignment ID {wh_entry.assignment_id}, Week: {wh_entry.week_start_date}, Function: {wh_entry.function_name}.")
        except Exception as e:
            db.session.rollback()
            print(f"  Error adding WeeklyHours: {e}")

    print("All projects, employees, assignments, and weekly hours processed and committed to the database!")

