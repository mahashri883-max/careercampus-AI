"""Career Campus AI - Coding & Aptitude Quiz Engine
Loads local MCQs, evaluates user responses, calculates scores by domain, and provides
instant feedback with detailed technical explanations and skill calibrations.
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List


def load_quiz_questions(json_path: str | None = None) -> List[Dict[str, Any]]:
    """Loads MCQs from the local quiz_data.json file."""
    path = json_path or os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "quiz_data.json"
    )
    if not os.path.exists(path):
        raise FileNotFoundError(f"Quiz questions JSON not found at {path}")

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


def evaluate_quiz(
    user_answers: Dict[int, int], questions: List[Dict[str, Any]] | None = None
) -> Dict[str, Any]:
    """Evaluates user responses against answer keys.

    Args:
        user_answers: Dict mapping question `id` to selected option index (0-3)
        questions: Optional preloaded list of questions

    Returns:
        Structured evaluation with score percentage, domain breakdowns, and itemized explanations.
    """
    if questions is None:
        questions = load_quiz_questions()

    total_questions = len(questions)
    correct_count = 0
    attempted_count = 0

    per_skill_stats: Dict[str, Dict[str, int]] = {}
    detailed_results: List[Dict[str, Any]] = []

    for q in questions:
        q_id = q["id"]
        correct_idx = q["correct_index"]
        skill = q.get("skill_tested", "General")

        if skill not in per_skill_stats:
            per_skill_stats[skill] = {"correct": 0, "total": 0}
        per_skill_stats[skill]["total"] += 1

        user_choice = user_answers.get(q_id)
        is_attempted = user_choice is not None

        if is_attempted:
            attempted_count += 1
            is_correct = (user_choice == correct_idx)
            if is_correct:
                correct_count += 1
                per_skill_stats[skill]["correct"] += 1
            user_option_text = q["options"][user_choice] if 0 <= user_choice < len(q["options"]) else "Invalid"
        else:
            is_correct = False
            user_option_text = "Not Answered"

        correct_option_text = q["options"][correct_idx]

        detailed_results.append({
            "id": q_id,
            "category": q.get("category", ""),
            "skill_tested": skill,
            "question": q["question"],
            "options": q["options"],
            "user_choice": user_choice,
            "user_option_text": user_option_text,
            "correct_index": correct_idx,
            "correct_option_text": correct_option_text,
            "is_correct": is_correct,
            "is_attempted": is_attempted,
            "explanation": q.get("explanation", ""),
        })

    score_pct = round((correct_count / total_questions * 100), 1) if total_questions > 0 else 0.0

    # Suggested calibrations
    calibrations: Dict[str, str] = {}
    for skill, stats in per_skill_stats.items():
        ratio = stats["correct"] / stats["total"] if stats["total"] > 0 else 0.0
        if ratio >= 0.8:
            calibrations[skill] = f"Mastery Verified ({stats['correct']}/{stats['total']}) -> Eligible for +5 pt rating boost"
        elif ratio <= 0.33:
            calibrations[skill] = f"Gap Detected ({stats['correct']}/{stats['total']}) -> Review suggested in 7-day sprint"
        else:
            calibrations[skill] = f"Proficient ({stats['correct']}/{stats['total']}) -> Solid baseline"

    if score_pct >= 80:
        performance_tier = "Exemplary"
        summary_msg = "Outstanding score! You demonstrated deep conceptual clarity across coding and aptitude."
    elif score_pct >= 60:
        performance_tier = "Proficient"
        summary_msg = "Good performance! A few conceptual brush-ups will get your scores into the top tier."
    else:
        performance_tier = "Needs Practice"
        summary_msg = "Valuable diagnostic baseline. Focus on the explained answers to strengthen fundamentals."

    return {
        "total_questions": total_questions,
        "attempted_count": attempted_count,
        "correct_count": correct_count,
        "incorrect_count": total_questions - correct_count,
        "score_percentage": score_pct,
        "performance_tier": performance_tier,
        "summary_message": summary_msg,
        "per_skill_stats": per_skill_stats,
        "calibrations": calibrations,
        "detailed_results": detailed_results,
    }
