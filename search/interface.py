from abc import ABC, abstractmethod

class SearchResult:
    def __init__(self, path=None, distance=0, expanded_nodes=0):
        self.path = path or []
        self.distance = distance
        self.expanded_nodes = expanded_nodes
    
    def is_optimal(self):
        # Este método deve ser implementado com base no conhecimento
        # do problema específico para verificar se a solução é ótima
        pass

class SearchAlgorithm(ABC):
    @abstractmethod
    def search(self, graph, start, goal, transport_type="air"):
        """
        Executa o algoritmo de busca
        
        Args:
            graph: O grafo que representa as cidades e conexões
            start: A cidade de origem
            goal: A cidade de destino
            transport_type: Tipo de transporte ("air" ou "land")
            
        Returns:
            SearchResult: O resultado da busca
        """
        pass