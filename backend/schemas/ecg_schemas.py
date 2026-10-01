"""
=========================================================
ECG Pydantic Response & Data Schemas
ECG Clinical Decision Support System
=========================================================
Defines strict Pydantic models for OpenAPI documentation
and API response validation.
=========================================================
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class ShapFeatureModel(BaseModel):
    """Schema for individual SHAP feature attribution items."""
    Feature: str = Field(..., description="Raw feature identifier")
    SHAP: float = Field(..., description="Raw SHAP attribution score")
    AbsSHAP: float = Field(..., description="Absolute SHAP magnitude")
    clean_name: str = Field(..., description="Physician-readable feature label")
    direction: str = Field(..., description="Feature impact direction: 'positive' or 'negative'")
    interpretation: str = Field(..., description="Clinical explanation sentence")


class SignalQualityModel(BaseModel):
    """Schema for 12-lead signal quality assessment (SQI)."""
    sqi_score: float = Field(..., description="Signal Quality Index score (0-100%)")
    status: str = Field(..., description="SQI status: 'Excellent', 'Acceptable', or 'Poor'")
    samples: int = Field(..., description="Total samples in ECG recording")
    n_leads: int = Field(..., description="Number of ECG leads analyzed")
    flatline_leads: List[str] = Field(default_factory=list, description="Disconnected or flatline leads")
    saturated_leads: List[str] = Field(default_factory=list, description="Voltage saturation leads")
    noisy_leads: List[str] = Field(default_factory=list, description="High baseline noise leads")


class RecordInfoModel(BaseModel):
    """Schema for WFDB ECG record metadata."""
    record_id: str = Field(..., description="ECG record ID or filename")
    timestamp: str = Field(..., description="ISO analysis timestamp")
    fs: float = Field(..., description="Sampling frequency in Hz")
    duration_seconds: float = Field(..., description="Recording duration in seconds")
    n_leads: int = Field(..., description="Number of ECG leads")
    hea_filename: str = Field(..., description="Input header filename")
    dat_filename: str = Field(..., description="Input signal data filename")
    extracted_features_count: Optional[int] = Field(322, description="Total raw extracted ECG features")
    model_features_count: Optional[int] = Field(274, description="Total preprocessed model features")



class WaveformDataModel(BaseModel):
    """Schema for 12-lead ECG signal data."""
    leads: Dict[str, List[float]] = Field(..., description="Lead name to signal voltage array mapping")
    time: List[float] = Field(..., description="Time axis in seconds")
    fs: float = Field(..., description="Sampling frequency in Hz")


class ECGPredictionResponseModel(BaseModel):
    """Schema for complete ECG prediction payload."""
    diagnosis: str = Field(..., description="Predicted diagnostic class: NORM, MI, CD, HYP, STTC")
    confidence: float = Field(..., description="Model certainty percentage (0-100%)")
    risk_level: str = Field(..., description="Clinical triage tier: Low, Medium, High")
    recommendation: str = Field(..., description="Medical action recommendation")
    probabilities: Dict[str, float] = Field(..., description="Probability breakdown across diagnostic classes")
    top_features: List[ShapFeatureModel] = Field(..., description="Top SHAP feature attributions")
    record_info: Optional[RecordInfoModel] = Field(None, description="Record metadata")
    waveform_data: Optional[WaveformDataModel] = Field(None, description="Actual signal waveform data")
    clinical_evidence: Optional[List[str]] = Field(None, description="Extracted clinical evidence statements")
    review_guidance: Optional[List[str]] = Field(None, description="Appropriate review guidance for clinician")
    signal_quality: Optional[SignalQualityModel] = Field(None, description="Signal quality metrics")
    clinical_warnings: Optional[List[str]] = Field(None, description="Clinical alerts and warnings")
    disclaimer: Optional[str] = Field(None, description="CDSS medical disclaimer")


class HealthResponseModel(BaseModel):
    """Schema for API health status."""
    status: str = Field(..., description="Health status indicator")
    model_loaded: bool = Field(..., description="Indicates if ML pipeline is loaded and ready")
    uptime_seconds: float = Field(..., description="System uptime in seconds")
    version: str = Field(..., description="API version")


class HomeResponseModel(BaseModel):
    """Schema for application metadata root endpoint."""
    application: str = Field(..., description="Application name")
    version: str = Field(..., description="Application version")
    status: str = Field(..., description="Application state")

