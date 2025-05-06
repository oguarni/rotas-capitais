class Graph:
    def __init__(self):
        self.cities = set()
        self.air_distances = {}
        self.land_distances = {}
    
    def add_city(self, city):
        self.cities.add(city)
    
    def add_air_distance(self, city1, city2, distance):
        if city1 not in self.cities:
            self.add_city(city1)
        if city2 not in self.cities:
            self.add_city(city2)
        
        self.air_distances[(city1, city2)] = distance
        self.air_distances[(city2, city1)] = distance
    
    def add_land_distance(self, city1, city2, distance):
        if city1 not in self.cities:
            self.add_city(city1)
        if city2 not in self.cities:
            self.add_city(city2)
        
        self.land_distances[(city1, city2)] = distance
        self.land_distances[(city2, city1)] = distance
    
    def get_neighbors(self, city, transport_type="air"):
        neighbors = []
        distances = self.air_distances if transport_type == "air" else self.land_distances
        
        for key, distance in distances.items():
            if key[0] == city:
                neighbors.append((key[1], distance))
        
        return neighbors
    
    def get_air_distance(self, city1, city2):
        return self.air_distances.get((city1, city2), float('inf'))
    
    def get_land_distance(self, city1, city2):
        return self.land_distances.get((city1, city2), float('inf'))