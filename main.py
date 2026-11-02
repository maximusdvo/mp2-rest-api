"""fastAPi application for the uploading and retrieving datasets!"""

import io
import json
import logging
from pathlib import Path

import pandas as pd
from fastapi import FastAPI, File, HTTPException, Query, UploadFile

from src import (
    DatasetInfo,
    DatasetStorage,
    HealthResponse,
    setup_logging,
    ProcessingReport,
    ProcessConfig,
    log_requests,
)
from data_pipeline import create_cleaning_report, process_data, validate_dataframe
setup_logging(verbose=True)
logger = logging.getLogger(__name__)

app = FastAPI(title="Data Processing API", version="1.0.0")
app.middleware("http")(log_requests)
storage = DatasetStorage()

@app.get("/health", response_model=HealthResponse)
def health_check():
    """returns application status and version"""
    return{"status": "ok", "version": app.version}

@app.post("/upload", response_model=DatasetInfo)
async def upload_dataset(file: UploadFile = File(...)):
    """read and stores the csv upload"""
    filename = file.filename or ""
    extension = Path(filename).suffix.lower()
    if extension != ".csv":
        logger.warning("Unsupported file format: %s", extension)
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format: {extension}. Only .csv files are accepted.",
        )

    contents = await file.read()
    try:
        df = pd.read_csv(io.BytesIO(contents))
    except (pd.errors.EmptyDataError, pd.errors.ParserError, UnicodeDecodeError) as error:
        logger.warning("Could not read CSV %s: %s", filename, error)
        raise HTTPException(
            status_code=400,
            detail="could not read the file as CSV. check that it is a non-empty, valid CSV."
        ) from error

    dataset_id =  storage.save(df, filename)
    logger.info(
        "Uploaded dataset: id=%d, filename=%s, rows=%d", dataset_id, filename, len(df)
    )
    return storage.get_metadata(dataset_id)

@app.get("/datasets/{dataset_id}")
def get_dataset(dataset_id: int, limit: int = Query(default=100, ge=1)):
    """Return up to limit rows from a stored dataset."""
    df = storage.get(dataset_id)
    if df is None:
        logger.warning("Dataset not found: %d", dataset_id)
        raise HTTPException(status_code=404, detail=f"Dataset {dataset_id} not found")

    records = json.loads(df.head(limit).to_json(orient="records"))
    logger.info("Retrieved dataset: id=%d, returned_rows=%d", dataset_id, len(records))
    return {"id": dataset_id, "data": records, "total_rows": len(df)}

@app.post(
    "/dataset/{dataset_id}/process",
    response_model=ProcessingReport
)
def process_dataset(dataset_id: int, config: ProcessConfig):
    """validates and processes a stored dataset using MP1 functions:"""
    df = storage.get(dataset_id)
    if df is None:
        logger.warning("Dataset not found: %d", dataset_id)
        raise HTTPException(status_code=404, detail=f"dataset {dataset_id} not found")

    config_dict = config.model_dump()
    required_columns = config_dict["validation"]["required_columns"]
    numeric_columns = config_dict["validation"]["numeric_columns"]

    missing_numeric = [col for col in numeric_columns if col not in df.columns]
    if missing_numeric:
        logger.warning("numeric column(s) not found in dataset %d: %s", dataset_id, missing_numeric)
        raise HTTPException(
            status_code=400,
            detail=f"Numeric column(s) not found: {', '.join(missing_numeric)}",
        )
    try:
        rows_before_validation = len(df)
        validated = validate_dataframe(df, required_columns, numeric_columns)
        validation_removed = rows_before_validation - len(validated)
        validated_copy = validated.copy()

        processed = process_data(validated, config_dict)
    except ValueError as error:
        logger.warning("Processing failed for dataset %d: %s", dataset_id, error)
        raise HTTPException(status_code=400, detail=str(error)) from error

    report = create_cleaning_report(validated_copy, processed)
    storage.update(dataset_id, processed)

    logger.info(
        "Processed dataset: id=%d, validation_removed=%d, rows_before=%d, rows_after=%d",
        dataset_id, validation_removed, report["rows_before"], report["rows_after"],
    )
    return {
        "id": dataset_id,
        "validation_rows_removed": validation_removed,
        "cleaning_report": report,
    }
