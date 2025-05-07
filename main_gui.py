import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import networkx as nx
import json
import os
from models.city import City
from models.graph import Graph
from search.bfs import BFS
from search.dfs import DFS
from search.ucs import UCS
from search.greedy import Greedy
from search.astar import AStar
from utils.data_loader import DataLoader

class RouteFinderApp(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("Busca de Rotas entre Capitais Brasileiras")
        self.geometry("1200x800")
        self.configure(bg="#f0f0f0")
        
        # Carregamento de dados
        self.data_loader = DataLoader()
        self.graph = self.load_graph()
        
        # Obtem a lista de capitais
        self.capitals = sorted([city.name for city in self.graph.cities])
        
        # Algoritmos de busca
        self.algorithms = {
            "BFS (Busca em Largura)": BFS(),
            "DFS (Busca em Profundidade)": DFS(),
            "UCS (Busca de Custo Uniforme)": UCS(),
            "Greedy (Busca Gulosa)": Greedy(),
            "A* (A-Star)": AStar()
        }
        
        # Inicializa a interface
        self.create_widgets()
    
    def load_graph(self):
        try:
            # Tenta carregar dados do JSON
            json_path = "data/distances.json"
            if os.path.exists(json_path):
                return self.data_loader.load_from_json(json_path)
            else:
                messagebox.showwarning("Aviso", f"Arquivo {json_path} não encontrado. Usando dados simulados.")
                return self.data_loader._create_mock_data()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar dados: {e}")
            return self.data_loader._create_mock_data()
    
    def create_widgets(self):
        # Frame principal
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Frames para organização
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Estilo
        style = ttk.Style()
        style.configure("TLabel", font=("Arial", 12))
        style.configure("TButton", font=("Arial", 12))
        style.configure("TRadiobutton", font=("Arial", 11))
        
        # Frame de entrada
        input_frame = ttk.LabelFrame(left_frame, text="Parâmetros de Busca", padding=10)
        input_frame.pack(fill=tk.BOTH, expand=False, padx=10, pady=10)
        
        # Seleção de origem e destino
        ttk.Label(input_frame, text="Cidade de origem:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.origin_var = tk.StringVar()
        origin_combo = ttk.Combobox(input_frame, textvariable=self.origin_var, values=self.capitals, state="readonly", width=30)
        origin_combo.grid(row=0, column=1, padx=5, pady=5)
        origin_combo.current(self.capitals.index("São Paulo") if "São Paulo" in self.capitals else 0)
        
        ttk.Label(input_frame, text="Cidade de destino:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.destination_var = tk.StringVar()
        destination_combo = ttk.Combobox(input_frame, textvariable=self.destination_var, values=self.capitals, state="readonly", width=30)
        destination_combo.grid(row=1, column=1, padx=5, pady=5)
        destination_combo.current(self.capitals.index("Rio de Janeiro") if "Rio de Janeiro" in self.capitals else 1)
        
        # Seleção do algoritmo
        ttk.Label(input_frame, text="Algoritmo:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.algorithm_var = tk.StringVar(value=list(self.algorithms.keys())[0])
        algorithm_frame = ttk.Frame(input_frame)
        algorithm_frame.grid(row=2, column=1, sticky=tk.W, pady=5)
        
        for i, algo_name in enumerate(self.algorithms.keys()):
            ttk.Radiobutton(
                algorithm_frame, 
                text=algo_name, 
                variable=self.algorithm_var, 
                value=algo_name
            ).grid(row=i//2, column=i%2, sticky=tk.W, padx=5, pady=2)
        
        # Seleção do tipo de transporte
        ttk.Label(input_frame, text="Tipo de transporte:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.transport_var = tk.StringVar(value="air")
        transport_frame = ttk.Frame(input_frame)
        transport_frame.grid(row=3, column=1, sticky=tk.W, pady=5)
        
        ttk.Radiobutton(
            transport_frame, 
            text="Aéreo", 
            variable=self.transport_var, 
            value="air"
        ).grid(row=0, column=0, sticky=tk.W, padx=5)
        
        ttk.Radiobutton(
            transport_frame, 
            text="Terrestre", 
            variable=self.transport_var, 
            value="land"
        ).grid(row=0, column=1, sticky=tk.W, padx=5)
        
        # Botão de busca
        search_button = ttk.Button(input_frame, text="Buscar Rota", command=self.search_route)
        search_button.grid(row=4, column=0, columnspan=2, pady=15)
        
        # Botão para comparar algoritmos
        compare_button = ttk.Button(input_frame, text="Comparar Algoritmos", command=self.compare_algorithms)
        compare_button.grid(row=5, column=0, columnspan=2, pady=5)
        
        # Frame de resultados
        result_frame = ttk.LabelFrame(left_frame, text="Resultados", padding=10)
        result_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Área de texto para resultados
        self.result_text = tk.Text(result_frame, wrap=tk.WORD, width=50, height=20)
        self.result_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Scrollbar para área de texto
        scrollbar = ttk.Scrollbar(self.result_text, command=self.result_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.result_text.config(yscrollcommand=scrollbar.set)
        
        # Frame para visualização do grafo
        graph_frame = ttk.LabelFrame(right_frame, text="Visualização do Caminho", padding=10)
        graph_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Inicializa a figura para o gráfico
        self.figure = plt.Figure(figsize=(6, 6), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, graph_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Inicializa o grafo vazio
        self.draw_empty_graph()
    
    def search_route(self):
        # Limpa resultados anteriores
        self.result_text.delete(1.0, tk.END)
        
        # Obtem parâmetros
        origin = self.origin_var.get()
        destination = self.destination_var.get()
        algorithm_name = self.algorithm_var.get()
        transport_type = self.transport_var.get()
        
        # Verifica se origem e destino são diferentes
        if origin == destination:
            messagebox.showerror("Erro", "Origem e destino devem ser diferentes!")
            return
        
        # Busca a rota
        self.result_text.insert(tk.END, f"Buscando rota de {origin} para {destination}...\n")
        self.result_text.insert(tk.END, f"Algoritmo: {algorithm_name}\n")
        self.result_text.insert(tk.END, f"Transporte: {'Aéreo' if transport_type == 'air' else 'Terrestre'}\n\n")
        
        # Converte strings para objetos City
        start = City(origin)
        goal = City(destination)
        
        # Verifica se as cidades existem
        if start not in self.graph.cities or goal not in self.graph.cities:
            self.result_text.insert(tk.END, "Erro: Uma ou ambas as cidades não foram encontradas no grafo.\n")
            return
        
        # Seleciona o algoritmo
        algorithm = self.algorithms[algorithm_name]
        
        # Executa a busca
        try:
            self.result_text.insert(tk.END, "Executando busca...\n")
            result = algorithm.search(self.graph, start, goal, transport_type)
            
            if result and result.path:
                # Exibe o resultado
                path_str = " → ".join([city.name for city in result.path])
                self.result_text.insert(tk.END, f"\nCaminho encontrado: {path_str}\n")
                self.result_text.insert(tk.END, f"Distância total: {result.distance} km\n")
                self.result_text.insert(tk.END, f"Nós expandidos: {result.expanded_nodes}\n")
                
                # Verifica se é solução ótima
                is_optimal = self.check_if_optimal(result, start, goal, transport_type)
                self.result_text.insert(tk.END, f"Solução ótima: {'Sim' if is_optimal else 'Não'}\n")
                
                # Visualiza o caminho
                self.visualize_path(result.path)
            else:
                self.result_text.insert(tk.END, "\nNão foi possível encontrar um caminho.\n")
                self.draw_empty_graph()
        
        except Exception as e:
            self.result_text.insert(tk.END, f"\nErro durante a busca: {e}\n")
            import traceback
            traceback.print_exc()
    
    def compare_algorithms(self):
        # Limpa resultados anteriores
        self.result_text.delete(1.0, tk.END)
        
        # Obtem parâmetros
        origin = self.origin_var.get()
        destination = self.destination_var.get()
        transport_type = self.transport_var.get()
        
        # Verifica se origem e destino são diferentes
        if origin == destination:
            messagebox.showerror("Erro", "Origem e destino devem ser diferentes!")
            return
        
        # Título
        self.result_text.insert(tk.END, f"Comparação de Algoritmos\n")
        self.result_text.insert(tk.END, f"Rota: {origin} → {destination}\n")
        self.result_text.insert(tk.END, f"Transporte: {'Aéreo' if transport_type == 'air' else 'Terrestre'}\n\n")
        
        # Converte strings para objetos City
        start = City(origin)
        goal = City(destination)
        
        # Verifica se as cidades existem
        if start not in self.graph.cities or goal not in self.graph.cities:
            self.result_text.insert(tk.END, "Erro: Uma ou ambas as cidades não foram encontradas no grafo.\n")
            return
        
        results = {}
        best_distance = float('inf')
        best_algorithm = None
        best_path = None
        
        # Executa cada algoritmo
        for name, algorithm in self.algorithms.items():
            try:
                self.result_text.insert(tk.END, f"Executando {name}...\n")
                result = algorithm.search(self.graph, start, goal, transport_type)
                
                if result and result.path:
                    path_str = " → ".join([city.name for city in result.path])
                    results[name] = {
                        "path": result.path,
                        "path_str": path_str,
                        "distance": result.distance,
                        "expanded_nodes": result.expanded_nodes
                    }
                    
                    if result.distance < best_distance:
                        best_distance = result.distance
                        best_algorithm = name
                        best_path = result.path
                else:
                    results[name] = {
                        "path": None,
                        "path_str": "Não encontrado",
                        "distance": float('inf'),
                        "expanded_nodes": 0
                    }
            except Exception as e:
                self.result_text.insert(tk.END, f"Erro durante a execução de {name}: {e}\n")
                results[name] = {
                    "path": None,
                    "path_str": f"Erro: {e}",
                    "distance": float('inf'),
                    "expanded_nodes": 0
                }
        
        # Exibe tabela comparativa
        self.result_text.insert(tk.END, "\n--- Resultados Comparativos ---\n\n")
        self.result_text.insert(tk.END, f"{'Algoritmo':<30} {'Distância':<15} {'Nós Expandidos':<20} {'Solução Ótima':<15}\n")
        self.result_text.insert(tk.END, "-" * 80 + "\n")
        
        for name, result in results.items():
            is_optimal = "Sim" if result["distance"] == best_distance and result["distance"] < float('inf') else "Não"
            is_optimal = "-" if result["distance"] == float('inf') else is_optimal
            
            distance_str = f"{result['distance']} km" if result["distance"] < float('inf') else "N/A"
            
            self.result_text.insert(tk.END, f"{name:<30} {distance_str:<15} {result['expanded_nodes']:<20} {is_optimal:<15}\n")
        
        # Exibe detalhes do melhor caminho
        self.result_text.insert(tk.END, "\n--- Melhor Caminho ---\n")
        if best_path:
            best_path_str = " → ".join([city.name for city in best_path])
            self.result_text.insert(tk.END, f"Algoritmo: {best_algorithm}\n")
            self.result_text.insert(tk.END, f"Caminho: {best_path_str}\n")
            self.result_text.insert(tk.END, f"Distância: {best_distance} km\n")
            
            # Visualiza o melhor caminho
            self.visualize_path(best_path)
        else:
            self.result_text.insert(tk.END, "Nenhum caminho encontrado por qualquer algoritmo.\n")
            self.draw_empty_graph()
        
        # Exibe análise de caminhos encontrados
        self.result_text.insert(tk.END, "\n--- Caminhos Encontrados ---\n")
        for name, result in results.items():
            if result["path"]:
                self.result_text.insert(tk.END, f"{name}: {result['path_str']}\n")
            else:
                self.result_text.insert(tk.END, f"{name}: Nenhum caminho encontrado\n")
    
    def check_if_optimal(self, result, start, goal, transport_type):
        # Executa UCS para verificar se a solução é ótima
        ucs = UCS()
        ucs_result = ucs.search(self.graph, start, goal, transport_type)
        
        if ucs_result and ucs_result.path:
            return result.distance == ucs_result.distance
        
        return False
    
    def visualize_path(self, path):
        # Limpa o gráfico anterior
        self.ax.clear()
        
        # Cria um grafo direcionado
        G = nx.DiGraph()
        
        # Adiciona nós
        for city in path:
            G.add_node(city.name)
        
        # Adiciona arestas
        for i in range(len(path) - 1):
            G.add_edge(path[i].name, path[i+1].name)
        
        # Define o layout
        pos = nx.spring_layout(G, seed=42)
        
        # Desenha os nós
        nx.draw_networkx_nodes(G, pos, node_size=700, node_color='lightblue', alpha=0.8, ax=self.ax)
        
        # Desenha as arestas
        nx.draw_networkx_edges(G, pos, width=2, alpha=0.5, edge_color='blue', arrows=True, ax=self.ax)
        
        # Adiciona rótulos
        nx.draw_networkx_labels(G, pos, font_size=10, font_family='sans-serif', ax=self.ax)
        
        # Ajusta o layout
        self.ax.set_title("Caminho Encontrado")
        self.ax.axis('off')
        self.canvas.draw()
    
    def draw_empty_graph(self):
        # Limpa o gráfico anterior
        self.ax.clear()
        self.ax.set_title("Nenhum caminho visualizado")
        self.ax.axis('off')
        self.canvas.draw()

if __name__ == "__main__":
    app = RouteFinderApp()
    app.mainloop()