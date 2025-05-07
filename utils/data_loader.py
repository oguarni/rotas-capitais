import json
import os
from models.city import City
from models.graph import Graph

class DataLoader:
    def __init__(self):
        self.graph = Graph()
        
    def load_from_json(self, json_file="data/distances.json"):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Adiciona todas as capitais ao grafo
            for capital in data['capitals']:
                self.graph.add_city(City(capital))
            
            # Adiciona distâncias terrestres
            for origin, destinations in data['distances']['land'].items():
                for destination, distance in destinations.items():
                    # Não adiciona distâncias para a mesma cidade
                    if origin != destination:
                        self.graph.add_land_distance(City(origin), City(destination), distance)
            
            # Se houver dados aéreos no JSON, usa eles
            if 'air' in data['distances']:
                for origin, destinations in data['distances']['air'].items():
                    for destination, distance in destinations.items():
                        if origin != destination:
                            self.graph.add_air_distance(City(origin), City(destination), distance)
            else:
                # Se não houver dados aéreos, usa os mesmos valores das distâncias terrestres
                # temporariamente (isso deve ser substituído por dados reais)
                print("ATENÇÃO: Dados de distâncias aéreas não encontrados no JSON.")
                print("As distâncias terrestres serão usadas como aproximação.")
                print("Substitua isto pelos dados reais de distâncias aéreas.")
                
                for origin, destinations in data['distances']['land'].items():
                    for destination, distance in destinations.items():
                        if origin != destination:
                            self.graph.add_air_distance(City(origin), City(destination), distance)
            
            return self.graph
        except Exception as e:
            print(f"Erro ao carregar dados do arquivo JSON {json_file}: {e}")
            # Fallback para dados simulados
            return self._create_mock_data()
    
    def create_air_distances_json(self):
        """
        Cria um template para adicionar distâncias aéreas.
        Use este método para criar um arquivo JSON que você pode
        preencher com dados reais das distâncias aéreas.
        """
        try:
            # Carrega as distâncias terrestres para usar os mesmos pares de cidades
            with open("data/distances.json", 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Cria a estrutura para distâncias aéreas (inicialmente vazias)
            air_distances = {}
            
            for origin in data['capitals']:
                air_distances[origin] = {}
                for destination in data['capitals']:
                    if origin != destination:
                        # Inicialmente, atribui valor 0 (deve ser substituído pelo valor real)
                        air_distances[origin][destination] = 0
            
            # Adiciona as distâncias aéreas ao dicionário de dados
            data['distances']['air'] = air_distances
            
            # Salva o arquivo JSON atualizado
            with open("data/distances_with_air.json", 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
            print("Arquivo template para distâncias aéreas criado: data/distances_with_air.json")
            print("Preencha os valores '0' com as distâncias aéreas reais.")
            
        except Exception as e:
            print(f"Erro ao criar template para distâncias aéreas: {e}")
    
    def _create_mock_data(self):
        """Cria dados simulados em caso de erro na leitura do JSON"""
        print("Usando dados simulados como fallback.")
        graph = Graph()
        
        # Cria algumas capitais
        bsb = City("Brasília")
        sp = City("São Paulo")
        rj = City("Rio de Janeiro")
        bh = City("Belo Horizonte")
        sal = City("Salvador")
        rec = City("Recife")
        fortaleza = City("Fortaleza")
        bel = City("Belém")
        man = City("Manaus")
        poa = City("Porto Alegre")
        
        # Adiciona cidades
        for city in [bsb, sp, rj, bh, sal, rec, fortaleza, bel, man, poa]:
            graph.add_city(city)
        
        # Adiciona distâncias terrestres das principais rotas
        # Brasília
        graph.add_land_distance(bsb, sp, 1015)
        graph.add_land_distance(bsb, rj, 1148)
        graph.add_land_distance(bsb, bh, 716)
        graph.add_land_distance(bsb, sal, 1446)
        
        # São Paulo
        graph.add_land_distance(sp, rj, 429)
        graph.add_land_distance(sp, bh, 586)
        graph.add_land_distance(sp, poa, 1109)
        
        # Rio de Janeiro
        graph.add_land_distance(rj, bh, 434)
        
        # Belo Horizonte
        graph.add_land_distance(bh, sal, 1372)
        
        # Salvador
        graph.add_land_distance(sal, rec, 839)
        
        # Recife
        graph.add_land_distance(rec, fortaleza, 800)
        
        # Adiciona distâncias aéreas das principais rotas
        # Brasília
        graph.add_air_distance(bsb, sp, 873)
        graph.add_air_distance(bsb, rj, 930)
        graph.add_air_distance(bsb, bh, 624)
        graph.add_air_distance(bsb, sal, 1060)
        
        # São Paulo
        graph.add_air_distance(sp, rj, 400)
        graph.add_air_distance(sp, bh, 480)
        graph.add_air_distance(sp, poa, 852)
        
        # Rio de Janeiro
        graph.add_air_distance(rj, bh, 361)
        
        # Belo Horizonte
        graph.add_air_distance(bh, sal, 964)
        
        # Salvador
        graph.add_air_distance(sal, rec, 675)
        
        # Recife
        graph.add_air_distance(rec, fortaleza, 629)
        
        # Conexões Norte
        graph.add_air_distance(bsb, man, 1932)
        graph.add_air_distance(man, bel, 1292)
        
        return graph


# Classe para testes
class MockDataLoader:
    def load_data(self):
        """Função mantida para compatibilidade com o código existente"""
        return DataLoader()._create_mock_data()
