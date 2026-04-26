"""
Configuration Package
Provides centralized settings management for Document AI System
"""

from config.settings import (
    settings,
    Settings,
    PathConfig,
    LoggingConfig,
    PDFConfig,
    OCRConfig,
    ComputerVisionConfig,
    NLPConfig,
    WordGenerationConfig,
    ProcessingConfig,
    APIConfig,
    ClassificationConfig,
    TableExtractionConfig,
    ReportingConfig
)

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

__version__ = "1.0.0"
__author__ = "Document AI Team"
