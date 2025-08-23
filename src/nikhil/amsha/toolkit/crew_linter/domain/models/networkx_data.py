# src/nikhil/amsha/toolkit/crew_linter/domain/models/networkx_data.py
from pydantic import BaseModel, Field
from typing import List, Tuple, Dict, Any, Optional


class GraphData(BaseModel):
    edges: List[Tuple[Any, Any]] = Field(..., description="List of edges representing relationships (e.g., task to agent).")
    nodes: Optional[List[Any]] = Field(None, description="Optional list of nodes. If None, inferred from edges.")

class GraphAnalysisResult(BaseModel):
    num_nodes: int
    num_edges: int
    is_directed: bool
    is_strongly_connected: Optional[bool] = None
    is_weakly_connected: Optional[bool] = None
    degree_centrality: Optional[Dict[Any, float]] = None
    has_isolated_nodes: bool
    isolated_nodes: Optional[List[Any]] = None