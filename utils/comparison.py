from tabulate import tabulate
import matplotlib.pyplot as plt
import numpy as np
import os

class AlgorithmComparison:
    def __init__(self):
        self.results = {}
        self.scenarios = []
    
    def add_scenario(self, name, results):
        self.scenarios.append(name)
        self.results[name] = results
    
    def print_table(self):
        algorithms = list(self.results[self.scenarios[0]].keys())
        
        for scenario in self.scenarios:
            print(f"\n=== Cenário: {scenario} ===\n")
            
            table_data = []
            headers = ["Algoritmo", "Caminho", "Distância", "Nós Expandidos", "Solução Ótima"]
            
            for algo in algorithms:
                result = self.results[scenario][algo]
                row = [
                    algo.upper(),
                    " -> ".join(result["path"]) if result["path"] else "Não encontrado",
                    f"{result['distance']} km",
                    result["expanded_nodes"],
                    result["is_optimal"]
                ]
                table_data.append(row)
            
            print(tabulate(table_data, headers=headers, tablefmt="grid"))
    
    def generate_chart(self, output_dir="./output"):
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        algorithms = list(self.results[self.scenarios[0]].keys())
        
        # Gráfico de barras para nós expandidos
        plt.figure(figsize=(12, 6))
        x = np.arange(len(self.scenarios))
        width = 0.15
        multiplier = 0
        
        for algorithm in algorithms:
            expanded_nodes = [self.results[scenario][algorithm]["expanded_nodes"] for scenario in self.scenarios]
            offset = width * multiplier
            rects = plt.bar(x + offset, expanded_nodes, width, label=algorithm.upper())
            multiplier += 1
        
        plt.xlabel('Cenários')
        plt.ylabel('Nós Expandidos')
        plt.title('Comparação de Nós Expandidos por Algoritmo')
        plt.xticks(x + width * (len(algorithms) - 1) / 2, self.scenarios)
        plt.legend(loc='upper left')
        plt.savefig(f"{output_dir}/expanded_nodes_comparison.png", dpi=300, bbox_inches='tight')
        
        # Gráfico de barras para distâncias
        plt.figure(figsize=(12, 6))
        multiplier = 0
        
        for algorithm in algorithms:
            distances = [self.results[scenario][algorithm]["distance"] for scenario in self.scenarios]
            offset = width * multiplier
            rects = plt.bar(x + offset, distances, width, label=algorithm.upper())
            multiplier += 1
        
        plt.xlabel('Cenários')
        plt.ylabel('Distância (km)')
        plt.title('Comparação de Distâncias por Algoritmo')
        plt.xticks(x + width * (len(algorithms) - 1) / 2, self.scenarios)
        plt.legend(loc='upper left')
        plt.savefig(f"{output_dir}/distance_comparison.png", dpi=300, bbox_inches='tight')
        
        print(f"Gráficos salvos no diretório {output_dir}")
        
    def export_to_csv(self, output_file="results.csv"):
        algorithms = list(self.results[self.scenarios[0]].keys())
        
        with open(output_file, 'w', encoding='utf-8') as f:
            # Cabeçalho
            f.write("Cenário,Algoritmo,Caminho,Distância (km),Nós Expandidos,Solução Ótima\n")
            
            # Dados
            for scenario in self.scenarios:
                for algo in algorithms:
                    result = self.results[scenario][algo]
                    path = " -> ".join(result["path"]) if result["path"] else "Não encontrado"
                    distance = result["distance"]
                    expanded_nodes = result["expanded_nodes"]
                    is_optimal = result["is_optimal"]
                    
                    f.write(f"{scenario},{algo.upper()},\"{path}\",{distance},{expanded_nodes},{is_optimal}\n")
        
        print(f"Resultados exportados para {output_file}")


# Exemplo de uso
if __name__ == "__main__":
    comparison = AlgorithmComparison()
    
    # Cenário 1: São Paulo -> Rio de Janeiro
    scenario1_results = {
        "bfs": {
            "path": ["São Paulo", "Rio de Janeiro"],
            "distance": 400,
            "expanded_nodes": 2,
            "is_optimal": "Sim"
        },
        "dfs": {
            "path": ["São Paulo", "Rio de Janeiro"],
            "distance": 400,
            "expanded_nodes": 2,
            "is_optimal": "Sim"
        },
        "ucs": {
            "path": ["São Paulo", "Rio de Janeiro"],
            "distance": 400,
            "expanded_nodes": 2,
            "is_optimal": "Sim"
        },
        "greedy": {
            "path": ["São Paulo", "Rio de Janeiro"],
            "distance": 400,
            "expanded_nodes": 2,
            "is_optimal": "Sim"
        },
        "astar": {
            "path": ["São Paulo", "Rio de Janeiro"],
            "distance": 400,
            "expanded_nodes": 2,
            "is_optimal": "Sim"
        }
    }
    
    comparison.add_scenario("São Paulo -> Rio de Janeiro", scenario1_results)
    
    # Adicione mais cenários...
    
    # Exibe tabela
    comparison.print_table()
    
    # Gera gráficos
    comparison.generate_chart()
    
    # Exporta para CSV
    comparison.export_to_csv()