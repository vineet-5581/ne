#!/usr/bin/env python3
"""
Main entry point for the Document AI System.
Orchestrates the complete PDF to DOCX conversion pipeline.
"""

import sys
import logging
from pathlib import Path
from typing import Optional, Dict, Any
import json
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from config.settings import Settings
from pipeline.orchestrator import DocumentAIPipeline
from utils.validators import validate_input_pdf, validate_output_path
from utils.exceptions import (
    ValidationError,
    ProcessingError,
    ConfigurationError
)


class DocumentConversionSystem:
    """
    Main system class that manages the complete PDF to DOCX conversion.
    Serves as the entry point for all conversion operations.
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the Document Conversion System.

        Args:
            config_path: Path to custom configuration file (optional)
        """
        try:
            self.settings = Settings(config_path)
            self.pipeline = DocumentAIPipeline(self.settings)
            logger.info("Document Conversion System initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize system: {str(e)}")
            raise ConfigurationError(f"Initialization failed: {str(e)}")

    def convert(
        self,
        input_pdf: str,
        output_docx: str,
        report_path: Optional[str] = None,
        enable_ocr: bool = True,
        preserve_styles: bool = True,
        enable_table_detection: bool = True,
        verbose: bool = False
    ) -> Dict[str, Any]:
        """
        Convert a PDF file to DOCX format with complete pipeline execution.

        Args:
            input_pdf: Path to input PDF file
            output_docx: Path to output DOCX file
            report_path: Optional path to save conversion report (JSON)
            enable_ocr: Enable OCR for scanned documents
            preserve_styles: Preserve formatting and styles
            enable_table_detection: Enable intelligent table detection
            verbose: Enable verbose logging

        Returns:
            Dictionary containing conversion results and metrics

        Raises:
            ValidationError: If input validation fails
            ProcessingError: If conversion process fails
        """
        logger.info(f"Starting conversion: {input_pdf} → {output_docx}")

        # Set verbosity
        if verbose:
            logging.getLogger().setLevel(logging.DEBUG)

        # Validation
        try:
            validate_input_pdf(input_pdf)
            validate_output_path(output_docx)
            logger.info("Input validation passed")
        except ValidationError as e:
            logger.error(f"Validation failed: {str(e)}")
            raise

        # Prepare conversion parameters
        conversion_params = {
            "enable_ocr": enable_ocr,
            "preserve_styles": preserve_styles,
            "enable_table_detection": enable_table_detection
        }

        try:
            # Execute pipeline
            logger.info("Executing 10-layer AI pipeline...")
            result = self.pipeline.process(
                input_pdf=input_pdf,
                output_docx=output_docx,
                **conversion_params
            )

            # Generate report
            report = self._generate_report(
                input_pdf=input_pdf,
                output_docx=output_docx,
                result=result
            )

            # Save report if path provided
            if report_path:
                self._save_report(report, report_path)
                logger.info(f"Report saved to: {report_path}")

            logger.info(f"Conversion completed successfully")
            return report

        except Exception as e:
            logger.error(f"Conversion failed: {str(e)}", exc_info=True)
            raise ProcessingError(f"Conversion failed: {str(e)}")

    def _generate_report(
        self,
        input_pdf: str,
        output_docx: str,
        result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate conversion report with metrics and statistics.

        Args:
            input_pdf: Input PDF path
            output_docx: Output DOCX path
            result: Pipeline execution result

        Returns:
            Report dictionary
        """
        report = {
            "timestamp": datetime.now().isoformat(),
            "input": {
                "file": input_pdf,
                "size_bytes": Path(input_pdf).stat().st_size
            },
            "output": {
                "file": output_docx,
                "size_bytes": Path(output_docx).stat().st_size if Path(output_docx).exists() else 0
            },
            "pipeline_layers": result.get("layers_executed", []),
            "metrics": result.get("metrics", {}),
            "document_type": result.get("document_type", "unknown"),
            "pages_processed": result.get("pages_processed", 0),
            "extraction_stats": result.get("extraction_stats", {}),
            "warnings": result.get("warnings", []),
            "errors": result.get("errors", [])
        }
        return report

    def _save_report(self, report: Dict[str, Any], report_path: str) -> None:
        """
        Save conversion report to JSON file.

        Args:
            report: Report dictionary
            report_path: Path to save report
        """
        output_path = Path(report_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)

    def batch_convert(
        self,
        pdf_directory: str,
        output_directory: str,
        pattern: str = "*.pdf",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Convert multiple PDF files in batch mode.

        Args:
            pdf_directory: Directory containing PDF files
            output_directory: Directory for output DOCX files
            pattern: File pattern to match (default: *.pdf)
            **kwargs: Additional conversion parameters

        Returns:
            Batch conversion report
        """
        logger.info(f"Starting batch conversion from: {pdf_directory}")

        input_dir = Path(pdf_directory)
        output_dir = Path(output_directory)
        output_dir.mkdir(parents=True, exist_ok=True)

        pdf_files = list(input_dir.glob(pattern))
        logger.info(f"Found {len(pdf_files)} PDF files to process")

        results = {
            "total_files": len(pdf_files),
            "successful": 0,
            "failed": 0,
            "conversions": []
        }

        for pdf_file in pdf_files:
            try:
                output_file = output_dir / f"{pdf_file.stem}.docx"
                report = self.convert(str(pdf_file), str(output_file), **kwargs)
                
                results["successful"] += 1
                results["conversions"].append({
                    "input": str(pdf_file),
                    "output": str(output_file),
                    "status": "success"
                })
                logger.info(f"✓ Converted: {pdf_file.name}")

            except Exception as e:
                results["failed"] += 1
                results["conversions"].append({
                    "input": str(pdf_file),
                    "status": "failed",
                    "error": str(e)
                })
                logger.error(f"✗ Failed: {pdf_file.name} - {str(e)}")

        logger.info(f"Batch conversion complete. Success: {results['successful']}, Failed: {results['failed']}")
        return results

    def validate_installation(self) -> Dict[str, Any]:
        """
        Validate system installation and dependencies.

        Returns:
            Validation report
        """
        logger.info("Validating system installation...")
        
        validation = {
            "timestamp": datetime.now().isoformat(),
            "dependencies": {},
            "configuration": {},
            "system_ready": True
        }

        # Check dependencies
        required_packages = [
            "pymupdf", "pdfplumber", "python_docx", "cv2",
            "pytesseract", "numpy", "transformers", "PIL"
        ]

        for package in required_packages:
            try:
                __import__(package)
                validation["dependencies"][package] = "installed"
            except ImportError:
                validation["dependencies"][package] = "missing"
                validation["system_ready"] = False
                logger.warning(f"Missing dependency: {package}")

        # Check configuration
        try:
            validation["configuration"]["settings_loaded"] = True
            validation["configuration"]["tesseract_available"] = self._check_tesseract()
        except Exception as e:
            validation["configuration"]["error"] = str(e)
            validation["system_ready"] = False

        return validation

    def _check_tesseract(self) -> bool:
        """Check if Tesseract OCR is available."""
        try:
            import pytesseract
            pytesseract.get_tesseract_version()
            return True
        except Exception:
            return False


def main():
    """
    Main entry point - demonstrates basic usage.
    """
    import argparse

    parser = argparse.ArgumentParser(
        description="Document AI System - PDF to DOCX Conversion"
    )
    parser.add_argument("--version", action="version", version="1.0.0")
    parser.add_argument("--validate", action="store_true", help="Validate installation")
    
    args = parser.parse_args()

    try:
        system = DocumentConversionSystem()

        if args.validate:
            validation = system.validate_installation()
            print("\n🔍 System Validation Report:")
            print(json.dumps(validation, indent=2))
            sys.exit(0 if validation["system_ready"] else 1)

        logger.info("Document Conversion System ready")
        logger.info("Use CLI, API, or GUI for conversion operations")

    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
