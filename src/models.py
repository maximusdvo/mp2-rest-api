"""pydantic models for API requests and response"""

from pydantic import BaseModel, Field
class HealthResponse(BaseModel):
    """response treutnred by health check enpoint"""

    status:str
    version: str

class DatasetInfo(BaseModel):
    """metadata returned after a dataset is uploaded"""

    id: int
    filename: str
    rows: int
    columns: int
    column_names: list[str]


class ValidationSettings(BaseModel):
    required_columns: list[str] = Field(default_factory=list)
    numeric_columns: list[str] = Field(default_factory=list)

class MissingSettings(BaseModel):
    enabled: bool = True
    axis: str = "rows"

class OutlierSettings(BaseModel):
    """settings for outlier removal"""

    enabled: bool = False
    columns: list[str] = Field(default_factory=list)
    method: str = "iqr"
    threshold: float = 1.5

class ProcessingSettings(BaseModel):
    """cleaning steps to apply, the same as MP1 processing section"""
    remove_duplicates: bool = True
    missing: MissingSettings = Field(default_factory=MissingSettings)
    outliers: OutlierSettings = Field(default_factory=OutlierSettings)

class ProcessConfig(BaseModel):
    """the full request body for processing a dataset"""

    validation: ValidationSettings = Field(default_factory=ValidationSettings)
    processing: ProcessingSettings = Field(default_factory=ProcessingSettings)


class ProcessingReport(BaseModel):
    """response returned after a dataset is processed"""

    id: int
    validation_rows_removed: int
    cleaning_report: dict[str, int]
