import heapq
from search.interface import SearchAlgorithm, SearchResult

class Greedy(SearchAlgorithm):
    def search(self, graph, start, goal, transport_type="air"):
        # Função heurística (distância direta)
        def heuristic(city):
            return graph.get_air_distance(city, goal)
        
        # Inicializa variáveis
        priority_queue = [(heuristic(start), 0, start, [start])]  # (heurística, custo, cidade, caminho)
        visited = set()
        expanded_nodes = 0
        
        while priority_queue:
            # Remove o nó de menor heurística
            _, cost, current, path = heapq.heappop(priority_queue)
            
            # Se já visitou, continua
            if current in visited:
                continue
            
            visited.add(current)
            expanded_nodes += 1
            
            # Verifica se é o objetivo
            if current == goal:
                return SearchResult(path, cost, expanded_nodes)
            
            # Expande o nó
            for neighbor, step_cost in graph.get_neighbors(current, transport_type):
                if neighbor not in visited:
                    new_cost = cost + step_cost
                    new_path = path + [neighbor]
                    # A prioridade é baseada apenas na heurística
                    heapq.heappush(priority_queue, (heuristic(neighbor), new_cost, neighbor, new_path))
        
        # Se não encontrar caminho
        return SearchResult(expanded_nodes=expanded_nodes)