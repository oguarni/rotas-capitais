from search.interface import SearchAlgorithm, SearchResult

class DFS(SearchAlgorithm):
    def search(self, graph, start, goal, transport_type="air"):
        # Inicializa variáveis
        stack = [(start, [start], 0)]  # (cidade, caminho, distância)
        visited = set([start])
        expanded_nodes = 0
        
        while stack:
            # Remove um nó da pilha
            current, path, distance = stack.pop()
            expanded_nodes += 1
            
            # Verifica se é o objetivo
            if current == goal:
                return SearchResult(path, distance, expanded_nodes)
            
            # Expande o nó
            neighbors = graph.get_neighbors(current, transport_type)
            # Inverte para processar na ordem correta
            for neighbor, step_distance in reversed(neighbors):
                if neighbor not in visited:
                    visited.add(neighbor)
                    new_path = path + [neighbor]
                    new_distance = distance + step_distance
                    stack.append((neighbor, new_path, new_distance))
        
        # Se não encontrar caminho
        return SearchResult(expanded_nodes=expanded_nodes)