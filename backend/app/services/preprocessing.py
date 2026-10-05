from __future__ import annotations

import re
import numpy as np
import pandas as pd

COLUMN_ALIASES = {
    "customer_id": ["customer_id", "customerid", "customer", "id", "customer id"],
    "age": ["age", "customer_age", "customer age"],
    "annual_income": ["annual_income", "income", "annualincome", "annual income"],
    "total_spend": ["total_spend", "spending", "purchase_amount", "monetary", "revenue", "total spend"],
    "purchase_frequency": ["purchase_frequency", "frequency", "orders", "total_orders", "purchase frequency"],
    "recency_days": ["recency", "recency_days", "days_since_last_purchase", "days since last purchase"],
    "average_order_value": ["average_order_value", "aov", "average order value"],
    "total_orders": ["total_orders", "orders", "order_count"],
    "gender": ["gender", "sex"],
    "city": ["city", "location", "region"],
    "preferred_category": ["preferred_category", "category", "product_category"],
    "customer_tenure_months": ["customer_tenure_months", "tenure", "tenure_months"],
    "satisfaction_score": ["satisfaction_score", "satisfaction", "rating"],
}


def _normalise(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.lower())


def detect_columns(frame: pd.DataFrame) -> dict[str, str]:
    indexed = {_normalise(column): column for column in frame.columns}
    mapping: dict[str, str] = {}
    for canonical, aliases in COLUMN_ALIASES.items():
        for alias in aliases:
            if _normalise(alias) in indexed:
                mapping[canonical] = indexed[_normalise(alias)]
                break
    return mapping


def standardise(frame: pd.DataFrame, mapping: dict[str, str] | None = None) -> tuple[pd.DataFrame, dict[str, str]]:
    if frame.empty:
        raise ValueError("The dataset is empty.")
    frame = frame.copy()
    detected = detect_columns(frame)
    if mapping:
        detected.update({key: value for key, value in mapping.items() if value in frame.columns})
    rename = {source: canonical for canonical, source in detected.items()}
    frame = frame.rename(columns=rename)
    for column in ["age", "annual_income", "total_spend", "purchase_frequency", "average_order_value", "recency_days", "total_orders", "customer_tenure_months", "discount_usage", "website_visits", "satisfaction_score"]:
        if column in frame:
            frame[column] = pd.to_numeric(frame[column], errors="coerce")
    return frame, detected


def quality_report(frame: pd.DataFrame) -> dict:
    numeric = frame.select_dtypes(include="number")
    outliers = 0
    for column in numeric.columns:
        values = numeric[column].dropna()
        if len(values) > 3:
            q1, q3 = values.quantile([.25, .75])
            iqr = q3 - q1
            if iqr:
                outliers += int(((values < q1 - 1.5 * iqr) | (values > q3 + 1.5 * iqr)).sum())
    total = frame.shape[0] * frame.shape[1]
    missing = int(frame.isna().sum().sum())
    return {"rows": int(len(frame)), "columns": int(len(frame.columns)), "missing_values": missing,
            "duplicates": int(frame.duplicated().sum()), "outliers": outliers,
            "completeness": round(100 * (1 - missing / total), 1) if total else 0,
            "numeric_columns": list(numeric.columns),
            "categorical_columns": list(frame.select_dtypes(exclude="number").columns),
            "missing_by_column": {key: int(value) for key, value in frame.isna().sum().items() if value}}


def clean_for_analysis(frame: pd.DataFrame) -> pd.DataFrame:
    result = frame.drop_duplicates().copy()
    for column in result.select_dtypes(include="number"):
        result[column] = result[column].fillna(result[column].median())
    for column in result.select_dtypes(exclude="number"):
        result[column] = result[column].fillna("Unknown")
    return result.replace([np.inf, -np.inf], np.nan).dropna(how="all")
