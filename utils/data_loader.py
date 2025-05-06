import csv
import requests
from io import StringIO
from models.city import City
from models.graph import Graph

class DataLoader:
    def __init__(self):
        self.graph = Graph()
        
    def load_from_url(self, url):
        try:
            response = requests.get(url)
            response.raise_for_status()
            csv_data = StringIO(response.text)
            self._parse_csv(csv_data)
            return self.graph
        except Exception as e:
            print(f"Erro ao carregar dados da URL {url}: {e}")
            return None
    
    def load_from_file(self, filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                self._parse_csv(file)
            return self.graph
        except Exception as e:
            print(f"Erro ao carregar dados do arquivo {filepath}: {e}")
            return None
    
    def _parse_csv(self, csv_data):
        # Implementação para parsear o CSV específico
        # Esta é uma versão simplificada, deve ser adaptada ao formato real
        
        reader = csv.reader(csv_data, delimiter=',')
        headers = next(reader)  # Primeira linha é o cabeçalho
        
        # Cria cidades baseadas no cabeçalho (ignorando primeira coluna)
        cities = [City(name) for name in headers[1:]]
        
        # Adiciona cidades ao grafo
        for city in cities:
            self.graph.add_city(city)
        
        # Processa distâncias
        for i, row in enumerate(reader):
            source_city = City(row[0])
            
            for j, value in enumerate(row[1:], 1):
                if value and value.strip():
                    # Assume que o formato é "aéreo/terrestre"
                    if '/' in value:
                        air, land = map(float, value.split('/'))
                        target_city = City(headers[j])
                        
                        self.graph.add_air_distance(source_city, target_city, air)
                        self.graph.add_land_distance(source_city, target_city, land)
        
        return self.graph

# Alternativa: implementar um carregador de dados simulados
class MockDataLoader:
    def load_data(self):
        graph = Graph()
        
        # Cria algumas capitais
        bsb = City("Brasília")
        sp = City("São Paulo")
        rj = City("Rio de Janeiro")
        bh = City("Belo Horizonte")
        sal = City("Salvador")
        rec = City("Recife")
        for = City("Fortaleza")
        bel = City("Belém")
        man = City("Manaus")
        poa = City("Porto Alegre")
        
        # Adiciona cidades
        for city in [bsb, sp, rj, bh, sal, rec, for, bel, man, poa]:
            graph.add_city(city)
        
        # Adiciona distâncias (valores são apenas exemplos)
        # Brasília conexões
        graph.add_air_distance(bsb, sp, 1000)
        graph.add_land_distance(bsb, sp, 1200)
        
        graph.add_air_distance(bsb, rj, 1100)
        graph.add_land_distance(bsb, rj, 1350)
        
        graph.add_air_distance(bsb, bh, 700)
        graph.add_land_distance(bsb, bh, 730)
        
        graph.add_air_distance(bsb, sal, 1400)
        graph.add_land_distance(bsb, sal, 1650)
        
        # São Paulo conexões
        graph.add_air_distance(sp, rj, 400)
        graph.add_land_distance(sp, rj, 450)
        
        graph.add_air_distance(sp, bh, 600)
        graph.add_land_distance(sp, bh, 630)
        
        graph.add_air_distance(sp, poa, 850)
        graph.add_land_distance(sp, poa, 1100)
        
        # Mais conexões...
        
        return graph