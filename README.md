# decorator

A simple routing & validation utility for civic issue reporting.

---

## Description

This project allows users to submit reports of civic issues (via image + description). The report is validated, classified, and routed to the the appropriate department.

---

## Features

- Validate user-submitted reports  
- Classify complaint into categories  
- Route complaint to the appropriate department  
- Configurable via JSON files (`categories.json`, `departments.json`)  

---

## Architecture

1. **Validation**  
   The `ReportValidator` checks whether the input (image URL + description) meets basic criteria.  
2. **Classification / Routing**  
   The `CivicIssueRouter` (or `ReportRouter`) reads from configuration files to map the complaint to the correct department.  
3. **Main Application**  
   The CLI in `main.py` ties validation + routing together to run the “report” workflow.

---



