"""
Dropout-risk model.

There's no real historical accept/complete data for PMIS yet, so this
generates a synthetic training set where the label is correlated with
features we *do* have on every candidate (rurality, past participation,
education level, category) plus noise, then trains XGBoost to recover
that pattern. Swap generate_training_data() for a real historical query
the moment real outcome data exists -- nothing else needs to change.

A SHAP TreeExplainer is built once alongside the model and reused, so we
can turn any candidate's risk score into "why" in a couple of lines.
"""

import random
import numpy as np
import pandas as pd
import xgboost as xgb
import shap

FEATURE_NAMES = ["is_rural", "past_participation", "education_level_enc", "category_enc"]

EDU_ENCODING = {"ITI": 0, "Diploma": 1, "Bachelor's": 2}
CATEGORY_ENCODING = {"general": 0, "reserved": 1}


def candidate_to_features(c) -> list:
    """Turn a Candidate row (or Candidate-like object) into the model's feature vector."""
    return [
        int(c.is_rural),
        int(c.past_participation),
        EDU_ENCODING.get(c.education_level, 1),
        CATEGORY_ENCODING.get(c.category, 0),
    ]


def generate_training_data(n=2000, seed=42):
    rng = random.Random(seed)
    rows, labels = [], []
    for _ in range(n):
        is_rural = rng.random() < 0.45
        past_participation = rng.random() < 0.2
        edu = rng.choice(list(EDU_ENCODING.values()))
        category = rng.choice(list(CATEGORY_ENCODING.values()))

        prob_dropout = 0.25
        if is_rural:
            prob_dropout += 0.15
        if past_participation:
            prob_dropout -= 0.20
        prob_dropout -= 0.05 * edu
        prob_dropout += rng.uniform(-0.08, 0.08)
        prob_dropout = min(max(prob_dropout, 0.02), 0.95)

        label = 1 if rng.random() < prob_dropout else 0
        rows.append([int(is_rural), int(past_participation), edu, category])
        labels.append(label)

    X = pd.DataFrame(rows, columns=FEATURE_NAMES)
    y = pd.Series(labels)
    return X, y


class RiskModel:
    """Trains once at startup, then reused for every /allocate and /explanation call."""

    def __init__(self):
        X, y = generate_training_data()
        self.model = xgb.XGBClassifier(
            n_estimators=80, max_depth=3, learning_rate=0.15,
            eval_metric="logloss", random_state=42,
        )
        self.model.fit(X, y)
        self.explainer = shap.TreeExplainer(self.model)

    def score(self, candidate) -> float:
        """Returns P(candidate declines or drops out), 0-1."""
        X = pd.DataFrame([candidate_to_features(candidate)], columns=FEATURE_NAMES)
        return float(self.model.predict_proba(X)[0][1])

    def explain(self, candidate) -> list:
        """Returns the top contributing factors as plain-language strings,
        ordered by how much they pushed risk up (or down). Phrasing reflects
        this candidate's *actual* feature value, not just the SHAP sign --
        e.g. "not rural" is a different (and clearer) statement than
        "rural location decreases risk"."""
        feats = candidate_to_features(candidate)
        X = pd.DataFrame([feats], columns=FEATURE_NAMES)
        shap_values = self.explainer.shap_values(X)[0]

        def describe(name, value):
            if name == "is_rural":
                return "rural location" if value else "non-rural (urban) location"
            if name == "past_participation":
                return "past scheme participation" if value else "no past scheme participation"
            if name == "education_level_enc":
                inv = {v: k for k, v in EDU_ENCODING.items()}
                return f"education level ({inv[value]})"
            if name == "category_enc":
                inv = {v: k for k, v in CATEGORY_ENCODING.items()}
                return f"category ({inv[value]})"
            return name

        contributions = list(zip(FEATURE_NAMES, feats, shap_values))
        contributions.sort(key=lambda t: abs(t[2]), reverse=True)

        reasons = []
        for name, value, val in contributions[:3]:
            direction = "raises" if val > 0 else "lowers"
            reasons.append(f"{describe(name, value)} {direction} their risk ({val:+.2f})")
        return reasons


# Built once, imported wherever needed (main.py holds the single instance).
