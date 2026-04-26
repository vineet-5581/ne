"""
Pipeline Orchestrator - Main Conductor of 10-Layer Architecture

Coordinates the complete document processing pipeline:
1. Classification → 2. Layout → 3. Graph → 4. Text → 5. OCR
6. Tables → 7. Semantic → 8. Style → 9. Word → 10. Post-Processing

Author: Document AI Team
Version: 1.0.0
"""

import json
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any
from datetime import datetime
import time

from utils import get_logger, ValidationError, ProcessingException
from config import settings

from .layer1_classifier import DocumentClassifier
from .layer2_layout_detection import LayoutDetector
from .layer3_graph_model import GraphModel
from .layer4_text_extraction import TextExtractor
from .layer5_ocr import OCRProcessor
from .layer6_tables import TableExtractor
from .layer7_semantic import SemanticAnalyzer
from .layer8_style import StyleReconstructor
from .layer9_word_generator import WordGenerator
from .layer10_postprocessing import PostProcessor


@dataclass
class LayerMetrics:
    """Metrics for each processing layer"""
    layer_name: str
    start_time: float
    end_time: float = 0.0
    success: bool = True
    error_message: str = ""
    details: Dict[str, Any] = field(default_factory=dict)

    @property
    def duration(self) -> float:
        return self.end_time - self.start_time if self.end_time > 0 else 0.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ProcessingResult:
    """Final result of document processing"""
    success: bool
    input_path: str
    output_path: str
    document_type: str
    total_pages: int
    processing_time: float
    layer_metrics: List[LayerMetrics]
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'success': self.success,
            'input_path': self.input_path,
            'output_path': self.output_path,
            'document_type': self.document_type,
            'total_pages': self.total_pages,
            'processing_time': self.processing_time,
            'layers': [m.to_dict() for m in self.layer_metrics],
            'errors': self.errors,
            'warnings': self.warnings,
            'metadata': self.metadata,
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)

    def save_report(self, filepath: Path) -> None:
        """Save processing report to JSON file"""
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w') as f:
            f.write(self.to_json())


class PipelineOrchestrator:
    """Main orchestrator for the 10-layer document processing pipeline"""

    def __init__(self):
        """Initialize the orchestrator and all layers"""
        self.logger = get_logger('pipeline_orchestrator')
        self.logger.info("Initializing Pipeline Orchestrator...")

        # Initialize all layers
        try:
            self.classifier = DocumentClassifier()
            self.layout_detector = LayoutDetector()
            self.graph_model = GraphModel()
            self.text_extractor = TextExtractor()
            self.ocr_processor = OCRProcessor()
            self.table_extractor = TableExtractor()
            self.semantic_analyzer = SemanticAnalyzer()
            self.style_reconstructor = StyleReconstructor()
            self.word_generator = WordGenerator()
            self.post_processor = PostProcessor()
            self.logger.info("✅ All 10 layers initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize layers: {e}")
            raise ProcessingException(f"Pipeline initialization failed: {e}")

        self.layer_metrics: List[LayerMetrics] = []

    def process(self, pdf_path: Path, output_path: Path) -> ProcessingResult:
        """Execute complete 10-layer pipeline"""
        start_time = time.time()
        self.layer_metrics = []

        self.logger.info(f"\n{'='*60}")
        self.logger.info(f"Starting Document Processing Pipeline")
        self.logger.info(f"Input: {pdf_path}")
        self.logger.info(f"Output: {output_path}")
        self.logger.info(f"{'='*60}\n")

        try:
            # Layer 1: Classification
            doc_type, classification_data = self._layer_1_classification(pdf_path)

            # Layer 2: Layout Detection
            layout_data = self._layer_2_layout_detection(pdf_path, classification_data)

            # Layer 3: Graph Model
            graph_data = self._layer_3_graph_model(layout_data)

            # Layer 4: Text Extraction
            text_data = self._layer_4_text_extraction(pdf_path, layout_data)

            # Layer 5: OCR Processing
            ocr_data = self._layer_5_ocr_processing(pdf_path, text_data)

            # Layer 6: Table Extraction
            table_data = self._layer_6_table_extraction(pdf_path, layout_data)

            # Layer 7: Semantic Analysis
            semantic_data = self._layer_7_semantic_analysis(text_data)

            # Layer 8: Style Reconstruction
            style_data = self._layer_8_style_reconstruction(text_data, semantic_data)

            # Layer 9: Word Generation
            self._layer_9_word_generation(
                output_path,
                text_data,
                style_data,
                table_data,
                doc_type
            )

            # Layer 10: Post-Processing
            self._layer_10_post_processing(output_path)

            total_time = time.time() - start_time

            # Build result
            result = ProcessingResult(
                success=True,
                input_path=str(pdf_path),
                output_path=str(output_path),
                document_type=doc_type,
                total_pages=classification_data.get('total_pages', 0),
                processing_time=total_time,
                layer_metrics=self.layer_metrics,
                metadata={
                    'timestamp': datetime.now().isoformat(),
                    'pipeline_version': '1.0.0',
                }
            )

            self.logger.info(f"\n✅ Pipeline completed successfully in {total_time:.2f}s")
            self._log_metrics_summary(result)

            return result

        except Exception as e:
            total_time = time.time() - start_time
            self.logger.error(f"Pipeline failed after {total_time:.2f}s: {e}")

            result = ProcessingResult(
                success=False,
                input_path=str(pdf_path),
                output_path=str(output_path),
                document_type="unknown",
                total_pages=0,
                processing_time=total_time,
                layer_metrics=self.layer_metrics,
                errors=[str(e)]
            )

            return result

    def _layer_1_classification(self, pdf_path: Path) -> tuple:
        """Layer 1: Document Classification"""
        self.logger.info("\n📋 LAYER 1: Document Classification")
        metric = LayerMetrics(layer_name="Classification", start_time=time.time())

        try:
            doc_type, classification_data = self.classifier.classify(pdf_path)
            metric.end_time = time.time()
            metric.success = True
            metric.details = {'document_type': doc_type}
            self.logger.info(f"✅ Document Type: {doc_type}")
            return doc_type, classification_data
        except Exception as e:
            metric.end_time = time.time()
            metric.success = False
            metric.error_message = str(e)
            self.logger.error(f"❌ Classification failed: {e}")
            raise
        finally:
            self.layer_metrics.append(metric)

    def _layer_2_layout_detection(self, pdf_path: Path, classification_data: Dict) -> Dict:
        """Layer 2: Visual Layout Detection"""
        self.logger.info("\n🎨 LAYER 2: Visual Layout Detection")
        metric = LayerMetrics(layer_name="Layout Detection", start_time=time.time())

        try:
            layout_data = self.layout_detector.detect(pdf_path, classification_data)
            metric.end_time = time.time()
            metric.success = True
            metric.details = {'detected_elements': len(layout_data.get('elements', []))}
            self.logger.info(f"✅ Detected {len(layout_data.get('elements', []))} layout elements")
            return layout_data
        except Exception as e:
            metric.end_time = time.time()
            metric.success = False
            metric.error_message = str(e)
            self.logger.error(f"❌ Layout detection failed: {e}")
            raise
        finally:
            self.layer_metrics.append(metric)

    def _layer_3_graph_model(self, layout_data: Dict) -> Dict:
        """Layer 3: Graph-Based Layout Model"""
        self.logger.info("\n🔗 LAYER 3: Graph-Based Layout Model")
        metric = LayerMetrics(layer_name="Graph Model", start_time=time.time())

        try:
            graph_data = self.graph_model.build_graph(layout_data)
            metric.end_time = time.time()
            metric.success = True
            metric.details = {'nodes': len(graph_data.get('nodes', [])), 'edges': len(graph_data.get('edges', []))}
            self.logger.info(f"✅ Graph built: {len(graph_data.get('nodes', []))} nodes, {len(graph_data.get('edges', []))} edges")
            return graph_data
        except Exception as e:
            metric.end_time = time.time()
            metric.success = False
            metric.error_message = str(e)
            self.logger.error(f"❌ Graph model failed: {e}")
            raise
        finally:
            self.layer_metrics.append(metric)

    def _layer_4_text_extraction(self, pdf_path: Path, layout_data: Dict) -> Dict:
        """Layer 4: Text Extraction Engine"""
        self.logger.info("\n📝 LAYER 4: Text Extraction")
        metric = LayerMetrics(layer_name="Text Extraction", start_time=time.time())

        try:
            text_data = self.text_extractor.extract(pdf_path, layout_data)
            metric.end_time = time.time()
            metric.success = True
            metric.details = {'extracted_characters': len(text_data.get('text', ''))}
            self.logger.info(f"✅ Extracted {len(text_data.get('text', ''))} characters")
            return text_data
        except Exception as e:
            metric.end_time = time.time()
            metric.success = False
            metric.error_message = str(e)
            self.logger.error(f"❌ Text extraction failed: {e}")
            raise
        finally:
            self.layer_metrics.append(metric)

    def _layer_5_ocr_processing(self, pdf_path: Path, text_data: Dict) -> Dict:
        """Layer 5: OCR Super-Pipeline for Scanned PDFs"""
        self.logger.info("\n👁️ LAYER 5: OCR Processing")
        metric = LayerMetrics(layer_name="OCR Processing", start_time=time.time())

        try:
            ocr_data = self.ocr_processor.process(pdf_path, text_data)
            metric.end_time = time.time()
            metric.success = True
            metric.details = {'ocr_confidence': ocr_data.get('average_confidence', 0)}
            self.logger.info(f"✅ OCR processed with confidence: {ocr_data.get('average_confidence', 0):.2%}")
            return ocr_data
        except Exception as e:
            metric.end_time = time.time()
            metric.success = False
            metric.error_message = str(e)
            self.logger.error(f"❌ OCR processing failed: {e}")
            raise
        finally:
            self.layer_metrics.append(metric)

    def _layer_6_table_extraction(self, pdf_path: Path, layout_data: Dict) -> Dict:
        """Layer 6: Table Understanding Engine"""
        self.logger.info("\n📊 LAYER 6: Table Extraction")
        metric = LayerMetrics(layer_name="Table Extraction", start_time=time.time())

        try:
            table_data = self.table_extractor.extract(pdf_path, layout_data)
            metric.end_time = time.time()
            metric.success = True
            metric.details = {'tables_detected': len(table_data.get('tables', []))}
            self.logger.info(f"✅ Extracted {len(table_data.get('tables', []))} tables")
            return table_data
        except Exception as e:
            metric.end_time = time.time()
            metric.success = False
            metric.error_message = str(e)
            self.logger.error(f"❌ Table extraction failed: {e}")
            raise
        finally:
            self.layer_metrics.append(metric)

    def _layer_7_semantic_analysis(self, text_data: Dict) -> Dict:
        """Layer 7: Semantic Analysis (NLP)"""
        self.logger.info("\n🧠 LAYER 7: Semantic Analysis")
        metric = LayerMetrics(layer_name="Semantic Analysis", start_time=time.time())

        try:
            semantic_data = self.semantic_analyzer.analyze(text_data)
            metric.end_time = time.time()
            metric.success = True
            metric.details = {
                'headings': len(semantic_data.get('headings', [])),
                'paragraphs': len(semantic_data.get('paragraphs', [])),
                'lists': len(semantic_data.get('lists', []))
            }
            self.logger.info(f"✅ Semantic analysis complete: {metric.details}")
            return semantic_data
        except Exception as e:
            metric.end_time = time.time()
            metric.success = False
            metric.error_message = str(e)
            self.logger.error(f"❌ Semantic analysis failed: {e}")
            raise
        finally:
            self.layer_metrics.append(metric)

    def _layer_8_style_reconstruction(self, text_data: Dict, semantic_data: Dict) -> Dict:
        """Layer 8: Style Reconstruction Engine"""
        self.logger.info("\n🎨 LAYER 8: Style Reconstruction")
        metric = LayerMetrics(layer_name="Style Reconstruction", start_time=time.time())

        try:
            style_data = self.style_reconstructor.reconstruct(text_data, semantic_data)
            metric.end_time = time.time()
            metric.success = True
            metric.details = {'styled_blocks': len(style_data.get('blocks', []))}
            self.logger.info(f"✅ Applied styles to {len(style_data.get('blocks', []))} blocks")
            return style_data
        except Exception as e:
            metric.end_time = time.time()
            metric.success = False
            metric.error_message = str(e)
            self.logger.error(f"❌ Style reconstruction failed: {e}")
            raise
        finally:
            self.layer_metrics.append(metric)

    def _layer_9_word_generation(self, output_path: Path, text_data: Dict, 
                                 style_data: Dict, table_data: Dict, doc_type: str) -> None:
        """Layer 9: Word Generation Engine"""
        self.logger.info("\n📄 LAYER 9: Word Generation")
        metric = LayerMetrics(layer_name="Word Generation", start_time=time.time())

        try:
            self.word_generator.generate(
                output_path=output_path,
                text_data=text_data,
                style_data=style_data,
                table_data=table_data,
                doc_type=doc_type
            )
            metric.end_time = time.time()
            metric.success = True
            metric.details = {'output_file': str(output_path)}
            self.logger.info(f"✅ Word document generated: {output_path}")
        except Exception as e:
            metric.end_time = time.time()
            metric.success = False
            metric.error_message = str(e)
            self.logger.error(f"❌ Word generation failed: {e}")
            raise
        finally:
            self.layer_metrics.append(metric)

    def _layer_10_post_processing(self, output_path: Path) -> None:
        """Layer 10: Post-Processing AI"""
        self.logger.info("\n✨ LAYER 10: Post-Processing")
        metric = LayerMetrics(layer_name="Post-Processing", start_time=time.time())

        try:
            self.post_processor.process(output_path)
            metric.end_time = time.time()
            metric.success = True
            self.logger.info(f"✅ Post-processing complete")
        except Exception as e:
            metric.end_time = time.time()
            metric.success = False
            metric.error_message = str(e)
            self.logger.error(f"❌ Post-processing failed: {e}")
            raise
        finally:
            self.layer_metrics.append(metric)

    def _log_metrics_summary(self, result: ProcessingResult) -> None:
        """Log summary of all layer metrics"""
        self.logger.info(f"\n{'='*60}")
        self.logger.info("📊 PIPELINE METRICS SUMMARY")
        self.logger.info(f"{'='*60}")
        self.logger.info(f"Total Processing Time: {result.processing_time:.2f}s")
        self.logger.info(f"Document Type: {result.document_type}")
        self.logger.info(f"Total Pages: {result.total_pages}")
        self.logger.info(f"\nLayer Breakdown:")

        for metric in result.layer_metrics:
            status = "✅" if metric.success else "❌"
            self.logger.info(f"  {status} {metric.layer_name}: {metric.duration:.2f}s")

        self.logger.info(f"{'='*60}\n")
