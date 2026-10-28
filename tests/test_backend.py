"""CareerCampus AI - Automated Test Suite
Tests ML inference, skill analysis, roadmap generator, resume parser,
job matcher, quiz engine, and report generation.
"""

from __future__ import annotations

import io
import os
import unittest
import pandas as pd

from backend.ml_engine import CareerPredictor, get_career_predictor
from backend.skill_analysis import (
    calculate_overall_readiness,
    analyze_skill_gaps,
    create_radar_chart,
    create_gap_bar_chart,
    create_skill_bars_chart,
)
from backend.roadmap_generator import generate_7day_roadmap
from backend.resume_parser import (
    extract_text_from_file,
    analyze_resume_text,
    _match_skill_in_text,
)
from backend.job_matcher import load_job_roles, match_job_roles
from backend.quiz_engine import load_quiz_questions, evaluate_quiz
from backend.report_generator import generate_txt_report, generate_csv_report


class TestCareerCampusBackend(unittest.TestCase):
    """Full unit test suite for CareerCampus AI backend."""

    def setUp(self):
        self.sample_skills = {
            "python": 85.0,
            "java": 60.0,
            "dsa": 80.0,
            "mathematics": 75.0,
            "communication": 70.0,
            "problem_solving": 82.0,
        }
        self.sample_profile = {
            "name": "Alex Chen",
            "degree": "B.Tech Computer Science",
            "college": "Stanford University",
            "grad_year": "2026",
            "primary_interest": "AI & Machine Learning",
        }

    # ==========================================
    # 1. ML Engine Tests
    # ==========================================
    def test_ml_training_and_metrics(self):
        predictor = CareerPredictor()
        metrics = predictor.train()
        self.assertTrue(predictor.is_trained)
        self.assertGreaterEqual(metrics["train_accuracy"], 70.0)
        self.assertGreaterEqual(metrics["samples_count"], 100)
        self.assertIn("categories", metrics)
        self.assertGreaterEqual(len(metrics["categories"]), 4)

    def test_ml_prediction_and_explanation(self):
        predictor = get_career_predictor()
        result = predictor.predict(
            self.sample_skills, primary_interest="AI & Machine Learning"
        )
        self.assertIn("primary_category", result)
        self.assertIn("confidence", result)
        self.assertGreaterEqual(result["confidence"], 0.0)
        self.assertLessEqual(result["confidence"], 100.0)
        self.assertIn("alternatives", result)
        self.assertIn("explanation", result)
        self.assertTrue(len(result["explanation"]["summary"]) > 20)

    # ==========================================
    # 2. Skill Assessment & Gap Analysis Tests
    # ==========================================
    def test_overall_readiness(self):
        readiness = calculate_overall_readiness(self.sample_skills)
        self.assertIn("score", readiness)
        self.assertIn("tier", readiness)
        self.assertGreaterEqual(readiness["score"], 70.0)

    def test_skill_gap_analysis(self):
        target = {
            "python": 90.0,
            "java": 50.0,
            "dsa": 85.0,
            "mathematics": 90.0,
            "communication": 70.0,
            "problem_solving": 90.0,
        }
        gaps = analyze_skill_gaps(self.sample_skills, target)
        self.assertIn("breakdown", gaps)
        self.assertEqual(len(gaps["breakdown"]), 6)
        self.assertIn("coverage_pct", gaps)

    def test_plotly_chart_generation(self):
        target = {k: 75.0 for k in self.sample_skills}
        radar = create_radar_chart(self.sample_skills, target, "Alex")
        self.assertIsNotNone(radar)
        gap_data = analyze_skill_gaps(self.sample_skills, target)
        gap_bar = create_gap_bar_chart(gap_data["breakdown"])
        self.assertIsNotNone(gap_bar)
        skill_bar = create_skill_bars_chart(self.sample_skills)
        self.assertIsNotNone(skill_bar)

    # ==========================================
    # 3. 7-Day Roadmap Tests
    # ==========================================
    def test_roadmap_generation(self):
        roadmap = generate_7day_roadmap(["dsa", "python"], target_role="ML Engineer")
        self.assertEqual(len(roadmap["days"]), 7)
        self.assertGreater(roadmap["total_est_hours"], 10)
        for d in roadmap["days"]:
            self.assertIn("day", d)
            self.assertIn("task", d)
            self.assertIn("deliverable", d)

    # ==========================================
    # 4. Resume Parser Tests
    # ==========================================
    def test_resume_text_extraction(self):
        # Test TXT parsing
        mock_txt = (
            "Alex Chen - Software Engineer\n"
            "Skills: Python, Java, DSA, React, Docker, Git, Machine Learning, SQL\n"
            "Experience: Implemented and optimized microservices reducing latency by 35%.\n"
            "Contact: alex@example.com | github.com/alexchen"
        ).encode("utf-8")
        extracted = extract_text_from_file(mock_txt, "resume.txt")
        self.assertTrue(extracted["success"])
        self.assertIn("Python", extracted["text"])

        # Test empty file handling
        empty = extract_text_from_file(b"", "empty.txt")
        self.assertFalse(empty["success"])

        # Test invalid extension
        invalid = extract_text_from_file(b"data", "test.exe")
        self.assertFalse(invalid["success"])

    def test_resume_skill_analysis(self):
        resume_text = (
            "Experienced with Python, Django, SQL, Git, and Docker. "
            "Engineered scalable data pipelines and built machine learning models."
        )
        analysis = analyze_resume_text(
            resume_text, target_required_skills="python, docker, kubernetes, aws, sql"
        )
        self.assertTrue(analysis["success"])
        self.assertIn("python", analysis["matched_target_skills"])
        self.assertIn("docker", analysis["matched_target_skills"])
        self.assertIn("kubernetes", analysis["missing_target_skills"])
        self.assertGreaterEqual(analysis["coverage_percentage"], 30.0)

    # ==========================================
    # 5. Job Matcher Tests
    # ==========================================
    def test_job_matcher(self):
        matches = match_job_roles(self.sample_skills)
        self.assertGreaterEqual(len(matches), 5)
        # Check sorting descending
        for i in range(len(matches) - 1):
            self.assertGreaterEqual(
                matches[i]["match_percentage"], matches[i + 1]["match_percentage"]
            )
        # Check percentage bounds
        for role in matches:
            self.assertGreaterEqual(role["match_percentage"], 0.0)
            self.assertLessEqual(role["match_percentage"], 100.0)
            self.assertIn(role["fit_tier"], ["Exceptional Fit", "Strong Match", "Moderate Match", "Requires Upskilling"])

    # ==========================================
    # 6. Quiz Engine Tests
    # ==========================================
    def test_quiz_engine(self):
        questions = load_quiz_questions()
        self.assertGreaterEqual(len(questions), 10)

        # Perfect answers test
        perfect_answers = {q["id"]: q["correct_index"] for q in questions}
        result = evaluate_quiz(perfect_answers, questions)
        self.assertEqual(result["correct_count"], len(questions))
        self.assertEqual(result["score_percentage"], 100.0)
        self.assertEqual(result["performance_tier"], "Exemplary")

        # Zero answers test
        empty_result = evaluate_quiz({}, questions)
        self.assertEqual(empty_result["correct_count"], 0)
        self.assertEqual(empty_result["score_percentage"], 0.0)

    # ==========================================
    # 7. Report Generator Tests
    # ==========================================
    def test_report_generation(self):
        readiness = calculate_overall_readiness(self.sample_skills)
        predictor = get_career_predictor()
        prediction = predictor.predict(self.sample_skills, "AI & Machine Learning")
        gaps = analyze_skill_gaps(self.sample_skills, {k: 75.0 for k in self.sample_skills})
        roadmap = generate_7day_roadmap(["dsa", "python"], "ML Engineer")
        job_matches = match_job_roles(self.sample_skills)

        txt_rep = generate_txt_report(
            self.sample_profile,
            self.sample_skills,
            readiness,
            prediction,
            gaps,
            roadmap,
            job_matches,
        )
        self.assertIn("CAREERCAMPUS AI - STUDENT CAREER REPORT", txt_rep)
        self.assertIn("Alex Chen", txt_rep)
        self.assertIn("MACHINE LEARNING CAREER PREDICTION", txt_rep)

        csv_rep = generate_csv_report(
            self.sample_profile,
            self.sample_skills,
            readiness,
            prediction,
            gaps,
            job_matches,
        )
        self.assertIn("Student Name", csv_rep)
        self.assertIn("Alex Chen", csv_rep)
        self.assertIn("JOB_MATCH_RANK", csv_rep)


if __name__ == "__main__":
    unittest.main()
