from __future__ import annotations
import io
import json
import logging
from typing import Any
import pandas as pd
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel, Field
from .config import settings
from .services.analytics import summary
from .services.clustering import cluster
from .services.preprocessing import clean_for_analysis, quality_report, standardise
from .services.rfm import run_rfm

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
app = FastAPI(title="Customer Segmentation API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=settings.origins, allow_credentials=True, allow_methods=["GET", "POST"], allow_headers=["Authorization", "Content-Type"])

class DatasetRequest(BaseModel):
    records: list[dict[str, Any]] = Field(min_length=1, max_length=10000)
    mapping: dict[str, str] | None = None

def prepare(request: DatasetRequest) -> tuple[pd.DataFrame, dict]:
    try:
        raw = pd.DataFrame(request.records)
        standard, mapping = standardise(raw, request.mapping)
        return clean_for_analysis(standard), {"mapping": mapping, "quality": quality_report(standard)}
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error))

@app.get("/api/health")
def health(): return {"status": "healthy", "service": settings.app_name}

@app.post("/api/preview")
def preview(request: DatasetRequest):
    frame, meta = prepare(request)
    return {**meta, "preview": frame.head(25).where(pd.notnull(frame), None).to_dict("records")}

@app.post("/api/analyze")
def analyze(request: DatasetRequest):
    frame, meta = prepare(request)
    return {**meta, "analytics": summary(frame)}

@app.post("/api/segment")
def segment(request: DatasetRequest):
    frame, meta = prepare(request)
    try:
        segmented, output = cluster(frame)
        output["points"] = segmented[["pca_x", "pca_y", "cluster_id", "segment_name"] + [col for col in ["annual_income", "total_spend"] if col in segmented]].head(1000).to_dict("records")
        return {**meta, "segmentation": output}
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error))

@app.post("/api/rfm")
def rfm(request: DatasetRequest):
    frame, meta = prepare(request)
    try:
        result = run_rfm(frame)
        distribution = [{"label": str(key), "value": int(value)} for key, value in result.rfm_segment.value_counts().items()]
        return {**meta, "distribution": distribution, "records": result.where(pd.notnull(result), None).to_dict("records")}
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error))

@app.post("/api/insights")
def insights(request: DatasetRequest):
    frame, _ = prepare(request)
    segmented, details = cluster(frame)
    profiles = details["profiles"]
    highest = max(profiles, key=lambda profile: profile["averages"].get("total_spend", 0))
    largest = max(profiles, key=lambda profile: profile["count"])
    insights = [
        {"title": "Highest-value segment", "body": f"{highest['name']} has the strongest average customer value.", "priority": "High"},
        {"title": "Largest opportunity", "body": f"{largest['name']} represents {largest['percentage']}% of customers.", "priority": "Medium"},
    ]
    if "preferred_category" in frame:
        category = frame.preferred_category.mode().iat[0]
        insights.append({"title": "Category demand", "body": f"{category} is the most popular customer category.", "priority": "Medium"})
    return {"insights": insights, "recommendations": [{"segment": p["name"], "opportunity": "Improve lifetime value", "action": p["strategy"], "priority": "High" if "High-Value" in p["name"] or "At-Risk" in p["name"] else "Medium"} for p in profiles]}

@app.post("/api/export/{kind}")
def export(kind: str, request: DatasetRequest):
    frame, _ = prepare(request)
    if kind == "segmented": result, _ = cluster(frame)
    elif kind == "rfm": result = run_rfm(frame)
    elif kind == "summary": return Response(content=json.dumps(summary(frame), default=str), media_type="application/json", headers={"Content-Disposition": "attachment; filename=analytics-summary.json"})
    else: raise HTTPException(status_code=404, detail="Export type not found.")
    return Response(content=result.to_csv(index=False), media_type="text/csv", headers={"Content-Disposition": f"attachment; filename={kind}.csv"})

@app.post("/api/upload")
async def upload(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".csv"): raise HTTPException(status_code=415, detail="Please upload a CSV file.")
    content = await file.read()
    if len(content) > settings.max_upload_mb * 1024 * 1024: raise HTTPException(status_code=413, detail="File exceeds the upload limit.")
    try: frame = pd.read_csv(io.BytesIO(content))
    except Exception: raise HTTPException(status_code=422, detail="This CSV could not be read. Check its format and encoding.")
    try:
        standard, mapping = standardise(frame)
        return {"mapping": mapping, "quality": quality_report(standard), "preview": standard.head(25).where(pd.notnull(standard), None).to_dict("records")}
    except ValueError as error: raise HTTPException(status_code=422, detail=str(error))
