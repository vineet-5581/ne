"""
LAYER 3: Graph-Based Layout Model

Represents document as a graph:
- Nodes = text blocks
- Edges = spatial relationships

Solves:
- Reading order
- Element grouping
- Hierarchical structure

Optional: Graph Neural Networks for advanced analysis

Author: Document AI Team
Version: 1.0.0
"""

from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple
from enum import Enum

from utils import get_logger
from config import settings


class RelationType(Enum):
    """Types of spatial relationships between elements"""
    FOLLOWS = "follows"  # Element comes after another
    CONTAINS = "contains"  # Element contains another
    ADJACENT = "adjacent"  # Elements are next to each other
    ABOVE = "above"  # Element is above another
    BELOW = "below"  # Element is below another
    LEFT_OF = "left_of"  # Element is left of another
    RIGHT_OF = "right_of"  # Element is right of another


@dataclass
class Node:
    """Graph node representing a text block"""
    node_id: str
    element_type: str
    bbox: Tuple[float, float, float, float]
    page_num: int
    content: str
    confidence: float
    metadata: Dict = field(default_factory=dict)

    @property
    def width(self) -> float:
        return self.bbox[2] - self.bbox[0]

    @property
    def height(self) -> float:
        return self.bbox[3] - self.bbox[1]

    @property
    def center_x(self) -> float:
        return (self.bbox[0] + self.bbox[2]) / 2

    @property
    def center_y(self) -> float:
        return (self.bbox[1] + self.bbox[3]) / 2


@dataclass
class Edge:
    """Graph edge representing relationship between nodes"""
    source_id: str
    target_id: str
    relation_type: RelationType
    distance: float
    confidence: float


class GraphModel:
    """Builds and analyzes document structure as a graph"""

    def __init__(self):
        """Initialize graph model"""
        self.logger = get_logger('graph_model')
        self.logger.info("Graph Model initialized")
        self.nodes: Dict[str, Node] = {}
        self.edges: List[Edge] = []
        self.adjacency_list: Dict[str, List[str]] = {}

    def build_graph(self, layout_data: Dict) -> Dict:
        """Build graph from layout elements"""
        try:
            self.logger.info("Building document graph...")
            self.nodes = {}
            self.edges = []
            self.adjacency_list = {}

            elements = layout_data.get('elements', [])

            # Step 1: Create nodes
            for idx, element in enumerate(elements):
                node_id = f"node_{idx}"
                node = Node(
                    node_id=node_id,
                    element_type=element.get('element_type', 'unknown') if isinstance(element, dict) else str(element.element_type),
                    bbox=element.get('bbox', (0, 0, 0, 0)) if isinstance(element, dict) else element.bbox,
                    page_num=element.get('page_num', 0) if isinstance(element, dict) else element.page_num,
                    content=element.get('content_preview', '') if isinstance(element, dict) else getattr(element, 'content_preview', ''),
                    confidence=element.get('confidence', 0.5) if isinstance(element, dict) else element.confidence,
                )
                self.nodes[node_id] = node
                self.adjacency_list[node_id] = []

            # Step 2: Create edges based on spatial relationships
            node_ids = list(self.nodes.keys())
            for i, src_id in enumerate(node_ids):
                for j, tgt_id in enumerate(node_ids):
                    if i == j:
                        continue

                    src_node = self.nodes[src_id]
                    tgt_node = self.nodes[tgt_id]

                    # Only connect nodes on same or adjacent pages
                    if abs(src_node.page_num - tgt_node.page_num) > 1:
                        continue

                    relation, distance, confidence = self._analyze_relationship(
                        src_node, tgt_node
                    )

                    if confidence > 0.5:  # Only add high-confidence edges
                        edge = Edge(
                            source_id=src_id,
                            target_id=tgt_id,
                            relation_type=relation,
                            distance=distance,
                            confidence=confidence
                        )
                        self.edges.append(edge)
                        self.adjacency_list[src_id].append(tgt_id)

            # Step 3: Determine reading order
            reading_order = self._determine_reading_order()

            # Step 4: Identify clusters/groupings
            clusters = self._identify_clusters()

            graph_data = {
                'nodes': list(self.nodes.values()),
                'edges': self.edges,
                'adjacency_list': self.adjacency_list,
                'reading_order': reading_order,
                'clusters': clusters,
                'total_nodes': len(self.nodes),
                'total_edges': len(self.edges),
            }

            self.logger.info(f"✅ Graph built: {len(self.nodes)} nodes, {len(self.edges)} edges")
            return graph_data

        except Exception as e:
            self.logger.error(f"Graph building failed: {e}")
            raise

    def _analyze_relationship(self, src: Node, tgt: Node) -> Tuple[RelationType, float, float]:
        """Analyze spatial relationship between two nodes"""
        # Calculate distances
        dy = tgt.center_y - src.center_y
        dx = tgt.center_x - src.center_x
        distance = (dx**2 + dy**2)**0.5

        # Determine relation type
        if abs(dx) < 50 and dy > 0:  # Below
            return RelationType.BELOW, distance, 0.9
        elif abs(dx) < 50 and dy < 0:  # Above
            return RelationType.ABOVE, distance, 0.9
        elif abs(dy) < 50 and dx > 0:  # Right of
            return RelationType.RIGHT_OF, distance, 0.8
        elif abs(dy) < 50 and dx < 0:  # Left of
            return RelationType.LEFT_OF, distance, 0.8
        elif distance < 100:
            return RelationType.ADJACENT, distance, 0.6
        else:
            return RelationType.ADJACENT, distance, 0.3

    def _determine_reading_order(self) -> List[str]:
        """Determine reading order using topological sort"""
        reading_order = []
        visited: Set[str] = set()

        def dfs(node_id: str):
            if node_id in visited:
                return
            visited.add(node_id)

            # Sort by position (top-to-bottom, left-to-right)
            neighbors = sorted(
                self.adjacency_list.get(node_id, []),
                key=lambda nid: (
                    self.nodes[nid].page_num,
                    self.nodes[nid].center_y,
                    self.nodes[nid].center_x
                )
            )

            for neighbor_id in neighbors:
                dfs(neighbor_id)

            reading_order.append(node_id)

        # Start from first node
        if self.nodes:
            first_node = min(
                self.nodes.keys(),
                key=lambda nid: (
                    self.nodes[nid].page_num,
                    self.nodes[nid].center_y,
                    self.nodes[nid].center_x
                )
            )
            dfs(first_node)

        return reading_order

    def _identify_clusters(self) -> List[List[str]]:
        """Identify element clusters/groupings"""
        clusters = []
        visited: Set[str] = set()

        def bfs(start_id: str) -> List[str]:
            cluster = []
            queue = [start_id]
            visited.add(start_id)

            while queue:
                node_id = queue.pop(0)
                cluster.append(node_id)

                for neighbor_id in self.adjacency_list.get(node_id, []):
                    if neighbor_id not in visited:
                        visited.add(neighbor_id)
                        queue.append(neighbor_id)

            return cluster

        for node_id in self.nodes:
            if node_id not in visited:
                cluster = bfs(node_id)
                if cluster:
                    clusters.append(cluster)

        return clusters
