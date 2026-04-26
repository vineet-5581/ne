#!/usr/bin/env python3
"""
Command-line interface for the Document AI System.
Provides CLI commands for PDF to DOCX conversion operations.
"""

import sys
import click
import logging
from pathlib import Path
from typing import Optional
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

from app import DocumentConversionSystem
from utils.exceptions import ValidationError, ProcessingError


# ============================================================================
# DECORATORS
# ============================================================================

def setup_logger(verbose: bool):
    """Configure logger based on verbosity level."""
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    else:
        logging.getLogger().setLevel(logging.INFO)


# ============================================================================
# MAIN CLI GROUP
# ============================================================================

@click.group()
@click.version_option(version="1.0.0", prog_name="document-ai")
@click.pass_context
def cli(ctx):
    """
    🚀 Document AI System - Professional PDF to DOCX Conversion
    
    Convert PDFs to editable Word documents with AI-powered layout preservation.
    """
    ctx.ensure_object(dict)


# ============================================================================
# COMMAND: CONVERT
# ============================================================================

@cli.command(name="convert")
@click.argument("input_pdf", type=click.Path(exists=True, path_type=Path))
@click.argument("output_docx", type=click.Path(path_type=Path))
@click.option(
    "--report",
    type=click.Path(path_type=Path),
    default=None,
    help="Save conversion report to JSON file"
)
@click.option(
    "--enable-ocr",
    type=bool,
    default=True,
    help="Enable OCR for scanned documents"
)
@click.option(
    "--preserve-styles",
    type=bool,
    default=True,
    help="Preserve original formatting and styles"
)
@click.option(
    "--enable-tables",
    type=bool,
    default=True,
    help="Enable intelligent table detection"
)
@click.option(
    "-v", "--verbose",
    is_flag=True,
    help="Enable verbose output"
)
@click.option(
    "--overwrite",
    is_flag=True,
    help="Overwrite output file if exists"
)
def convert_command(
    input_pdf: Path,
    output_docx: Path,
    report: Optional[Path],
    enable_ocr: bool,
    preserve_styles: bool,
    enable_tables: bool,
    verbose: bool,
    overwrite: bool
):
    """
    Convert a PDF file to DOCX format.
    
    Example:
        document-ai convert input.pdf output.docx --report report.json
    """
    setup_logger(verbose)

    # Check if output exists
    if output_docx.exists() and not overwrite:
        click.echo(click.style("❌ Error: Output file already exists", fg="red"), err=True)
        click.echo("Use --overwrite to replace existing file", err=True)
        sys.exit(1)

    try:
        with click.progressbar(length=100, label="Converting PDF", show_eta=True) as bar:
            system = DocumentConversionSystem()
            
            bar.update(10)
            result = system.convert(
                input_pdf=str(input_pdf),
                output_docx=str(output_docx),
                report_path=str(report) if report else None,
                enable_ocr=enable_ocr,
                preserve_styles=preserve_styles,
                enable_table_detection=enable_tables,
                verbose=verbose
            )
            bar.update(90)

        click.echo(click.style("\n✅ Conversion successful!", fg="green"))
        
        # Display summary
        click.echo("\n📊 Conversion Summary:")
        click.echo(f"  Input:  {input_pdf.name} ({result['input']['size_bytes']} bytes)")
        click.echo(f"  Output: {output_docx.name} ({result['output']['size_bytes']} bytes)")
        click.echo(f"  Type:   {result['document_type']}")
        click.echo(f"  Pages:  {result['pages_processed']}")
        
        if result['metrics']:
            click.echo("\n📈 Metrics:")
            for key, value in result['metrics'].items():
                click.echo(f"  {key}: {value}")

        if report:
            click.echo(f"\n📄 Report saved to: {report}")

    except ValidationError as e:
        click.echo(click.style(f"❌ Validation Error: {str(e)}", fg="red"), err=True)
        sys.exit(1)
    except ProcessingError as e:
        click.echo(click.style(f"❌ Processing Error: {str(e)}", fg="red"), err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(click.style(f"❌ Unexpected Error: {str(e)}", fg="red"), err=True)
        logger.exception("Conversion failed with exception")
        sys.exit(1)


# ============================================================================
# COMMAND: BATCH
# ============================================================================

@cli.command(name="batch")
@click.argument("input_dir", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.argument("output_dir", type=click.Path(file_okay=False, path_type=Path))
@click.option(
    "--pattern",
    default="*.pdf",
    help="File pattern to match (default: *.pdf)"
)
@click.option(
    "-v", "--verbose",
    is_flag=True,
    help="Enable verbose output"
)
@click.option(
    "--report",
    type=click.Path(path_type=Path),
    default=None,
    help="Save batch report to JSON file"
)
def batch_command(
    input_dir: Path,
    output_dir: Path,
    pattern: str,
    verbose: bool,
    report: Optional[Path]
):
    """
    Convert all PDFs in a directory to DOCX format (batch mode).
    
    Example:
        document-ai batch ./pdfs ./docx_output --report batch_report.json
    """
    setup_logger(verbose)

    try:
        system = DocumentConversionSystem()
        
        click.echo(f"🔄 Starting batch conversion...")
        click.echo(f"  Input:  {input_dir}")
        click.echo(f"  Output: {output_dir}")
        click.echo(f"  Pattern: {pattern}\n")

        results = system.batch_convert(
            pdf_directory=str(input_dir),
            output_directory=str(output_dir),
            pattern=pattern,
            verbose=verbose
        )

        # Display results
        click.echo(click.style(f"\n✅ Batch conversion complete!\n", fg="green"))
        click.echo("📊 Results:")
        click.echo(f"  Total:     {results['total_files']}")
        click.echo(f"  Success:   {click.style(str(results['successful']), fg='green')}")
        click.echo(f"  Failed:    {click.style(str(results['failed']), fg='red' if results['failed'] > 0 else 'green')}")

        # Show failed files
        if results['failed'] > 0:
            click.echo("\n❌ Failed conversions:")
            for conversion in results['conversions']:
                if conversion['status'] == 'failed':
                    click.echo(f"  • {Path(conversion['input']).name}: {conversion.get('error', 'Unknown error')}")

        # Save report
        if report:
            with open(report, 'w') as f:
                json.dump(results, f, indent=2)
            click.echo(f"\n📄 Report saved to: {report}")

    except Exception as e:
        click.echo(click.style(f"❌ Error: {str(e)}", fg="red"), err=True)
        logger.exception("Batch conversion failed")
        sys.exit(1)


# ============================================================================
# COMMAND: VALIDATE
# ============================================================================

@cli.command(name="validate")
@click.option(
    "-v", "--verbose",
    is_flag=True,
    help="Enable verbose output"
)
def validate_command(verbose: bool):
    """
    Validate system installation and dependencies.
    
    Example:
        document-ai validate
    """
    setup_logger(verbose)

    try:
        click.echo("🔍 Validating system installation...\n")
        
        system = DocumentConversionSystem()
        validation = system.validate_installation()

        # Dependencies
        click.echo("📦 Dependencies:")
        for package, status in validation['dependencies'].items():
            icon = "✅" if status == "installed" else "❌"
            click.echo(f"  {icon} {package}: {status}")

        # Configuration
        click.echo("\n⚙️  Configuration:")
        for key, value in validation['configuration'].items():
            if isinstance(value, bool):
                icon = "✅" if value else "❌"
                click.echo(f"  {icon} {key}: {value}")
            else:
                click.echo(f"  • {key}: {value}")

        # Overall status
        if validation['system_ready']:
            click.echo(click.style("\n✅ System is ready!", fg="green"))
            sys.exit(0)
        else:
            click.echo(click.style("\n❌ System has issues. Please install missing dependencies.", fg="red"))
            sys.exit(1)

    except Exception as e:
        click.echo(click.style(f"❌ Validation failed: {str(e)}", fg="red"), err=True)
        sys.exit(1)


# ============================================================================
# COMMAND: INFO
# ============================================================================

@cli.command(name="info")
def info_command():
    """
    Display system information and capabilities.
    
    Example:
        document-ai info
    """
    info_text = """
╔════════════════════════════════════════════════════════════════╗
║          Document AI System - Information                      ║
╚════════════════════════════════════════════════════════════════╝

🎯 CORE FEATURES
  • 10-Layer AI Pipeline for PDF processing
  • 95%+ Layout Fidelity Preservation
  • 99% Text Accuracy
  • Smart Document Classification
  • Intelligent Table Detection
  • OCR for Scanned Documents
  • Style & Formatting Preservation

📊 SUPPORTED DOCUMENT TYPES
  ✓ Resumes
  ✓ Research Papers
  ✓ Invoices
  ✓ Forms
  ✓ Books & Articles
  ✓ Any PDF format

🔧 CONVERSION MODES
  ✓ Single file conversion
  ✓ Batch directory processing
  ✓ REST API integration
  ✓ Web GUI interface

📈 OUTPUT METRICS
  ✓ Layout similarity score
  ✓ Text extraction accuracy
  ✓ Table detection metrics
  ✓ Processing time
  ✓ Detailed conversion reports

🚀 QUICK START

  1. Convert single file:
     document-ai convert input.pdf output.docx

  2. Batch convert:
     document-ai batch ./pdfs ./output

  3. Validate installation:
     document-ai validate

  4. Start REST API:
     python -m uvicorn api:app --reload

  5. Launch Web GUI:
     streamlit run gui.py

📚 DOCUMENTATION
  For detailed documentation, visit the README.md file.

═══════════════════════════════════════════════════════════════════
"""
    click.echo(info_text)


# ============================================================================
# ENTRY POINT
# ============================================================================

def main():
    """Main CLI entry point."""
    try:
        cli(obj={})
    except KeyboardInterrupt:
        click.echo("\n⚠️  Operation cancelled by user", err=True)
        sys.exit(130)
    except Exception as e:
        click.echo(click.style(f"\n❌ Fatal Error: {str(e)}", fg="red"), err=True)
        logger.exception("CLI failed with exception")
        sys.exit(1)


if __name__ == "__main__":
    main()
