"""
LAYER 4: Text Extraction Engine

Extracts text with formatting preservation:
- Font size
- Font weight (bold, italic)
- Spacing information
- Coordinates
- Hyperlinks

Uses PyMuPDF for structured text

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


class TextStyle(Enum):
    """Text styling options"""
    NORMAL = "normal"
    BOLD = "bold"
    ITALIC = "italic"
    BOLD_ITALIC = "bold_italic"
    UNDERLINE = "underline"


@dataclass
class FormattedText:
    """Text with formatting information"""
    text: str
    font_name: str
    font_size: float
    style: TextStyle
    color: Tuple[float, float, float]  # RGB
    bbox: Tuple[float, float, float, float]
    page_num: int
    is_hyperlink: bool = False
    link_url: str = ""


class TextExtractor:
    """Extracts text with detailed formatting information"""

    def __init__(self):
        """Initialize text extractor"""
        self.logger = get_logger('text_extractor')
        self.logger.info("Text Extractor initialized")

    def extract(self, pdf_path: Path, layout_data: Dict) -> Dict:
        """Extract text with formatting from PDF"""
        try:
            pdf_path = validate_input_pdf(str(pdf_path))
            self.logger.info(f"Extracting text: {pdf_path}")

            doc = fitz.open(pdf_path)
            all_text = ""
            formatted_texts: List[FormattedText] = []
            hyperlinks: List[Dict] = []

            for page_num, page in enumerate(doc):
                self.logger.info(f"Extracting text from page {page_num + 1}/{len(doc)}")

                # Extract plain text
                page_text = page.get_text()
                all_text += page_text + "\n"

                # Extract formatted text
                page_formatted = self._extract_formatted_text(page, page_num)
                formatted_texts.extend(page_formatted)

                # Extract hyperlinks
                page_links = self._extract_hyperlinks(page, page_num)
                hyperlinks.extend(page_links)

            doc.close()

            text_data = {
                'text': all_text,
                'formatted_texts': formatted_texts,
                'hyperlinks': hyperlinks,
                'total_characters': len(all_text),
                'hyperlink_count': len(hyperlinks),
            }

            self.logger.info(f"✅ Extracted {len(all_text)} characters, {len(hyperlinks)} links")
            return text_data

        except Exception as e:
            self.logger.error(f"Text extraction failed: {e}")
            raise

    def _extract_formatted_text(self, page: fitz.Page, page_num: int) -> List[FormattedText]:
        """Extract text with formatting information"""
        formatted_texts = []

        try:
            # Get text with spans (includes formatting info)
            text_dict = page.get_text('dict')

            for block in text_dict.get('blocks', []):
                if block['type'] != 0:  # 0 = text block
                    continue

                for line in block.get('lines', []):
                    for span in line.get('spans', []):
                        text = span.get('text', '')
                        if not text.strip():
                            continue

                        # Extract formatting
                        font_name = span.get('font', 'Unknown')
                        font_size = span.get('size', 12)
                        bbox = span.get('bbox', (0, 0, 0, 0))
                        color = span.get('color', (0, 0, 0))

                        # Detect style (flags indicate bold, italic, etc.)
                        flags = span.get('flags', 0)
                        style = self._detect_style(flags)

                        formatted_text = FormattedText(
                            text=text,
                            font_name=font_name,
                            font_size=font_size,
                            style=style,
                            color=color,
                            bbox=bbox,
                            page_num=page_num
                        )
                        formatted_texts.append(formatted_text)

        except Exception as e:
            self.logger.warning(f"Error extracting formatted text: {e}")

        return formatted_texts

    def _detect_style(self, flags: int) -> TextStyle:
        """Detect text style from font flags"""
        is_bold = bool(flags & 1)
        is_italic = bool(flags & 2)

        if is_bold and is_italic:
            return TextStyle.BOLD_ITALIC
        elif is_bold:
            return TextStyle.BOLD
        elif is_italic:
            return TextStyle.ITALIC
        else:
            return TextStyle.NORMAL

    def _extract_hyperlinks(self, page: fitz.Page, page_num: int) -> List[Dict]:
        """Extract hyperlinks from page"""
        hyperlinks = []

        try:
            for link in page.get_links():
                if link['type'] == fitz.PDF_LINK_URI:
                    hyperlinks.append({
                        'url': link.get('uri', ''),
                        'bbox': link.get('from', None),
                        'page_num': page_num,
                    })
        except Exception as e:
            self.logger.warning(f"Error extracting hyperlinks: {e}")

        return hyperlinks
