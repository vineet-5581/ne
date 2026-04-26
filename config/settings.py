"""
Configuration Management Module
Centralized configuration for the Document AI System
Supports environment variables, config files, and defaults
"""

import os
import json
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


@dataclass
class PathConfig:
    """Path configuration"""
    BASE_DIR: Path = field(default_factory=lambda: Path(__file__).parent.parent)
    INPUT_DIR: Path = field(default_factory=lambda: Path(__file__).parent.parent / "inputs")
    OUTPUT_DIR: Path = field(default_factory=lambda: Path(__file__).parent.parent / "outputs")
    TEMP_DIR: Path = field(default_factory=lambda: Path(__file__).parent.parent / "temp")
    LOGS_DIR: Path = field(default_factory=lambda: Path(__file__).parent.parent / "logs")
    MODELS_DIR: Path = field(default_factory=lambda: Path(__file__).parent.parent / "models")
    CACHE_DIR: Path = field(default_factory=lambda: Path(__file__).parent.parent / "cache")
    REPORTS_DIR: Path = field(default_factory=lambda: Path(__file__).parent.parent / "reports")

    def __post_init__(self):
        """Create directories if they don't exist"""
        for dir_path in [self.INPUT_DIR, self.OUTPUT_DIR, self.TEMP_DIR, 
                         self.LOGS_DIR, self.MODELS_DIR, self.CACHE_DIR, self.REPORTS_DIR]:
            dir_path.mkdir(parents=True, exist_ok=True)


@dataclass
class LoggingConfig:
    """Logging configuration"""
    LEVEL: str = field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))
    FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    DATE_FORMAT: str = "%Y-%m-%d %H:%M:%S"
    FILE_NAME: str = "document_ai.log"
    MAX_BYTES: int = 10485760  # 10MB
    BACKUP_COUNT: int = 5
    ENABLE_FILE_LOGGING: bool = field(default_factory=lambda: os.getenv("FILE_LOGGING", "true").lower() == "true")
    ENABLE_CONSOLE_LOGGING: bool = field(default_factory=lambda: os.getenv("CONSOLE_LOGGING", "true").lower() == "true")


@dataclass
class PDFConfig:
    """PDF Processing Configuration"""
    MAX_FILE_SIZE_MB: int = field(default_factory=lambda: int(os.getenv("MAX_PDF_SIZE", "100")))
    SUPPORTED_FORMATS: List[str] = field(default_factory=lambda: [".pdf"])
    DPI_FOR_OCR: int = field(default_factory=lambda: int(os.getenv("PDF_DPI", "300")))
    EXTRACT_IMAGES: bool = field(default_factory=lambda: os.getenv("EXTRACT_IMAGES", "true").lower() == "true")
    PRESERVE_FORMATTING: bool = field(default_factory=lambda: os.getenv("PRESERVE_FORMATTING", "true").lower() == "true")
    DETECT_TABLES: bool = field(default_factory=lambda: os.getenv("DETECT_TABLES", "true").lower() == "true")


@dataclass
class OCRConfig:
    """OCR Configuration"""
    ENABLE_OCR: bool = field(default_factory=lambda: os.getenv("ENABLE_OCR", "true").lower() == "true")
    OCR_ENGINE: str = field(default_factory=lambda: os.getenv("OCR_ENGINE", "tesseract"))  # tesseract or easyocr
    TESSERACT_PATH: Optional[str] = field(default_factory=lambda: os.getenv("TESSERACT_PATH"))
    LANGUAGE: str = field(default_factory=lambda: os.getenv("OCR_LANGUAGE", "eng"))
    MULTIPLE_LANGUAGES: List[str] = field(default_factory=lambda: os.getenv("OCR_LANGUAGES", "eng").split(","))
    PREPROCESSING_ENABLED: bool = field(default_factory=lambda: os.getenv("OCR_PREPROCESSING", "true").lower() == "true")
    CONFIDENCE_THRESHOLD: float = field(default_factory=lambda: float(os.getenv("OCR_CONFIDENCE", "0.5")))
    DESKEW: bool = field(default_factory=lambda: os.getenv("OCR_DESKEW", "true").lower() == "true")
    DENOISE: bool = field(default_factory=lambda: os.getenv("OCR_DENOISE", "true").lower() == "true")


@dataclass
class ComputerVisionConfig:
    """Computer Vision Configuration"""
    USE_DETECTRON2: bool = field(default_factory=lambda: os.getenv("USE_DETECTRON2", "true").lower() == "true")
    USE_YOLO: bool = field(default_factory=lambda: os.getenv("USE_YOLO", "false").lower() == "true")
    LAYOUT_MODEL: str = field(default_factory=lambda: os.getenv("LAYOUT_MODEL", "layoutlmv3"))
    CONFIDENCE_THRESHOLD: float = field(default_factory=lambda: float(os.getenv("CV_CONFIDENCE", "0.5")))
    DEVICE: str = field(default_factory=lambda: os.getenv("CV_DEVICE", "cpu"))  # cpu or cuda
    BATCH_SIZE: int = field(default_factory=lambda: int(os.getenv("CV_BATCH_SIZE", "1")))


@dataclass
class NLPConfig:
    """NLP Configuration"""
    ENABLE_NLP: bool = field(default_factory=lambda: os.getenv("ENABLE_NLP", "true").lower() == "true")
    MODEL_NAME: str = field(default_factory=lambda: os.getenv("NLP_MODEL", "bert-base-uncased"))
    DEVICE: str = field(default_factory=lambda: os.getenv("NLP_DEVICE", "cpu"))
    BATCH_SIZE: int = field(default_factory=lambda: int(os.getenv("NLP_BATCH_SIZE", "32")))
    MAX_SEQUENCE_LENGTH: int = field(default_factory=lambda: int(os.getenv("NLP_MAX_SEQ", "512")))
    CONFIDENCE_THRESHOLD: float = field(default_factory=lambda: float(os.getenv("NLP_CONFIDENCE", "0.5")))


@dataclass
class WordGenerationConfig:
    """Word Document Generation Configuration"""
    PRESERVE_IMAGES: bool = field(default_factory=lambda: os.getenv("PRESERVE_IMAGES", "true").lower() == "true")
    PRESERVE_COLORS: bool = field(default_factory=lambda: os.getenv("PRESERVE_COLORS", "true").lower() == "true")
    PRESERVE_FONTS: bool = field(default_factory=lambda: os.getenv("PRESERVE_FONTS", "true").lower() == "true")
    AUTO_HEADING_DETECTION: bool = field(default_factory=lambda: os.getenv("AUTO_HEADING_DETECTION", "true").lower() == "true")
    DEFAULT_FONT: str = field(default_factory=lambda: os.getenv("DEFAULT_FONT", "Calibri"))
    DEFAULT_FONT_SIZE: int = field(default_factory=lambda: int(os.getenv("DEFAULT_FONT_SIZE", "11")))
    LINE_SPACING: float = field(default_factory=lambda: float(os.getenv("LINE_SPACING", "1.15")))
    PAGE_MARGINS: Dict[str, float] = field(default_factory=lambda: {
        "top": float(os.getenv("MARGIN_TOP", "1")),
        "bottom": float(os.getenv("MARGIN_BOTTOM", "1")),
        "left": float(os.getenv("MARGIN_LEFT", "1")),
        "right": float(os.getenv("MARGIN_RIGHT", "1"))
    })


@dataclass
class ProcessingConfig:
    """Document Processing Configuration"""
    PARALLEL_PROCESSING: bool = field(default_factory=lambda: os.getenv("PARALLEL_PROCESSING", "true").lower() == "true")
    NUM_WORKERS: int = field(default_factory=lambda: int(os.getenv("NUM_WORKERS", "4")))
    TIMEOUT_SECONDS: int = field(default_factory=lambda: int(os.getenv("TIMEOUT_SECONDS", "300")))
    ENABLE_CACHING: bool = field(default_factory=lambda: os.getenv("ENABLE_CACHING", "true").lower() == "true")
    CACHE_TTL_HOURS: int = field(default_factory=lambda: int(os.getenv("CACHE_TTL", "24")))
    ENABLE_COMPRESSION: bool = field(default_factory=lambda: os.getenv("ENABLE_COMPRESSION", "false").lower() == "true")
    COMPRESSION_LEVEL: int = field(default_factory=lambda: int(os.getenv("COMPRESSION_LEVEL", "6")))
    BATCH_SIZE: int = field(default_factory=lambda: int(os.getenv("BATCH_SIZE", "5")))


@dataclass
class APIConfig:
    """API Configuration"""
    HOST: str = field(default_factory=lambda: os.getenv("API_HOST", "0.0.0.0"))
    PORT: int = field(default_factory=lambda: int(os.getenv("API_PORT", "8000")))
    DEBUG: bool = field(default_factory=lambda: os.getenv("API_DEBUG", "false").lower() == "true")
    WORKERS: int = field(default_factory=lambda: int(os.getenv("API_WORKERS", "4")))
    RELOAD: bool = field(default_factory=lambda: os.getenv("API_RELOAD", "true").lower() == "true")
    ALLOW_ORIGINS: List[str] = field(default_factory=lambda: os.getenv("ALLOW_ORIGINS", "*").split(","))
    ALLOW_CREDENTIALS: bool = field(default_factory=lambda: os.getenv("ALLOW_CREDENTIALS", "true").lower() == "true")
    ALLOW_METHODS: List[str] = field(default_factory=lambda: ["GET", "POST", "PUT", "DELETE", "OPTIONS"])
    ALLOW_HEADERS: List[str] = field(default_factory=lambda: ["*"])
    MAX_UPLOAD_SIZE_MB: int = field(default_factory=lambda: int(os.getenv("MAX_UPLOAD_SIZE", "100")))
    RATE_LIMIT_ENABLED: bool = field(default_factory=lambda: os.getenv("RATE_LIMIT", "true").lower() == "true")
    RATE_LIMIT_REQUESTS: int = field(default_factory=lambda: int(os.getenv("RATE_LIMIT_REQ", "100")))
    RATE_LIMIT_PERIOD_SECONDS: int = field(default_factory=lambda: int(os.getenv("RATE_LIMIT_PERIOD", "60")))


@dataclass
class ClassificationConfig:
    """Document Classification Configuration"""
    ENABLE_CLASSIFICATION: bool = field(default_factory=lambda: os.getenv("ENABLE_CLASSIFICATION", "true").lower() == "true")
    CONFIDENCE_THRESHOLD: float = field(default_factory=lambda: float(os.getenv("CLASS_CONFIDENCE", "0.7")))
    SUPPORTED_TYPES: List[str] = field(default_factory=lambda: [
        "resume",
        "research_paper",
        "invoice",
        "form",
        "book_page",
        "article",
        "letter",
        "report",
        "contract",
        "other"
    ])


@dataclass
class TableExtractionConfig:
    """Table Extraction Configuration"""
    ENABLE_TABLE_EXTRACTION: bool = field(default_factory=lambda: os.getenv("ENABLE_TABLES", "true").lower() == "true")
    USE_PDFPLUMBER: bool = field(default_factory=lambda: os.getenv("USE_PDFPLUMBER", "true").lower() == "true")
    USE_DEEP_LEARNING: bool = field(default_factory=lambda: os.getenv("USE_DL_TABLES", "false").lower() == "true")
    MIN_TABLE_SIZE: int = field(default_factory=lambda: int(os.getenv("MIN_TABLE_SIZE", "2")))
    CONFIDENCE_THRESHOLD: float = field(default_factory=lambda: float(os.getenv("TABLE_CONFIDENCE", "0.5")))
    EXTRACT_TABLE_TEXT: bool = field(default_factory=lambda: os.getenv("EXTRACT_TABLE_TEXT", "true").lower() == "true")


@dataclass
class ReportingConfig:
    """Reporting Configuration"""
    GENERATE_REPORTS: bool = field(default_factory=lambda: os.getenv("GENERATE_REPORTS", "true").lower() == "true")
    REPORT_FORMAT: str = field(default_factory=lambda: os.getenv("REPORT_FORMAT", "json"))  # json or html
    INCLUDE_METRICS: bool = field(default_factory=lambda: os.getenv("INCLUDE_METRICS", "true").lower() == "true")
    INCLUDE_TIMING: bool = field(default_factory=lambda: os.getenv("INCLUDE_TIMING", "true").lower() == "true")
    INCLUDE_CONFIDENCE_SCORES: bool = field(default_factory=lambda: os.getenv("INCLUDE_CONFIDENCE", "true").lower() == "true")


@dataclass
class Settings:
    """Main Settings Class - Central Configuration Hub"""
    
    # Sub-configurations
    paths: PathConfig = field(default_factory=PathConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    pdf: PDFConfig = field(default_factory=PDFConfig)
    ocr: OCRConfig = field(default_factory=OCRConfig)
    cv: ComputerVisionConfig = field(default_factory=ComputerVisionConfig)
    nlp: NLPConfig = field(default_factory=NLPConfig)
    word: WordGenerationConfig = field(default_factory=WordGenerationConfig)
    processing: ProcessingConfig = field(default_factory=ProcessingConfig)
    api: APIConfig = field(default_factory=APIConfig)
    classification: ClassificationConfig = field(default_factory=ClassificationConfig)
    tables: TableExtractionConfig = field(default_factory=TableExtractionConfig)
    reporting: ReportingConfig = field(default_factory=ReportingConfig)
    
    # General settings
    APP_NAME: str = "Document AI System"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = field(default_factory=lambda: os.getenv("ENVIRONMENT", "development"))
    DEBUG: bool = field(default_factory=lambda: os.getenv("DEBUG", "false").lower() == "true")
    ENABLE_TELEMETRY: bool = field(default_factory=lambda: os.getenv("ENABLE_TELEMETRY", "true").lower() == "true")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert settings to dictionary"""
        return asdict(self)
    
    def to_json(self) -> str:
        """Convert settings to JSON string"""
        settings_dict = self.to_dict()
        # Convert Path objects to strings
        def convert_paths(obj):
            if isinstance(obj, dict):
                return {k: convert_paths(v) for k, v in obj.items()}
            elif isinstance(obj, (list, tuple)):
                return [convert_paths(item) for item in obj]
            elif isinstance(obj, Path):
                return str(obj)
            return obj
        
        settings_dict = convert_paths(settings_dict)
        return json.dumps(settings_dict, indent=2)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Settings":
        """Create settings from dictionary"""
        return cls(**data)
    
    @classmethod
    def from_json(cls, json_str: str) -> "Settings":
        """Create settings from JSON string"""
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    @classmethod
    def from_env_file(cls, env_file_path: str) -> "Settings":
        """Load settings from .env file"""
        load_dotenv(env_file_path)
        return cls()
    
    def save_to_file(self, file_path: str) -> None:
        """Save settings to JSON file"""
        Path(file_path).write_text(self.to_json())
        logger.info(f"Settings saved to {file_path}")
    
    @classmethod
    def load_from_file(cls, file_path: str) -> "Settings":
        """Load settings from JSON file"""
        json_str = Path(file_path).read_text()
        logger.info(f"Settings loaded from {file_path}")
        return cls.from_json(json_str)
    
    def validate(self) -> bool:
        """Validate configuration settings"""
        try:
            # Check PDF max size
            if self.pdf.MAX_FILE_SIZE_MB <= 0:
                raise ValueError("PDF max size must be positive")
            
            # Check DPI
            if self.pdf.DPI_FOR_OCR < 100 or self.pdf.DPI_FOR_OCR > 600:
                raise ValueError("DPI should be between 100 and 600")
            
            # Check OCR confidence
            if not 0 <= self.ocr.CONFIDENCE_THRESHOLD <= 1:
                raise ValueError("OCR confidence must be between 0 and 1")
            
            # Check API port
            if not (1024 <= self.api.PORT <= 65535):
                raise ValueError("API port must be between 1024 and 65535")
            
            # Check timeout
            if self.processing.TIMEOUT_SECONDS <= 0:
                raise ValueError("Timeout must be positive")
            
            logger.info("Configuration validation passed")
            return True
        except ValueError as e:
            logger.error(f"Configuration validation failed: {e}")
            return False
    
    def get_summary(self) -> str:
        """Get a human-readable summary of settings"""
        summary = f"""
========================================
{self.APP_NAME} - Configuration Summary
========================================

Environment: {self.ENVIRONMENT}
Version: {self.VERSION}

📁 PATHS:
  Base: {self.paths.BASE_DIR}
  Input: {self.paths.INPUT_DIR}
  Output: {self.paths.OUTPUT_DIR}
  Temp: {self.paths.TEMP_DIR}
  Logs: {self.paths.LOGS_DIR}

📊 PDF PROCESSING:
  Max Size: {self.pdf.MAX_FILE_SIZE_MB}MB
  DPI: {self.pdf.DPI_FOR_OCR}
  Extract Images: {self.pdf.EXTRACT_IMAGES}
  Detect Tables: {self.pdf.DETECT_TABLES}

🔍 OCR:
  Enabled: {self.ocr.ENABLE_OCR}
  Engine: {self.ocr.OCR_ENGINE}
  Language: {self.ocr.LANGUAGE}
  Preprocessing: {self.ocr.PREPROCESSING_ENABLED}

🤖 NLP:
  Enabled: {self.nlp.ENABLE_NLP}
  Model: {self.nlp.MODEL_NAME}
  Device: {self.nlp.DEVICE}

⚙️ PROCESSING:
  Parallel: {self.processing.PARALLEL_PROCESSING}
  Workers: {self.processing.NUM_WORKERS}
  Timeout: {self.processing.TIMEOUT_SECONDS}s
  Caching: {self.processing.ENABLE_CACHING}

🌐 API:
  Host: {self.api.HOST}
  Port: {self.api.PORT}
  Debug: {self.api.DEBUG}

📈 REPORTING:
  Generate Reports: {self.reporting.GENERATE_REPORTS}
  Format: {self.reporting.REPORT_FORMAT}

========================================
        """
        return summary


# Global settings instance
settings = Settings()

# Validate on import
if not settings.validate():
    logger.warning("Configuration validation found issues")

# Export settings
__all__ = [
    'settings',
    'Settings',
    'PathConfig',
    'LoggingConfig',
    'PDFConfig',
    'OCRConfig',
    'ComputerVisionConfig',
    'NLPConfig',
    'WordGenerationConfig',
    'ProcessingConfig',
    'APIConfig',
    'ClassificationConfig',
    'TableExtractionConfig',
    'ReportingConfig'
]
