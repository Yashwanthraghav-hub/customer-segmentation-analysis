# Customer Segmentation Analysis

A full-stack customer analytics application that turns customer CSV files into exploratory analysis, RFM audiences, explainable KMeans segments, and action-oriented recommendations.

## Features

- Secure Supabase email/password and Google OAuth integration when configured
- Protected React dashboard with an immediate one-click sample-data experience
- CSV validation, flexible column recognition, preview, and data-quality reporting
- Interactive EDA: demographic, income, spend, category, and relationship charts
- RFM scoring with business-friendly lifecycle audiences
- Dynamic KMeans selection (K=2–8), scaling, silhouette validation, PCA plotting, and segment profiles
- Exportable segmented customers, RFM results, and analytics summary

## Architecture

`frontend/` is a Vite + React + TypeScript interface. `backend/` is a FastAPI service using Pandas and scikit-learn. Supabase provides hosted authentication and optional user-owned metadata persistence; [supabase/schema.sql](supabase/schema.sql) applies row-level-security policies.

## Dataset

[data/sample_customers.csv](data/sample_customers.csv) contains 700 synthetic customer records. It is generated deterministically with `python scripts/generate_sample_data.py`; it contains no personal data.

Expected columns are flexible, but the demo schema includes `customer_id`, `age`, `gender`, `city`, `annual_income`, `total_spend`, `purchase_frequency`, `average_order_value`, `recency_days`, `total_orders`, `preferred_category`, `customer_tenure_months`, `discount_usage`, `website_visits`, and `satisfaction_score`.

## Run locally

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

In another terminal:

```bash
cd frontend
npm install
npm run dev
```

Copy `.env.example` to the applicable frontend/backend environment file and set the Supabase URL, anonymous key, and API base URL. Public Supabase keys may be used in the frontend; never use a service-role key there.

## Testing

```bash
$env:PYTHONPATH = "backend"
python -m pytest backend/tests -q
cd frontend && npm run build
```

## API

- `GET /api/health`
- `POST /api/upload`
- `POST /api/preview`, `/api/analyze`, `/api/rfm`, `/api/segment`, `/api/insights`
- `POST /api/export/{segmented|rfm|summary}`

## Deployment

[render.yaml](render.yaml) declares the Python service. Set `CORS_ORIGINS` to the deployed frontend domain and configure `VITE_API_BASE_URL` in the frontend host. Set Supabase redirect URLs to `https://YOUR-FRONTEND/auth/callback` before enabling Google OAuth.

## Security

The repository contains no secrets. Uploads accept CSV only, have a configurable size cap, and parsing errors are returned as safe messages. The included Supabase policies restrict profiles, dataset metadata, and analysis metadata to their owner.

## Author

Yashwanth Raghav — [GitHub repository](https://github.com/Yashwanthraghav-hub/customer-segmentation-analysis)
