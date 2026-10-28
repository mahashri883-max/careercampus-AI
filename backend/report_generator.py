"""Career Campus AI - Student Career Report Generator
Generates comprehensive student career development reports formatted for instant
download in TXT and CSV formats.
"""

from __future__ import annotations

import csv
import io
from datetime import datetime
from typing import Any, Dict, List


def generate_txt_report(
    profile: Dict[str, Any],
    skills: Dict[str, float | int],
    readiness: Dict[str, Any],
    prediction: Dict[str, Any],
    gaps: Dict[str, Any],
    roadmap: Dict[str, Any],
    job_matches: List[Dict[str, Any]],
    quiz_results: Dict[str, Any] | None = None,
) -> str:
    """Creates a comprehensive, formatted plain text career report."""
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    name = profile.get("name", "Student")
    degree = profile.get("degree", "Undergraduate")
    college = profile.get("college", "University")
    grad_year = profile.get("grad_year", "2026")
    interest = profile.get("primary_interest", "Computer Science")

    lines = []
    lines.append("=" * 76)
    lines.append("                 CAREERCAMPUS AI - STUDENT CAREER REPORT")
    lines.append("=" * 76)
    lines.append(f"Generated On  : {now_str}")
    lines.append(f"Student Name  : {name}")
    lines.append(f"Education     : {degree} ({grad_year}) | {college}")
    lines.append(f"Core Interest : {interest}")
    lines.append("-" * 76)
    lines.append("")

    # Section 1: Overall Readiness
    lines.append("1. OVERALL READINESS SCORE & BENCHMARK")
    lines.append("----------------------------------------------------------------------------")
    lines.append(f"Composite Score : {readiness.get('score', 0)} / 100")
    lines.append(f"Proficiency Tier: {readiness.get('tier', 'Intermediate')}")
    lines.append(f"Assessment      : {readiness.get('description', '')}")
    lines.append("")

    # Section 2: Assessed Skill Ratings
    lines.append("2. ASSESSED SKILL RATINGS (0 - 100)")
    lines.append("----------------------------------------------------------------------------")
    lines.append(f"{'Skill Name':<25} | {'Score':<10} | {'Status'}")
    lines.append("-" * 76)
    for skill_key, score in skills.items():
        disp_name = skill_key.upper() if skill_key == "dsa" else skill_key.replace("_", " ").title()
        val = float(score)
        rating_tag = "Advanced" if val >= 80 else ("Proficient" if val >= 65 else "Developing")
        lines.append(f"{disp_name:<25} | {val:<10.1f} | {rating_tag}")
    lines.append("")

    # Section 3: ML Career Prediction
    lines.append("3. MACHINE LEARNING CAREER PREDICTION (Decision Tree Classifier)")
    lines.append("----------------------------------------------------------------------------")
    lines.append(f"Primary Recommended Category : {prediction.get('primary_category', 'N/A')}")
    lines.append(f"Model Confidence Score       : {prediction.get('confidence', 0)}%")
    lines.append("")
    lines.append("Alternative Career Pathways:")
    for alt in prediction.get("alternatives", []):
        lines.append(f"  * {alt['category']:<32} - Probability: {alt['probability']}%")
    lines.append("")
    expl = prediction.get("explanation", {})
    if isinstance(expl, dict):
        lines.append(f"Rationale: {expl.get('summary', '')}")
    lines.append("")

    # Section 4: Skill Gap Analysis
    lines.append("4. SKILL GAP ANALYSIS vs TARGET BENCHMARK")
    lines.append("----------------------------------------------------------------------------")
    lines.append(f"{'Skill':<20} | {'Current':<8} | {'Target':<8} | {'Delta':<10} | {'Status'}")
    lines.append("-" * 76)
    for item in gaps.get("breakdown", []):
        d_str = f"{'+' if item['delta'] > 0 else ''}{item['delta']}"
        lines.append(f"{item['skill']:<20} | {item['current']:<8.1f} | {item['target']:<8.1f} | {d_str:<10} | {item['status']}")
    lines.append("")
    lines.append(f"Benchmark Coverage: {gaps.get('coverage_pct', 0)}%")
    lines.append(f"Primary Focus Area: {gaps.get('primary_focus_skill', 'N/A')}")
    lines.append("")

    # Section 5: 7-Day Sprint Roadmap
    lines.append("5. PERSONALIZED 7-DAY ACCELERATED UPSKILLING SPRINT")
    lines.append("----------------------------------------------------------------------------")
    lines.append(f"Roadmap Title: {roadmap.get('title', '7-Day Sprint')}")
    lines.append(f"Target Role  : {roadmap.get('target_role', 'Engineering')}")
    lines.append(f"Total Est.   : {roadmap.get('total_est_hours', 20)} Hours")
    lines.append("")
    for day in roadmap.get("days", []):
        lines.append(f"[Day {day['day']}] {day['theme']} ({day['skill']}) - {day['duration']}")
        lines.append(f"  Focus      : {day['focus']}")
        lines.append(f"  Key Topics : {day['topics']}")
        lines.append(f"  Action Task: {day['task']}")
        lines.append(f"  Deliverable: {day['deliverable']}")
        lines.append("")

    # Section 6: Top Job Matches
    lines.append("6. TOP JOB-ROLE MATCH RANKINGS (Local Benchmark Database)")
    lines.append("----------------------------------------------------------------------------")
    lines.append(f"{'Rank':<5} | {'Role Title':<28} | {'Match %':<9} | {'Fit Tier':<18} | {'Outlook'}")
    lines.append("-" * 76)
    for idx, role in enumerate(job_matches[:6]):
        lines.append(
            f"{idx+1:<5} | {role['role_title']:<28} | {role['match_percentage']:<9.1f}% | {role['fit_tier']:<18} | {role.get('job_outlook', '')}"
        )
    lines.append("")

    # Section 7: Quiz Performance (if taken)
    if quiz_results:
        lines.append("7. DIAGNOSTIC QUIZ PERFORMANCE")
        lines.append("----------------------------------------------------------------------------")
        lines.append(f"Score: {quiz_results.get('correct_count', 0)} / {quiz_results.get('total_questions', 0)} ({quiz_results.get('score_percentage', 0)}%)")
        lines.append(f"Performance Tier: {quiz_results.get('performance_tier', '')}")
        lines.append("")

    lines.append("=" * 76)
    lines.append("DISCLAIMER: CareerCampus AI predictions are educational decision-support tools")
    lines.append("trained on representative datasets. They do not constitute formal employment guarantees.")
    lines.append("=" * 76)

    return "\n".join(lines)


def generate_csv_report(
    profile: Dict[str, Any],
    skills: Dict[str, float | int],
    readiness: Dict[str, Any],
    prediction: Dict[str, Any],
    gaps: Dict[str, Any],
    job_matches: List[Dict[str, Any]],
) -> str:
    """Creates a structured CSV report capturing all metrics and ranked matches."""
    output = io.StringIO()
    writer = csv.writer(output)

    # Section 1: Student Metadata
    writer.writerow(["SECTION", "METRIC", "VALUE", "NOTES"])
    writer.writerow(["Profile", "Student Name", profile.get("name", "Student"), ""])
    writer.writerow(["Profile", "Education", profile.get("degree", "UG"), ""])
    writer.writerow(["Profile", "Graduation Year", profile.get("grad_year", "2026"), ""])
    writer.writerow(["Profile", "College", profile.get("college", "University"), ""])
    writer.writerow(["Profile", "Primary Interest", profile.get("primary_interest", ""), ""])
    writer.writerow(["Readiness", "Composite Score", readiness.get("score", 0), "Out of 100"])
    writer.writerow(["Readiness", "Tier", readiness.get("tier", ""), ""])

    # Section 2: Skills
    for skill_name, score in skills.items():
        writer.writerow(["Skill Rating", skill_name, score, "Scale 0-100"])

    # Section 3: ML Predictions
    writer.writerow(["ML Prediction", "Primary Category", prediction.get("primary_category", ""), "DecisionTreeClassifier"])
    writer.writerow(["ML Prediction", "Confidence", f"{prediction.get('confidence', 0)}%", ""])
    for alt in prediction.get("alternatives", []):
        writer.writerow(["Alternative Path", alt["category"], f"{alt['probability']}%", f"Rank {alt.get('rank', 2)}"])

    # Section 4: Gaps
    for gap in gaps.get("breakdown", []):
        writer.writerow(["Skill Gap", gap["skill"], f"Delta: {gap['delta']}", f"Current: {gap['current']}, Target: {gap['target']}"])

    # Section 5: Job Matches
    writer.writerow([])
    writer.writerow(["JOB_MATCH_RANK", "ROLE_TITLE", "CATEGORY", "MATCH_PERCENTAGE", "FIT_TIER", "EXPERIENCE_LEVEL", "OUTLOOK"])
    for idx, role in enumerate(job_matches):
        writer.writerow([
            idx + 1,
            role["role_title"],
            role["career_category"],
            f"{role['match_percentage']}%",
            role["fit_tier"],
            role["experience_level"],
            role["job_outlook"],
        ])

    return output.getvalue()
