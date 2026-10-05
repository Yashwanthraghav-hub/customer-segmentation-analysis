"""Create reproducible, realistic demonstration data (no personal data)."""
from pathlib import Path
import numpy as np
import pandas as pd

rng = np.random.default_rng(42)
n = 700
profiles = rng.choice(["champion", "regular", "at_risk", "new"], n, p=[.22,.38,.23,.17])
rows = []
for i, profile in enumerate(profiles, 1):
    params = {"champion": (88, 2400, 9.5, 5, 24), "regular": (56, 950, 4.8, 22, 16), "at_risk": (64, 680, 2.3, 94, 28), "new": (43, 420, 1.8, 10, 4)}[profile]
    age = int(np.clip(rng.normal(params[0]-8, 11), 18, 76)); income = round(max(18000, rng.normal(params[0]*950, 16000)), 2)
    frequency = round(max(.5, rng.normal(params[2], 1.4)), 1); spend = round(max(40, rng.normal(params[1], params[1]*.24)), 2)
    rows.append({"customer_id": f"CUS-{i:04d}", "age": age, "gender": rng.choice(["Female","Male","Non-binary"], p=[.48,.48,.04]), "city": rng.choice(["Bengaluru","Mumbai","Delhi","Hyderabad","Pune","Chennai"]), "annual_income": income, "total_spend": spend, "purchase_frequency": frequency, "average_order_value": round(spend/max(frequency, .5),2), "recency_days": int(max(0,rng.normal(params[3], max(3,params[3]*.25)))), "total_orders": int(max(1, round(frequency*3))), "preferred_category": rng.choice(["Electronics","Fashion","Home & Living","Beauty","Sports"]), "customer_tenure_months": int(max(1,rng.normal(params[4],7))), "discount_usage": round(float(rng.uniform(.02,.8)),2), "website_visits": int(max(1,rng.normal(11,5))), "satisfaction_score": round(float(np.clip(rng.normal(4.0 if profile != 'at_risk' else 3.0,.55),1,5)),1)})
target = Path(__file__).resolve().parents[1] / "data" / "sample_customers.csv"
target.parent.mkdir(exist_ok=True)
pd.DataFrame(rows).to_csv(target, index=False)
print(target)
