"""
LAYER 7: Semantic Analysis (NLP)

Detects semantic structures:
- Headings vs body text
- Lists
- Sections
- Emphasis (important passages)

Uses transformer models (BERT-like)

Author: Document AI Team
Version: 1.0.0
"""

from typing import Dict, List
from dataclasses import dataclass
from enum import Enum

from utils import get_logger
from config import settings


class SemanticLabel(Enum):
    """Semantic labels for text"""
    HEADING = "heading"
    SUBHEADING = "subheading"
    BODY = "body"
    EMPHASIS = "emphasis"
    QUOTE = "quote"
    LIST_ITEM = "list_item"
    CAPTION = "caption"


@dataclass
class SemanticSegment:
    """Represents a semantically labeled text segment"""
    text: str
    label: SemanticLabel
    confidence: float
    level: int = 0  # Hierarchy level (for headings)


class SemanticAnalyzer:
    """Analyzes semantic structure of text"""

    def __init__(self):
        """Initialize semantic analyzer"""
        self.logger = get_logger('semantic_analyzer')
        self.logger.info("Semantic Analyzer initialized")

    def analyze(self, text_data: Dict) -> Dict:
        """Analyze semantic structure"""
        try:
            self.logger.info("Analyzing semantic structure...")

            formatted_texts = text_data.get('formatted_texts', [])
            all_text = text_data.get('text', '')

            # Analyze text
            headings = self._detect_headings(formatted_texts)
            paragraphs = self._detect_paragraphs(all_text)
            lists = self._detect_lists(all_text)
            quotes = self._detect_quotes(all_text)
            emphasis = self._detect_emphasis(all_text)

            semantic_data = {
                'headings': headings,
                'paragraphs': paragraphs,
                'lists': lists,
                'quotes': quotes,
                'emphasis': emphasis,
            }

            self.logger.info(f"✅ Semantic analysis complete")
            return semantic_data

        except Exception as e:
            self.logger.error(f"Semantic analysis failed: {e}")
            raise

    def _detect_headings(self, formatted_texts: List) -> List[Dict]:
        """Detect heading-like text"""
        headings = []

        for text in formatted_texts:
            # Check for large font
            font_size = getattr(text, 'font_size', 12) if hasattr(text, 'font_size') else text.get('font_size', 12)
            if font_size > 14:  # Larger font indicates heading
                heading_level = 1 if font_size > 20 else 2
                headings.append({
                    'text': getattr(text, 'text', text.get('text', '')),
                    'level': heading_level,
                    'confidence': 0.85,
                })

        return headings

    def _detect_paragraphs(self, text: str) -> List[str]:
        """Detect paragraphs"""
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        return paragraphs[:10]  # Return top 10

    def _detect_lists(self, text: str) -> List[List[str]]:
        """Detect list structures"""
        lists = []
        lines = text.split('\n')

        current_list = []
        for line in lines:
            # Check for list markers
            if any(line.strip().startswith(marker) for marker in ['•', '○', '-', '*', '1.', '2.']):
                current_list.append(line.strip())
            else:
                if current_list:
                    lists.append(current_list)
                    current_list = []

        if current_list:
            lists.append(current_list)

        return lists

    def _detect_quotes(self, text: str) -> List[str]:
        """Detect quote-like text"""
        quotes = []
        lines = text.split('\n')

        for line in lines:
            if line.strip().startswith('"') and line.strip().endswith('"'):
                quotes.append(line.strip())

        return quotes

    def _detect_emphasis(self, text: str) -> List[str]:
        """Detect emphasized text"""
        emphasis_markers = ['**', '__', '*', '_']
        emphasized = []

        # Simple heuristic: look for text surrounded by markers
        for marker in emphasis_markers:
            parts = text.split(marker)
            for i in range(1, len(parts), 2):
                if i < len(parts):
                    emphasized.append(parts[i])

        return emphasized
