import pandas as pd
from app.services.clustering import cluster

def test_clustering_returns_assignments():
    data = pd.DataFrame({'annual_income':[30,31,32,80,82,85], 'total_spend':[100,120,110,900,880,920], 'purchase_frequency':[1,2,1,9,8,10], 'recency_days':[40,35,42,2,3,1]})
    result, metadata = cluster(data)
    assert len(result) == len(data)
    assert metadata['selected_k'] >= 2
