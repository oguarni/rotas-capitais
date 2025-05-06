from collections import deque
from search.interface import SearchAlgorithm, SearchResult

class BFS(SearchAlgorithm):
    def search(self, graph, start, goal, transport_type="air"):
        # Inicializa variáveis
        queue = deque([(start, [start], 0)])  # (cidade, caminho, distância)
        visited = set([start])
        expanded_nodes = 0
        
        while queue:
            # Remove um nó da fila
            current, path, distance = queue.popleft()
            expanded_nodes += 1
            
            # Verifica se é o objetivo
            if current == goal:
                return SearchResult(path, distance, expanded_nodes)
            
            # Expande o nó
            for neighbor, step_distance in graph.get_neighbors(current, transport_type):
                if neighbor not in visited:
                    visited.add(neighbor)
                    new_path = path + [neighbor]
                    new_distance = distance + step_distance
                    queue.append((neighbor, new_path, new_distance))
        
        # Se não encontrar caminho
        return SearchResult(expanded_nodes=expanded_nodes)
