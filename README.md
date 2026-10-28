# CareerCampus AI 🎓

> **An Intelligent Student Career Development Platform powered by scikit-learn Machine Learning, Streamlit, and Plotly.**

CareerCampus AI is an offline, privacy-first career development platform designed for computer science and engineering students. It uses a trained **scikit-learn `DecisionTreeClassifier`** for career-path prediction, provides multi-dimensional **skill gap analysis**, generates a personalized **7-day sprint learning roadmap**, offers an interactive **12-MCQ coding & aptitude diagnostic quiz**, analyzes resumes via an **ATS keyword extractor** (supporting PDF and TXT), and calculates **mathematical job-role fit** via cosine similarity and weighted overlap.

---

## 🌟 Key Features

1. **Student Profile & Education Tracker**: Captures student credentials, graduation timeline, primary career aspirations, and self-assessed competencies with input validation and instant demo pre-fill.
2. **Multi-Domain Skill Assessment**: Evaluates proficiencies across Python, Java, Data Structures & Algorithms (DSA), Mathematics & Statistics, Communication, and Analytical Problem Solving (0–100 scale).
3. **Interactive Visualizations & Readiness Metrics**: Composite weighted readiness score with performance tier badge, interactive Plotly Spider/Radar chart, and competency distribution bar charts.
4. **Machine Learning Career Prediction**: Real scikit-learn `DecisionTreeClassifier` trained on local student benchmark data (`dataset.csv`). Provides class probability distributions, model confidence, top alternative career tracks, and transparent feature importances.
5. **Skill Gap Analysis**: Compares current student scores against target job role thresholds with interactive delta charts highlighting surplus skills, minor gaps, and critical deficits.
6. **Personalized 7-Day Sprint Roadmap**: Curates a daily step-by-step upskilling sprint targeting the student's weakest skills, complete with daily objectives, coding tasks, deliverables, and estimated hours.
7. **Diagnostic Coding & Aptitude Quiz**: 12 local MCQs covering Python, Java, DSA, Math, and Problem Solving with instant scoring, performance tiers, technical explanations, and one-click profile skill calibrations.
8. **Resume ATS Keyword Analyzer**: Robust TXT and PDF text extraction using `pypdf`, skill taxonomy mapping, keyword coverage percentage against target job roles, action verb count, and actionable ATS optimization advice.
9. **Job-Role Skill Overlap Matcher**: Mathematical cosine similarity and weighted point overlap calculated against local benchmark roles (`job_roles.csv`). Displays compatibility badges and skill requirement breakdowns.
10. **Exportable Career Development Reports**: Instant one-click download of comprehensive reports in plain-text (`.txt`) and structured tabular (`.csv`) formats.
11. **Session State Progress Tracker**: Persistent milestone tracker without requiring any external databases or cloud services.
12. **Demo Mode & Feedback**: One-click demo profile ("Alex Chen"), reset button, and interactive user feedback rating form.

---

## 📁 Project Structure

```text
CareerCampusAI/
│
├── dataset.csv                  # 120 verified student profiles for ML training
├── job_roles.csv                # Benchmark job roles and target skill thresholds
├── quiz_data.json               # 12 coding & aptitude MCQs with explanations
├── requirements.txt             # Project dependencies
├── README.md                    # Documentation & run instructions
│
├── backend/
│   ├── __init__.py
│   ├── ml_engine.py             # DecisionTreeClassifier training, inference & explanations
│   ├── skill_analysis.py        # Readiness calculation, skill gap analysis & Plotly charts
│   ├── roadmap_generator.py     # Personalized 7-day learning sprint generator
│   ├── resume_parser.py         # PDF/TXT extraction, taxonomy matching & ATS analysis
│   ├── job_matcher.py           # Cosine similarity & weighted overlap job matching
│   ├── quiz_engine.py           # Quiz evaluation, scoring & skill calibrations
│   └── report_generator.py      # Downloadable TXT & CSV report generator
│
├── tests/
│   ├── __init__.py
│   └── test_backend.py          # Complete automated test suite (11 unit tests)
│
└── app.py                       # Polished Streamlit web dashboard application
```

---

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.10+ (Tested on Python 3.13)
- Windows / macOS / Linux

### 1. Clone or Navigate to Project Directory
```powershell
cd "C:\Users\mahas\.gemini\antigravity\scratch\CareerCampusAI"
```

### 2. Create and Activate Virtual Environment
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies
```powershell
pip install -r requirements.txt
```

---

## 🧪 Running Automated Tests

Run the backend test suite:
```powershell
python -m unittest tests/test_backend.py -v
```
All 11 tests verify:
- Scikit-learn model training, cross-validation, and inference
- Skill gap delta calculations and Plotly figure generation
- 7-day sprint roadmap generation
- PDF and TXT resume text extraction, taxonomy matching, and error handling
- Cosine similarity and weighted job matching
- Quiz scoring, feedback, and calibrations
- TXT and CSV report generation

---

## 🚀 Launching the Web Application

To run the interactive Streamlit dashboard:

```powershell
streamlit run app.py
```

Or using python directly:
```powershell
python -m streamlit run app.py
```

Once launched, access the platform in your browser at:
`http://localhost:8501`

---

## 🔒 Offline & Privacy Guarantee

- **Zero Cloud Calls**: Runs 100% locally on your machine.
- **No API Keys**: Does not require OpenAI, Google Cloud, or third-party paid services.
- **No Database Setup**: Leverages Streamlit session state and local CSV/JSON files.
- **Lightweight**: Entire source codebase is under 150 KB.
