import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import networkx as nx
import json
import os
import numpy as np
from models.city import City
from models.graph import Graph
from search.bfs import BFS
from search.dfs import DFS
from search.ucs import UCS
from search.greedy import Greedy
from search.astar import AStar
from utils.data_loader import DataLoader
import matplotlib.colors as mcolors
import geopandas as gpd
import io
import requests
from matplotlib.patches import Patch
import urllib.request
import zipfile

# Importar as coordenadas geográficas das capitais
from geo_coordinates import CAPITAL_COORDINATES

# URL do shapefile do Brasil
BRAZIL_SHAPEFILE_URL = "https://www.ibge.gov.br/geociencias/cartas-e-mapas/bases-cartograficas-continuas/15759-brasil.html?=&t=downloads"

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
        
        # Carrega ou baixa os shapefiles do Brasil
        self.brazil_gdf = self.load_brazil_shapefile()
        
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
    
    def load_brazil_shapefile(self):
        # Verifica se já temos os shapefiles baixados
        shapefile_path = "data/brazil_states"
        if not os.path.exists(shapefile_path):
            os.makedirs(shapefile_path, exist_ok=True)
        
        # Verifica se os arquivos já existem
        shp_file = os.path.join(shapefile_path, "BR_UF_2022.shp")
        if not os.path.exists(shp_file):
            try:
                # Baixa os dados simplificados do Brasil
                self.download_simplified_brazil_shapefile(shapefile_path)
            except Exception as e:
                print(f"Erro ao baixar shapefiles: {e}")
                # Se não conseguir baixar, criaremos um polígono simples para o Brasil
                return self.create_simplified_brazil_polygon()
        
        try:
            # Carrega os shapefiles
            return gpd.read_file(shp_file)
        except Exception as e:
            print(f"Erro ao carregar shapefiles: {e}")
            return self.create_simplified_brazil_polygon()
    
    def download_simplified_brazil_shapefile(self, output_dir):
        """Baixa uma versão simplificada do shapefile do Brasil"""
        
        # URL para um shapefile simplificado do Brasil
        url = "https://download.geofabrik.de/south-america/brazil-latest-free.shp.zip"
        
        try:
            # Caminho para o arquivo zip
            zip_path = os.path.join(output_dir, "brazil.zip")
            
            # Baixa o arquivo zip
            urllib.request.urlretrieve(url, zip_path)
            
            # Extrai o arquivo zip
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(output_dir)
                
            # Remove o arquivo zip
            os.remove(zip_path)
            
            print("Shapefiles baixados com sucesso!")
        except Exception as e:
            print(f"Erro ao baixar os shapefiles: {e}")
            raise e
    
    def create_simplified_brazil_polygon(self):
        """Cria um polígono simplificado do Brasil caso não seja possível baixar os shapefiles"""
        # Contorno simplificado do Brasil
        brazil_outline = [
                (-33.8, -53.2), (-33.7, -53.5), (-32.0, -52.0), (-30.0, -51.0),
                (-28.5, -49.0), (-27.0, -48.5), (-26.0, -48.5), (-25.0, -48.0),
                (-23.0, -47.0), (-22.9, -43.2), (-22.5, -41.9), (-21.0, -40.9),
                (-18.3, -39.7), (-16.0, -39.0), (-14.0, -38.5), (-12.9, -38.5),
                (-11.5, -37.4), (-10.0, -36.5), (-9.0, -35.0), (-7.1, -34.8),
                (-5.8, -35.2), (-4.8, -37.1), (-3.5, -38.5), (-2.5, -40.4),
                (-1.5, -43.3), (-1.1, -44.5), (-0.1, -49.9), (0.5, -51.0),
                (1.3, -50.0), (2.0, -51.0), (3.9, -51.8), (4.5, -51.9),
                (4.0, -52.6), (3.1, -54.6), (2.5, -55.9), (2.0, -56.0),
                (2.8, -57.9), (2.4, -60.0), (4.4, -61.8), (3.7, -67.1),
                (1.3, -69.6), (-2.3, -69.9), (-4.2, -69.9), (-7.1, -73.0),
                (-9.4, -72.5), (-9.2, -70.8), (-11.1, -68.8), (-10.9, -66.0),
                (-12.4, -63.1), (-12.6, -60.0), (-15.0, -59.9), (-18.0, -58.4),
                (-20.5, -58.0), (-22.0, -57.8), (-23.4, -58.2), (-25.5, -57.7),
                (-27.1, -58.4), (-30.2, -57.3), (-30.5, -56.0), (-31.3, -55.9),
                (-32.9, -56.8), (-33.5, -53.5), (-33.8, -53.2)
        ]
        
        # Cria um DataFrame com o polígono
        df = {'geometry': [None]}
        from shapely.geometry import Polygon
        
        # Inverte as coordenadas para (longitude, latitude) que é o formato usado pelo shapely
        coords = [(lon, lat) for lat, lon in brazil_outline]
        df['geometry'] = [Polygon(coords)]
        
        # Cria um GeoDataFrame
        gdf = gpd.GeoDataFrame(df, geometry='geometry')
        gdf['name'] = ['Brasil']
        
        return gdf
    
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
        self.draw_empty_map()
    
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
                self.visualize_path_on_map(result.path, transport_type)
            else:
                self.result_text.insert(tk.END, "\nNão foi possível encontrar um caminho.\n")
                self.draw_empty_map()
        
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
            self.visualize_path_on_map(best_path, transport_type)
        else:
            self.result_text.insert(tk.END, "Nenhum caminho encontrado por qualquer algoritmo.\n")
            self.draw_empty_map()
        
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
    
    def visualize_path_on_map(self, path, transport_type):
        # Limpa o gráfico anterior
        self.ax.clear()
        
        # Desenha o mapa base do Brasil
        self.draw_brazil_map()
        
        # Plota todas as capitais com um tamanho pequeno
        for city_name, (lat, lon) in CAPITAL_COORDINATES.items():
            if city_name in [city.name for city in self.graph.cities]:
                self.ax.plot(lon, lat, 'o', markersize=4, color='silver', alpha=0.7)
        
        # Plota as cidades no caminho com tamanho maior e cores destacadas
        for i, city in enumerate(path):
            if city.name in CAPITAL_COORDINATES:
                lat, lon = CAPITAL_COORDINATES[city.name]
                
                if i == 0:  # Origem
                    self.ax.plot(lon, lat, 'o', markersize=10, color='green', alpha=0.9)
                    self.ax.annotate(city.name, (lon, lat), fontsize=9, ha='center', va='bottom', 
                                    bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8))
                elif i == len(path) - 1:  # Destino
                    self.ax.plot(lon, lat, 'o', markersize=10, color='red', alpha=0.9)
                    self.ax.annotate(city.name, (lon, lat), fontsize=9, ha='center', va='bottom', 
                                    bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8))
                else:  # Cidades intermediárias
                    self.ax.plot(lon, lat, 'o', markersize=8, color='blue', alpha=0.9)
                    self.ax.annotate(city.name, (lon, lat), fontsize=8, ha='center', va='bottom', 
                                    bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8))
        
        # Plota as conexões do caminho
        for i in range(len(path) - 1):
            if path[i].name in CAPITAL_COORDINATES and path[i+1].name in CAPITAL_COORDINATES:
                lat1, lon1 = CAPITAL_COORDINATES[path[i].name]
                lat2, lon2 = CAPITAL_COORDINATES[path[i+1].name]
                
                # Estilo da linha com base no tipo de transporte
                if transport_type == "air":
                    # Para transporte aéreo, linha reta
                    self.ax.plot([lon1, lon2], [lat1, lat2], '-', linewidth=2.5, color='blue', alpha=0.7)
                else:
                    # Para transporte terrestre, linha pontilhada
                    self.ax.plot([lon1, lon2], [lat1, lat2], '--', linewidth=2.5, color='brown', alpha=0.7)
        
        # Adiciona título
        transport_name = "Aéreo" if transport_type == "air" else "Terrestre"
        self.ax.set_title(f"Rota {transport_name}: {path[0].name} → {path[-1].name}")
        
        # Adiciona legenda
        legend_elements = [
            Patch(facecolor='green', edgecolor='green', label='Origem'),
            Patch(facecolor='red', edgecolor='red', label='Destino'),
            Patch(facecolor='blue', edgecolor='blue', label='Intermediária'),
            Patch(facecolor='white', edgecolor='blue' if transport_type == "air" else 'brown', 
                 label='Rota ' + transport_name)
        ]
        self.ax.legend(handles=legend_elements, loc='lower right', fontsize=8)
        
        # Atualiza o canvas
        self.canvas.draw()
    
    def draw_brazil_map(self):
        try:
            # Desenha o mapa do Brasil com estados
            self.brazil_gdf.plot(
                ax=self.ax,
                edgecolor='black',
                color='lightblue',
                linewidth=0.8,
                alpha=0.6
            )
            
            # Limita o mapa ao Brasil
            self.ax.set_xlim(-75, -30)
            self.ax.set_ylim(-35, 5)
            
            # Remove eixos de coordenadas
            self.ax.set_axis_off()
            
        except Exception as e:
            print(f"Erro ao desenhar mapa do Brasil: {e}")
            # Fallback: desenha um contorno simplificado
            self.draw_brazil_outline()
    
    def draw_brazil_outline(self):
        # Contorno simplificado do Brasil (apenas para fallback)
        brazil_outline = [
            (-33.8, -53.2), (-33.7, -53.5), (-32.0, -52.0), (-29.3, -49.7),
            (-25.3, -48.0), (-22.9, -43.2), (-22.5, -41.9), (-21.0, -40.9),
            (-18.3, -39.7), (-15.5, -38.9), (-12.9, -38.5), (-11.5, -37.4),
            (-9.5, -35.5), (-7.1, -34.8), (-5.8, -35.2), (-4.8, -37.1),
            (-2.5, -40.4), (-1.5, -43.3), (-1.1, -44.5), (-0.1, -49.9),
            (-0.2, -50.4), (1.3, -50.0), (3.9, -51.8), (4.5, -51.9),
            (4.0, -52.6), (2.8, -52.6), (3.1, -54.6), (2.5, -55.9),
            (2.0, -56.0), (2.8, -57.9), (2.4, -60.0), (4.4, -61.8),
            (3.7, -67.1), (1.3, -69.6), (-2.3, -69.9), (-4.2, -69.9),
            (-7.1, -73.0), (-9.4, -72.5), (-9.2, -70.8), (-11.1, -68.8),
            (-10.9, -66.0), (-12.4, -63.1), (-12.6, -60.0), (-15.0, -59.9),
            (-18.0, -58.4), (-20.5, -58.0), (-22.0, -57.8), (-23.4, -58.2),
            (-25.5, -57.7), (-27.1, -58.4), (-30.2, -57.3), (-30.5, -56.0),
            (-31.3, -55.9), (-32.9, -56.8), (-33.5, -53.5), (-33.8, -53.2)
        ]
        
        # Converte para arrays numpy
        brazil_x = [point[1] for point in brazil_outline]
        brazil_y = [point[0] for point in brazil_outline]
        
        # Plota o contorno do Brasil
        self.ax.fill(brazil_x, brazil_y, color='lightblue', alpha=0.5)
        self.ax.plot(brazil_x, brazil_y, 'k-', linewidth=1, alpha=0.7)
        
        # Configura os limites do mapa
        self.ax.set_xlim(-75, -30)
        self.ax.set_ylim(-35, 5)
        
        # Remove eixos de coordenadas
        self.ax.set_axis_off()
    
    def draw_empty_map(self):
        # Limpa o gráfico anterior
        self.ax.clear()
        
        # Desenha o mapa base do Brasil
        self.draw_brazil_map()
        
        # Plota todas as capitais
        for city_name, (lat, lon) in CAPITAL_COORDINATES.items():
            if city_name in [city.name for city in self.graph.cities]:
                self.ax.plot(lon, lat, 'o', markersize=5, color='darkblue', alpha=0.6)
                # Adiciona apenas o nome das capitais principais
                if city_name in ["São Paulo", "Rio de Janeiro", "Brasília", "Salvador", 
                                "Manaus", "Porto Alegre", "Recife", "Belém"]:
                    self.ax.annotate(city_name, (lon, lat), fontsize=8, ha='center',
                                    bbox=dict(boxstyle="round,pad=0.2", facecolor='white', alpha=0.7))
        
        # Adiciona título
        self.ax.set_title("Mapa do Brasil - Capitais", fontsize=12)
        
        # Atualiza o canvas
        self.canvas.draw()

if __name__ == "__main__":
    app = RouteFinderApp()
    app.mainloop()
