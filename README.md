# MiC Dynamic Scheduler V9.5

A Streamlit-based dynamic scheduling system for Modular Integrated Construction (MiC) projects, integrating K-Means clustering, NSGA-II multi-objective optimization, and Rolling Horizon strategies.

## 1. Project Overview
This project is developed for CIVIL 6060 - Project III, aiming to optimize the dynamic scheduling of MiC projects by considering resource constraints, weather risks, and emergency tasks. The core features include task clustering, multi-objective optimization, and rolling horizon-based task adjustment.

## 2. Key Features
- K-Means clustering for task grouping (spatial coordinates, resource demand, urgency, system type)
- NSGA-II multi-objective optimization (minimize cost, risk, and project delay)
- Rolling Horizon strategy with task preemption and splitting
- Excel-based data input/output (template generation, data parsing, report export)
- Weather risk integration (Hong Kong monthly weather risk factors)
- Resource constraint management (labor, equipment, tools)
- Emergency task handling with priority adjustment

## 3. Installation
### 3.1 Clone the Repository
```bash
git clone https://github.com/yw35561-wq/Mic_Scheduler.git
cd Mic_Scheduler

### 3.2 Install Dependencies
pip install -r requirements.txt

## 4. Quick Start
### 4.1 Run the application:

### 4.2 Access the web app in your browser:

### 4.3 Workflow:
Download the Excel input template from the web page
Fill in task/resource/emergency data in the template
Upload the filled template to the app
Initialize the scheduling model and generate optimized schedules

## 5. Project Structure
mic_scheduler/
├── config/          # Core configuration (cost, resource, algorithm parameters)
├── core/            # Scheduling engine (ProjectModel, optimization logic)
├── io/              # Excel file handling (template generation, data parsing)
├── utils/           # Helper functions (risk calculation, time handling, cycle detection)
├── web/             # Streamlit web interface (page layout, user interaction)
├── requirements.txt # Python dependencies list
├── run.py           # Application entry point (one-click start)
└── README.md        # Project documentation

## 6. Technical Stack

Frontend/Interaction: Streamlit
Data Processing: Pandas, NumPy
Machine Learning: Scikit-learn (K-Means)
Visualization: Plotly
File Handling: XlsxWriter, OpenPyXL

## 7. Academic Use
This project is developed for academic purposes only (CIVIL 6060 - Project III).


