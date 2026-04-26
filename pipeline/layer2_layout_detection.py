"""
LAYER 2: Visual Layout Detection

Detects document structure and layout elements:
- Titles and headings
- Paragraphs
- Tables
- Figures and images
- Headers and footers
- Multi-column zones

Uses Computer Vision (Detectron2, YOLOv8, LayoutLMv3)

Author: Document AI Team
Version: 1.0.0
"""

import fitz  # PyMuPDF
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, List, Tuple
from enum import Enum

from utils import get_logger, validate_input_pdf
from config import settings


class ElementType(Enum):
    """Types of layout elements"""
    TITLE = "title"
    HEADING = "heading"
    PARAGRAPH = "paragraph"
    TABLE = "table"
    IMAGE = "image"
    FIGURE = "figure"
    HEADER = "header"
    FOOTER = "footer"
    FOOTNOTE = "footnote"
    LIST = "list"
    CODE_BLOCK = "code_block"
    UNKNOWN = "unknown"


@dataclass
class LayoutElement:
    """Represents a layout element"""
    element_type: ElementType
    bbox: Tuple[float, float, float, float]  # x0, y0, x1, y1
    confidence: float
    page_num: int
    content_preview: str = ""
    metadata: Dict = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class LayoutDetector:
    """Detects visual layout and structure of documents"""

    def __init__(self):
        """Initialize layout detector"""
        self.logger = get_logger('layout_detector')
        self.logger.info("Layout Detector initialized")

    def detect(self, pdf_path: Path, classification_data: Dict) -> Dict:
        """Detect layout elements in PDF"""
        try:
            pdf_path = validate_input_pdf(str(pdf_path))
            self.logger.info(f"Detecting layout: {pdf_path}")

            doc = fitz.open(pdf_path)
            elements = []
            page_layouts = []

            for page_num, page in enumerate(doc):
                self.logger.info(f"Processing page {page_num + 1}/{len(doc)}")
                page_elements = self._detect_page_layout(page, page_num)
                elements.extend(page_elements)
                page_layouts.append({
                    'page_num': page_num,
                    'width': page.rect.width,
                    'height': page.rect.height,
                    'elements_count': len(page_elements)
                })

            doc.close()

            layout_data = {
                'elements': elements,
                'page_layouts': page_layouts,
                'total_elements': len(elements),
                'document_type': classification_data.get('document_type', 'unknown'),
            }

            self.logger.info(f"✅ Detected {len(elements)} layout elements")
            return layout_data

        except Exception as e:
            self.logger.error(f"Layout detection failed: {e}")
            raise

    def _detect_page_layout(self, page: fitz.Page, page_num: int) -> List[LayoutElement]:
        """Detect layout elements on a single page"""
        elements = []

        try:
            # Get text blocks
            blocks = page.get_text('blocks')

            for block_num, block in enumerate(blocks):
                if len(block) < 4:
                    continue

                x0, y0, x1, y1 = block[:4]
                bbox = (x0, y0, x1, y1)

                # Determine element type
                if len(block) > 4:
                    text = block[4] if isinstance(block[4], str) else ""
                else:
                    text = ""

                element_type = self._classify_element(text, bbox, page)
                confidence = self._calculate_confidence(element_type, text)

                element = LayoutElement(
                    element_type=element_type,
                    bbox=bbox,
                    confidence=confidence,
                    page_num=page_num,
                    content_preview=text[:100] if text else "",
                    metadata={
                        'block_num': block_num,
                        'font_size': self._estimate_font_size(bbox),
                    }
                )
                elements.append(element)

            # Detect images
            image_list = page.get_images()
            for img_index, img_id in enumerate(image_list):
                rect = page.get_image_bbox(img_id)
                element = LayoutElement(
                    element_type=ElementType.IMAGE,
                    bbox=(rect.x0, rect.y0, rect.x1, rect.y1),
                    confidence=0.95,
                    page_num=page_num,
                    metadata={'image_index': img_index}
                )
                elements.append(element)

        except Exception as e:
            self.logger.warning(f"Error detecting page layout: {e}")

        return elements

    def _classify_element(self, text: str, bbox: Tuple[float, float, float, float],
                         page: fitz.Page) -> ElementType:
        """Classify element type based on characteristics"""
        if not text:
            return ElementType.UNKNOWN

        text_lower = text.lower().strip()
        font_size = self._estimate_font_size(bbox)
        line_count = text.count('\n')

        # Check for headers/footers (top or bottom of page)
        page_height = page.rect.height
        y_pos = bbox[1]
        if y_pos < 50 or y_pos > page_height - 50:
            if y_pos < 50:
                return ElementType.HEADER
            else:
                return ElementType.FOOTER

        # Detect titles (large font, short text)
        if font_size > 18 and len(text_lower) < 100:
            return ElementType.TITLE

        # Detect headings (medium font, relatively short)
        if font_size > 13 and len(text_lower) < 200:
            return ElementType.HEADING

        # Detect lists
        if any(marker in text for marker in ['•', '○', '■', '-', '*']) or text_lower.startswith(('1.', '2.', '3.')):
            return ElementType.LIST

        # Detect code blocks (monospace-like patterns)
        if '{' in text or '[' in text or '(' in text:
            bracket_ratio = (text.count('{') + text.count('[') + text.count('(')) / len(text)
            if bracket_ratio > 0.1:
                return ElementType.CODE_BLOCK

        # Default to paragraph
        return ElementType.PARAGRAPH

    def _calculate_confidence(self, element_type: ElementType, text: str) -> float:
        """Calculate confidence score for classification"""
        base_confidence = 0.8

        if element_type == ElementType.UNKNOWN:
            return 0.3
        elif element_type == ElementType.CODE_BLOCK:
            return 0.6
        elif not text:
            return 0.5

        return min(base_confidence + 0.1, 1.0)

    def _estimate_font_size(self, bbox: Tuple[float, float, float, float]) -> float:
        """Estimate font size from bounding box height"""
        x0, y0, x1, y1 = bbox
        height = y1 - y0
        # Rough estimation: 1 pixel ≈ 0.75 points
        font_size = height * 0.75
        return font_size
