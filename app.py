"""CareerCampus AI - Intelligent Student Career Development Platform
Main Streamlit Application.
"""

from __future__ import annotations

import io
import os
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Backend modules
from backend.ml_engine import get_career_predictor, CareerPredictor
from backend.skill_analysis import (
    calculate_overall_readiness,
    analyze_skill_gaps,
    create_radar_chart,
    create_gap_bar_chart,
    create_skill_bars_chart,
    SKILL_DISPLAY_NAMES,
)
from backend.roadmap_generator import generate_7day_roadmap
from backend.resume_parser import extract_text_from_file, analyze_resume_text
from backend.job_matcher import load_job_roles, match_job_roles
from backend.quiz_engine import load_quiz_questions, evaluate_quiz
from backend.report_generator import generate_txt_report, generate_csv_report

# ==========================================
# PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="CareerCampus AI | Career Development Platform",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling for Sleek, Professional UI
st.markdown("""
<style>
    /* Metric Card Styling */
    div[data-testid="stMetric"] {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 14px 18px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    div[data-testid="stMetric"]:hover {
        border-color: #6366F1;
        transition: all 0.2s ease-in-out;
    }
    /* Section Card Containers */
    .feature-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 1px 4px rgba(0,0,0,0.04);
    }
    .badge {
        display: inline-block;
        padding: 4px 12px;
        font-size: 12px;
        font-weight: 600;
        border-radius: 9999px;
        margin-right: 6px;
    }
    .badge-success { background: #ECFDF5; color: #065F46; border: 1px solid #A7F3D0; }
    .badge-info { background: #EFF6FF; color: #1E40AF; border: 1px solid #BFDBFE; }
    .badge-warning { background: #FFFBEB; color: #92400E; border: 1px solid #FDE68A; }
    .badge-danger { background: #FEF2F2; color: #991B1B; border: 1px solid #FECACA; }
    
    /* Disclaimer banner */
    .disclaimer-box {
        font-size: 11.5px;
        color: #64748B;
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 10px 14px;
        margin-top: 15px;
    }
</style>
""", unsafe_allow_html=True)


# ==========================================
# SESSION STATE INITIALIZATION
# ==========================================
def initialize_session():
    """Initializes all session state keys with default values."""
    default_skills = {
        "python": 75.0,
        "java": 55.0,
        "dsa": 70.0,
        "mathematics": 72.0,
        "communication": 68.0,
        "problem_solving": 74.0,
    }

    if "profile" not in st.session_state:
        st.session_state.profile = {
            "name": "Jane Doe",
            "degree": "B.S. in Computer Science",
            "college": "Tech Institute",
            "grad_year": "2026",
            "primary_interest": "AI & Machine Learning",
        }

    if "skills" not in st.session_state:
        st.session_state.skills = default_skills.copy()

    if "milestones" not in st.session_state:
        st.session_state.milestones = {
            "profile_completed": True,
            "skills_assessed": True,
            "ml_prediction_run": False,
            "skill_gap_analyzed": False,
            "quiz_completed": False,
            "resume_analyzed": False,
            "roadmap_generated": False,
        }

    if "quiz_answers" not in st.session_state:
        st.session_state.quiz_answers = {}

    if "quiz_results" not in st.session_state:
        st.session_state.quiz_results = None

    if "quiz_submitted" not in st.session_state:
        st.session_state.quiz_submitted = False

    if "feedback_submitted" not in st.session_state:
        st.session_state.feedback_submitted = False

    if "resume_analysis" not in st.session_state:
        st.session_state.resume_analysis = None

    if "target_role_selected" not in st.session_state:
        st.session_state.target_role_selected = "Machine Learning Engineer"


initialize_session()


# Helper: Load Demo Profile
def load_demo_profile():
    st.session_state.profile = {
        "name": "Alex Chen",
        "degree": "B.Tech Computer Science & AI",
        "college": "California Institute of Technology",
        "grad_year": "2026",
        "primary_interest": "AI & Machine Learning",
    }
    st.session_state.skills = {
        "python": 92.0,
        "java": 62.0,
        "dsa": 86.0,
        "mathematics": 88.0,
        "communication": 72.0,
        "problem_solving": 85.0,
    }
    st.session_state.target_role_selected = "Machine Learning Engineer"
    st.session_state.milestones["profile_completed"] = True
    st.session_state.milestones["skills_assessed"] = True
    st.toast("⚡ Demo Profile 'Alex Chen' successfully loaded!", icon="🚀")


# Helper: Reset Profile
def reset_to_defaults():
    st.session_state.clear()
    initialize_session()
    st.toast("🔄 System state reset to default configuration.", icon="🧹")


# Calculate Progress Metrics
def get_completion_pct() -> int:
    milestones = st.session_state.milestones
    total = len(milestones)
    done = sum(1 for v in milestones.values() if v)
    return int((done / total) * 100)


# ==========================================
# SIDEBAR NAVIGATION & CONTROLS
# ==========================================
with st.sidebar:
    st.image(
        "https://api.iconify.design/lucide:graduation-cap.svg?color=%236366f1",
        width=46,
    )
    st.title("CareerCampus AI")
    st.caption("Intelligent Student Career Development")

    st.markdown("---")

    nav_selection = st.radio(
        "Navigation Menu",
        [
            "🏠 Dashboard Overview",
            "👤 Profile & Skills",
            "🤖 AI Career Predictor",
            "🎯 Skill Gap & 7-Day Sprint",
            "📝 Coding & Aptitude Quiz",
            "📄 Resume ATS Analyzer",
            "💼 Job Role Matcher",
            "📥 Career Report & Progress",
        ],
        index=0,
    )

    st.markdown("---")

    # Platform Progress Bar
    comp_pct = get_completion_pct()
    st.write(f"**Platform Progress: {comp_pct}%**")
    st.progress(comp_pct / 100)

    # Demo & Reset Action Buttons
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("⚡ Demo Mode", use_container_width=True, help="Load Alex Chen's sample profile"):
            load_demo_profile()
            st.rerun()
    with col_btn2:
        if st.button("🔄 Reset", use_container_width=True, help="Clear all inputs and session state"):
            reset_to_defaults()
            st.rerun()

    st.markdown("---")
    st.markdown(
        """
        <div class="disclaimer-box">
            <b>Offline Platform Notice:</b> All calculations & ML inference run locally. No external APIs or cloud databases utilized.
        </div>
        """,
        unsafe_allow_html=True,
    )


# ==========================================
# SHARED GLOBAL CALCULATIONS
# ==========================================
readiness_summary = calculate_overall_readiness(st.session_state.skills)
predictor = get_career_predictor()
job_roles_df = load_job_roles()
available_roles = list(job_roles_df["role_title"].unique())


# ==========================================
# PAGE 1: DASHBOARD OVERVIEW
# ==========================================
if nav_selection == "🏠 Dashboard Overview":
    st.title("Student Career Intelligence Dashboard")
    st.write(
        f"Welcome back, **{st.session_state.profile['name']}**! Here is your real-time career readiness snapshot."
    )

    # Top KPI Metrics Row
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric(
            label="Overall Readiness Score",
            value=f"{readiness_summary['score']}/100",
            delta=f"{readiness_summary['tier']}",
        )
    with m2:
        top_skill_name = max(st.session_state.skills, key=st.session_state.skills.get)
        st.metric(
            label="Peak Skill Competency",
            value=SKILL_DISPLAY_NAMES.get(top_skill_name, top_skill_name.title()),
            delta=f"{st.session_state.skills[top_skill_name]} pts",
        )
    with m3:
        st.metric(
            label="Target Aspiration",
            value=st.session_state.target_role_selected.split(" ")[0],
            delta=st.session_state.profile["primary_interest"],
        )
    with m4:
        st.metric(
            label="Milestones Completed",
            value=f"{sum(1 for v in st.session_state.milestones.values() if v)} / {len(st.session_state.milestones)}",
            delta=f"{comp_pct}% Journey",
        )

    st.markdown("---")

    # Visualizations Row: Skill Radar + Bar Breakdown
    col_chart1, col_chart2 = st.columns([1, 1])

    # Lookup target role vector
    selected_role_row = job_roles_df[
        job_roles_df["role_title"] == st.session_state.target_role_selected
    ].iloc[0]
    target_vector = {
        k: float(selected_role_row.get(f"target_{k}", 70))
        for k in SKILL_DISPLAY_NAMES.keys()
    }

    with col_chart1:
        st.subheader("Proficiency Radar vs Benchmark")
        radar_fig = create_radar_chart(
            current_skills=st.session_state.skills,
            target_skills=target_vector,
            student_name=st.session_state.profile["name"].split(" ")[0],
            target_name=st.session_state.target_role_selected,
        )
        st.plotly_chart(radar_fig, use_container_width=True)

    with col_chart2:
        st.subheader("Competency Distribution")
        skill_bars_fig = create_skill_bars_chart(st.session_state.skills)
        st.plotly_chart(skill_bars_fig, use_container_width=True)

    # Quick Action Cards
    st.subheader("Recommended Next Actions")
    a1, a2, a3 = st.columns(3)
    with a1:
        st.info("🤖 **Run ML Career Predictor**\n\nGenerate AI decision-tree predictions based on your skill distribution.")
    with a2:
        st.warning("🎯 **Review Skill Gaps**\n\nIdentify deficits against your chosen target job role and see your 7-day sprint.")
    with a3:
        st.success("📝 **Take Technical Quiz**\n\nTest your knowledge across 12 aptitude and coding MCQs with instant feedback.")


# ==========================================
# PAGE 2: PROFILE & SKILLS
# ==========================================
elif nav_selection == "👤 Profile & Skills":
    st.title("Student Profile & Skill Assessment")
    st.write("Keep your academic credentials and skill ratings up-to-date for accurate career intelligence.")

    with st.form("profile_form"):
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            name_input = st.text_input("Full Name", value=st.session_state.profile["name"])
            degree_input = st.text_input("Degree / Major", value=st.session_state.profile["degree"])
            college_input = st.text_input("College / University", value=st.session_state.profile["college"])
        with col_p2:
            grad_year_input = st.selectbox(
                "Expected Graduation Year",
                ["2024", "2025", "2026", "2027", "2028"],
                index=["2024", "2025", "2026", "2027", "2028"].index(
                    st.session_state.profile.get("grad_year", "2026")
                ),
            )
            interest_input = st.selectbox(
                "Primary Career Interest",
                CareerPredictor.ALLOWED_INTERESTS,
                index=CareerPredictor.ALLOWED_INTERESTS.index(
                    st.session_state.profile.get("primary_interest", "AI & Machine Learning")
                ),
            )
            target_role_input = st.selectbox(
                "Aspirational Target Role",
                available_roles,
                index=available_roles.index(st.session_state.target_role_selected)
                if st.session_state.target_role_selected in available_roles
                else 0,
            )

        st.markdown("#### Self-Assessed Skill Competencies (0 - 100)")
        st.caption("Rate your proficiency accurately to enable tailored machine learning recommendations.")

        s1, s2, s3 = st.columns(3)
        with s1:
            py_score = st.slider("Python Programming", 0, 100, int(st.session_state.skills["python"]))
            java_score = st.slider("Java Programming", 0, 100, int(st.session_state.skills["java"]))
        with s2:
            dsa_score = st.slider("Data Structures & Algorithms", 0, 100, int(st.session_state.skills["dsa"]))
            math_score = st.slider("Mathematics & Statistics", 0, 100, int(st.session_state.skills["mathematics"]))
        with s3:
            comm_score = st.slider("Communication & Soft Skills", 0, 100, int(st.session_state.skills["communication"]))
            prob_score = st.slider("Analytical Problem Solving", 0, 100, int(st.session_state.skills["problem_solving"]))

        submit_profile = st.form_submit_button("💾 Save Profile & Recalculate", use_container_width=True)

        if submit_profile:
            # Input validation
            if not name_input.strip():
                st.error("Validation Error: Full name cannot be empty.")
            else:
                st.session_state.profile["name"] = name_input.strip()
                st.session_state.profile["degree"] = degree_input.strip()
                st.session_state.profile["college"] = college_input.strip()
                st.session_state.profile["grad_year"] = grad_year_input
                st.session_state.profile["primary_interest"] = interest_input
                st.session_state.target_role_selected = target_role_input

                st.session_state.skills = {
                    "python": float(py_score),
                    "java": float(java_score),
                    "dsa": float(dsa_score),
                    "mathematics": float(math_score),
                    "communication": float(comm_score),
                    "problem_solving": float(prob_score),
                }

                st.session_state.milestones["profile_completed"] = True
                st.session_state.milestones["skills_assessed"] = True
                st.success("✅ Profile and skills saved successfully!")
                st.rerun()


# ==========================================
# PAGE 3: AI CAREER PREDICTOR (Decision Tree)
# ==========================================
elif nav_selection == "🤖 AI Career Predictor":
    st.title("Decision Tree Career-Category Prediction")
    st.write(
        "Trained scikit-learn `DecisionTreeClassifier` evaluating your skill vector against 120+ benchmark student profiles."
    )

    # Run Prediction
    with st.spinner("Executing scikit-learn DecisionTreeClassifier inference..."):
        ml_prediction = predictor.predict(
            skills=st.session_state.skills,
            primary_interest=st.session_state.profile["primary_interest"],
        )
        st.session_state.milestones["ml_prediction_run"] = True

    # Primary Result Banner
    prim_cat = ml_prediction["primary_category"]
    conf = ml_prediction["confidence"]

    st.markdown(
        f"""
        <div style="background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%); padding: 24px; border-radius: 12px; color: white; margin-bottom: 25px;">
            <h3 style="margin: 0; color: white; font-size: 24px;">Recommended Career Category: {prim_cat}</h3>
            <p style="margin: 8px 0 0 0; font-size: 16px; opacity: 0.9;">
                <b>ML Model Confidence:</b> {conf}% &nbsp;|&nbsp; <b>Algorithm:</b> scikit-learn DecisionTreeClassifier (Gini Impurity)
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_pred1, col_pred2 = st.columns([1, 1])

    with col_pred1:
        st.subheader("Class Probability Distribution")
        pred_df = pd.DataFrame(ml_prediction["ranked_predictions"])
        fig_prob = px.bar(
            pred_df,
            x="probability",
            y="category",
            orientation="h",
            labels={"probability": "Confidence (%)", "category": "Career Domain"},
            color="probability",
            color_continuous_scale="Viridis",
            text=[f"{p}%" for p in pred_df["probability"]],
        )
        fig_prob.update_layout(yaxis=dict(autorange="reversed"), showlegend=False, height=320)
        st.plotly_chart(fig_prob, use_container_width=True)

    with col_pred2:
        st.subheader("Alternative Viable Pathways")
        if ml_prediction["alternatives"]:
            for alt in ml_prediction["alternatives"]:
                st.markdown(
                    f"""
                    <div class="feature-card" style="padding: 12px 16px; margin-bottom: 10px;">
                        <span class="badge badge-info">Rank #{alt.get('rank', 2)}</span>
                        <b>{alt['category']}</b> &mdash; <i>{alt['probability']}% Match</i>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.info("No alternative categories exceeded the 5% probability threshold.")

        st.subheader("Model Feature Importances")
        feat_df = (
            pd.DataFrame(
                list(ml_prediction["feature_importances"].items()),
                columns=["Feature", "Importance"],
            )
            .sort_values(by="Importance", ascending=False)
            .head(5)
        )
        st.dataframe(feat_df, hide_index=True, use_container_width=True)

    # Transparent Rationale Box
    st.subheader("Transparent AI Decision Rationale")
    expl = ml_prediction["explanation"]
    st.markdown(
        f"""
        <div class="feature-card">
            <p style="font-size: 15px; line-height: 1.6; color: #1E293B; margin-bottom: 12px;">
                {expl.get('summary', '')}
            </p>
            <b>Key Decision Drivers Identified:</b>
            <ul>
                {''.join(f'<li>{d}</li>' for d in expl.get('key_drivers', []))}
            </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Disclaimers & Training Metrics
    st.markdown(
        f"""
        <div class="disclaimer-box">
            <b>Training Metadata:</b> Trained on {ml_prediction['training_metrics']['samples_count']} verified student records 
            across {ml_prediction['training_metrics']['categories_count']} career categories. 
            Cross-validation accuracy: {ml_prediction['training_metrics']['cv_accuracy_mean']}%. 
            <i>Note: Model predictions are intended for academic guidance and do not represent guaranteed hiring decisions.</i>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ==========================================
# PAGE 4: SKILL GAP & 7-DAY SPRINT
# ==========================================
elif nav_selection == "🎯 Skill Gap & 7-Day Sprint":
    st.title("Skill Gap Analysis & 7-Day Learning Sprint")
    st.write("Compare your skill proficiencies against target benchmarks and follow an actionable daily roadmap.")

    # Target Selector
    c_role, c_mode = st.columns([2, 1])
    with c_role:
        target_role = st.selectbox(
            "Select Benchmark Job Role",
            available_roles,
            index=available_roles.index(st.session_state.target_role_selected),
        )
        st.session_state.target_role_selected = target_role

    selected_row = job_roles_df[job_roles_df["role_title"] == target_role].iloc[0]
    target_scores = {
        k: float(selected_row.get(f"target_{k}", 70))
        for k in SKILL_DISPLAY_NAMES.keys()
    }

    # Perform Gap Analysis
    gap_analysis = analyze_skill_gaps(st.session_state.skills, target_scores)
    st.session_state.milestones["skill_gap_analyzed"] = True

    # Gap Summary Metrics
    g1, g2, g3 = st.columns(3)
    with g1:
        st.metric("Benchmark Coverage", f"{gap_analysis['coverage_pct']}%")
    with g2:
        st.metric("Primary Growth Area", gap_analysis["primary_focus_skill"])
    with g3:
        st.metric("Critical Deficits Count", gap_analysis["critical_gaps_count"])

    # Gap Delta Chart
    st.subheader("Skill Deficit vs Surplus Breakdown")
    fig_gap = create_gap_bar_chart(gap_analysis["breakdown"])
    st.plotly_chart(fig_gap, use_container_width=True)

    st.markdown("---")

    # Personalized 7-Day Roadmap
    weak_keys = [d["key"] for d in gap_analysis["deficits"]]
    if not weak_keys:
        weak_keys = ["dsa", "python"]

    roadmap_data = generate_7day_roadmap(weakest_skills=weak_keys, target_role=target_role)
    st.session_state.milestones["roadmap_generated"] = True

    st.subheader(f"📅 {roadmap_data['title']}")
    st.write(
        f"**Primary Track:** `{roadmap_data['primary_focus']}` &nbsp;|&nbsp; "
        f"**Secondary Track:** `{roadmap_data['secondary_focus']}` &nbsp;|&nbsp; "
        f"**Est. Time:** `{roadmap_data['total_est_hours']} Hours`"
    )

    # Interactive 7-Day Accordion / Timeline
    for day in roadmap_data["days"]:
        with st.expander(f"**Day {day['day']}: {day['theme']}** — *{day['skill']}* ({day['duration']})", expanded=(day['day'] == 1)):
            c_d1, c_d2 = st.columns([2, 1])
            with c_d1:
                st.markdown(f"**Focus:** {day['focus']}")
                st.markdown(f"**Key Concepts:** {day['topics']}")
                st.markdown(f"**Practical Coding Task:**\n> {day['task']}")
            with c_d2:
                st.markdown(f"**Expected Deliverable:**\n*{day['deliverable']}*")
                st.checkbox(f"Mark Day {day['day']} as Completed", key=f"day_check_{day['day']}")


# ==========================================
# PAGE 5: CODING & APTITUDE QUIZ
# ==========================================
elif nav_selection == "📝 Coding & Aptitude Quiz":
    st.title("Technical Aptitude & Coding Diagnostics")
    st.write(
        "Complete these 12 comprehensive MCQs covering Python, Java, DSA, Mathematics, and Analytical Problem Solving. Receive instant grading and explanations."
    )

    questions = load_quiz_questions()

    # Quiz Form
    with st.form("quiz_form"):
        user_choices = {}
        for q in questions:
            q_id = q["id"]
            st.markdown(f"**Question {q_id} ({q['category']}):** {q['question']}")
            user_choice = st.radio(
                f"Select your answer for Q{q_id}:",
                options=list(range(len(q["options"]))),
                format_func=lambda idx, opts=q["options"]: opts[idx],
                index=st.session_state.quiz_answers.get(q_id, 0),
                key=f"q_radio_{q_id}",
            )
            user_choices[q_id] = user_choice
            st.markdown("<br>", unsafe_allow_html=True)

        submit_quiz = st.form_submit_button("🏁 Submit Diagnostic Quiz", use_container_width=True)

        if submit_quiz:
            st.session_state.quiz_answers = user_choices
            st.session_state.quiz_submitted = True
            st.session_state.quiz_results = evaluate_quiz(user_choices, questions)
            st.session_state.milestones["quiz_completed"] = True
            st.toast("🎉 Quiz successfully evaluated!", icon="✅")

    # Display Quiz Results
    if st.session_state.quiz_submitted and st.session_state.quiz_results:
        results = st.session_state.quiz_results
        st.markdown("---")
        st.subheader("Quiz Diagnostic Results")

        q1, q2, q3, q4 = st.columns(4)
        with q1:
            st.metric("Total Score", f"{results['score_percentage']}%")
        with q2:
            st.metric("Correct Answers", f"{results['correct_count']} / {results['total_questions']}")
        with q3:
            st.metric("Performance Tier", results["performance_tier"])
        with q4:
            st.metric("Status", "Evaluated")

        st.info(results["summary_message"])

        # Detailed Question Breakdown & Explanations
        st.subheader("Question-by-Question Technical Explanations")
        for item in results["detailed_results"]:
            icon = "✅" if item["is_correct"] else "❌"
            card_class = "badge-success" if item["is_correct"] else "badge-danger"

            with st.expander(f"{icon} Q{item['id']} ({item['category']}): {item['question'][:65]}...", expanded=not item["is_correct"]):
                st.write(f"**Full Question:** {item['question']}")
                st.write(f"**Your Answer:** {item['user_option_text']}")
                st.write(f"**Correct Answer:** {item['correct_option_text']}")
                st.markdown(
                    f"""
                    <div class="feature-card" style="background: #F8FAFC; margin-top: 8px;">
                        <b>Technical Explanation:</b><br>{item['explanation']}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        # Calibrations Action Button
        st.subheader("Calibrate Profile Ratings")
        st.write("Would you like to automatically calibrate your skill sliders based on your quiz results?")
        if st.button("📈 Apply Quiz Calibrations to Profile"):
            for skill, stats in results["per_skill_stats"].items():
                skill_key = skill.lower().replace(" ", "_")
                if skill_key in st.session_state.skills:
                    ratio = stats["correct"] / stats["total"] if stats["total"] > 0 else 0
                    if ratio >= 0.8:
                        st.session_state.skills[skill_key] = min(100.0, st.session_state.skills[skill_key] + 5.0)
                    elif ratio <= 0.33:
                        st.session_state.skills[skill_key] = max(20.0, st.session_state.skills[skill_key] - 5.0)
            st.success("Applied calibrations to your skill ratings!")
            st.rerun()


# ==========================================
# PAGE 6: RESUME ATS ANALYZER
# ==========================================
elif nav_selection == "📄 Resume ATS Analyzer":
    st.title("Resume Keyword Extractor & ATS Analyzer")
    st.write(
        "Upload your resume in **TXT** or **PDF** format. The analyzer extracts text locally, maps technical competencies against target roles, and highlights missing keywords."
    )

    uploaded_file = st.file_uploader(
        "Upload Resume (PDF or TXT)",
        type=["pdf", "txt"],
        help="Files are processed strictly in local memory. No data is stored externally.",
    )

    # Target Role for Resume ATS
    target_role_for_resume = st.selectbox(
        "Target Role for Keyword Comparison",
        available_roles,
        index=available_roles.index(st.session_state.target_role_selected),
    )

    role_reqs = job_roles_df[job_roles_df["role_title"] == target_role_for_resume].iloc[0]["required_skills"]

    if uploaded_file is not None:
        with st.spinner("Extracting and parsing text..."):
            file_bytes = uploaded_file.read()
            extraction = extract_text_from_file(file_bytes, uploaded_file.name)

        if not extraction["success"]:
            st.error(f"Error Processing Resume: {extraction.get('error', 'Unknown parsing error.')}")
        else:
            resume_text = extraction["text"]
            st.success(
                f"Successfully parsed **{extraction['format']}** ({extraction.get('file_size_kb', 0)} KB, {extraction.get('pages', 1)} page(s))"
            )

            # Analyze Resume Text
            analysis = analyze_resume_text(resume_text, target_required_skills=role_reqs)
            st.session_state.resume_analysis = analysis
            st.session_state.milestones["resume_analyzed"] = True

            # Metrics Row
            r1, r2, r3, r4 = st.columns(4)
            with r1:
                st.metric("Target Keyword Coverage", f"{analysis['coverage_percentage']}%")
            with r2:
                st.metric("Total Skills Identified", analysis["skills_found_count"])
            with r3:
                st.metric("Word Count", analysis["word_count"])
            with r4:
                st.metric("Action Verbs Detected", analysis["action_verbs_count"])

            st.markdown("---")

            col_res1, col_res2 = st.columns(2)

            with col_res1:
                st.subheader("✅ Matched Target Skills")
                if analysis["matched_target_skills"]:
                    tags = "".join(f"<span class='badge badge-success'>{s.title()}</span>" for s in analysis["matched_target_skills"])
                    st.markdown(f"<div style='margin-bottom: 15px;'>{tags}</div>", unsafe_allow_html=True)
                else:
                    st.write("No matching required skills detected.")

                st.subheader("❌ Missing Target Keywords")
                if analysis["missing_target_skills"]:
                    tags_missing = "".join(f"<span class='badge badge-danger'>{s.title()}</span>" for s in analysis["missing_target_skills"])
                    st.markdown(f"<div style='margin-bottom: 15px;'>{tags_missing}</div>", unsafe_allow_html=True)
                else:
                    st.success("All required target skills were matched in your resume!")

            with col_res2:
                st.subheader("Identified Skills by Domain")
                for cat, sk_list in analysis["found_by_category"].items():
                    st.write(f"**{cat}:** {', '.join(s.title() for s in sk_list)}")

            st.markdown("---")

            # ATS Recommendations
            st.subheader("Actionable ATS Recommendations")
            for rec in analysis["recommendations"]:
                st.markdown(f"- {rec}")

            # Contact Signals Check
            st.markdown("#### Resume Contact Signals")
            sig = analysis["signals"]
            s_col1, s_col2, s_col3 = st.columns(3)
            with s_col1:
                st.write(f"{'✅' if sig['has_email'] else '⚠️'} Email Address Detected")
            with s_col2:
                st.write(f"{'✅' if sig['has_github'] else '⚠️'} GitHub Link Detected")
            with s_col3:
                st.write(f"{'✅' if sig['has_linkedin'] else '⚠️'} LinkedIn Link Detected")


# ==========================================
# PAGE 7: JOB ROLE MATCHER
# ==========================================
elif nav_selection == "💼 Job Role Matcher":
    st.title("Job-Role Skill Overlap & Similarity Matcher")
    st.write(
        "Real mathematical cosine similarity and weighted skill overlap calculated across all benchmark job roles."
    )

    # Compute matches
    matched_roles = match_job_roles(
        student_skills=st.session_state.skills,
        primary_category=st.session_state.profile["primary_interest"],
    )

    top_role = matched_roles[0]
    st.success(
        f"🏆 Top Job Match: **{top_role['role_title']}** ({top_role['match_percentage']}% Compatibility — *{top_role['fit_tier']}*)"
    )

    # Tabular Display
    display_data = []
    for r in matched_roles:
        display_data.append({
            "Role Title": r["role_title"],
            "Category": r["career_category"],
            "Overall Match %": f"{r['match_percentage']}%",
            "Cosine Sim %": f"{r['cosine_similarity']}%",
            "Overlap %": f"{r['overlap_percentage']}%",
            "Fit Tier": r["fit_tier"],
            "Experience": r["experience_level"],
            "Industry Outlook": r["job_outlook"],
        })

    st.dataframe(pd.DataFrame(display_data), hide_index=True, use_container_width=True)

    st.markdown("---")
    st.subheader("Role Breakdown & Skill Targets")

    for role in matched_roles[:4]:
        with st.expander(f"{role['role_title']} &mdash; {role['match_percentage']}% Match ({role['fit_tier']})"):
            c1, c2 = st.columns([1, 1])
            with c1:
                st.write(f"**Career Category:** {role['career_category']}")
                st.write(f"**Experience Level:** {role['experience_level']}")
                st.write(f"**Job Market Outlook:** {role['job_outlook']}")
                st.write(f"**Required Core Tech:** `{role['required_skills']}`")
            with c2:
                st.write("**Target Skill Benchmarks:**")
                for s_key, s_val in role["targets"].items():
                    user_val = st.session_state.skills.get(s_key, 0)
                    delta = user_val - s_val
                    icon = "✅" if delta >= 0 else "🔻"
                    st.write(f"{icon} {SKILL_DISPLAY_NAMES[s_key]}: Target {s_val} | Current {user_val} ({'+' if delta > 0 else ''}{delta} pts)")


# ==========================================
# PAGE 8: CAREER REPORT & PROGRESS
# ==========================================
elif nav_selection == "📥 Career Report & Progress":
    st.title("Student Career Report & Platform Progress")
    st.write(
        "Download your customized Career Development Report in TXT or CSV formats and track milestone progress."
    )

    # 1. Milestone Tracker
    st.subheader("Milestone Completion Tracker")
    milestones = st.session_state.milestones
    m_cols = st.columns(len(milestones))
    labels = {
        "profile_completed": "Profile Setup",
        "skills_assessed": "Skills Assessed",
        "ml_prediction_run": "ML Inference",
        "skill_gap_analyzed": "Skill Gap",
        "quiz_completed": "Quiz Tested",
        "resume_analyzed": "Resume ATS",
        "roadmap_generated": "7-Day Sprint",
    }

    for idx, (k, done) in enumerate(milestones.items()):
        with m_cols[idx]:
            icon = "✅" if done else "⏳"
            st.markdown(f"**{icon} {labels.get(k, k)}**")
            st.caption("Done" if done else "Pending")

    st.markdown("---")

    # 2. Report Generation
    target_role_selected = st.session_state.target_role_selected
    selected_row = job_roles_df[job_roles_df["role_title"] == target_role_selected].iloc[0]
    target_vector = {k: float(selected_row.get(f"target_{k}", 70)) for k in SKILL_DISPLAY_NAMES.keys()}
    gaps_data = analyze_skill_gaps(st.session_state.skills, target_vector)
    roadmap_data = generate_7day_roadmap(weakest_skills=[d["key"] for d in gaps_data["deficits"]], target_role=target_role_selected)
    prediction_data = predictor.predict(st.session_state.skills, st.session_state.profile["primary_interest"])
    matched_roles = match_job_roles(st.session_state.skills, primary_category=st.session_state.profile["primary_interest"])

    txt_report = generate_txt_report(
        profile=st.session_state.profile,
        skills=st.session_state.skills,
        readiness=readiness_summary,
        prediction=prediction_data,
        gaps=gaps_data,
        roadmap=roadmap_data,
        job_matches=matched_roles,
        quiz_results=st.session_state.quiz_results,
    )

    csv_report = generate_csv_report(
        profile=st.session_state.profile,
        skills=st.session_state.skills,
        readiness=readiness_summary,
        prediction=prediction_data,
        gaps=gaps_data,
        job_matches=matched_roles,
    )

    st.subheader("Download Career Development Report")
    d1, d2 = st.columns(2)
    with d1:
        st.download_button(
            label="📄 Download Report (TXT Format)",
            data=txt_report,
            file_name=f"CareerCampusAI_Report_{st.session_state.profile['name'].replace(' ', '_')}.txt",
            mime="text/plain",
            use_container_width=True,
        )
    with d2:
        st.download_button(
            label="📊 Download Metrics (CSV Format)",
            data=csv_report,
            file_name=f"CareerCampusAI_Metrics_{st.session_state.profile['name'].replace(' ', '_')}.csv",
            mime="text/csv",
            use_container_width=True,
        )

    # Preview Accordion
    with st.expander("👁️ Preview Formatted Plain-Text Report"):
        st.text(txt_report)

    st.markdown("---")

    # 3. User Feedback Form
    st.subheader("Platform Feedback & Reflection")
    with st.form("feedback_form"):
        stars = st.select_slider(
            "Rate your CareerCampus AI experience:",
            options=["⭐ Poor", "⭐⭐ Fair", "⭐⭐⭐ Good", "⭐⭐⭐⭐ Very Good", "⭐⭐⭐⭐⭐ Outstanding"],
            value="⭐⭐⭐⭐⭐ Outstanding",
        )
        comments = st.text_area("What features did you find most useful, or what would you like added?", "")
        sub_feedback = st.form_submit_button("Submit Feedback", use_container_width=True)

        if sub_feedback:
            st.session_state.feedback_submitted = True
            st.success("Thank you for your valuable feedback! Your response has been recorded.")
