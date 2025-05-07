class City:
    def __init__(self, name):
        self.name = name
    
    def __eq__(self, other):
        if isinstance(other, City):
            return self.name == other.name
        return False
    
    def __hash__(self):
        return hash(self.name)
    
    def __str__(self):
        return self.name
    
    def __lt__(self, other):
        # Necessário para comparações em filas de prioridade (heapq)
        if isinstance(other, City):
            return self.name < other.name
        return NotImplemented