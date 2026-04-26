"""
LAYER 1: Document Intelligence Classifier

Classifies document type to optimize processing pipeline:
- Resume
- Research Paper
- Invoice
- Form
- Book/Article
- Contract
- Report

Author: Document AI Team
Version: 1.0.0
"""

import fitz  # PyMuPDF
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, Tuple, List

from utils import get_logger, PDFException, validate_input_pdf
from config import settings


@dataclass
class ClassificationResult:
    """Document classification result"""
    doc_type: str
    confidence: float
    characteristics: Dict[str, any]


class DocumentClassifier:
    """Classifies document type using heuristics and ML models"""

    # Document type indicators
    RESUME_KEYWORDS = {
        'experience', 'education', 'skills', 'objective', 'summary',
        'employment', 'work history', 'qualifications', 'phone', 'email'
    }

    RESEARCH_PAPER_KEYWORDS = {
        'abstract', 'introduction', 'methodology', 'results', 'conclusion',
        'references', 'conclusion', 'literature', 'research', 'analysis',
        'hypothesis', 'experiment', 'study'
    }

    INVOICE_KEYWORDS = {
        'invoice', 'bill', 'total', 'amount', 'payment', 'due date',
        'customer', 'vendor', 'item', 'quantity', 'price', 'subtotal'
    }

    FORM_KEYWORDS = {
        'form', 'application', 'checkbox', 'field', 'required', 'signature',
        'date', 'name', 'address', 'phone', 'email'
    }

    CONTRACT_KEYWORDS = {
        'agreement', 'contract', 'party', 'terms', 'conditions', 'liability',
        'confidential', 'effective date', 'termination', 'jurisdiction'
    }

    REPORT_KEYWORDS = {
        'report', 'executive summary', 'findings', 'analysis', 'conclusions',
        'recommendations', 'chart', 'graph', 'table', 'statistics'
    }

    DOCUMENT_TYPES = [
        ('resume', RESUME_KEYWORDS),
        ('research_paper', RESEARCH_PAPER_KEYWORDS),
        ('invoice', INVOICE_KEYWORDS),
        ('form', FORM_KEYWORDS),
        ('contract', CONTRACT_KEYWORDS),
        ('report', REPORT_KEYWORDS),
    ]

    def __init__(self):
        """Initialize classifier"""
        self.logger = get_logger('classifier')
        self.logger.info("Document Classifier initialized")

    def classify(self, pdf_path: Path) -> Tuple[str, Dict]:
        """Classify document type and return metadata"""
        try:
            pdf_path = validate_input_pdf(str(pdf_path))
            self.logger.info(f"Classifying: {pdf_path}")

            # Open PDF
            try:
                doc = fitz.open(pdf_path)
            except Exception as e:
                raise PDFException(filepath=str(pdf_path), reason="Cannot open PDF")

            # Extract metadata
            total_pages = len(doc)
            first_page_text = self._extract_first_page_text(doc)
            text_density = self._calculate_text_density(doc)
            has_images = self._detect_images(doc)
            has_tables = self._detect_tables(doc, first_page_text)
            layout_complexity = self._analyze_layout_complexity(doc)

            # Classify
            doc_type, confidence = self._classify_by_keywords(first_page_text)

            # Refine classification using characteristics
            doc_type, confidence = self._refine_classification(
                doc_type, confidence,
                total_pages, text_density, has_tables, layout_complexity
            )

            doc.close()

            classification_data = {
                'document_type': doc_type,
                'confidence': confidence,
                'total_pages': total_pages,
                'text_density': text_density,
                'has_images': has_images,
                'has_tables': has_tables,
                'layout_complexity': layout_complexity,
                'first_page_text': first_page_text[:500],  # First 500 chars
            }

            self.logger.info(f"✅ Classified as: {doc_type} (confidence: {confidence:.2%})")
            return doc_type, classification_data

        except Exception as e:
            self.logger.error(f"Classification failed: {e}")
            raise

    def _extract_first_page_text(self, doc: fitz.Document) -> str:
        """Extract text from first page"""
        try:
            first_page = doc[0]
            text = first_page.get_text()
            return text.lower()
        except Exception as e:
            self.logger.warning(f"Could not extract first page text: {e}")
            return ""

    def _calculate_text_density(self, doc: fitz.Document) -> float:
        """Calculate average text density (0-1)"""
        try:
            sample_pages = min(5, len(doc))
            total_chars = 0
            for i in range(sample_pages):
                text = doc[i].get_text()
                total_chars += len(text)

            avg_chars_per_page = total_chars / sample_pages
            # Normalize: assume max ~5000 chars per page
            density = min(1.0, avg_chars_per_page / 5000)
            return density
        except Exception as e:
            self.logger.warning(f"Could not calculate text density: {e}")
            return 0.5

    def _detect_images(self, doc: fitz.Document) -> bool:
        """Detect if document contains images"""
        try:
            for page in doc:
                if page.get_images():
                    return True
            return False
        except Exception as e:
            self.logger.warning(f"Could not detect images: {e}")
            return False

    def _detect_tables(self, doc: fitz.Document, text: str) -> bool:
        """Detect if document likely contains tables"""
        try:
            # Check for table keywords
            table_keywords = {'table', 'row', 'column', 'cell', '|', '─', '│'}
            has_keywords = any(kw in text for kw in table_keywords)

            # Check for tabular layout in first few pages
            for page_num in range(min(3, len(doc))):
                page = doc[page_num]
                blocks = page.get_text('blocks')
                # If many horizontally aligned blocks, likely table
                if len(blocks) > 10:
                    has_keywords = True
                    break

            return has_keywords
        except Exception as e:
            self.logger.warning(f"Could not detect tables: {e}")
            return False

    def _analyze_layout_complexity(self, doc: fitz.Document) -> str:
        """Analyze layout complexity: simple, moderate, complex"""
        try:
            first_page = doc[0]
            blocks = first_page.get_text('blocks')

            # Count distinct text block positions
            num_blocks = len(blocks)

            if num_blocks < 5:
                return 'simple'
            elif num_blocks < 20:
                return 'moderate'
            else:
                return 'complex'
        except Exception as e:
            self.logger.warning(f"Could not analyze layout: {e}")
            return 'moderate'

    def _classify_by_keywords(self, text: str) -> Tuple[str, float]:
        """Classify based on keyword matching"""
        if not text:
            return 'unknown', 0.5

        scores = {}
        for doc_type, keywords in self.DOCUMENT_TYPES:
            # Count keyword matches
            matches = sum(1 for kw in keywords if kw in text)
            score = matches / len(keywords) if keywords else 0
            scores[doc_type] = score

        # Get top match
        best_type = max(scores, key=scores.get)
        best_score = scores[best_type]

        # If no strong match, classify as generic
        if best_score < 0.1:
            return 'generic_document', 0.5

        return best_type, min(best_score, 1.0)

    def _refine_classification(self, doc_type: str, confidence: float,
                              total_pages: int, text_density: float,
                              has_tables: bool, layout_complexity: str) -> Tuple[str, float]:
        """Refine classification using document characteristics"""
        # Adjust confidence based on characteristics
        if has_tables and doc_type in ['invoice', 'report']:
            confidence += 0.1
        if layout_complexity == 'complex' and doc_type in ['report', 'research_paper']:
            confidence += 0.1
        if total_pages > 10 and doc_type == 'research_paper':
            confidence += 0.05

        confidence = min(confidence, 1.0)
        return doc_type, confidence
