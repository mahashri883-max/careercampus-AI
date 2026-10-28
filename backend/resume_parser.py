"""Career Campus AI - Resume Text Extractor & ATS Keyword Analyzer
Extracts text from TXT and PDF files, detects technical and domain skills, computes
keyword coverage against target job roles, and recommends high-impact missing keywords.
"""

from __future__ import annotations

import io
import re
from typing import Any, Dict, List, Set
import pypdf


SKILL_TAXONOMY: Dict[str, List[str]] = {
    "Languages": [
        "python", "java", "c++", "c#", "javascript", "typescript", "go",
        "rust", "sql", "r", "bash", "shell", "html", "css", "kotlin", "swift",
    ],
    "Frameworks & Libraries": [
        "react", "node.js", "spring boot", "django", "flask", "fastapi",
        "pytorch", "tensorflow", "scikit-learn", "pandas", "numpy", "next.js",
        "express", "angular", "vue", "tailwind", "junit",
    ],
    "Cloud & Infrastructure": [
        "aws", "azure", "gcp", "docker", "kubernetes", "terraform", "linux",
        "ci/cd", "jenkins", "git", "github", "bash", "ansible", "nginx",
    ],
    "Databases & Big Data": [
        "postgresql", "mysql", "mongodb", "redis", "elasticsearch", "kafka",
        "spark", "hadoop", "sqlite", "snowflake", "bigquery",
    ],
    "Concepts & Competencies": [
        "dsa", "algorithms", "data structures", "system design", "rest apis",
        "microservices", "machine learning", "deep learning", "statistics",
        "mathematics", "unit testing", "agile", "scrum", "problem solving",
        "communication", "leadership", "tableau", "power bi", "excel",
    ],
}

ALL_TAXONOMY_SKILLS: List[str] = sorted(
    {skill for group in SKILL_TAXONOMY.values() for skill in group}
)

ACTION_VERBS: List[str] = [
    "accelerated", "architected", "automated", "built", "collaborated",
    "configured", "delivered", "deployed", "designed", "developed",
    "engineered", "enhanced", "implemented", "improved", "increased",
    "integrated", "led", "managed", "maximized", "mentored", "minimized",
    "optimized", "orchestrated", "reduced", "refactored", "resolved",
    "scaled", "spearheaded", "streamlined", "transformed",
]


def extract_text_from_file(file_obj: Any, filename: str) -> Dict[str, Any]:
    """Extracts raw text from uploaded TXT or PDF file.

    Handles encoding issues, password protection, and corrupted files gracefully.

    Args:
        file_obj: BytesIO, file-like object, or raw bytes
        filename: Name of the uploaded file

    Returns:
        Dict with status, extracted text, page count, and error if any.
    """
    ext = filename.lower().split(".")[-1] if "." in filename else ""

    if ext not in ["txt", "pdf"]:
        return {
            "success": False,
            "text": "",
            "error": f"Unsupported file extension '.{ext}'. Please upload a .txt or .pdf file.",
        }

    # Normalize bytes
    try:
        if isinstance(file_obj, (bytes, bytearray)):
            file_bytes = file_obj
        elif hasattr(file_obj, "read"):
            file_bytes = file_obj.read()
            if hasattr(file_obj, "seek"):
                file_obj.seek(0)
        else:
            return {
                "success": False,
                "text": "",
                "error": "Invalid file buffer received.",
            }

        if len(file_bytes) == 0:
            return {
                "success": False,
                "text": "",
                "error": "The uploaded file is completely empty (0 bytes).",
            }

    except Exception as exc:
        return {
            "success": False,
            "text": "",
            "error": f"Failed reading file buffer: {str(exc)}",
        }

    # Extract text based on file format
    if ext == "txt":
        encodings = ["utf-8", "latin-1", "cp1252", "iso-8859-1"]
        for enc in encodings:
            try:
                text = file_bytes.decode(enc)
                return {
                    "success": True,
                    "text": text,
                    "pages": 1,
                    "format": "TXT",
                    "file_size_kb": round(len(file_bytes) / 1024, 2),
                }
            except UnicodeDecodeError:
                continue
        return {
            "success": False,
            "text": "",
            "error": "Unable to decode text file. Ensure it is encoded in UTF-8 or ASCII.",
        }

    elif ext == "pdf":
        try:
            reader = pypdf.PdfReader(io.BytesIO(file_bytes))
            if reader.is_encrypted:
                try:
                    # Attempt empty password decryption
                    reader.decrypt("")
                except Exception:
                    return {
                        "success": False,
                        "text": "",
                        "error": "The PDF is password protected. Please upload an unlocked PDF.",
                    }

            extracted_pages = []
            for idx, page in enumerate(reader.pages):
                page_text = page.extract_text() or ""
                if page_text.strip():
                    extracted_pages.append(page_text)

            full_text = "\n\n".join(extracted_pages).strip()
            if not full_text:
                return {
                    "success": False,
                    "text": "",
                    "error": "No selectable text found in PDF. It might be a scanned image-only PDF.",
                }

            return {
                "success": True,
                "text": full_text,
                "pages": len(reader.pages),
                "format": "PDF",
                "file_size_kb": round(len(file_bytes) / 1024, 2),
            }

        except Exception as exc:
            return {
                "success": False,
                "text": "",
                "error": f"PDF parsing error: {str(exc)}. Please check that the file is not corrupted.",
            }

    return {"success": False, "text": "", "error": "Unknown error occurred."}


def _match_skill_in_text(skill: str, text_lower: str) -> bool:
    """Uses word boundary regex to check if skill keyword exists in text."""
    # Special cases for symbols
    if skill == "c++":
        pattern = r"(?:^|\W)c\+\+(?:$|\W)"
    elif skill == "c#":
        pattern = r"(?:^|\W)c#(?:$|\W)"
    elif skill == "node.js":
        pattern = r"(?:^|\W)node(?:\.js)?(?:$|\W)"
    elif skill == "next.js":
        pattern = r"(?:^|\W)next(?:\.js)?(?:$|\W)"
    elif skill == "ci/cd":
        pattern = r"(?:^|\W)ci\s*/\s*cd(?:$|\W)"
    elif skill == "rest apis":
        pattern = r"(?:^|\W)rest(?:ful)?\s*(?:api|apis)?(?:$|\W)"
    elif skill == "spring boot":
        pattern = r"(?:^|\W)spring\s*(?:boot)?(?:$|\W)"
    elif skill == "scikit-learn":
        pattern = r"(?:^|\W)(?:scikit-learn|sklearn)(?:$|\W)"
    elif skill == "dsa":
        pattern = r"(?:^|\W)(?:dsa|data\s+structures\s+and\s+algorithms)(?:$|\W)"
    else:
        pattern = r"\b" + re.escape(skill) + r"\b"

    return bool(re.search(pattern, text_lower))


def analyze_resume_text(
    text: str, target_required_skills: List[str] | str | None = None
) -> Dict[str, Any]:
    """Analyzes resume text against the skill taxonomy and target role requirements.

    Args:
        text: Extracted text of resume
        target_required_skills: Required skills list or comma-separated string

    Returns:
        Structured analysis with identified skills, keyword coverage, and ATS recommendations.
    """
    if not text or not text.strip():
        return {
            "success": False,
            "error": "Empty text provided for analysis.",
        }

    text_lower = text.lower()
    words = re.findall(r"\b[A-Za-z0-9+#.-]+\b", text)
    word_count = len(words)

    # 1. Identify skills present in resume by category
    found_by_category: Dict[str, List[str]] = {}
    all_found_skills: Set[str] = set()

    for category, skills in SKILL_TAXONOMY.items():
        matched = []
        for s in skills:
            if _match_skill_in_text(s, text_lower):
                matched.append(s)
                all_found_skills.add(s)
        if matched:
            found_by_category[category] = matched

    # 2. Parse target required skills
    if isinstance(target_required_skills, str):
        target_list = [s.strip().lower() for s in target_required_skills.split(",") if s.strip()]
    elif isinstance(target_required_skills, list):
        target_list = [str(s).strip().lower() for s in target_required_skills if str(s).strip()]
    else:
        target_list = ["python", "dsa", "sql", "git", "rest apis", "problem solving"]

    # Deduplicate while preserving order
    target_clean = []
    seen = set()
    for s in target_list:
        if s not in seen:
            seen.add(s)
            target_clean.append(s)

    # 3. Match against target skills
    matched_target = []
    missing_target = []

    for req in target_clean:
        if _match_skill_in_text(req, text_lower) or req in all_found_skills:
            matched_target.append(req)
        else:
            missing_target.append(req)

    coverage_pct = round((len(matched_target) / len(target_clean) * 100), 1) if target_clean else 0.0

    # 4. Check action verbs
    found_verbs = [v for v in ACTION_VERBS if re.search(r"\b" + re.escape(v) + r"\b", text_lower)]

    # 5. Check contact info signals
    has_email = bool(re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text))
    has_github = bool(re.search(r"github\.com|github", text_lower))
    has_linkedin = bool(re.search(r"linkedin\.com|linkedin", text_lower))

    # 6. Generate actionable recommendations
    recommendations = []
    if missing_target:
        top_missing = ", ".join(f"'{m.title()}'" for m in missing_target[:5])
        recommendations.append(
            f"Add missing core keywords: Consider incorporating {top_missing} in your experience or project descriptions."
        )

    if len(found_verbs) < 5:
        recommendations.append(
            "Use more strong action verbs: Start bullet points with impact verbs such as 'Architected', 'Optimized', 'Deployed', or 'Spearheaded'."
        )

    if word_count < 250:
        recommendations.append(
            "Resume length is short: Your resume contains fewer than 250 words. Elaborate on project deliverables and technical architecture."
        )
    elif word_count > 900:
        recommendations.append(
            "Resume is lengthy: Aim for a concise 1-page profile (typically 400-650 words for early career roles)."
        )

    if not has_github:
        recommendations.append(
            "Include your GitHub link: Demonstrating open-source contributions or personal repositories strongly boosts recruiter trust."
        )

    if not recommendations:
        recommendations.append(
            "Excellent ATS optimization! Your resume showcases strong keywords and crisp action-oriented language."
        )

    return {
        "success": True,
        "word_count": word_count,
        "skills_found_count": len(all_found_skills),
        "found_by_category": found_by_category,
        "all_found_skills": sorted(list(all_found_skills)),
        "matched_target_skills": matched_target,
        "missing_target_skills": missing_target,
        "coverage_percentage": coverage_pct,
        "action_verbs_count": len(found_verbs),
        "found_verbs": found_verbs,
        "signals": {
            "has_email": has_email,
            "has_github": has_github,
            "has_linkedin": has_linkedin,
        },
        "recommendations": recommendations,
    }
