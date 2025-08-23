# src/nikhil/amsha/toolkit/crew_linter/guardrails/networkx_guardrail.py
import networkx as nx

from nikhil.amsha.toolkit.crew_linter.domain.models.networkx_data import GraphData, GraphAnalysisResult


class NetworkXGuardrail:
    def __init__(self, directed: bool = False):
        self.directed = directed

    def check(self, graph_data: GraphData) -> GraphAnalysisResult:
        if self.directed:
            graph = nx.DiGraph()
        else:
            graph = nx.Graph()

        if graph_data.nodes:
            graph.add_nodes_from(graph_data.nodes)
        graph.add_edges_from(graph_data.edges)

        isolated_nodes = list(nx.isolates(graph))

        analysis = GraphAnalysisResult(
            num_nodes=graph.number_of_nodes(),
            num_edges=graph.number_of_edges(),
            is_directed=self.directed,
            has_isolated_nodes=len(isolated_nodes) > 0,
            isolated_nodes=isolated_nodes if len(isolated_nodes) > 0 else None,
        )

        if self.directed:
            try:
                analysis.is_strongly_connected = nx.is_strongly_connected(graph)
            except nx.NetworkXError:
                analysis.is_strongly_connected = False
            analysis.is_weakly_connected = nx.is_weakly_connected(graph)
            try:
                analysis.degree_centrality = nx.degree_centrality(graph)
            except Exception:
                analysis.degree_centrality = None
        else:
            try:
                analysis.is_weakly_connected = nx.is_connected(graph)
            except nx.NetworkXError:
                analysis.is_weakly_connected = False
            try:
                analysis.degree_centrality = nx.degree_centrality(graph)
            except Exception:
                analysis.degree_centrality = None

        return analysis
