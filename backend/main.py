"""
==========================================
ECG Clinical Decision Support System
Production FastAPI Application Entrypoint
==========================================
"""

import time
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.api.routes import get_ecg_predictor, get_feature_extractor, router
from backend.config.logging_config import setup_logger
from backend.config.settings import API_VERSION, APP_NAME
from backend.middleware.timing_middleware import RequestTimingMiddleware

logger = setup_logger("main")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    FastAPI Lifespan Context Manager:
    Pre-warms ML model loading and SHAP TreeExplainers during app startup.
    """
    logger.info("Initializing ECG CDSS Production Server boot sequence...")
    start_time = time.perf_counter()

    try:
        # Pre-warm singletons during startup
        get_feature_extractor()
        predictor = get_ecg_predictor()

        # Dummy forward pass to ensure pipeline model and explainers execute cleanly
        logger.info("Running pre-warm dummy forward pass...")
        dummy_raw = {feat: 0.0 for feat in predictor.loader.feature_names_in}
        dummy_raw_df = predictor.align_raw_features(dummy_raw)
        dummy_prep_df = predictor.preprocess_features(dummy_raw_df)
        predictor.predict_probabilities(dummy_prep_df)
        predictor.explainer.top_features(dummy_prep_df, predictor.loader.class_names[0])

        boot_duration = time.perf_counter() - start_time
        logger.info(f"ECG CDSS Models pre-warmed & verified successfully in {boot_duration:.3f}s. Server ready.")
    except Exception as e:
        logger.critical(f"FATAL: Failed to initialize ML model pipeline during startup: {e}", exc_info=True)
        raise e

    yield

    logger.info("ECG CDSS Production Server shutting down...")


app = FastAPI(
    title=APP_NAME,
    description=(
        "Automatic 12-Lead ECG Classification and Clinical Decision Support API using "
        "XGBoost Multi-Output Classification, SHAP Explainability, and Signal Quality Index (SQI) validation."
    ),
    version=API_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# --------------------------------------------------------
# Register Custom Middlewares
# --------------------------------------------------------

app.add_middleware(RequestTimingMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------------------------------------
# Global Exception Handlers
# --------------------------------------------------------

@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Standardized JSON response for HTTP exceptions."""
    logger.warning(f"HTTPException [{exc.status_code}] on {request.method} {request.url.path}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "status_code": exc.status_code, "path": request.url.path},
    )


@app.exception_handler(ValueError)
async def custom_value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
    """Handler for validation / data format ValueErrors."""
    logger.warning(f"ValueError on {request.method} {request.url.path}: {exc}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": str(exc), "status_code": 400, "path": request.url.path},
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Unhandled internal server error catch-all handler."""
    logger.error(f"Unhandled Exception on {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": f"Internal Server Error: {str(exc)}",
            "status_code": 500,
            "path": request.url.path,
        },
    )

# --------------------------------------------------------
# Register API Router
# --------------------------------------------------------

app.include_router(router)