from typing import List, Optional, Dict, Tuple, Set

from Pool import Pool
from Token import Token


class Graph:
    def __init__(self):
        self.graph: Dict[Token, List[Tuple[Token, Pool]]] = {}

    # Add a new Pair to the graph
    def add_pair(self, pair: Pool):
        if pair.tokenX not in self.graph:
            self.graph[pair.tokenX] = []
        if pair.tokenY not in self.graph:
            self.graph[pair.tokenY] = []

        # Ensure the pair isn't already in the graph
        if not any(p for t, p in self.graph[pair.tokenX] if p == pair):
            self.graph[pair.tokenX].append((pair.tokenY, pair))
            self.graph[pair.tokenY].append((pair.tokenX, pair))

    def get_neighbors(self, token: Token) -> List[Token]:
        return [t for t, _ in self.graph.get(token, [])]

    def get_pair(self, token1: Token, token2: Token) -> Optional[Pool]:
        for t, pair in self.graph.get(token1, []):
            if t == token2:
                return pair
        return None

    # Retrieve a token using its address or name
    def get_token(self, identifier: str) -> Optional[Token]:
        for token_list in self.graph.values():
            for token, _ in token_list:
                if token.tokenAddress == identifier or token.name == identifier:
                    return token
        return None

    # Recursively find all paths (as pairs) in the graph from start to end
    def find_path_pairs(self, start_id: str, end_id: str, visited: Set[Token] = None, max_length: int = 3) -> List[List[Pool]]:
        start = self.get_token(start_id)
        end = self.get_token(end_id)

        if not start or not end:
            return []  # One of the tokens doesn't exist

        if visited is None:
            visited = set()
        if start == end:
            return [[]]

        visited.add(start)
        paths = []
        seen_paths = set()  # Store hashes of seen paths
        for neighbor, current_pair in self.graph.get(start, []):
            if neighbor not in visited:
                for path in self.find_path_pairs(neighbor.tokenAddress, end.tokenAddress, visited, max_length):
                    combined_path = [current_pair] + path
                    # Create a hash of the current path
                    path_hash = hash(tuple(
                        (p.tokenX.tokenAddress, p.tokenY.tokenAddress, p.name, p.lbBinStep) for p in combined_path))
                    if len(combined_path) <= max_length and path_hash not in seen_paths:
                        paths.append(combined_path)
                        seen_paths.add(path_hash)

        visited.remove(start)
        return paths