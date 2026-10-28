"""Career Campus AI - Job-Role Skill Matching Engine
Calculates real mathematical similarity and skill overlap between a student's profile
and benchmark job roles from the local dataset.
"""

from __future__ import annotations

import math
import os
from typing import Any, Dict, List
import pandas as pd


CORE_SKILLS: List[str] = [
    "python",
    "java",
    "dsa",
    "mathematics",
    "communication",
    "problem_solving",
]


def load_job_roles(dataset_path: str | None = None) -> pd.DataFrame:
    """Loads job roles benchmark dataset."""
    path = dataset_path or os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "job_roles.csv"
    )
    if not os.path.exists(path):
        raise FileNotFoundError(f"Job roles CSV not found at {path}")
    return pd.read_csv(path)


def _cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    """Calculates cosine similarity between two non-zero vectors."""
    dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = math.sqrt(sum(a * a for a in vec_a))
    norm_b = math.sqrt(sum(b * b for b in vec_b))

    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot_product / (norm_a * norm_b)


def _weighted_overlap(current: List[float], target: List[float]) -> float:
    """Calculates skill sufficiency percentage against target thresholds."""
    if not target:
        return 0.0

    penalties = []
    for c, t in zip(current, target):
        if t <= 0:
            continue
        # Ratio of student score achieved towards target
        ratio = min(1.2, c / t)
        penalties.append(ratio)

    mean_ratio = sum(penalties) / len(penalties) if penalties else 1.0
    # Scaled to 0-100%
    return min(100.0, max(0.0, mean_ratio * 100.0))


def match_job_roles(
    student_skills: Dict[str, float | int],
    dataset_path: str | None = None,
    primary_category: str | None = None,
) -> List[Dict[str, Any]]:
    """Calculates real match percentages for all job roles against student's skill scores.

    Args:
        student_skills: Dict of skill name to score (0-100)
        dataset_path: Optional path to job_roles.csv
        primary_category: Optional ML-predicted career category for bonus affinity

    Returns:
        List of ranked job match dictionaries.
    """
    df = load_job_roles(dataset_path)

    student_vec = [float(student_skills.get(s, 50)) for s in CORE_SKILLS]

    results = []

    for _, row in df.iterrows():
        role_vec = [
            float(row.get(f"target_{s}", 70)) for s in CORE_SKILLS
        ]

        # 1. Real Cosine Similarity (directional alignment of skill profile)
        cos_sim = _cosine_similarity(student_vec, role_vec)
        cos_pct = cos_sim * 100.0

        # 2. Overlap Ratio (actual point sufficiency)
        overlap_pct = _weighted_overlap(student_vec, role_vec)

        # 3. Category alignment bonus (up to +3%)
        cat_bonus = 3.0 if primary_category and str(row.get("career_category", "")).strip().lower() == primary_category.strip().lower() else 0.0

        # Blended final match percentage
        final_match = round(min(100.0, (0.55 * overlap_pct + 0.45 * cos_pct) + cat_bonus), 1)

        # Suitability Tier & Badge
        if final_match >= 85:
            fit_tier = "Exceptional Fit"
            badge_color = "#10B981"  # Emerald Green
        elif final_match >= 72:
            fit_tier = "Strong Match"
            badge_color = "#3B82F6"  # Blue
        elif final_match >= 58:
            fit_tier = "Moderate Match"
            badge_color = "#F59E0B"  # Amber
        else:
            fit_tier = "Requires Upskilling"
            badge_color = "#EF4444"  # Red

        results.append({
            "role_id": row.get("role_id", ""),
            "role_title": row.get("role_title", "Engineering Role"),
            "career_category": row.get("career_category", "Tech"),
            "match_percentage": final_match,
            "cosine_similarity": round(cos_pct, 1),
            "overlap_percentage": round(overlap_pct, 1),
            "fit_tier": fit_tier,
            "badge_color": badge_color,
            "experience_level": row.get("experience_level", "Entry-Level"),
            "job_outlook": row.get("job_outlook", "Steady"),
            "required_skills": row.get("required_skills", ""),
            "targets": {s: float(row.get(f"target_{s}", 70)) for s in CORE_SKILLS},
        })

    # Sort descending by match percentage
    results.sort(key=lambda x: x["match_percentage"], reverse=True)
    return results
