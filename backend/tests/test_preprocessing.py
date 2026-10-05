import pandas as pd
from app.services.preprocessing import standardise, quality_report

def test_detects_common_columns():
    frame, mapping = standardise(pd.DataFrame({'CustomerID':['a'], 'Age':[25], 'income':[1000], 'spending':[200]}))
    assert {'customer_id', 'age', 'annual_income', 'total_spend'}.issubset(frame.columns)
    assert quality_report(frame)['rows'] == 1
