import pandas as pd
from app.services.rfm import run_rfm

def test_rfm_assigns_every_customer():
    data = pd.DataFrame({'recency_days':range(1,16), 'purchase_frequency':range(15,0,-1), 'total_spend':[v*100 for v in range(1,16)]})
    result = run_rfm(data)
    assert len(result) == 15 and result.rfm_segment.notna().all()
