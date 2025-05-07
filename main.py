import sys
import os
from models.city import City
from utils.data_loader import DataLoader, MockDataLoader
from search.bfs import BFS
from search.dfs import DFS
from search.ucs import UCS
from search.greedy import Greedy
from search.astar import AStar

class PathFinder:
    def __init__(self, use_mock_data=False):
        # Carrega os dados
        if use_mock_data:
            self.graph = MockDataLoader().load_data()
        else:
            # Tenta carregar dados do JSON
            data_loader = DataLoader()
            
            # Verifica se o arquivo JSON existe
            json_path = "data/distances.json"
            if os.path.exists(json_path):
                self.graph = data_loader.load_from_json(json_path)
            else:
                print(f"Arquivo {json_path} não encontrado. Usando dados simulados.")
                self.graph = data_loader._create_mock_data()
        
        # Inicializa os algoritmos
        self.algorithms = {
            "bfs": BFS(),
            "dfs": DFS(),
            "ucs": UCS(),
            "greedy": Greedy(),
            "astar": AStar()
        }
    
    def find_path(self, origin, destination, algorithm_name="astar", transport_type="air"):
        # Converte strings para objetos City
        start = City(origin)
        goal = City(destination)
        
        # Verifica se as cidades existem
        if start not in self.graph.cities or goal not in self.graph.cities:
            print(f"Erro: Uma ou ambas as cidades não foram encontradas.")
            return None
        
        # Seleciona o algoritmo
        algorithm = self.algorithms.get(algorithm_name.lower())
        if not algorithm:
            print(f"Erro: Algoritmo '{algorithm_name}' não encontrado.")
            return None
        
        # Executa a busca
        result = algorithm.search(self.graph, start, goal, transport_type)
        return result
    
    def find_best_transport(self, origin, destination, algorithm_name="astar"):
        # Busca por via aérea
        air_result = self.find_path(origin, destination, algorithm_name, "air")
        
        # Busca por via terrestre
        land_result = self.find_path(origin, destination, algorithm_name, "land")
        
        # Determina o melhor meio de transporte
        if air_result and air_result.path and land_result and land_result.path:
            if air_result.distance <= land_result.distance:
                best_transport = "aéreo"
                best_result = air_result
            else:
                best_transport = "terrestre"
                best_result = land_result
            
            return {
                "air_distance": air_result.distance,
                "land_distance": land_result.distance,
                "best_transport": best_transport,
                "best_result": best_result
            }
        else:
            # Se algum caminho não foi encontrado
            return None
    
    def compare_algorithms(self, origin, destination, transport_type="air"):
        results = {}
        
        for name, algorithm in self.algorithms.items():
            result = algorithm.search(self.graph, City(origin), City(destination), transport_type)
            results[name] = {
                "path": [city.name for city in result.path] if result.path else None,
                "distance": result.distance,
                "expanded_nodes": result.expanded_nodes,
                "is_optimal": result.is_optimal() if hasattr(result, "is_optimal") else "N/A"
            }
        
        return results


def print_menu():
    print("\n===== Sistema de Rotas entre Capitais =====")
    print("1. Encontrar rota entre duas capitais")
    print("2. Comparar algoritmos para uma rota")
    print("3. Analisar cenários de teste")
    print("0. Sair")
    print("==========================================")


def main():
    # Inicializa o sistema
    path_finder = PathFinder(use_mock_data=False)  # Agora usa dados do JSON por padrão
    
    while True:
        print_menu()
        option = input("Escolha uma opção: ")
        
        if option == "0":
            print("Encerrando o programa...")
            break
            
        elif option == "1":
            origin = input("Cidade de origem: ")
            destination = input("Cidade de destino: ")
            algorithm = input("Algoritmo (bfs, dfs, ucs, greedy, astar): ") or "astar"
            
            result = path_finder.find_best_transport(origin, destination, algorithm)
            
            if result:
                print("\n--- Resultados ---")
                print(f"Distância aérea: {result['air_distance']} km")
                print(f"Distância terrestre: {result['land_distance']} km")
                print(f"Melhor meio de transporte: {result['best_transport']}")
                
                best_path = result['best_result'].path
                path_str = " -> ".join([city.name for city in best_path])
                print(f"Caminho: {path_str}")
                print(f"Nós expandidos: {result['best_result'].expanded_nodes}")
            else:
                print("Não foi possível encontrar um caminho.")
                
        elif option == "2":
            origin = input("Cidade de origem: ")
            destination = input("Cidade de destino: ")
            transport = input("Meio de transporte (air/land): ") or "air"
            
            results = path_finder.compare_algorithms(origin, destination, transport)
            
            print("\n--- Comparação de Algoritmos ---")
            for name, result in results.items():
                print(f"\nAlgoritmo: {name.upper()}")
                print(f"Caminho: {' -> '.join(result['path']) if result['path'] else 'Não encontrado'}")
                print(f"Distância: {result['distance']} km")
                print(f"Nós expandidos: {result['expanded_nodes']}")
                print(f"Solução ótima: {result['is_optimal']}")
                
        elif option == "3":
            # Análise de cenários
            scenarios = [
                ("São Paulo", "Rio de Janeiro"),
                ("Porto Alegre", "Manaus"),
                ("Brasília", "Salvador")
            ]
            
            print("\n--- Análise de Cenários ---")
            for origin, destination in scenarios:
                print(f"\nCenário: {origin} -> {destination}")
                results = path_finder.compare_algorithms(origin, destination)
                
                for name, result in results.items():
                    print(f"\n  Algoritmo: {name.upper()}")
                    print(f"  Caminho: {' -> '.join(result['path']) if result['path'] else 'Não encontrado'}")
                    print(f"  Distância: {result['distance']} km")
                    print(f"  Nós expandidos: {result['expanded_nodes']}")
                
        else:
            print("Opção inválida. Tente novamente.")


if __name__ == "__main__":
    main()