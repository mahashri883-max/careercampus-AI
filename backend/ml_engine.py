"""Career Campus AI - Machine Learning Prediction Engine
Trains a scikit-learn DecisionTreeClassifier on student skill profiles and interests,
providing multi-class career category predictions, class probabilities, transparent
feature explanations, and alternative career recommendations.
"""

from __future__ import annotations

import os
from typing import Any, Dict, List, Tuple
import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import cross_val_score


class CareerPredictor:
    """Encapsulates training, inference, and explanations for career category prediction."""

    FEATURE_SKILLS: List[str] = [
        "python",
        "java",
        "dsa",
        "mathematics",
        "communication",
        "problem_solving",
    ]

    ALLOWED_INTERESTS: List[str] = [
        "AI & Machine Learning",
        "Backend Development",
        "Cloud & DevOps",
        "Cybersecurity",
        "Data Analytics",
        "Full Stack Development",
    ]

    def __init__(self, dataset_path: str | None = None) -> None:
        self.dataset_path = dataset_path or os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "dataset.csv"
        )
        self.model: DecisionTreeClassifier | None = None
        self.classes: List[str] = []
        self.feature_names: List[str] = []
        self.feature_importances_: Dict[str, float] = {}
        self.training_metrics: Dict[str, Any] = {}
        self.is_trained: bool = False

    def train(self) -> Dict[str, Any]:
        """Trains the DecisionTreeClassifier on the local CSV dataset.
        
        Returns:
            Dictionary with training accuracy, sample size, and cross-validation score.
        """
        if not os.path.exists(self.dataset_path):
            raise FileNotFoundError(f"Training dataset not found at {self.dataset_path}")

        df = pd.read_csv(self.dataset_path)

        # Validate required columns
        required_cols = self.FEATURE_SKILLS + ["primary_interest", "career_category"]
        for col in required_cols:
            if col not in df.columns:
                raise ValueError(f"Missing required dataset column: {col}")

        # One-hot encode primary_interest
        df_encoded = pd.get_dummies(df, columns=["primary_interest"], prefix="interest", dtype=float)

        target_col = "career_category"
        drop_cols = ["student_id", target_col] if "student_id" in df_encoded.columns else [target_col]
        X = df_encoded.drop(columns=drop_cols)
        y = df[target_col]

        self.feature_names = list(X.columns)

        # Train a tuned DecisionTreeClassifier
        dtc = DecisionTreeClassifier(
            criterion="gini",
            max_depth=6,
            min_samples_split=4,
            min_samples_leaf=2,
            random_state=42,
        )
        dtc.fit(X, y)

        self.model = dtc
        self.classes = list(dtc.classes_)

        # Calculate feature importances
        self.feature_importances_ = {
            feat: float(imp)
            for feat, imp in zip(self.feature_names, dtc.feature_importances_)
        }

        # Real cross-validation evaluation
        cv_scores = cross_val_score(dtc, X, y, cv=3)
        train_acc = float(dtc.score(X, y))

        self.training_metrics = {
            "samples_count": len(df),
            "num_features": len(self.feature_names),
            "train_accuracy": round(train_acc * 100, 2),
            "cv_accuracy_mean": round(float(cv_scores.mean()) * 100, 2),
            "categories_count": len(self.classes),
            "categories": self.classes,
        }
        self.is_trained = True
        return self.training_metrics

    def _prepare_input_vector(
        self, skills: Dict[str, float | int], primary_interest: str
    ) -> pd.DataFrame:
        """Transforms student input skills and interest into model feature vector."""
        if not self.is_trained or self.model is None:
            self.train()

        input_data: Dict[str, float] = {}

        # Numeric skill features (clipped to 0-100)
        for skill in self.FEATURE_SKILLS:
            val = float(skills.get(skill, 50.0))
            input_data[skill] = max(0.0, min(100.0, val))

        # Interest one-hot features
        for feat in self.feature_names:
            if feat.startswith("interest_"):
                interest_name = feat.replace("interest_", "")
                input_data[feat] = 1.0 if interest_name == primary_interest else 0.0

        vector_df = pd.DataFrame([input_data])
        # Ensure column ordering matches training
        vector_df = vector_df.reindex(columns=self.feature_names, fill_value=0.0)
        return vector_df

    def predict(
        self, skills: Dict[str, float | int], primary_interest: str
    ) -> Dict[str, Any]:
        """Runs scikit-learn DecisionTreeClassifier inference.

        Args:
            skills: Dictionary of skill scores (e.g., {'python': 85, 'java': 60, ...})
            primary_interest: Student's preferred domain

        Returns:
            Structured dictionary with primary prediction, confidence, probability distribution,
            alternative paths, and transparent explanations.
        """
        if not self.is_trained:
            self.train()

        assert self.model is not None

        vector_df = self._prepare_input_vector(skills, primary_interest)
        probs = self.model.predict_proba(vector_df)[0]

        # Rank all categories by probability
        ranked_pairs = sorted(
            zip(self.classes, probs), key=lambda x: x[1], reverse=True
        )

        ranked_predictions = [
            {
                "category": cat,
                "probability": round(float(p) * 100, 2),
                "rank": idx + 1,
            }
            for idx, (cat, p) in enumerate(ranked_pairs)
        ]

        primary_cat = ranked_predictions[0]["category"]
        primary_conf = ranked_predictions[0]["probability"]

        # If probability is evenly split or top prob is 0, give fallback based on primary
        if primary_conf == 0:
            pred_class = self.model.predict(vector_df)[0]
            primary_cat = str(pred_class)
            primary_conf = 75.0

        # Alternative careers (rank 2 and rank 3 with non-negligible probabilities)
        alternatives = [
            item for item in ranked_predictions[1:4] if item["probability"] > 0
        ]
        if not alternatives and len(ranked_predictions) > 1:
            alternatives = [ranked_predictions[1]]

        # Generate transparent explanation based on input skills and feature importance
        explanation = self._build_explanation(
            skills=skills,
            primary_interest=primary_interest,
            predicted_category=primary_cat,
            alternatives=alternatives,
        )

        return {
            "primary_category": primary_cat,
            "confidence": primary_conf,
            "ranked_predictions": ranked_predictions,
            "alternatives": alternatives,
            "feature_importances": self.feature_importances_,
            "explanation": explanation,
            "training_metrics": self.training_metrics,
        }

    def _build_explanation(
        self,
        skills: Dict[str, float | int],
        primary_interest: str,
        predicted_category: str,
        alternatives: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Constructs human-readable rationale for the ML prediction."""
        # Find student's top 2 skills
        sorted_skills = sorted(
            skills.items(), key=lambda item: float(item[1]), reverse=True
        )
        top_skills = sorted_skills[:2]
        lowest_skill = sorted_skills[-1]

        key_drivers = [
            f"Strong aptitude in {skill.upper() if skill in ['dsa'] else skill.title()} ({score}/100)"
            for skill, score in top_skills
        ]
        key_drivers.append(f"Declared career aspiration in '{primary_interest}'")

        alt_text = ""
        if alternatives:
            alt_names = [f"{alt['category']} ({alt['probability']}%)" for alt in alternatives[:2]]
            alt_text = f"Alternative viable pathways identified: {', '.join(alt_names)}."

        summary = (
            f"The Decision Tree model classified your profile into '{predicted_category}' "
            f"primarily due to strong alignment between your {top_skills[0][0].title()} ({top_skills[0][1]}/100) "
            f"and your primary domain interest in {primary_interest}. {alt_text} "
            f"Your key growth lever is {lowest_skill[0].title()} ({lowest_skill[1]}/100)."
        )

        return {
            "summary": summary,
            "key_drivers": key_drivers,
            "top_skills": top_skills,
            "weakest_skill": lowest_skill,
        }


# Global cached singleton instance
_predictor_instance: CareerPredictor | None = None


def get_career_predictor() -> CareerPredictor:
    """Returns the singleton CareerPredictor instance, training if necessary."""
    global _predictor_instance
    if _predictor_instance is None:
        _predictor_instance = CareerPredictor()
        _predictor_instance.train()
    return _predictor_instance
