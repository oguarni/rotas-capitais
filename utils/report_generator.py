import os
from datetime import datetime

class ReportGenerator:
    def __init__(self, output_dir="./output"):
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
    
    def generate_report(self, comparison_results, scenarios):
        # Nome do arquivo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.output_dir}/relatorio_{timestamp}.md"
        
        with open(filename, 'w', encoding='utf-8') as f:
            # Cabeçalho
            f.write("# Relatório Comparativo de Algoritmos de Busca\n\n")
            f.write(f"Data de geração: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n")
            
            # Introdução
            f.write("## Introdução\n\n")
            f.write("Este relatório apresenta uma comparação entre diferentes algoritmos de busca ")
            f.write("para encontrar rotas entre capitais brasileiras. Os algoritmos comparados são:\n\n")
            f.write("1. Busca em Largura (BFS)\n")
            f.write("2. Busca em Profundidade (DFS)\n")
            f.write("3. Busca de Custo Uniforme (UCS)\n")
            f.write("4. Busca Gulosa (Greedy)\n")
            f.write("5. Busca A* (A-Star)\n\n")
            
            # Metodologia
            f.write("## Metodologia\n\n")
            f.write("Para cada cenário, foram executados os cinco algoritmos e coletados os seguintes dados:\n\n")
            f.write("- Caminho encontrado\n")
            f.write("- Distância total\n")
            f.write("- Número de nós expandidos\n")
            f.write("- Se a solução é ótima\n\n")
            
            # Cenários
            f.write("## Cenários Analisados\n\n")
            for i, scenario in enumerate(scenarios, 1):
                f.write(f"### Cenário {i}: {scenario}\n\n")
                
                # Resultados tabulares
                f.write("#### Resultados\n\n")
                f.write("| Algoritmo | Caminho | Distância (km) | Nós Expandidos | Solução Ótima |\n")
                f.write("|-----------|---------|----------------|----------------|---------------|\n")
                
                for algo, result in comparison_results[scenario].items():
                    path = " -> ".join(result["path"]) if result["path"] else "Não encontrado"
                    distance = result["distance"]
                    expanded_nodes = result["expanded_nodes"]
                    is_optimal = result["is_optimal"]
                    
                    f.write(f"| {algo.upper()} | {path} | {distance} | {expanded_nodes} | {is_optimal} |\n")
                
                f.write("\n")
                
                # Análise do cenário
                f.write("#### Análise\n\n")
                
                # Encontra o algoritmo com menor distância
                min_distance = float('inf')
                min_distance_algos = []
                
                for algo, result in comparison_results[scenario].items():
                    if result["path"] and result["distance"] < min_distance:
                        min_distance = result["distance"]
                        min_distance_algos = [algo]
                    elif result["path"] and result["distance"] == min_distance:
                        min_distance_algos.append(algo)
                
                f.write(f"Para o cenário {scenario}, ")
                if min_distance_algos:
                    if len(min_distance_algos) == 1:
                        f.write(f"o algoritmo {min_distance_algos[0].upper()} encontrou ")
                    else:
                        algos_str = ", ".join([a.upper() for a in min_distance_algos[:-1]]) + " e " + min_distance_algos[-1].upper()
                        f.write(f"os algoritmos {algos_str} encontraram ")
                    f.write(f"o caminho mais curto, com distância de {min_distance} km.\n\n")
                else:
                    f.write("nenhum algoritmo encontrou um caminho válido.\n\n")
                
                # Encontra o algoritmo com menor número de nós expandidos
                min_nodes = float('inf')
                min_nodes_algos = []
                
                for algo, result in comparison_results[scenario].items():
                    if result["path"] and result["expanded_nodes"] < min_nodes:
                        min_nodes = result["expanded_nodes"]
                        min_nodes_algos = [algo]
                    elif result["path"] and result["expanded_nodes"] == min_nodes:
                        min_nodes_algos.append(algo)
                
                if min_nodes_algos:
                    if len(min_nodes_algos) == 1:
                        f.write(f"O algoritmo {min_nodes_algos[0].upper()} foi o mais eficiente ")
                    else:
                        algos_str = ", ".join([a.upper() for a in min_nodes_algos[:-1]]) + " e " + min_nodes_algos[-1].upper()
                        f.write(f"Os algoritmos {algos_str} foram os mais eficientes ")
                    f.write(f"em termos de nós expandidos, com apenas {min_nodes} nós.\n\n")
                
                # Comparação geral
                f.write("Comparando os algoritmos:\n\n")
                
                all_optimal = True
                for algo, result in comparison_results[scenario].items():
                    if result["path"] and result["is_optimal"] != "Sim":
                        all_optimal = False
                        break
                
                if all_optimal:
                    f.write("- Todos os algoritmos encontraram soluções ótimas para este cenário.\n")
                else:
                    f.write("- Nem todos os algoritmos encontraram soluções ótimas para este cenário.\n")
                    
                    for algo, result in comparison_results[scenario].items():
                        if result["path"] and result["is_optimal"] != "Sim":
                            f.write(f"  - {algo.upper()} não encontrou uma solução ótima.\n")
                
                f.write("\n")
            
            # Análise geral
            f.write("## Análise Geral\n\n")
            
            # Desempenho médio dos algoritmos
            f.write("### Desempenho Médio\n\n")
            f.write("| Algoritmo | Distância Média (km) | Nós Expandidos Médios |\n")
            f.write("|-----------|----------------------|------------------------|\n")
            
            algorithms = list(comparison_results[scenarios[0]].keys())
            
            for algo in algorithms:
                total_distance = 0
                total_nodes = 0
                count = 0
                
                for scenario in scenarios:
                    result = comparison_results[scenario][algo]
                    if result["path"]:
                        total_distance += result["distance"]
                        total_nodes += result["expanded_nodes"]
                        count += 1
                
                if count > 0:
                    avg_distance = total_distance / count
                    avg_nodes = total_nodes / count
                    f.write(f"| {algo.upper()} | {avg_distance:.2f} | {avg_nodes:.2f} |\n")
                else:
                    f.write(f"| {algo.upper()} | N/A | N/A |\n")
            
            f.write("\n")
            
            # Conclusão
            f.write("## Conclusão\n\n")
            
            # Encontra o melhor algoritmo geral
            best_algo = None
            best_avg_nodes = float('inf')
            all_optimal = True
            
            for algo in algorithms:
                total_nodes = 0
                count = 0
                optimal_count = 0
                
                for scenario in scenarios:
                    result = comparison_results[scenario][algo]
                    if result["path"]:
                        total_nodes += result["expanded_nodes"]
                        count += 1
                        if result["is_optimal"] == "Sim":
                            optimal_count += 1
                
                if count > 0:
                    avg_nodes = total_nodes / count
                    if optimal_count == count and avg_nodes < best_avg_nodes:
                        best_avg_nodes = avg_nodes
                        best_algo = algo
                    if optimal_count != count:
                        all_optimal = False
            
            if best_algo:
                f.write(f"Com base nos cenários analisados, o algoritmo {best_algo.upper()} ")
                f.write("se mostrou o mais eficiente em termos de nós expandidos, ")
                f.write("mantendo a otimalidade da solução em todos os casos. ")
                
                if best_algo == "astar":
                    f.write("Isso era esperado, pois A* é conhecido por sua eficiência ")
                    f.write("quando se tem uma boa heurística.\n\n")
                elif best_algo == "greedy":
                    f.write("Isso é um resultado interessante, pois a Busca Gulosa normalmente ")
                    f.write("não garante otimalidade, mas nestes cenários específicos, ")
                    f.write("a heurística utilizada foi suficiente para encontrar caminhos ótimos.\n\n")
                elif best_algo == "ucs":
                    f.write("Isso é consistente com a teoria, pois a Busca de Custo Uniforme ")
                    f.write("sempre encontra o caminho ótimo, embora possa expandir mais nós ")
                    f.write("que algoritmos informados como A*.\n\n")
                else:
                    f.write("Este resultado é interessante e pode ser explicado pelas características ")
                    f.write("específicas dos cenários analisados.\n\n")
            
            if not all_optimal:
                f.write("Vale notar que nem todos os algoritmos garantem soluções ótimas em todos os cenários. ")
                f.write("Particularmente, DFS e Busca Gulosa não têm garantia teórica de otimalidade, ")
                f.write("enquanto BFS (para grafos não ponderados), UCS e A* garantem soluções ótimas.\n\n")
            
            f.write("Este relatório demonstra a importância de escolher o algoritmo adequado ")
            f.write("para cada problema específico, considerando fatores como garantia de ")
            f.write("otimalidade, eficiência computacional e características do domínio do problema.\n")
        
        print(f"Relatório gerado: {filename}")
        return filename


# Exemplo de uso
if __name__ == "__main__":
    from utils.comparison import AlgorithmComparison
    
    # Configura a comparação (mesmo exemplo do módulo comparison.py)
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
    
    # Gera relatório
    report_generator = ReportGenerator()
    report_file = report_generator.generate_report(
        comparison.results, 
        comparison.scenarios
    )