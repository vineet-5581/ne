"""
📚 Usage Examples - Document AI System

This file contains comprehensive examples for using the Document AI System
in various scenarios: CLI, API, Python library, and batch processing.

Run these examples to understand how to use the system:
    python examples.py <example_name>
"""

import sys
import json
from pathlib import Path
from datetime import datetime
import asyncio

# ==============================================================================
# EXAMPLE 1: Single PDF Conversion (Python Library)
# ==============================================================================

def example_single_conversion():
    """Convert a single PDF to DOCX using Python library"""
    print("\n" + "="*70)
    print("📄 EXAMPLE 1: Single PDF Conversion")
    print("="*70)
    
    from pipeline import PipelineOrchestrator
    
    # Initialize orchestrator
    orchestrator = PipelineOrchestrator()
    
    # Process PDF
    input_pdf = Path("sample.pdf")
    output_docx = Path("output.docx")
    
    print(f"📥 Input: {input_pdf}")
    print(f"📤 Output: {output_docx}")
    print("\n⏳ Processing...")
    
    try:
        result = orchestrator.process(
            pdf_path=input_pdf,
            output_path=output_docx
        )
        
        # Display results
        print("\n✅ Conversion Successful!")
        print(f"   Document Type: {result.document_type}")
        print(f"   Total Pages: {result.total_pages}")
        print(f"   Time: {result.processing_time:.2f}s")
        print(f"   Output: {result.output_path}")
        
        # Show layer metrics
        print("\n📊 Layer Metrics:")
        for metric in result.layer_metrics:
            status = "✅" if metric.success else "❌"
            print(f"   {status} {metric.layer_name}: {metric.duration:.2f}s")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")


# ==============================================================================
# EXAMPLE 2: Batch Conversion (Python Library)
# ==============================================================================

def example_batch_conversion():
    """Convert multiple PDFs from a directory"""
    print("\n" + "="*70)
    print("📚 EXAMPLE 2: Batch PDF Conversion")
    print("="*70)
    
    from pipeline import PipelineOrchestrator
    import glob
    
    # Initialize orchestrator
    orchestrator = PipelineOrchestrator()
    
    # Get all PDFs in directory
    input_dir = Path("inputs")
    output_dir = Path("outputs")
    output_dir.mkdir(exist_ok=True)
    
    pdf_files = list(input_dir.glob("*.pdf"))
    
    if not pdf_files:
        print(f"⚠️  No PDFs found in {input_dir}")
        return
    
    print(f"📁 Found {len(pdf_files)} PDFs in {input_dir}")
    print("\n⏳ Processing batch...\n")
    
    results = []
    for i, pdf_file in enumerate(pdf_files, 1):
        output_file = output_dir / pdf_file.stem / ".docx"
        
        print(f"[{i}/{len(pdf_files)}] Processing {pdf_file.name}...")
        
        try:
            result = orchestrator.process(
                pdf_path=pdf_file,
                output_path=output_file
            )
            results.append(result)
            print(f"    ✅ Success ({result.processing_time:.2f}s)")
            
        except Exception as e:
            print(f"    ❌ Error: {e}")
    
    # Summary
    print("\n" + "="*70)
    print("📊 BATCH SUMMARY")
    print("="*70)
    successful = sum(1 for r in results if r.success)
    total_time = sum(r.processing_time for r in results)
    
    print(f"✅ Successful: {successful}/{len(pdf_files)}")
    print(f"⏱️  Total Time: {total_time:.2f}s")
    print(f"📁 Output: {output_dir}")


# ==============================================================================
# EXAMPLE 3: Configuration and Custom Settings
# ==============================================================================

def example_custom_configuration():
    """Configure system with custom settings"""
    print("\n" + "="*70)
    print("⚙️  EXAMPLE 3: Custom Configuration")
    print("="*70)
    
    from config import settings
    
    # Display current settings
    print("\n📋 Current Configuration:")
    print(settings.get_summary())
    
    # Modify settings
    print("\n🔧 Modifying Settings...")
    original_dpi = settings.pdf.DPI
    settings.pdf.DPI = 600
    print(f"   PDF DPI: {original_dpi} → {settings.pdf.DPI}")
    
    original_workers = settings.processing.NUM_WORKERS
    settings.processing.NUM_WORKERS = 8
    print(f"   Workers: {original_workers} → {settings.processing.NUM_WORKERS}")
    
    # Save configuration
    config_file = Path("my_config.json")
    print(f"\n💾 Saving configuration to {config_file}")
    settings.save_to_file(config_file)
    
    # Load configuration
    print(f"📂 Loading configuration from {config_file}")
    from config import Settings
    loaded_settings = Settings.load_from_file(config_file)
    
    print(f"✅ Settings loaded successfully")
    print(f"   DPI: {loaded_settings.pdf.DPI}")
    print(f"   Workers: {loaded_settings.processing.NUM_WORKERS}")


# ==============================================================================
# EXAMPLE 4: Error Handling and Validation
# ==============================================================================

def example_error_handling():
    """Demonstrate error handling and validation"""
    print("\n" + "="*70)
    print("🛡️  EXAMPLE 4: Error Handling & Validation")
    print("="*70)
    
    from utils import (
        Validator,
        ValidationError,
        PDFCorruptedError,
        get_logger
    )
    
    logger = get_logger("error_handling_example")
    
    # Example 1: Validate DPI
    print("\n1️⃣  Validating DPI:")
    try:
        dpi = Validator.validate_dpi(300)
        print(f"   ✅ Valid DPI: {dpi}")
    except ValidationError as e:
        print(f"   ❌ Invalid DPI: {e.message}")
    
    try:
        dpi = Validator.validate_dpi(1000)
        print(f"   ✅ Valid DPI: {dpi}")
    except ValidationError as e:
        print(f"   ❌ Invalid DPI: {e.message} (max is 600)")
    
    # Example 2: Validate confidence
    print("\n2️⃣  Validating Confidence:")
    try:
        conf = Validator.validate_confidence(0.85)
        print(f"   ✅ Valid confidence: {conf}")
    except ValidationError as e:
        print(f"   ❌ Invalid confidence: {e.message}")
    
    try:
        conf = Validator.validate_confidence(1.5)
        print(f"   ✅ Valid confidence: {conf}")
    except ValidationError as e:
        print(f"   ❌ Invalid confidence: {e.message} (must be 0-1)")
    
    # Example 3: Validate file
    print("\n3️⃣  Validating File:")
    try:
        path = Validator.validate_input_pdf("nonexistent.pdf")
        print(f"   ✅ File valid: {path}")
    except FileNotFoundError as e:
        print(f"   ❌ File not found: {e}")
    
    # Example 4: Logging errors
    print("\n4️⃣  Error Logging:")
    logger.info("Processing started")
    logger.warning("High memory usage detected", extra={'memory_mb': 2048})
    logger.error("PDF processing failed", extra={'error_code': 'PDF_CORRUPTED'})
    print("   ✅ Errors logged to logs/")


# ==============================================================================
# EXAMPLE 5: CLI Usage
# ==============================================================================

def example_cli_usage():
    """Show CLI commands (informational only)"""
    print("\n" + "="*70)
    print("💻 EXAMPLE 5: CLI Usage Commands")
    print("="*70)
    
    commands = [
        ("Single conversion", "python cli.py convert input.pdf output.docx"),
        ("Batch conversion", "python cli.py batch ./inputs ./outputs"),
        ("Verbose mode", "python cli.py convert input.pdf output.docx --verbose"),
        ("With report", "python cli.py convert input.pdf output.docx --report report.json"),
        ("Validate system", "python cli.py validate"),
        ("System info", "python cli.py info"),
    ]
    
    print("\n📝 Available Commands:\n")
    for desc, cmd in commands:
        print(f"  {desc}:")
        print(f"    $ {cmd}\n")


# ==============================================================================
# EXAMPLE 6: REST API Usage
# ==============================================================================

def example_api_usage():
    """Show REST API usage (informational)"""
    print("\n" + "="*70)
    print("🔌 EXAMPLE 6: REST API Endpoints")
    print("="*70)
    
    endpoints = [
        ("Health check", "GET", "/health", "{}"),
        ("System info", "GET", "/api/info", "{}"),
        ("Convert (sync)", "POST", "/api/convert", "form: file"),
        ("Convert (async)", "POST", "/api/convert/async", "form: file"),
        ("Check job", "GET", "/api/jobs/{job_id}", "{}"),
        ("Download file", "GET", "/api/jobs/{job_id}/download", "binary"),
        ("List jobs", "GET", "/api/jobs", "{}"),
        ("Validate", "GET", "/api/validate", "{}"),
    ]
    
    print("\n📡 API Endpoints:\n")
    for desc, method, path, body in endpoints:
        print(f"  {desc}:")
        print(f"    {method} {path}")
        print(f"    Body: {body}\n")
    
    print("🚀 Start API server:")
    print("    python -m uvicorn api:app --reload --port 8000")
    print("\n📖 Interactive docs:")
    print("    http://localhost:8000/api/docs")


# ==============================================================================
# EXAMPLE 7: Logging and Monitoring
# ==============================================================================

def example_logging():
    """Demonstrate logging system"""
    print("\n" + "="*70)
    print("📋 EXAMPLE 7: Logging System")
    print("="*70)
    
    from utils import setup_logging
    
    # Setup logging
    logger = setup_logging(
        name='example_app',
        level='DEBUG',
        log_dir=Path('logs')
    )
    
    print("\n🔍 Logging Examples:\n")
    
    logger.debug("This is a debug message")
    print("   ✅ DEBUG message logged")
    
    logger.info("Application started successfully")
    print("   ✅ INFO message logged")
    
    logger.warning("Memory usage is high", extra={'memory_mb': 3000})
    print("   ✅ WARNING message logged")
    
    logger.error("Failed to process PDF", extra={'error_code': 'PROCESSING_FAILED'})
    print("   ✅ ERROR message logged")
    
    print("\n📁 Logs saved to: logs/")


# ==============================================================================
# EXAMPLE 8: Document Type Detection
# ==============================================================================

def example_document_classification():
    """Demonstrate document classification"""
    print("\n" + "="*70)
    print("🏷️  EXAMPLE 8: Document Classification")
    print("="*70)
    
    from pipeline import DocumentClassifier
    
    classifier = DocumentClassifier()
    
    # Sample keywords for different document types
    samples = [
        {
            "name": "Resume",
            "text": "JOHN DOE\nSkills: Python, JavaScript\nExperience: 5 years\nEducation: BS Computer Science"
        },
        {
            "name": "Invoice",
            "text": "INVOICE\nInvoice #12345\nBill To: Company XYZ\nAmount Due: $1,000"
        },
        {
            "name": "Research Paper",
            "text": "ABSTRACT\nThis research paper investigates...\nINTRODUCTION\nBackground and literature review..."
        },
    ]
    
    print("\n🔍 Classifying Documents:\n")
    for sample in samples:
        result = classifier.classify(sample["text"])
        print(f"  Input: {sample['name']}")
        print(f"  Detected: {result['type']}")
        print(f"  Confidence: {result['confidence']:.2%}\n")


# ==============================================================================
# EXAMPLE 9: Performance Metrics
# ==============================================================================

def example_performance_metrics():
    """Show performance tracking"""
    print("\n" + "="*70)
    print("📊 EXAMPLE 9: Performance Metrics")
    print("="*70)
    
    from datetime import datetime, timedelta
    import json
    
    # Simulate conversion metrics
    metrics = {
        "timestamp": datetime.now().isoformat(),
        "document": "sample.pdf",
        "pages": 12,
        "total_time": 8.45,
        "layers": [
            {"name": "Classification", "time": 0.12},
            {"name": "Layout Detection", "time": 1.23},
            {"name": "Text Extraction", "time": 0.87},
            {"name": "OCR", "time": 2.10},
            {"name": "Tables", "time": 0.56},
            {"name": "Semantic Analysis", "time": 1.02},
            {"name": "Style Reconstruction", "time": 0.45},
            {"name": "Word Generation", "time": 1.15},
            {"name": "Post-Processing", "time": 0.21},
        ],
        "accuracy": 0.98,
        "file_size_mb": 2.5,
    }
    
    print("\n📈 Performance Report:")
    print(f"   Document: {metrics['document']}")
    print(f"   Pages: {metrics['pages']}")
    print(f"   Total Time: {metrics['total_time']:.2f}s")
    print(f"   Accuracy: {metrics['accuracy']:.1%}\n")
    
    print("   ⏱️  Layer Times:")
    for layer in metrics['layers']:
        bar_length = int(layer['time'] * 30)
        bar = "█" * bar_length
        print(f"      {layer['name']:25} {bar} {layer['time']:.2f}s")
    
    # Save metrics
    metrics_file = Path("metrics.json")
    with open(metrics_file, 'w') as f:
        json.dump(metrics, f, indent=2)
    print(f"\n   💾 Metrics saved to: {metrics_file}")


# ==============================================================================
# EXAMPLE 10: Create Test PDF
# ==============================================================================

def example_create_test_pdf():
    """Create a test PDF for demonstration"""
    print("\n" + "="*70)
    print("🎨 EXAMPLE 10: Create Test PDF")
    print("="*70)
    
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, Image
        from reportlab.lib import colors
        
        # Create PDF
        pdf_file = "test_sample.pdf"
        doc = SimpleDocTemplate(pdf_file, pagesize=letter)
        story = []
        styles = getSampleStyleSheet()
        
        # Add title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1f4788'),
            spaceAfter=30,
        )
        story.append(Paragraph("Document AI System - Test PDF", title_style))
        story.append(Spacer(1, 0.3*inch))
        
        # Add content
        story.append(Paragraph("Introduction", styles['Heading2']))
        story.append(Paragraph(
            "This is a test PDF created for demonstrating the Document AI System. "
            "It contains various elements like headings, paragraphs, and tables.",
            styles['Normal']
        ))
        story.append(Spacer(1, 0.2*inch))
        
        # Add table
        story.append(Paragraph("Sample Table", styles['Heading2']))
        data = [
            ['Name', 'Age', 'City'],
            ['John Doe', '30', 'New York'],
            ['Jane Smith', '28', 'Los Angeles'],
            ['Bob Johnson', '35', 'Chicago'],
        ]
        t = Table(data)
        t.setStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ])
        story.append(t)
        story.append(Spacer(1, 0.3*inch))
        
        # Add more content
        story.append(Paragraph("Key Features", styles['Heading2']))
        story.append(Paragraph("✓ High accuracy text extraction", styles['Normal']))
        story.append(Paragraph("✓ Table detection and extraction", styles['Normal']))
        story.append(Paragraph("✓ Image preservation", styles['Normal']))
        story.append(Paragraph("✓ Style and formatting preservation", styles['Normal']))
        
        # Build PDF
        doc.build(story)
        print(f"\n✅ Test PDF created: {pdf_file}")
        print(f"   Size: {Path(pdf_file).stat().st_size / 1024:.1f} KB")
        
    except ImportError:
        print("\n⚠️  reportlab not installed. Install with:")
        print("    pip install reportlab")


# ==============================================================================
# MAIN ENTRY POINT
# ==============================================================================

def main():
    """Run examples"""
    examples = {
        '1': ('Single Conversion', example_single_conversion),
        '2': ('Batch Conversion', example_batch_conversion),
        '3': ('Custom Configuration', example_custom_configuration),
        '4': ('Error Handling', example_error_handling),
        '5': ('CLI Usage', example_cli_usage),
        '6': ('API Usage', example_api_usage),
        '7': ('Logging System', example_logging),
        '8': ('Document Classification', example_document_classification),
        '9': ('Performance Metrics', example_performance_metrics),
        '10': ('Create Test PDF', example_create_test_pdf),
        'all': ('Run All Examples', lambda: [example_fn() for example_fn in [
            example_single_conversion,
            example_batch_conversion,
            example_custom_configuration,
            example_error_handling,
            example_cli_usage,
            example_api_usage,
            example_logging,
            example_document_classification,
            example_performance_metrics,
            example_create_test_pdf,
        ]]),
    }
    
    # Show menu
    print("\n" + "="*70)
    print("📚 DOCUMENT AI SYSTEM - USAGE EXAMPLES")
    print("="*70)
    print("\n🎯 Available Examples:\n")
    for key, (name, _) in examples.items():
        print(f"   {key:4} - {name}")
    
    # Get user input
    if len(sys.argv) > 1:
        choice = sys.argv[1]
    else:
        choice = input("\n👉 Select example (1-10, 'all', or 'q' to quit): ").strip().lower()
    
    if choice == 'q':
        print("\n👋 Goodbye!")
        return
    
    if choice in examples:
        try:
            examples[choice][1]()
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
    else:
        print(f"\n❌ Invalid choice: {choice}")


if __name__ == '__main__':
    main()
