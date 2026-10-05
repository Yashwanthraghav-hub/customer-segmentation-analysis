from __future__ import annotations
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

FEATURES = ["annual_income", "total_spend", "purchase_frequency", "average_order_value", "recency_days", "customer_tenure_months", "satisfaction_score"]

def _name(row: pd.Series, overall: pd.Series) -> str:
    spend = row.get("total_spend", 0) >= overall.get("total_spend", 0)
    frequency = row.get("purchase_frequency", 0) >= overall.get("purchase_frequency", 0)
    recency = row.get("recency_days", overall.get("recency_days", 0)) <= overall.get("recency_days", 0)
    if spend and frequency and recency: return "High-Value Champions"
    if spend and frequency: return "Loyal High Spenders"
    if not recency: return "At-Risk Customers"
    if frequency: return "Budget Regulars"
    return "Growth Potential Customers"

def cluster(frame: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    features = [column for column in FEATURES if column in frame.columns and frame[column].notna().any()]
    if len(features) < 2 or len(frame) < 4: raise ValueError("Segmentation needs at least four rows and two usable numeric features.")
    matrix = frame[features].apply(pd.to_numeric, errors="coerce").fillna(frame[features].apply(pd.to_numeric, errors="coerce").median())
    matrix = matrix.fillna(0)
    scaled = StandardScaler().fit_transform(matrix)
    upper = min(8, len(frame)-1)
    candidates = []
    for k in range(2, upper + 1):
        model = KMeans(n_clusters=k, n_init=15, random_state=42).fit(scaled)
        score = silhouette_score(scaled, model.labels_) if len(set(model.labels_)) > 1 else -1
        candidates.append((k, float(score), float(model.inertia_)))
    selected_k = max(candidates, key=lambda item: item[1])[0]
    model = KMeans(n_clusters=selected_k, n_init=20, random_state=42).fit(scaled)
    result = frame.copy(); result["cluster_id"] = model.labels_
    profiles = result.groupby("cluster_id")[features].mean().round(2)
    overall = result[features].mean()
    base_names = {int(index): _name(row, overall) for index, row in profiles.iterrows()}
    seen = {}
    names = {}
    for key, value in base_names.items():
        seen[value] = seen.get(value, 0) + 1
        names[key] = value if seen[value] == 1 else f"{value} {seen[value]}"
    result["segment_name"] = result.cluster_id.map(names)
    components = PCA(n_components=2, random_state=42).fit_transform(scaled)
    result["pca_x"], result["pca_y"] = components[:, 0], components[:, 1]
    profile_records = []
    for cluster_id, row in profiles.iterrows():
        members = result[result.cluster_id == cluster_id]
        strategy = "Prioritize personalized offers and monitor engagement."
        if names[int(cluster_id)].startswith("High-Value"): strategy = "Protect loyalty with VIP rewards, early access, and premium personalization."
        elif "At-Risk" in names[int(cluster_id)]: strategy = "Launch a timely re-engagement campaign with relevant incentives."
        profile_records.append({"cluster_id": int(cluster_id), "name": names[int(cluster_id)], "count": int(len(members)), "percentage": round(100*len(members)/len(result),1), "averages": {key: float(value) for key,value in row.items()}, "strategy": strategy})
    return result, {"selected_k": selected_k, "silhouette_score": round(max(candidates, key=lambda item:item[1])[1], 3), "features": features, "candidates": [{"k": k,"silhouette":round(s,3),"inertia":round(i,2)} for k,s,i in candidates], "profiles": profile_records}
