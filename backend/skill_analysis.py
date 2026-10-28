"""Career Campus AI - Skill Assessment & Gap Analysis Engine
Computes weighted readiness scores, performs multi-dimensional gap analysis against
target role benchmarks or custom goals, and creates Plotly visualizations.
"""

from __future__ import annotations

from typing import Any, Dict, List, Tuple
import plotly.graph_objects as go


SKILL_DISPLAY_NAMES: Dict[str, str] = {
    "python": "Python",
    "java": "Java",
    "dsa": "DSA",
    "mathematics": "Mathematics",
    "communication": "Communication",
    "problem_solving": "Problem Solving",
}

DEFAULT_WEIGHTS: Dict[str, float] = {
    "python": 0.18,
    "java": 0.14,
    "dsa": 0.22,
    "problem_solving": 0.20,
    "mathematics": 0.14,
    "communication": 0.12,
}


def calculate_overall_readiness(
    skills: Dict[str, float | int], weights: Dict[str, float] | None = None
) -> Dict[str, Any]:
    """Calculates weighted overall career readiness score and tier classification.

    Args:
        skills: Dict of skill name to score (0-100)
        weights: Optional custom weight mapping summing to 1.0

    Returns:
        Dict with overall score, rating tier, badge color, and summary text.
    """
    w = weights or DEFAULT_WEIGHTS
    total_score = 0.0
    total_weight = 0.0

    for skill, weight in w.items():
        score = float(skills.get(skill, 0))
        total_score += score * weight
        total_weight += weight

    overall = round(total_score / (total_weight if total_weight > 0 else 1.0), 1)

    if overall >= 85:
        tier = "Industry Ready"
        color = "#10B981"  # Emerald Green
        description = "Outstanding profile! You possess production-grade competencies across core domains."
    elif overall >= 72:
        tier = "Proficient & Competitive"
        color = "#3B82F6"  # Blue
        description = "Solid foundation! Competitive for campus recruitments and entry-level engineering roles."
    elif overall >= 55:
        tier = "Intermediate Developer"
        color = "#F59E0B"  # Amber
        description = "Good progress! Focused sprint on your critical deficits will elevate your placement readiness."
    else:
        tier = "Foundational Stage"
        color = "#EF4444"  # Red
        description = "Early learning stage. Follow the personalized 7-day sprint to establish core building blocks."

    return {
        "score": overall,
        "tier": tier,
        "color": color,
        "description": description,
    }


def analyze_skill_gaps(
    current_skills: Dict[str, float | int],
    target_skills: Dict[str, float | int],
) -> Dict[str, Any]:
    """Performs delta comparison between student's current skills and target benchmarks.

    Args:
        current_skills: Current skill scores (0-100)
        target_skills: Benchmark target scores (0-100)

    Returns:
        Structured gap breakdown, sorted deficits, and summary statistics.
    """
    breakdown: List[Dict[str, Any]] = []
    deficits: List[Dict[str, Any]] = []
    surpluses: List[Dict[str, Any]] = []

    all_keys = list(SKILL_DISPLAY_NAMES.keys())

    for key in all_keys:
        curr = float(current_skills.get(key, 0))
        target = float(target_skills.get(key, 70))
        delta = round(curr - target, 1)
        name = SKILL_DISPLAY_NAMES.get(key, key.title())

        if delta >= 0:
            status = "Target Met"
            status_code = "met"
            color = "#10B981"
            surpluses.append({"skill": name, "key": key, "delta": delta, "current": curr, "target": target})
        elif delta >= -15:
            status = "Minor Gap"
            status_code = "minor"
            color = "#F59E0B"
            deficits.append({"skill": name, "key": key, "delta": delta, "current": curr, "target": target})
        else:
            status = "Critical Gap"
            status_code = "critical"
            color = "#EF4444"
            deficits.append({"skill": name, "key": key, "delta": delta, "current": curr, "target": target})

        breakdown.append({
            "key": key,
            "skill": name,
            "current": curr,
            "target": target,
            "delta": delta,
            "status": status,
            "status_code": status_code,
            "color": color,
        })

    # Sort deficits with largest gap first (most negative delta)
    deficits.sort(key=lambda x: x["delta"])

    total_target = sum(item["target"] for item in breakdown)
    total_current = sum(item["current"] for item in breakdown)
    coverage_pct = round((total_current / total_target * 100), 1) if total_target > 0 else 100.0

    return {
        "breakdown": breakdown,
        "deficits": deficits,
        "surpluses": surpluses,
        "has_gaps": len(deficits) > 0,
        "critical_gaps_count": sum(1 for item in breakdown if item["status_code"] == "critical"),
        "coverage_pct": min(100.0, coverage_pct),
        "primary_focus_skill": deficits[0]["skill"] if deficits else "All Targets Met",
        "primary_focus_key": deficits[0]["key"] if deficits else "none",
    }


def create_radar_chart(
    current_skills: Dict[str, float | int],
    target_skills: Dict[str, float | int],
    student_name: str = "Student",
    target_name: str = "Role Benchmark",
) -> go.Figure:
    """Generates an interactive Plotly Radar (Spider) chart comparing Current vs Target."""
    categories = [SKILL_DISPLAY_NAMES[k] for k in SKILL_DISPLAY_NAMES.keys()]
    current_vals = [float(current_skills.get(k, 0)) for k in SKILL_DISPLAY_NAMES.keys()]
    target_vals = [float(target_skills.get(k, 70)) for k in SKILL_DISPLAY_NAMES.keys()]

    # Close the polygon loop for polar plot
    categories_closed = categories + [categories[0]]
    current_closed = current_vals + [current_vals[0]]
    target_closed = target_vals + [target_vals[0]]

    fig = go.Figure()

    # Target Benchmark Trace
    fig.add_trace(go.Scatterpolar(
        r=target_closed,
        theta=categories_closed,
        fill="toself",
        name=target_name,
        line=dict(color="#6366F1", width=2, dash="dash"),
        fillcolor="rgba(99, 102, 241, 0.15)",
    ))

    # Current Student Trace
    fig.add_trace(go.Scatterpolar(
        r=current_closed,
        theta=categories_closed,
        fill="toself",
        name=f"{student_name} (Current)",
        line=dict(color="#10B981", width=3),
        fillcolor="rgba(16, 185, 129, 0.25)",
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickfont=dict(size=10, color="#64748B"),
                gridcolor="#E2E8F0",
            ),
            angularaxis=dict(
                tickfont=dict(size=12, color="#1E293B", family="Arial, sans-serif"),
                gridcolor="#E2E8F0",
            ),
            bgcolor="rgba(255, 255, 255, 0.8)",
        ),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.08, xanchor="center", x=0.5),
        margin=dict(l=40, r=40, t=50, b=40),
        height=380,
    )
    return fig


def create_gap_bar_chart(gap_breakdown: List[Dict[str, Any]]) -> go.Figure:
    """Generates an interactive delta bar chart showing skill deficits & surpluses."""
    skills = [item["skill"] for item in gap_breakdown]
    deltas = [item["delta"] for item in gap_breakdown]
    colors = [item["color"] for item in gap_breakdown]
    texts = [f"{'+' if d > 0 else ''}{d} pts" for d in deltas]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=skills,
        y=deltas,
        marker_color=colors,
        text=texts,
        textposition="outside",
        cliponaxis=False,
        hovertemplate="<b>%{x}</b><br>Delta: %{text}<extra></extra>",
    ))

    fig.add_hline(y=0, line_dash="solid", line_color="#94A3B8", line_width=1.5)

    fig.update_layout(
        title="Skill Gap Delta (Current vs Target)",
        title_font=dict(size=14, color="#1E293B"),
        xaxis_title="",
        yaxis_title="Point Delta (+ Surplus / - Deficit)",
        yaxis=dict(gridcolor="#F1F5F9", zeroline=False),
        margin=dict(l=40, r=20, t=50, b=40),
        height=320,
    )
    return fig


def create_skill_bars_chart(skills: Dict[str, float | int]) -> go.Figure:
    """Creates a horizontal bar chart displaying student proficiency across skills."""
    skill_names = [SKILL_DISPLAY_NAMES[k] for k in SKILL_DISPLAY_NAMES.keys()]
    vals = [float(skills.get(k, 0)) for k in SKILL_DISPLAY_NAMES.keys()]

    # Gradient coloring based on score thresholds
    colors = [
        "#10B981" if v >= 80 else ("#3B82F6" if v >= 65 else ("#F59E0B" if v >= 50 else "#EF4444"))
        for v in vals
    ]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=skill_names,
        x=vals,
        orientation="h",
        marker_color=colors,
        text=[f"{v}/100" for v in vals],
        textposition="auto",
        hovertemplate="<b>%{y}</b>: %{x}/100<extra></extra>",
    ))

    fig.update_layout(
        xaxis=dict(range=[0, 100], gridcolor="#F1F5F9"),
        yaxis=dict(autorange="reversed"),
        margin=dict(l=40, r=20, t=20, b=30),
        height=280,
    )
    return fig
