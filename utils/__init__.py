"""
Utilities Package Initialization
Exports all utility modules for easy importing.
"""

from utils.logger import (
    Logger,
    LoggerManager,
    get_logger,
    setup_logging,
    debug,
    info,
    warning,
    error,
    critical,
    JsonFormatter,
    ColoredFormatter
)

from utils.exceptions import (
    # Base exceptions
    DocumentAIException,
    ErrorCode,
    
    # File exceptions
    FileException,
    FileNotFoundError,
    FileReadError,
    FileWriteError,
    InvalidFileFormatError,
    FileSizeExceededError,
    
    # PDF exceptions
    PDFException,
    PDFCorruptedError,
    PDFPasswordProtectedError,
    PDFExtractionError,
    PDFNoContentError,
    
    # OCR exceptions
    OCRException,
    OCREngineNotFoundError,
    OCRProcessingError,
    OCRLanguageNotSupportedError,
    
    # Computer Vision exceptions
    CVException,
    CVModelNotLoadedError,
    CVProcessingError,
    CVDeviceNotAvailableError,
    
    # NLP exceptions
    NLPException,
    NLPModelNotLoadedError,
    NLPProcessingError,
    
    # Word generation exceptions
    WordException,
    WordGenerationError,
    WordWriteError,
    
    # Table exceptions
    TableException,
    TableExtractionError,
    
    # Validation exceptions
    ValidationException,
    ValidationError,
    InvalidParameterError,
    
    # Processing exceptions
    ProcessingException,
    ProcessingTimeoutError,
    ProcessingOutOfMemoryError,
    
    # API exceptions
    APIException,
    APIRateLimitExceededError,
    
    # System exceptions
    SystemException,
    DependencyNotInstalledError,
    ConfigurationError
)

from utils.validators import (
    Validator,
    validate_params,
    validate_input_pdf,
    validate_output_path,
    validate_params_dict
)

__all__ = [
    # Logger
    'Logger',
    'LoggerManager',
    'get_logger',
    'setup_logging',
    'debug',
    'info',
    'warning',
    'error',
    'critical',
    'JsonFormatter',
    'ColoredFormatter',
    
    # Exceptions
    'DocumentAIException',
    'ErrorCode',
    'FileException',
    'FileNotFoundError',
    'FileReadError',
    'FileWriteError',
    'InvalidFileFormatError',
    'FileSizeExceededError',
    'PDFException',
    'PDFCorruptedError',
    'PDFPasswordProtectedError',
    'PDFExtractionError',
    'PDFNoContentError',
    'OCRException',
    'OCREngineNotFoundError',
    'OCRProcessingError',
    'OCRLanguageNotSupportedError',
    'CVException',
    'CVModelNotLoadedError',
    'CVProcessingError',
    'CVDeviceNotAvailableError',
    'NLPException',
    'NLPModelNotLoadedError',
    'NLPProcessingError',
    'WordException',
    'WordGenerationError',
    'WordWriteError',
    'TableException',
    'TableExtractionError',
    'ValidationException',
    'ValidationError',
    'InvalidParameterError',
    'ProcessingException',
    'ProcessingTimeoutError',
    'ProcessingOutOfMemoryError',
    'APIException',
    'APIRateLimitExceededError',
    'SystemException',
    'DependencyNotInstalledError',
    'ConfigurationError',
    
    # Validators
    'Validator',
    'validate_params',
    'validate_input_pdf',
    'validate_output_path',
    'validate_params_dict'
]
