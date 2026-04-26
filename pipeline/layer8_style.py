"""
LAYER 8: Style Reconstruction Engine

Maps extracted formatting to Word styles:
- Font size → heading levels
- Spacing → paragraph breaks
- Bold, italic, underline preservation
- Color mapping

Author: Document AI Team
Version: 1.0.0
"""

from typing import Dict, List
from dataclasses import dataclass

from utils import get_logger
from config import settings


@dataclass
class StyledBlock:
    """Text block with styling information"""
    text: str
    style_name: str
    font_name: str
    font_size: float
    bold: bool = False
    italic: bool = False
    underline: bool = False
    color: tuple = (0, 0, 0)  # RGB
    alignment: str = 'left'  # left, center, right, justify
    line_spacing: float = 1.0


class StyleReconstructor:
    """Reconstructs document styles for Word output"""

    # Font size to heading level mapping
    FONT_SIZE_TO_HEADING = {
        28: 'Heading 1',
        20: 'Heading 2',
        16: 'Heading 3',
        14: 'Heading 4',
        12: 'Normal',
    }

    def __init__(self):
        """Initialize style reconstructor"""
        self.logger = get_logger('style_reconstructor')
        self.logger.info("Style Reconstructor initialized")

    def reconstruct(self, text_data: Dict, semantic_data: Dict) -> Dict:
        """Reconstruct styles from extracted text"""
        try:
            self.logger.info("Reconstructing styles...")

            formatted_texts = text_data.get('formatted_texts', [])
            blocks = []

            # Create styled blocks from formatted text
            for text_item in formatted_texts:
                styled_block = self._create_styled_block(text_item)
                blocks.append(styled_block)

            # Enhance with semantic information
            self._apply_semantic_styling(blocks, semantic_data)

            style_data = {
                'blocks': blocks,
                'total_blocks': len(blocks),
            }

            self.logger.info(f"✅ Applied styles to {len(blocks)} blocks")
            return style_data

        except Exception as e:
            self.logger.error(f"Style reconstruction failed: {e}")
            raise

    def _create_styled_block(self, text_item) -> StyledBlock:
        """Create a styled block from formatted text"""
        # Handle both dict and object formats
        if isinstance(text_item, dict):
            text = text_item.get('text', '')
            font_name = text_item.get('font_name', 'Calibri')
            font_size = text_item.get('font_size', 12)
            style_name = text_item.get('style_name', 'Normal')
            color = text_item.get('color', (0, 0, 0))
        else:
            text = getattr(text_item, 'text', '')
            font_name = getattr(text_item, 'font_name', 'Calibri')
            font_size = getattr(text_item, 'font_size', 12)
            style_name = self._map_font_size_to_style(font_size)
            color = getattr(text_item, 'color', (0, 0, 0))

        # Determine bold/italic from style
        style_str = getattr(text_item, 'style', 'normal') if hasattr(text_item, 'style') else 'normal'
        bold = 'bold' in str(style_str).lower()
        italic = 'italic' in str(style_str).lower()

        styled_block = StyledBlock(
            text=text,
            style_name=style_name,
            font_name=font_name,
            font_size=font_size,
            bold=bold,
            italic=italic,
            color=color,
        )
        return styled_block

    def _map_font_size_to_style(self, font_size: float) -> str:
        """Map font size to Word style"""
        # Find closest heading level
        closest_size = min(self.FONT_SIZE_TO_HEADING.keys(),
                         key=lambda x: abs(x - font_size))
        return self.FONT_SIZE_TO_HEADING[closest_size]

    def _apply_semantic_styling(self, blocks: List[StyledBlock], semantic_data: Dict) -> None:
        """Apply semantic information to styling"""
        headings = semantic_data.get('headings', [])
        emphasis_texts = semantic_data.get('emphasis', [])

        # Mark headings
        for heading_info in headings:
            heading_text = heading_info.get('text', '')
            for block in blocks:
                if heading_text.lower() in block.text.lower():
                    block.style_name = f"Heading {heading_info.get('level', 1)}"
                    block.bold = True
                    break

        # Mark emphasized text
        for emphasis_text in emphasis_texts:
            for block in blocks:
                if emphasis_text.lower() in block.text.lower():
                    block.bold = True
                    break
