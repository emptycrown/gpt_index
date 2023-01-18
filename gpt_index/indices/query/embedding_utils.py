"""Embedding utils for queries."""

from typing import List, Optional, Tuple, Dict

from gpt_index.embeddings.openai import BaseEmbedding
from gpt_index.data_structs.data_structs import Node


def get_top_k_embeddings(
    embed_model: BaseEmbedding,
    query_embedding: List[float],
    embeddings: List[List[float]],
    similarity_top_k: Optional[int] = None,
    embedding_ids: Optional[List] = None,
) -> Tuple[List[float], List]:
    """Get top nodes by similarity to the query."""
    if embedding_ids is None:
        embedding_ids = [i for i in range(len(embeddings))]

    similarities = []
    for emb in embeddings:
        similarity = embed_model.similarity(query_embedding, emb)
        similarities.append(similarity)

    sorted_tups = sorted(
        zip(similarities, embedding_ids), key=lambda x: x[0], reverse=True
    )
    similarity_top_k = similarity_top_k or len(sorted_tups)
    result_tups = sorted_tups[:similarity_top_k]

    result_similarities = [s for s, _ in result_tups]
    result_ids = [n for _, n in result_tups]

    return result_similarities, result_ids


class SimilarityTracker:
    """Helper class to manage node similarities 
    during lifecycle of a single query."""

    # TODO: smarter way to store this information
    lookup: Dict[str, float] = {}

    def _hash(self, node: Node):
        # TODO: Better way to get unique identifier of a node
        return abs(hash(node.get_text()))

    def add(self, node: Node, similarity: float):
        node_hash = self._hash(node)
        self.lookup[node_hash] = similarity

    def find(self, node: Node):
        node_hash = self._hash(node)
        if node_hash not in self.lookup:
            return None
        return self.lookup[node_hash]

    def get_zipped_nodes(self, nodes: List[Node]):
        similarities = [self.find(node) for node in nodes]
        return zip(nodes, similarities)
