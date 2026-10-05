from __future__ import annotations
import pandas as pd


def _distribution(frame: pd.DataFrame, column: str, bins: int = 12):
    if column not in frame: return []
    values = pd.to_numeric(frame[column], errors="coerce").dropna()
    if values.empty: return []
    grouped = pd.cut(values, bins=min(bins, max(2, values.nunique())), duplicates="drop").value_counts().sort_index()
    return [{"label": str(index), "value": int(value)} for index, value in grouped.items()]


def summary(frame: pd.DataFrame) -> dict:
    def avg(column): return round(float(pd.to_numeric(frame[column], errors="coerce").mean()), 2) if column in frame else None
    total_spend = float(pd.to_numeric(frame.get("total_spend", pd.Series(dtype=float)), errors="coerce").sum())
    top_category = None
    if "preferred_category" in frame and not frame["preferred_category"].dropna().empty:
        top_category = str(frame["preferred_category"].mode().iat[0])
    charts = {key: _distribution(frame, key) for key in ["age", "annual_income", "total_spend", "purchase_frequency", "satisfaction_score"]}
    for column, key in [("gender", "gender"), ("city", "city"), ("preferred_category", "category")]:
        if column in frame:
            charts[key] = [{"label": str(k), "value": int(v)} for k, v in frame[column].value_counts().head(10).items()]
    scatter = []
    if {"annual_income", "total_spend"}.issubset(frame.columns):
        scatter = frame[["annual_income", "total_spend"]].dropna().head(500).rename(columns={"annual_income": "x", "total_spend": "y"}).to_dict("records")
    top_customers = frame.sort_values("total_spend", ascending=False).head(10) if "total_spend" in frame else frame.head(10)
    return {"kpis": {"total_customers": int(len(frame)), "total_revenue": round(total_spend, 2), "average_customer_spend": avg("total_spend"), "average_order_value": avg("average_order_value"), "average_purchase_frequency": avg("purchase_frequency"), "average_customer_age": avg("age"), "top_category": top_category}, "charts": charts, "income_spend": scatter, "top_customers": top_customers.head(10).fillna("").to_dict("records")}
