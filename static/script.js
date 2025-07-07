// Global variable for the main message container
// (Will be initialized on DOMContentLoaded)
// --- NEW: PWA Service Worker Registration ---
// This script registers a service worker for the Progressive Web App (PWA) functionality.
// The service worker enables features like offline support and background caching.
if ('serviceWorker' in navigator) { // Checks if the browser supports Service Workers
    window.addEventListener('load', function() { // Waits until the entire page is loaded
        navigator.serviceWorker.register('/static/service-worker.js').then(function(registration) {
            // Registration was successful
            console.log('ServiceWorker registration successful with scope: ', registration.scope);
        }, function(err) {
            // registration failed :(
            console.log('ServiceWorker registration failed: ', err);
        });
    });
}
// ------------------------------------------
let globalMessageContainer;

// Helper to display messages in a specific container or the global one
function showMessage(msg, type = 'info', containerElement = null) {
    const targetContainer = containerElement || globalMessageContainer;
    if (!targetContainer) {
        console.warn("Message container not found. Message:", msg);
        return;
    }

    targetContainer.innerHTML = ''; // Clear previous messages
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${type}`;
    msgDiv.textContent = msg;
    targetContainer.appendChild(msgDiv);
    targetContainer.style.display = 'block'; // Ensure container is visible

    setTimeout(() => {
        msgDiv.remove(); // Remove the specific message div
        if (targetContainer.children.length === 0) {
            targetContainer.style.display = 'none';
        }
    }, 5000);
}

// Bulletproof export function
function exportData(dataType) {
    const exportMessageContainer = document.getElementById('export-message-container');
    
    if (!exportMessageContainer) {
        console.error('Export message container not found');
        return;
    }
    
    showMessage('Starting export...', 'info', exportMessageContainer);
    
    // Direct window location method - most reliable
    const url = `/api/export_data?type=${dataType}&timestamp=${Date.now()}`;
    window.location.href = url;
    
    // Show success message after a delay
    setTimeout(() => {
        showMessage(`${dataType.replace('_', ' ')} export completed!`, 'success', exportMessageContainer);
    }, 2000);
}

// Delete functions
function deleteEmployee(employeeId, employeeName) {
    if (!confirm(`Are you sure you want to delete employee "${employeeName}"? This action cannot be undone.`)) {
        return;
    }
    
    fetch(`/api/employees/${employeeId}`, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.message) {
            showMessage(data.message, data.message.includes('Error') ? 'error' : 'success', globalMessageContainer);
            if (data.message.includes('deleted successfully')) {
                // Refresh the employees list
                location.reload();
            }
        }
    })
    .catch(error => {
        showMessage(`Error deleting employee: ${error.message}`, 'error', globalMessageContainer);
    });
}

function deleteProject(projectId, projectName) {
    if (!confirm(`Are you sure you want to delete project "${projectName}"? This action cannot be undone.`)) {
        return;
    }
    
    fetch(`/api/projects/${projectId}`, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.message) {
            showMessage(data.message, data.message.includes('Error') ? 'error' : 'success', globalMessageContainer);
            if (data.message.includes('deleted successfully')) {
                // Refresh the projects list
                location.reload();
            }
        }
    })
    .catch(error => {
        showMessage(`Error deleting project: ${error.message}`, 'error', globalMessageContainer);
    });
}

function deleteAssignment(assignmentId, employeeName, projectName) {
    if (!confirm(`Are you sure you want to delete assignment of "${employeeName}" to "${projectName}"? This action cannot be undone.`)) {
        return;
    }
    
    fetch(`/api/assignments/${assignmentId}`, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.message) {
            showMessage(data.message, data.message.includes('Error') ? 'error' : 'success', globalMessageContainer);
            if (data.message.includes('deleted successfully')) {
                // Refresh the assignments list
                location.reload();
            }
        }
    })
    .catch(error => {
        showMessage(`Error deleting assignment: ${error.message}`, 'error', globalMessageContainer);
    });
}

function deleteWeeklyHours(weeklyHoursId, employeeName, projectName, weekDate) {
    if (!confirm(`Are you sure you want to delete weekly hours record for "${employeeName}" on "${projectName}" for week ${weekDate}? This action cannot be undone.`)) {
        return;
    }
    
    fetch(`/api/weekly_hours/${weeklyHoursId}`, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.message) {
            showMessage(data.message, data.message.includes('Error') ? 'error' : 'success', globalMessageContainer);
            if (data.message.includes('deleted successfully')) {
                // Refresh the page or update the display
                location.reload();
            }
        }
    })
    .catch(error => {
        showMessage(`Error deleting weekly hours: ${error.message}`, 'error', globalMessageContainer);
    });
}

// This function handles the download logic for various report types
function downloadExcel(reportType) {
    let url = '';
    let filename = '';
    const exportMessageContainer = document.getElementById('export-message-container');

    // Determine the correct API endpoint and filename based on the report type
    if (reportType === 'workload') {
        url = '/api/export_workload_excel';
        filename = 'Workload_Summary_Report.xlsx';
    } else if (reportType === 'actual_hours_detailed') {
        url = '/api/export_actual_hours_detailed_excel';
        filename = 'Detailed_Actual_Hours_Report.xlsx';
    }
        else if (reportType === 'processed_imported_data') {
        url = '/api/export_processed_imported_data';
        filename = 'Processed_Imported_Data_Report.xlsx';
    }
     else {
        console.error('Unknown report type:', reportType);
        // Call global showMessage, passing the specific container
        showMessage('Error: Unknown report type requested.', 'error', exportMessageContainer);
        return;
    }

    showMessage('Generating Excel file...', 'info', exportMessageContainer); // Show loading message

    // Fetch the Excel file from the server
    fetch(url)
        .then(response => {
            // Check if the server response was successful
            if (!response.ok) {
                // If not successful, try to parse error message from JSON
                return response.json().then(errorData => {
                    throw new Error(errorData.message || 'Network response was not ok');
                });
            }
            // If successful, get the response as a Blob (binary data)
            return response.blob();
        })
        .then(blob => {
            // Create a temporary URL for the Blob
            const url = window.URL.createObjectURL(new Blob([blob]));
            const a = document.createElement('a'); // Create a temporary anchor element
            a.href = url;
            a.download = filename; // Set the download filename
            document.body.appendChild(a); // Append to body (necessary for Firefox)
            a.click(); // Programmatically click the link to trigger download
            a.remove(); // Clean up the temporary element
            window.URL.revokeObjectURL(url); // Release the object URL
            showMessage(`'${filename}' downloaded successfully!`, 'success', exportMessageContainer);
        })
        .catch(error => {
            // Handle any errors during the fetch or processing
            console.error('Error exporting data:', error);
            showMessage(`Error exporting data: ${error.message}`, 'error', exportMessageContainer);
        });
}


document.addEventListener('DOMContentLoaded', function() {
    const navLinks = document.querySelectorAll('nav ul li a');
    globalMessageContainer = document.getElementById('message-container'); // Initialize global variable here

    // Define the 13 constant functions (Consistent with app.py's expectations)
    const FUNCTIONS = [
        "Project Management",
        "Site Management",
        "Quality Management",
        "Engineering",
        "Scheduling Management",
        "EHS Management",
        "Sales",
        "System Engineer",
        "Project Engineer",
        "Document Management",
        "Requirement Management",
        "Commercial",
        "Product Management",
        "Other" // Added "Other" as a fallback, consistent with backend
    ];

    // Function to highlight active navigation link based on current URL path
    function highlightNavLink() {
        const currentPath = window.location.pathname;
        navLinks.forEach(link => {
            link.classList.remove('active');
            const linkHref = link.getAttribute('href');
            const linkPath = new URL(linkHref, window.location.origin).pathname;

            if (currentPath === '/' && linkPath === '/index') {
                link.classList.add('active');
            } else if (currentPath === linkPath) {
                link.classList.add('active');
            }
        });
    }

    // --- General Data Fetching Helper (Includes search term parameter) ---
    async function fetchData(baseUrl, errorMsg, searchTerm = '') {
        let url = baseUrl;
        if (searchTerm) {
            url += `?q=${encodeURIComponent(searchTerm)}`;
        }
        try {
            const response = await fetch(url);
            if (!response.ok) {
                const errorDetail = await response.json().catch(() => ({ message: response.statusText }));
                throw new Error(`${errorMsg}: ${errorDetail.message || 'Unknown error'}`);
            }
            return await response.json();
        } catch (error) {
            console.error(errorMsg, error);
            showMessage(`Failed to load data: ${error.message || errorMsg}`, 'error');
            return null;
        }
    }

    // --- Employee Section Logic (Includes search term parameter) ---
    window.loadEmployees = async function(searchTerm = '') { // Added searchTerm parameter
        const employees = await fetchData('/api/employees', 'Error loading employees', searchTerm); // Pass searchTerm
        const employeesTableBody = document.getElementById('employees-table')?.querySelector('tbody');

        if (employees && employeesTableBody) {
            employeesTableBody.innerHTML = '';
            if (employees.length === 0) {
                employeesTableBody.innerHTML = '<tr><td colspan="4">No employees found.</td></tr>';
                return;
            }
            employees.forEach(employee => {
                const row = employeesTableBody.insertRow();
                row.insertCell().textContent = employee.name;
                row.insertCell().textContent = employee.role;
                row.insertCell().textContent = employee.email;
                
                // Add actions cell with delete button
                const actionsCell = row.insertCell();
                actionsCell.innerHTML = `
                    <button class="btn btn-danger btn-sm" onclick="deleteEmployee(${employee.id}, '${employee.name.replace(/'/g, "\\'")}')">
                        Delete
                    </button>
                `;
            });
        }
    };

    // --- Projects Section Logic (Includes search term parameter) ---
    const monthStringToInt = (monthName) => {
        const monthMap = {
            "january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6,
            "july": 7, "august": 8, "september": 9, "october": 10, "november": 11, "december": 12
        };
        return monthMap[monthName.toLowerCase()] || 0;
    };

    const getLastDayOfMonth = (year, month) => {
        return new Date(year, month, 0).getDate();
    };

    window.loadProjects = async function(searchTerm = '') { // Added searchTerm parameter
        const projects = await fetchData('/api/projects', 'Error loading projects', searchTerm); // Pass searchTerm
        const projectsTableBody = document.getElementById('projects-table')?.querySelector('tbody');

        if (projects && projectsTableBody) {
            projectsTableBody.innerHTML = '';
            if (projects.length === 0) {
                projectsTableBody.innerHTML = '<tr><td colspan="5">No projects found.</td></tr>';
                return;
            }
            projects.forEach(project => {
                const startMonthNum = monthStringToInt(project.start_month);
                const endMonthNum = monthStringToInt(project.end_month);

                const startDateStr = project.start_year && startMonthNum
                    ? `${project.start_year}-${String(startMonthNum).padStart(2, '0')}-01`
                    : 'N/A';
                const endDateStr = project.end_year && endMonthNum
                    ? `${project.end_year}-${String(endMonthNum).padStart(2, '0')}-${String(getLastDayOfMonth(project.end_year, endMonthNum)).padStart(2, '0')}`
                    : 'N/A';

                const row = projectsTableBody.insertRow();
                row.insertCell().textContent = project.name;
                row.insertCell().textContent = project.duration_months;
                row.insertCell().textContent = startDateStr;
                row.insertCell().textContent = endDateStr;
                
                // Add actions cell with delete button
                const actionsCell = row.insertCell();
                actionsCell.innerHTML = `
                    <button class="btn btn-danger btn-sm" onclick="deleteProject(${project.id}, '${project.name.replace(/'/g, "\\'")}')">
                        Delete
                    </button>
                `;
            });
        }
    };

    // --- Helper to get Monday of current week ---
    function getMondayOfCurrentWeek() {
        const today = new Date();
        const dayOfWeek = today.getDay(); // Sunday - 0, Monday - 1, ..., Saturday - 6
        const diff = today.getDate() - dayOfWeek + (dayOfWeek === 0 ? -6 : 1); // Adjust for Sunday (0)
        const monday = new Date(today.setDate(diff));
        return monday.toISOString().split('T')[0];
    }

    // --- Functions to populate dropdowns ---
    window.populateEmployeeDropdowns = async function() {
        const employees = await fetchData('/api/employees', 'Error loading employees for dropdowns');
        if (employees) {
            const employeeSelects = [
                document.getElementById('assign-employee-id'),
                document.getElementById('actual-hours-employee-id')
            ].filter(el => el != null);

            employeeSelects.forEach(select => {
                select.innerHTML = '<option value="">-- Select Employee --</option>';
                employees.forEach(employee => {
                    select.add(new Option(employee.name, employee.id));
                });
            });
        }
    };

    window.populateProjectDropdownsForActualHours = async function() {
        const projects = await fetchData('/api/projects', 'Error loading projects for actual hours dropdown');
        const actualHoursProjectSelect = document.getElementById('actual-hours-project-id');

        if (projects && actualHoursProjectSelect) {
            actualHoursProjectSelect.innerHTML = '<option value="">-- Select Project --</option>';
            projects.forEach(project => {
                actualHoursProjectSelect.add(new Option(project.name, project.id));
            });
        }
    };

    window.populateProjectDropdowns = async function() {
        const projectInput = document.getElementById('assign-project-name');
        const projectIdInput = document.getElementById('assign-project-id');
        if (!projectInput || !projectIdInput) return;

        const projects = await fetchData('/api/projects', 'Error loading projects for assignment dropdown');
        if (projects) {
            projectInput.addEventListener('input', () => {
                const inputVal = projectInput.value.trim();
                const matchedProject = projects.find(p => p.name.toLowerCase() === inputVal.toLowerCase());
                if (matchedProject) {
                    projectIdInput.value = matchedProject.id;
                } else {
                    projectIdInput.value = '';
                }
            });
        }
    };

    window.populateMonthYearDropdowns = function() {
        const monthSelects = [
            document.getElementById('assign-start-month'),
            document.getElementById('assign-end-month')
        ].filter(el => el != null);

        const yearSelects = [
            document.getElementById('assign-start-year'),
            document.getElementById('assign-end-year')
        ].filter(el => el != null);

        monthSelects.forEach(select => {
            select.innerHTML = '<option value="">-- Select Month --</option>';
            for (let i = 1; i <= 12; i++) {
                const monthName = new Date(0, i - 1).toLocaleString('en-US', { month: 'long' });
                select.add(new Option(monthName, i));
            }
        });

        yearSelects.forEach(select => {
            select.innerHTML = '<option value="">-- Select Year --</option>';
            const currentYear = new Date().getFullYear();
            for (let i = currentYear - 2; i <= currentYear + 5; i++) {
                select.add(new Option(i, i));
            }
        });
    };

    function populateMonthlyDateInputs() {
        const monthlyStartMonthSelect = document.getElementById('monthly-start-month');
        const monthlyStartYearInput = document.getElementById('monthly-start-year');
        const monthlyNumMonthsInput = document.getElementById('monthly-num-months');

        const currentYear = new Date().getFullYear();
        const currentMonth = new Date().getMonth() + 1;

        if (monthlyStartMonthSelect) {
            monthlyStartMonthSelect.innerHTML = '';
            for (let i = 1; i <= 12; i++) {
                const monthName = new Date(0, i - 1).toLocaleString('en-US', { month: 'long' });
                const option = new Option(monthName, i);
                if (i === currentMonth) {
                    option.selected = true;
                }
                monthlyStartMonthSelect.add(option);
            }
        }

        if (monthlyStartYearInput) {
            monthlyStartYearInput.value = currentYear;
        }
    }

    // NEW FUNCTION: Populate the Function/Position dropdown (Updated ID)
    window.populateFunctionDropdown = function() {
        const functionSelect = document.getElementById('actual-hours-function-name'); // Updated ID here
        if (functionSelect) {
            functionSelect.innerHTML = '<option value="">-- Select Function --</option>';
            FUNCTIONS.forEach(func => {
                functionSelect.add(new Option(func, func));
            });
        }
    };

    window.populateAllForms = async function(formType) {
        if (formType === 'assign_employee' || formType === 'actual_hours') {
            await populateEmployeeDropdowns();
            if (formType === 'assign_employee') {
                await populateProjectDropdowns();
                populateMonthYearDropdowns();
            } else if (formType === 'actual_hours') {
                await populateProjectDropdownsForActualHours();
                const actualWeekStartDateInput = document.getElementById('actual-week-start-date');
                if (actualWeekStartDateInput) {
                    actualWeekStartDateInput.value = getMondayOfCurrentWeek();
                }
                populateFunctionDropdown(); // Call new function to populate function dropdown
            }
        }
    };

    // --- Event Listeners for Forms ---
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;

            try {
                const response = await fetch('/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username, password })
                });

                const result = await response.json();

                if (response.ok) {
                    showMessage(result.message, 'success');
                    window.location.href = result.redirect_url || "/index";
                } else {
                    showMessage(result.message || 'Login failed.', 'error');
                }
            } catch (error) {
                console.error('Error during login:', error);
                showMessage('Network error or server unreachable during login.', 'error');
            }
        });
    }

    window.setupAddEmployeeForm = function() {
        const addEmployeeForm = document.getElementById('add-employee-form');
        const newEmployeeNameInput = document.getElementById('new-employee-name');
        const newEmployeeEmailInput = document.getElementById('new-employee-email');
        const newEmployeeRoleInput = document.getElementById('new-employee-role');
        const addEmployeeMessageContainer = document.getElementById('add-employee-message-container');

        if (addEmployeeForm) {
            addEmployeeForm.addEventListener('submit', async (e) => {
                e.preventDefault();

                const name = newEmployeeNameInput.value.trim();
                const email = newEmployeeEmailInput.value.trim();
                const role = newEmployeeRoleInput.value.trim();

                if (!name || !email || !role) {
                    showMessage('Please fill in all employee fields.', 'error', addEmployeeMessageContainer);
                    return;
                }

                try {
                    const response = await fetch('/api/employees', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ name, email, role })
                    });

                    const result = await response.json();
                    if (response.ok) {
                        showMessage(result.message, 'success', addEmployeeMessageContainer);
                        addEmployeeForm.reset();
                        loadEmployees();
                        populateEmployeeDropdowns();
                    } else {
                        showMessage(`Error: ${result.message}`, 'error', addEmployeeMessageContainer);
                    }
                }
                catch (error) {
                    console.error('Error adding new employee:', error);
                    showMessage('An unexpected error occurred while adding employee. Please try again.', 'error', addEmployeeMessageContainer);
                }
            });
        }
    };

    window.setupAssignEmployeeForm = function() {
        const assignEmployeeForm = document.getElementById('assign-employee-form');
        const assignProjectNameInput = document.getElementById('assign-project-name');
        const assignProjectIdInput = document.getElementById('assign-project-id');
        const assignmentMessageContainer = document.getElementById('assignment-message-container');

        if (assignEmployeeForm) {
            assignEmployeeForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                const formData = new FormData(assignEmployeeForm);
                const assignmentData = Object.fromEntries(formData.entries());

                assignmentData.assigned_start_month = parseInt(assignmentData.assigned_start_month);
                assignmentData.assigned_start_year = parseInt(assignmentData.assigned_start_year);
                assignmentData.assigned_end_month = parseInt(assignmentData.assigned_end_month);
                assignmentData.assigned_end_year = parseInt(assignmentData.assigned_end_year);
                assignmentData.assigned_hours_per_week = parseInt(assignmentData.assigned_hours_per_week);
                assignmentData.employee_id = parseInt(assignmentData.employee_id);

                const projectName = assignProjectNameInput.value.trim();

                if (!assignmentData.project_id) {
                    const existingProjects = await fetchData('/api/projects', 'Error loading projects for new project check');
                    let matchedProject = null;

                    if (existingProjects) {
                        matchedProject = existingProjects.find(p => p.name.toLowerCase() === projectName.toLowerCase());
                    }

                    if (matchedProject) {
                        assignmentData.project_id = matchedProject.id;
                    } else {
                        showMessage(`Project "${projectName}" not found. Attempting to create new project...`, 'info', assignmentMessageContainer);
                        try {
                            const newProjectData = {
                                name: projectName,
                                start_month: assignmentData.assigned_start_month,
                                start_year: assignmentData.assigned_start_year,
                                end_month: assignmentData.assigned_end_month,
                                end_year: assignmentData.assigned_end_year,
                            };

                            const newProjectResponse = await fetch('/api/projects', {
                                method: 'POST',
                                headers: { 'Content-Type': 'application/json' },
                                body: JSON.stringify(newProjectData)
                            });

                            const newProjectResult = await newProjectResponse.json();

                            if (newProjectResponse.ok && newProjectResult.project_id) {
                                assignmentData.project_id = newProjectResult.project_id;
                                showMessage(`New project "${projectName}" created successfully!`, 'success', assignmentMessageContainer);
                                populateProjectDropdowns();
                                populateProjectDropdownsForActualHours();
                            } else {
                                throw new Error(newProjectResult.message || 'Failed to create new project.');
                            }
                        } catch (projectError) {
                            console.error('Error creating new project:', projectError);
                            showMessage(`Failed to create new project "${projectName}": ${projectError.message}.`, 'error', assignmentMessageContainer);
                            return;
                        }
                    }
                }

                if (!assignmentData.project_id) {
                    showMessage('Project ID could not be determined. Cannot assign employee.', 'error', assignmentMessageContainer);
                    return;
                }

                delete assignmentData.project_name;

                try {
                    const response = await fetch('/api/assign_employee', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(assignmentData)
                    });

                    const result = await response.json();
                    if (response.ok) {
                        showMessage(result.message, 'success', assignmentMessageContainer);
                        assignEmployeeForm.reset();
                        populateAllForms('assign_employee');
                        loadAssignments();
                        window.dispatchEvent(new Event('workloadUpdated'));
                    } else {
                        showMessage(`Error: ${result.message}`, 'error', assignmentMessageContainer);
                    }
                } catch (error) {
                    console.error('Error submitting assignment:', error);
                    showMessage('An unexpected error occurred during assignment. Please try again.', 'error', assignmentMessageContainer);
                }
            });
        }
    };

    window.setupRecordActualHoursForm = function() {
        const recordActualHoursForm = document.getElementById('record-actual-hours-form');
        const actualHoursEmployeeSelect = document.getElementById('actual-hours-employee-id');
        const actualHoursProjectSelect = document.getElementById('actual-hours-project-id');
        const functionSelect = document.getElementById('actual-hours-function-name'); // Updated ID here
        const actualWeekStartDateInput = document.getElementById('actual-week-start-date');
        const actualHoursWorkedInput = document.getElementById('actual-hours-worked');
        const actualHoursMessageContainer = document.getElementById('record-actual-hours-message-container'); // Corrected message container ID

        if (recordActualHoursForm) {
            recordActualHoursForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                const employeeId = actualHoursEmployeeSelect.value;
                const projectId = actualHoursProjectSelect.value;
                const functionName = functionSelect.value; // Get selected function name
                const weekStartDate = actualWeekStartDateInput.value;
                const actualHoursRaw = actualHoursWorkedInput.value; // Get raw value as string
                const parsedActualHours = parseInt(actualHoursRaw); // Attempt to parse

                // Enhanced client-side validation
                if (!employeeId || !projectId || !functionName || !weekStartDate || actualHoursRaw.trim() === '' || isNaN(parsedActualHours)) {
                    showMessage('Please ensure Employee, Project, Function, Week Start Date, and Hours Worked are all valid and filled with a number.', 'error', actualHoursMessageContainer);
                    return;
                }

                const dateObj = new Date(weekStartDate + 'T00:00:00Z');
                if (dateObj.getUTCDay() !== 1) {
                    showMessage('Week Start Date must be a Monday.', 'error', actualHoursMessageContainer);
                    return;
                }

                try {
                    const response = await fetch('/api/record_actual_hours', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            employee_id: parseInt(employeeId),
                            project_id: parseInt(projectId),
                            function_name: functionName, // Send the selected function name
                            week_start_date: weekStartDate,
                            hours_worked: parsedActualHours // Use hours_worked here as per backend
                        }),
                    });

                    const result = await response.json();
                    if (response.ok) {
                        showMessage(result.message, 'success', actualHoursMessageContainer);
                        recordActualHoursForm.reset();
                        actualWeekStartDateInput.value = getMondayOfCurrentWeek();
                        loadActualHoursReport(); // Call loadActualHoursReport after recording to refresh the table
                        window.dispatchEvent(new Event('workloadUpdated'));
                    } else {
                        showMessage(`Error: ${result.message}`, 'error', actualHoursMessageContainer);
                    }
                } catch (error) {
                    console.error('Error saving actual weekly hours:', error);
                    showMessage('An unexpected error occurred while saving actual hours. Please try again.', 'error', actualHoursMessageContainer);
                }
            });
        }
    };

    // --- Workload, Assignments, Actual Hours Loading (Includes search term parameter) ---

    // Function to load and display current workload (no change to loadWorkload itself yet, depends on backend)
    window.loadWorkload = async function() {
        const workloadContainer = document.getElementById('workload-container');
        if (!workloadContainer) return;

        const employees = await fetchData('/api/employees', 'Error loading workload data (expected structured workload)');

        if (employees) {
            workloadContainer.innerHTML = '';
            if (employees.length > 0) {
                const normalHours = 40;
                let tableHtml = `
                    <h3>Current Workload Overview (Employee List Only)</h3>
                    <p><i>Note: Full workload calculations require the /api/employee_workload endpoint in app.py.</i></p>
                    <div class="workload-summary">
                        <div class="summary-box">Standard Weekly Hours: ${normalHours}</div>
                    </div>
                    <table id="employee-workload-table">
                        <thead>
                            <tr>
                                <th>Employee Name</th>
                                <th>Position</th>
                                <th>Email</th>
                            </tr>
                        </thead>
                        <tbody>
                `;

                employees.forEach(employee => {
                    const row = document.createElement('tr');
                    row.insertCell().textContent = employee.name;
                    row.insertCell().textContent = employee.role || 'N/A';
                    row.insertCell().textContent = employee.email || 'N/A';
                    // Append row to a temporary tbody to avoid reflows
                    const tempTbody = document.createElement('tbody');
                    tempTbody.appendChild(row);
                    tableHtml += tempTbody.innerHTML;
                });

                tableHtml += `
                        </tbody>
                    </table>
                `;
                workloadContainer.innerHTML = tableHtml;
            } else {
                workloadContainer.innerHTML = '<p>No employees found to display workload overview.</p>';
            }
        }
    };

    // Function to load and display monthly workload (no change here)
    window.loadMonthlyWorkload = async function() {
        const monthlyWorkloadTable = document.getElementById('monthly-workload-table');
        if (!monthlyWorkloadTable) return;

        const monthlyStartMonth = document.getElementById('monthly-start-month')?.value;
        const monthlyStartYear = document.getElementById('monthly-start-year')?.value;
        const monthlyNumMonths = document.getElementById('monthly-num-months')?.value;

        if (!monthlyStartMonth || !monthlyStartYear || !monthlyNumMonths) {
            showMessage("Please select a Start Month and enter valid Start Year and Number of Months.", "error");
            return;
        }

        const startYear = parseInt(monthlyStartYear);
        const numMonths = parseInt(monthlyNumMonths);

        if (isNaN(startYear) || startYear < 2000 || startYear > 2100) {
            showMessage("Please enter a valid Start Year (e.g., 2024).", "error");
            return;
        }
        if (isNaN(numMonths) || numMonths < 1 || numMonths > 36) {
            showMessage("Please enter a valid Number of Months (1-36).", "error");
            return;
        }

        // Monthly workload also accepts search term if applicable (though less common for aggregated report)
        // For now, it will only filter employees on backend.
        const monthlyWorkloadSearchInput = document.getElementById('monthly-workload-search-input'); // Assuming you might add this later
        const searchTerm = monthlyWorkloadSearchInput ? monthlyWorkloadSearchInput.value.trim() : '';

        const url = `/api/monthly_workload?start_month=${monthlyStartMonth}&start_year=${startYear}&num_months=${numMonths}&q=${encodeURIComponent(searchTerm)}`;
        const monthlyWorkloadData = await fetchData(url, 'Error loading monthly workload data');

        const tableHead = monthlyWorkloadTable.querySelector('thead');
        const tableBody = monthlyWorkloadTable.querySelector('tbody');
        const normalHoursDisplay = document.getElementById('monthly-normal-hours');

        if (monthlyWorkloadData && monthlyWorkloadData.employee_monthly_load && monthlyWorkloadData.months) {
            const normalHours = monthlyWorkloadData.normal_hours || 40;
            if (normalHoursDisplay) normalHoursDisplay.textContent = normalHours;

            tableHead.innerHTML = '';
            tableBody.innerHTML = '';

            let headerRow = `<tr><th style="min-width: 150px;">Employee Name</th><th style="min-width: 120px;">Position</th>`;
            monthlyWorkloadData.months.forEach(month => {
                headerRow += `<th style="min-width: 100px;">${month}</th>`;
            });
            headerRow += `</tr>`;
            tableHead.innerHTML = headerRow;

            if (monthlyWorkloadData.employee_monthly_load.length === 0) {
                tableBody.innerHTML = `<tr><td colspan="${monthlyWorkloadData.months.length + 2}">No monthly workload data found.</td></tr>`;
                return;
            }

            monthlyWorkloadData.employee_monthly_load.forEach(employeeData => {
                let rowHtml = `<tr><td>${employeeData.employee.name}</td><td>${employeeData.employee.role || 'N/A'}</td>`;
                monthlyWorkloadData.months.forEach(monthLabel => {
                    const monthLoad = employeeData.monthly_loads.find(m => m.month_year === monthLabel);
                    let displayValue = 'N/A';
                    let cellClass = '';
                    let percentage = 0;

                    if (monthLoad) {
                        displayValue = `${monthLoad.load}`;
                        percentage = monthLoad.load_percentage;

                        if (monthLoad.load === normalHours) {
                            cellClass = 'cell-normal';
                        } else if (monthLoad.load > normalHours) {
                            cellClass = 'cell-overloaded';
                        } else {
                            cellClass = 'cell-free';
                        }
                        displayValue += ` (${percentage.toFixed(0)}%)`;
                    }
                    rowHtml += `<td class="${cellClass}">${displayValue}</td>`;
                });
                rowHtml += `</tr>`;
                tableBody.innerHTML += rowHtml;
            });
        } else {
            tableBody.innerHTML = `<tr><td colspan="2">Failed to load monthly workload data.</td></tr>`;
        }
    };

    // Function to load and display assignments (Includes search term parameter)
    window.loadAssignments = async function(searchTerm = '') { // Added searchTerm parameter
        const assignmentsTableBody = document.getElementById('assignments-table')?.querySelector('tbody');
        if (!assignmentsTableBody) return;

        const assignments = await fetchData('/api/employee_project_assignments', 'Error loading assignments', searchTerm); // Pass searchTerm

        if (assignments) {
            assignmentsTableBody.innerHTML = '';
            const hasAssignments = assignments.some(empData =>
                empData.projects && empData.projects.length > 0
            );

            if (!hasAssignments) {
                assignmentsTableBody.innerHTML = '<tr><td colspan="6">No assignments found.</td></tr>';
                return;
            }

            assignments.forEach(empData => { // Iterate directly over the array of employee data
                if (empData.projects && empData.projects.length > 0) {
                    empData.projects.forEach(p => {
                        const row = assignmentsTableBody.insertRow();
                        row.insertCell().textContent = empData.employee.name;
                        row.insertCell().textContent = p.project_name;
                        row.insertCell().textContent = p.hours_per_week;
                        row.insertCell().textContent = p.assigned_start;
                        row.insertCell().textContent = p.assigned_end;
                        const actionsCell = row.insertCell();
                        actionsCell.innerHTML = `<button class="action-button edit-button" data-id="${p.assignment_id}">Edit</button> <button class="action-button delete-button" data-id="${p.assignment_id}">Delete</button>`;
                    });
                }
            });
        }
    };

    // NEW FUNCTION: Load and display the Excel-like Actual Hours Report
    window.loadActualHoursReport = async function(searchTerm = '') {
        const actualHoursReportTable = document.getElementById('actual-weekly-report-table');
        if (!actualHoursReportTable) return;

        // Ensure the table container handles horizontal overflow
        const tableContainer = actualHoursReportTable.closest('.excel-like-table-container');
        if (tableContainer) {
            tableContainer.style.overflowX = 'auto';
        }

        // Clear existing table content
        const tableHead = actualHoursReportTable.querySelector('thead');
        const tableBody = actualHoursReportTable.querySelector('tbody');
        tableBody.innerHTML = '<tr><td colspan="4" style="text-align: center;">Loading report data...</td></tr>'; // Reset loading message

        const allWeeklyHours = await fetchData('/api/weekly_hours', 'Error loading actual hours report', searchTerm);

        if (!allWeeklyHours || allWeeklyHours.length === 0) {
            tableBody.innerHTML = '<tr><td colspan="4" style="text-align: center;">No actual hours recorded for the report.</td></tr>';
            return;
        }

        const normalHoursPerWeek = 40; // Define normal weekly hours for status calculation

        // --- Data Aggregation and Transformation ---
        const groupedByEmployee = {};
        allWeeklyHours.forEach(entry => {
            if (!groupedByEmployee[entry.employee_name]) {
                groupedByEmployee[entry.employee_name] = {
                    employee_id: entry.employee_id,
                    uniqueProjects: new Set(),
                    uniqueFunctions: new Set(),
                    weeklyTotals: {}, // Store total hours per week for this employee
                    details: {} // Store details for each project-function combination
                };
            }

            const employeeData = groupedByEmployee[entry.employee_name];
            employeeData.uniqueProjects.add(entry.project_name);
            employeeData.uniqueFunctions.add(entry.function_name || 'N/A');

            // Aggregate weekly totals for the employee
            employeeData.weeklyTotals[entry.week_start_date] = (employeeData.weeklyTotals[entry.week_start_date] || 0) + entry.hours_worked;

            // Store detailed hours
            const detailKey = `${entry.project_name}|${entry.function_name || 'N/A'}`;
            if (!employeeData.details[detailKey]) {
                employeeData.details[detailKey] = {
                    project_name: entry.project_name,
                    function_name: entry.function_name || 'N/A',
                    hours_by_week: {}
                };
            }
            employeeData.details[detailKey].hours_by_week[entry.week_start_date] = entry.hours_worked;
        });

        // Collect all unique week start dates across all data to form dynamic headers
        let allWeekStartDates = new Set();
        allWeeklyHours.forEach(entry => allWeekStartDates.add(entry.week_start_date));
        allWeekStartDates = Array.from(allWeekStartDates).sort(); // Sort dates chronologically

        // --- Table Header Generation ---
        // Clear both header rows
        tableHead.innerHTML = '';

        const headerRow1 = tableHead.insertRow();
        const headerRow2 = tableHead.insertRow(); // This row will contain nothing or sub-headers if implemented later

        // Static headers with rowspan for the first row
        const sNoTh = document.createElement('th');
        sNoTh.textContent = 'S.No.';
        sNoTh.rowSpan = 2;
        headerRow1.appendChild(sNoTh);

        const employeeNameTh = document.createElement('th');
        employeeNameTh.textContent = 'Employee Name';
        employeeNameTh.rowSpan = 2;
        headerRow1.appendChild(employeeNameTh);

        const projectNameTh = document.createElement('th');
        projectNameTh.textContent = 'Project Name';
        projectNameTh.rowSpan = 2;
        headerRow1.appendChild(projectNameTh);

        const functionTh = document.createElement('th');
        functionTh.textContent = 'Function';
        functionTh.rowSpan = 2;
        headerRow1.appendChild(functionTh);
        
        // Add dynamic week headers
        allWeekStartDates.forEach(weekDate => {
            const startDate = new Date(weekDate + 'T00:00:00Z'); // Ensure UTC or local consistency
            const endDate = new Date(startDate);
            endDate.setDate(startDate.getDate() + 6);

            const monthFormatter = new Intl.DateTimeFormat('en-US', { month: 'short' });
            const weekNumber = getWeekNumber(startDate);

            const formattedWeekHeader = `WK${weekNumber} (${monthFormatter.format(startDate)} ${startDate.getDate()} - ${monthFormatter.format(endDate)} ${endDate.getDate()})`;

            const weekTh = document.createElement('th');
            weekTh.textContent = formattedWeekHeader;
            weekTh.colSpan = 1; // Or 2 if you add Hours/Status sub-headers
            headerRow1.appendChild(weekTh);
        });

        // --- Table Body Population ---
        tableBody.innerHTML = '';
        let sNo = 1;
        for (const employeeName in groupedByEmployee) {
            const empData = groupedByEmployee[employeeName];

            // 1. Employee Summary Row (Bolded)
            const summaryRow = tableBody.insertRow();
            summaryRow.classList.add('summary-row'); // Add class for styling from CSS

            summaryRow.insertCell().innerHTML = `<b>${sNo++}.</b>`;
            summaryRow.insertCell().innerHTML = `<b>${employeeName}</b>`;
            summaryRow.insertCell().innerHTML = `<b>${empData.uniqueProjects.size} Projects</b>`; // Count of unique projects
            summaryRow.insertCell().innerHTML = `<b>${empData.uniqueFunctions.size} Functions</b>`; // Count of unique functions

            allWeekStartDates.forEach(weekDate => {
                const totalHours = empData.weeklyTotals[weekDate] || 0;
                const cell = summaryRow.insertCell();
                cell.innerHTML = `<b>${totalHours}</b>`; // Display total hours
                cell.classList.add('summary-total-cell'); // Add a class for specific styling

                // Add status class based on total hours
                if (totalHours > normalHoursPerWeek) {
                    cell.classList.add('cell-overloaded');
                } else if (totalHours < normalHoursPerWeek && totalHours > 0) {
                    cell.classList.add('cell-free'); // 'Free' or 'Underloaded'
                } else if (totalHours === normalHoursPerWeek) {
                    cell.classList.add('cell-normal');
                } else if (totalHours === 0) {
                     cell.classList.add('cell-zero'); // Custom class for zero hours, if you want specific styling
                }
            });

            // 2. Detailed Rows for each Project-Function combination
            // Sort details for consistent display (e.g., by project name, then function name)
            const sortedDetailKeys = Object.keys(empData.details).sort(); // Sorts by combined key for consistency

            sortedDetailKeys.forEach(detailKey => {
                const detail = empData.details[detailKey];
                const detailRow = tableBody.insertRow();
                detailRow.classList.add('detail-row'); // Add class for styling

                detailRow.insertCell(); // Empty for S.No.
                detailRow.insertCell(); // Empty for Employee Name
                detailRow.insertCell().textContent = detail.project_name;
                detailRow.insertCell().textContent = detail.function_name;

                allWeekStartDates.forEach(weekDate => {
                    const hours = detail.hours_by_week[weekDate] !== undefined ? detail.hours_by_week[weekDate] : '';
                    const cell = detailRow.insertCell();
                    cell.textContent = hours;
                    cell.classList.add('detail-hours-cell'); // Add a class for specific styling
                    if (hours === 0 || hours === '') {
                        cell.classList.add('cell-zero-detail'); // Apply a class if you want specific styling for empty/zero detail cells
                    }
                });
            });

            // 3. Add a spacer row after each employee group (except the last one)
            if (employeeName !== Object.keys(groupedByEmployee)[Object.keys(groupedByEmployee).length - 1]) {
                const spacerRow = tableBody.insertRow();
                spacerRow.classList.add('spacer-row'); // Apply CSS for visual spacing
                const spacerCell = spacerRow.insertCell();
                spacerCell.colSpan = 4 + allWeekStartDates.length; // Span across all columns
            }
        }

        // If after filtering/grouping, no data remains, display a message
        if (Object.keys(groupedByEmployee).length === 0) {
            tableBody.innerHTML = '<tr><td colspan="4" style="text-align: center;">No actual hours recorded matching your search.</td></tr>';
        }

        // Helper function to get week number (ISO Week Date)
        // This is a common implementation, you might need to adjust for specific week numbering conventions
        function getWeekNumber(d) {
            // Copy date so don't modify original
            d = new Date(Date.UTC(d.getFullYear(), d.getMonth(), d.getDate()));
            // Set to nearest Thursday: current date + 4 - current day number
            // Make Sunday's day number 7
            d.setUTCDate(d.getUTCDate() + 4 - (d.getUTCDay() || 7));
            // Get first day of year
            var yearStart = new Date(Date.UTC(d.getUTCFullYear(), 0, 1));
            // Calculate full weeks to nearest Thursday
            var weekNo = Math.ceil((((d - yearStart) / 86400000) + 1) / 7);
            return weekNo;
        }
    };


    // Listen for custom event to refresh workload data (global event, triggered after assignment/actual hours)
    window.addEventListener('workloadUpdated', loadWorkload);

    // --- Master Initialization Logic on DOMContentLoaded (Attaches search listeners) ---
    highlightNavLink();

    const currentPath = window.location.pathname;

    switch (currentPath) {
        case '/members':
            loadEmployees();
            setupAddEmployeeForm();
            // NEW: Add search listener for employees
            const employeeSearchInput = document.getElementById('employee-search-input');
            const employeeSearchBtn = document.getElementById('employee-search-btn');
            if (employeeSearchBtn && employeeSearchInput) {
                employeeSearchBtn.addEventListener('click', () => {
                    loadEmployees(employeeSearchInput.value.trim());
                });
                employeeSearchInput.addEventListener('keypress', (e) => {
                    if (e.key === 'Enter') {
                        loadEmployees(employeeSearchInput.value.trim());
                    }
                });
            }
            break;
        case '/projects':
            loadProjects();
            // NEW: Add search listener for projects
            const projectSearchInput = document.getElementById('project-search-input');
            const projectSearchBtn = document.getElementById('project-search-btn');
            if (projectSearchBtn && projectSearchInput) {
                projectSearchBtn.addEventListener('click', () => {
                    loadProjects(projectSearchInput.value.trim());
                });
                projectSearchInput.addEventListener('keypress', (e) => {
                    if (e.key === 'Enter') {
                        loadProjects(projectSearchInput.value.trim());
                    }
                });
            }
            break;
        case '/assignments':
            populateAllForms('assign_employee');
            setupAssignEmployeeForm();
            loadAssignments();
            // NEW: Add search listener for assignments (Assuming you'll add an input/button for it)
            const assignmentSearchInput = document.getElementById('assignment-search-input');
            const assignmentSearchBtn = document.getElementById('assignment-search-btn');
            if (assignmentSearchBtn && assignmentSearchInput) {
                assignmentSearchBtn.addEventListener('click', () => {
                    loadAssignments(assignmentSearchInput.value.trim());
                });
                assignmentSearchInput.addEventListener('keypress', (e) => {
                    if (e.key === 'Enter') {
                        loadAssignments(assignmentSearchInput.value.trim());
                    }
                });
            }
            break;
        case '/workload_current':
            populateAllForms('assign_employee');
            populateAllForms('actual_hours');
            loadWorkload();
            setupAddEmployeeForm();
            setupAssignEmployeeForm();
            setupRecordActualHoursForm();
            break;
        case '/actual_hours':
            populateAllForms('actual_hours');
            setupRecordActualHoursForm();
            loadActualHoursReport(); // Call loadActualHoursReport on page load
            // NEW: Add search listener for actual hours report (Updated IDs)
            const reportSearchInput = document.getElementById('actual-hours-search-input'); // Corrected ID
            const reportSearchBtn = document.getElementById('actual-hours-search-btn'); // Corrected ID
            if (reportSearchBtn && reportSearchInput) {
                reportSearchBtn.addEventListener('click', () => {
                    loadActualHoursReport(reportSearchInput.value.trim());
                });
                reportSearchInput.addEventListener('keypress', (e) => {
                    if (e.key === 'Enter') {
                        loadActualHoursReport(reportSearchInput.value.trim());
                    }
                });
            }
            break;
        case '/monthly_workload':
            populateMonthlyDateInputs();
            const loadMonthlyWorkloadBtn = document.getElementById('load-monthly-workload-btn');
            if (loadMonthlyWorkloadBtn) {
                loadMonthlyWorkloadBtn.addEventListener('click', loadMonthlyWorkload);
            }
            // NEW: Add search listener for monthly workload (assuming you'll add an input/button for it)
            const monthlyWorkloadSearchInput = document.getElementById('monthly-workload-search-input');
            const monthlyWorkloadSearchBtn = document.getElementById('monthly-workload-search-btn');
            if (monthlyWorkloadSearchBtn && monthlyWorkloadSearchInput) {
                monthlyWorkloadSearchBtn.addEventListener('click', () => {
                    loadMonthlyWorkload(monthlyWorkloadSearchInput.value.trim()); // Pass search term
                });
                monthlyWorkloadSearchInput.addEventListener('keypress', (e) => {
                    if (e.key === 'Enter') {
                        loadMonthlyWorkload(monthlyWorkloadSearchInput.value.trim()); // Pass search term
                    }
                });
            }
            break;
        case '/export_data':
            // No specific JS to load on this page, as buttons have onclick events
            break;
            // NEW ADDITION START: Handling for the new import page
    case '/import_data':
        const importForm = document.getElementById('import-excel-form');
        const importMessageContainer = document.getElementById('import-message-container');

        if (importForm) {
            importForm.addEventListener('submit', async function(event) {
                event.preventDefault(); // Prevent default form submission

                const formData = new FormData(importForm); // Get form data, including the file

                showMessage('Uploading and importing data...', 'info', importMessageContainer);

                try {
                    const response = await fetch('/api/import_data', {
                        method: 'POST',
                        body: formData // Send FormData directly for file uploads
                    });

                    const result = await response.json();

                    if (response.ok) {
                        showMessage(result.message, 'success', importMessageContainer);
                        if (result.errors && result.errors.length > 0) {
                            // Display specific errors if any
                            result.errors.forEach(error => {
                                showMessage(`- ${error}`, 'error', importMessageContainer); // Format error for better readability
                            });
                        }
                        importForm.reset(); // Clear the form after successful upload
                        // Potentially reload relevant tables after import
                        // These window.load... and window.populate... functions might not exist on every page.
                        // The `&&` operator ensures they are only called if they are defined.
                        if (formData.get('data_type') === 'employees') {
                            window.loadEmployees && window.loadEmployees();
                            window.populateEmployeeDropdowns && window.populateEmployeeDropdowns();
                        } else if (formData.get('data_type') === 'projects') {
                            window.loadProjects && window.loadProjects();
                            window.populateProjectDropdowns && window.populateProjectDropdowns();
                            window.populateProjectDropdownsForActualHours && window.populateProjectDropdownsForActualHours();
                        } else if (formData.get('data_type') === 'actual_hours_bulk') {
                            window.loadActualHoursReport && window.loadActualHoursReport();
                            window.loadMonthlyWorkload && window.loadMonthlyWorkload(); // May affect monthly workload
                        }
                        window.dispatchEvent(new Event('workloadUpdated')); // Trigger global workload update
                    } else {
                        showMessage(result.message || 'An error occurred during import.', 'error', importMessageContainer);
                    }
                } catch (error) {
                    console.error('Error during import:', error);
                    showMessage('Network error or server unavailable.', 'error', importMessageContainer);
                }
            });
        }
        break; // End of /import_data case
    // NEW ADDITION END
        default:
            break;
    }
});
