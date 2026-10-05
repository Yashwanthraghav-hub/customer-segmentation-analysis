from __future__ import annotations
import pandas as pd


def run_rfm(frame: pd.DataFrame) -> pd.DataFrame:
    required = {"recency_days", "total_spend"}
    if not required.issubset(frame.columns):
        raise ValueError("RFM needs recency_days and total_spend (or mapped equivalent) columns.")
    result = frame.copy()
    frequency = "purchase_frequency" if "purchase_frequency" in result else "total_orders"
    if frequency not in result: raise ValueError("RFM also needs purchase_frequency or total_orders.")
    result["recency_score"] = pd.qcut(result["recency_days"].rank(method="first"), 5, labels=[5,4,3,2,1]).astype(int)
    result["frequency_score"] = pd.qcut(result[frequency].rank(method="first"), 5, labels=[1,2,3,4,5]).astype(int)
    result["monetary_score"] = pd.qcut(result["total_spend"].rank(method="first"), 5, labels=[1,2,3,4,5]).astype(int)
    result["rfm_score"] = result[["recency_score", "frequency_score", "monetary_score"]].sum(axis=1)
    def label(row):
        if row.rfm_score >= 13: return "Champions"
        if row.frequency_score >= 4 and row.recency_score >= 3: return "Loyal Customers"
        if row.recency_score >= 4: return "New Customers"
        if row.recency_score <= 2 and row.monetary_score >= 4: return "Cannot Lose Them"
        if row.recency_score <= 2: return "At Risk"
        if row.rfm_score <= 7: return "Hibernating"
        return "Potential Loyalists"
    result["rfm_segment"] = result.apply(label, axis=1)
    return result
