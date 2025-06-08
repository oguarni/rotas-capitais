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

# URLs para shapefiles do Brasil (backup)

class RouteFinderApp(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("Busca de Rotas entre Capitais Brasileiras")
        self.geometry("1400x900")
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
        # Primeiro tenta carregar o GeoJSON baixado da internet
        geojson_files = [
            "data/brazil_country.geojson"
        ]
        
        for geojson_file in geojson_files:
            if os.path.exists(geojson_file):
                try:
                    print(f"Carregando mapa do Brasil de: {geojson_file}")
                    gdf = gpd.read_file(geojson_file)
                    # Verifica se o GeoJSON tem dados válidos
                    if not gdf.empty and gdf.geometry.iloc[0] is not None:
                        print(f"Mapa carregado com sucesso! Contém {len(gdf)} geometria(s)")
                        return gdf
                except Exception as e:
                    print(f"Erro ao carregar {geojson_file}: {e}")
        
        # Fallback: verifica se já temos os shapefiles baixados
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
        """Cria arquivos de shapefile simplificados localmente"""
        print("Criando shapefiles simplificados localmente...")
        
        # Cria um shapefile simples com apenas o contorno do Brasil
        try:
            from shapely.geometry import Polygon
            import geopandas as gpd
            
            # Contorno do Brasil (simplificado)
            brazil_coords = [
                (-33.742, -53.374), (-33.750, -53.647), (-32.392, -52.166), (-31.216, -51.320),
                (-30.034, -51.217), (-29.358, -50.338), (-28.558, -49.571), (-27.384, -48.555),
                (-26.330, -48.710), (-25.493, -48.301), (-24.578, -47.287), (-23.966, -46.603),
                (-23.335, -46.574), (-22.970, -43.207), (-22.775, -42.032), (-22.057, -41.058),
                (-21.046, -40.920), (-18.348, -39.467), (-16.697, -39.167), (-15.253, -38.954),
                (-14.234, -38.808), (-12.946, -38.839), (-11.851, -37.317), (-10.478, -36.579),
                (-9.511, -35.128), (-8.533, -35.096), (-7.588, -35.377), (-7.122, -34.834),
                (-6.295, -35.036), (-5.195, -36.523), (-4.553, -37.288), (-3.239, -38.613),
                (-2.243, -40.051), (-1.349, -42.000), (-0.947, -44.644), (-0.159, -46.594),
                (0.040, -48.973), (0.728, -50.454), (1.689, -51.140), (2.813, -51.643),
                (4.307, -52.684), (5.266, -54.624), (4.281, -55.969), (2.329, -56.778),
                (1.626, -58.925), (2.021, -59.748), (3.416, -60.048), (4.776, -60.733),
                (5.210, -61.849), (4.060, -63.370), (3.780, -64.547), (4.583, -67.868),
                (2.347, -68.880), (1.176, -69.803), (-0.703, -70.093), (-2.564, -70.160),
                (-4.229, -69.906), (-6.298, -70.039), (-7.345, -72.017), (-9.032, -73.236),
                (-10.305, -72.248), (-10.846, -70.992), (-11.525, -69.455), (-11.773, -67.467),
                (-12.870, -65.746), (-14.535, -64.548), (-15.867, -63.196), (-16.582, -60.584),
                (-17.738, -59.313), (-19.407, -57.870), (-21.948, -57.130), (-23.798, -57.777),
                (-25.166, -57.636), (-26.171, -57.847), (-27.378, -58.427), (-28.877, -57.881),
                (-30.174, -57.182), (-30.741, -55.919), (-31.585, -55.611), (-32.619, -55.797),
                (-33.253, -54.625), (-33.742, -53.374)
            ]
            
            # Converte para formato correto (longitude, latitude)
            coords = [(lon, lat) for lat, lon in brazil_coords]
            polygon = Polygon(coords)
            
            # Cria GeoDataFrame
            gdf = gpd.GeoDataFrame({'name': ['Brasil']}, geometry=[polygon])
            
            # Salva como shapefile
            shapefile_path = os.path.join(output_dir, "BR_UF_2022.shp")
            gdf.to_file(shapefile_path)
            
            print("Shapefile criado com sucesso!")
            
        except Exception as e:
            print(f"Erro ao criar shapefile: {e}")
            raise e
    
    def create_simplified_brazil_polygon(self):
        """Cria um polígono mais detalhado do Brasil caso não seja possível baixar os shapefiles"""
        # Contorno mais detalhado e preciso do Brasil
        brazil_outline = [
            (-33.742, -53.374), (-33.750, -53.647), (-32.392, -52.166), (-31.216, -51.320),
            (-30.034, -51.217), (-29.358, -50.338), (-28.558, -49.571), (-27.384, -48.555),
            (-26.330, -48.710), (-25.493, -48.301), (-24.578, -47.287), (-23.966, -46.603),
            (-23.335, -46.574), (-22.970, -43.207), (-22.775, -42.032), (-22.057, -41.058),
            (-21.046, -40.920), (-18.348, -39.467), (-16.697, -39.167), (-15.253, -38.954),
            (-14.234, -38.808), (-12.946, -38.839), (-11.851, -37.317), (-10.478, -36.579),
            (-9.511, -35.128), (-8.533, -35.096), (-7.588, -35.377), (-7.122, -34.834),
            (-6.295, -35.036), (-5.195, -36.523), (-4.553, -37.288), (-3.239, -38.613),
            (-2.243, -40.051), (-1.349, -42.000), (-0.947, -44.644), (-0.159, -46.594),
            (0.040, -48.973), (0.728, -50.454), (1.689, -51.140), (2.813, -51.643),
            (4.307, -52.684), (5.266, -54.624), (4.281, -55.969), (2.329, -56.778),
            (1.626, -58.925), (2.021, -59.748), (3.416, -60.048), (4.776, -60.733),
            (5.210, -61.849), (4.060, -63.370), (3.780, -64.547), (4.583, -67.868),
            (2.347, -68.880), (1.176, -69.803), (-0.703, -70.093), (-2.564, -70.160),
            (-4.229, -69.906), (-6.298, -70.039), (-7.345, -72.017), (-9.032, -73.236),
            (-10.305, -72.248), (-10.846, -70.992), (-11.525, -69.455), (-11.773, -67.467),
            (-12.870, -65.746), (-14.535, -64.548), (-15.867, -63.196), (-16.582, -60.584),
            (-17.738, -59.313), (-19.407, -57.870), (-21.948, -57.130), (-23.798, -57.777),
            (-25.166, -57.636), (-26.171, -57.847), (-27.378, -58.427), (-28.877, -57.881),
            (-30.174, -57.182), (-30.741, -55.919), (-31.585, -55.611), (-32.619, -55.797),
            (-33.253, -54.625), (-33.742, -53.374)
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
        
        # Inicializa a figura para o gráfico com tamanho maior
        self.figure = plt.Figure(figsize=(10, 8), dpi=100)
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
    
    def calculate_best_legend_position(self, path):
        """Calcula a melhor posição para a legenda baseada nas cidades da rota"""
        # Obtem coordenadas de todas as cidades da rota
        route_coords = []
        for city in path:
            if city.name in CAPITAL_COORDINATES:
                lat, lon = CAPITAL_COORDINATES[city.name]
                route_coords.append((lon, lat))
        
        if not route_coords:
            return 'lower right'  # fallback padrão
        
        # Calcula centro da rota
        center_lon = sum(coord[0] for coord in route_coords) / len(route_coords)
        center_lat = sum(coord[1] for coord in route_coords) / len(route_coords)
        
        # Define limites do mapa (mesmos usados na visualização)
        map_bounds = {
            'left': -73,
            'right': -33,
            'bottom': -33,
            'top': 5
        }
        
        # Calcula em que região do mapa a rota está concentrada
        rel_lon = (center_lon - map_bounds['left']) / (map_bounds['right'] - map_bounds['left'])
        rel_lat = (center_lat - map_bounds['bottom']) / (map_bounds['top'] - map_bounds['bottom'])
        
        # Escolhe posição da legenda baseada na posição da rota
        if rel_lon > 0.6:  # Rota à direita
            if rel_lat > 0.6:  # Parte superior direita
                return 'lower left'
            else:  # Parte inferior direita  
                return 'upper left'
        else:  # Rota à esquerda ou centro
            if rel_lat > 0.6:  # Parte superior
                return 'lower right'
            else:  # Parte inferior
                return 'upper right'
    
    def create_land_route(self, lat1, lon1, lat2, lon2):
        """Cria uma rota terrestre que evita passar pelo mar"""
        # Pontos de controle para roteamento terrestre inteligente
        # Baseado na geografia do Brasil para evitar oceano
        
        # Se a rota é principalmente norte-sul (mesma região)
        if abs(lon2 - lon1) < 3:  # Mesma região longitudinal
            return [(lon1, lat1), (lon2, lat2)]
        
        # Se a rota é leste-oeste, usa pontos intermediários terrestres
        elif abs(lat2 - lat1) < 3:  # Mesma região latitudinal
            # Encontra um ponto intermediário no interior
            mid_lat = (lat1 + lat2) / 2
            interior_lon = min(lon1, lon2) + abs(lon2 - lon1) * 0.3  # Mais para o interior
            return [(lon1, lat1), (interior_lon, mid_lat), (lon2, lat2)]
        
        # Para rotas diagonais longas, usa roteamento por regiões
        else:
            # Determina se passa pelo interior (Brasília como hub)
            if "Brasília" in CAPITAL_COORDINATES:
                brasilia_lat, brasilia_lon = CAPITAL_COORDINATES["Brasília"]
            else:
                brasilia_lat, brasilia_lon = -15.7975, -47.8919
            
            # Se uma das cidades é muito ao norte ou nordeste
            if (lat1 > -10 or lat2 > -10) and (lon1 > -45 or lon2 > -45):
                # Rota pelo interior passando por região central
                return [(lon1, lat1), (brasilia_lon, brasilia_lat), (lon2, lat2)]
            
            # Para outras rotas, ponto intermediário no interior
            mid_lat = (lat1 + lat2) / 2
            mid_lon = (lon1 + lon2) / 2
            # Ajusta para o interior se estiver muito próximo da costa
            if mid_lon > -42:  # Muito próximo da costa leste
                mid_lon = -45  # Move para o interior
            
            return [(lon1, lat1), (mid_lon, mid_lat), (lon2, lat2)]
    
    def visualize_path_on_map(self, path, transport_type):
        # Limpa o gráfico anterior
        self.ax.clear()
        
        # Desenha o mapa base do Brasil
        self.draw_brazil_map()
        
        # Plota todas as capitais com um tamanho pequeno
        for city_name, (lat, lon) in CAPITAL_COORDINATES.items():
            if city_name in [city.name for city in self.graph.cities]:
                self.ax.plot(lon, lat, 'o', markersize=3, color='#708090', alpha=0.6, 
                           markeredgecolor='white', markeredgewidth=0.5)
        
        # Dicionário com posicionamentos para labels das rotas
        label_positions = {
            "São Paulo": ("center", "top"),
            "Rio de Janeiro": ("left", "bottom"), 
            "Brasília": ("center", "bottom"),
            "Salvador": ("right", "bottom"),
            "Manaus": ("center", "bottom"),
            "Porto Alegre": ("center", "top"),
            "Recife": ("left", "center"),
            "Belém": ("center", "top"),
            "Fortaleza": ("right", "center"),
            "Belo Horizonte": ("right", "top"),
            "Curitiba": ("right", "bottom"),
            "Goiânia": ("left", "top"),
            "Vitória": ("right", "center"),
            "Florianópolis": ("left", "center"),
            "Campo Grande": ("center", "bottom"),
            "Cuiabá": ("left", "bottom"),
            "João Pessoa": ("right", "top"),
            "Natal": ("right", "bottom"),
            "Aracaju": ("left", "center"),
            "Maceió": ("left", "bottom"),
            "Teresina": ("center", "top"),
            "São Luís": ("right", "bottom"),
            "Palmas": ("right", "center"),
            "Macapá": ("center", "bottom"),
            "Boa Vista": ("center", "bottom"),
            "Rio Branco": ("center", "top"),
            "Porto Velho": ("left", "center")
        }
        
        # Plota as cidades no caminho com tamanho maior e cores destacadas
        for i, city in enumerate(path):
            if city.name in CAPITAL_COORDINATES:
                lat, lon = CAPITAL_COORDINATES[city.name]
                
                # Obtém posicionamento inteligente
                ha, va = label_positions.get(city.name, ("center", "bottom"))
                offset_x = 0.4 if ha == "left" else (-0.4 if ha == "right" else 0)
                offset_y = 0.4 if va == "bottom" else (-0.4 if va == "top" else 0)
                
                if i == 0:  # Origem
                    self.ax.plot(lon, lat, 'o', markersize=14, color='#228B22', alpha=0.9,
                               markeredgecolor='white', markeredgewidth=2)
                    self.ax.annotate(city.name, (lon + offset_x, lat + offset_y), 
                                   fontsize=11, ha=ha, va=va, weight='bold',
                                   bbox=dict(boxstyle="round,pad=0.4", facecolor='#90EE90', 
                                            alpha=0.95, edgecolor='#228B22', linewidth=2))
                elif i == len(path) - 1:  # Destino
                    self.ax.plot(lon, lat, 'o', markersize=14, color='#DC143C', alpha=0.9,
                               markeredgecolor='white', markeredgewidth=2)
                    self.ax.annotate(city.name, (lon + offset_x, lat + offset_y), 
                                   fontsize=11, ha=ha, va=va, weight='bold',
                                   bbox=dict(boxstyle="round,pad=0.4", facecolor='#FFB6C1', 
                                            alpha=0.95, edgecolor='#DC143C', linewidth=2))
                else:  # Cidades intermediárias
                    self.ax.plot(lon, lat, 'o', markersize=11, color='#4169E1', alpha=0.9,
                               markeredgecolor='white', markeredgewidth=1.5)
                    self.ax.annotate(city.name, (lon + offset_x*0.7, lat + offset_y*0.7), 
                                   fontsize=9, ha=ha, va=va,
                                   bbox=dict(boxstyle="round,pad=0.3", facecolor='#ADD8E6', 
                                            alpha=0.9, edgecolor='#4169E1', linewidth=1))
        
        # Plota as conexões do caminho
        for i in range(len(path) - 1):
            if path[i].name in CAPITAL_COORDINATES and path[i+1].name in CAPITAL_COORDINATES:
                lat1, lon1 = CAPITAL_COORDINATES[path[i].name]
                lat2, lon2 = CAPITAL_COORDINATES[path[i+1].name]
                
                # Estilo da linha com base no tipo de transporte
                if transport_type == "air":
                    # Para transporte aéreo, linha reta
                    self.ax.plot([lon1, lon2], [lat1, lat2], '-', linewidth=3, color='#4169E1', 
                               alpha=0.8, solid_capstyle='round')
                    # Adiciona setas para indicar direção
                    mid_lon, mid_lat = (lon1 + lon2) / 2, (lat1 + lat2) / 2
                    self.ax.annotate('', xy=(lon2, lat2), xytext=(mid_lon, mid_lat),
                                   arrowprops=dict(arrowstyle='->', color='#4169E1', lw=2))
                else:
                    # Para transporte terrestre, usa roteamento inteligente
                    route_points = self.create_land_route(lat1, lon1, lat2, lon2)
                    
                    # Desenha a rota com múltiplos segmentos se necessário
                    for j in range(len(route_points) - 1):
                        x1, y1 = route_points[j]
                        x2, y2 = route_points[j + 1]
                        self.ax.plot([x1, x2], [y1, y2], '-', linewidth=3, color='#8B4513', 
                                   alpha=0.8, solid_capstyle='round')
                    
                    # Adiciona seta no final da rota
                    if len(route_points) >= 2:
                        # Seta do penúltimo para o último ponto
                        pen_x, pen_y = route_points[-2]
                        last_x, last_y = route_points[-1]
                        self.ax.annotate('', xy=(last_x, last_y), xytext=(pen_x, pen_y),
                                       arrowprops=dict(arrowstyle='->', color='#8B4513', lw=2))
        
        # Adiciona título com melhor formatação
        transport_name = "Aéreo" if transport_type == "air" else "Terrestre"
        self.ax.set_title(f"Rota {transport_name}: {path[0].name} → {path[-1].name}", 
                         fontsize=14, fontweight='bold', pad=20)
        
        # Calcula posição inteligente da legenda para evitar sobreposição
        legend_position = self.calculate_best_legend_position(path)
        
        # Adiciona legenda melhorada com posicionamento inteligente
        legend_elements = [
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#228B22', 
                      markersize=10, label='Origem', markeredgecolor='white', markeredgewidth=2),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#DC143C', 
                      markersize=10, label='Destino', markeredgecolor='white', markeredgewidth=2),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#4169E1', 
                      markersize=8, label='Parada', markeredgecolor='white', markeredgewidth=1),
            plt.Line2D([0], [0], color='#4169E1' if transport_type == "air" else '#8B4513', 
                      linewidth=3, label=f'Rota {transport_name}')
        ]
        
        # Posiciona a legenda de forma inteligente
        legend = self.ax.legend(handles=legend_elements, loc=legend_position, fontsize=9, 
                               framealpha=0.95, shadow=True, fancybox=True,
                               borderpad=0.8, columnspacing=1, handlelength=1.5)
        
        # Atualiza o canvas
        self.canvas.draw()
    
    def draw_brazil_map(self):
        try:
            # Desenha o mapa do Brasil com visual melhorado
            self.brazil_gdf.plot(
                ax=self.ax,
                edgecolor='#2F4F4F',
                color='#E6F3FF',
                linewidth=1.2,
                alpha=0.8
            )
            
            # Adiciona uma borda mais escura para definir melhor o país
            self.brazil_gdf.boundary.plot(
                ax=self.ax,
                color='#1C3A3A',
                linewidth=2.0,
                alpha=0.9
            )
            
            # Limita o mapa ao Brasil com zoom aproximado
            self.ax.set_xlim(-73, -33)
            self.ax.set_ylim(-33, 5)
            
            # Remove eixos de coordenadas
            self.ax.set_axis_off()
            
            # Adiciona um fundo oceânico sutil
            self.ax.set_facecolor('#F0F8FF')
            
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
        
        # Configura os limites do mapa com zoom aproximado
        self.ax.set_xlim(-73, -33)
        self.ax.set_ylim(-33, 5)
        
        # Remove eixos de coordenadas
        self.ax.set_axis_off()
    
    def draw_empty_map(self):
        # Limpa o gráfico anterior
        self.ax.clear()
        
        # Desenha o mapa base do Brasil
        self.draw_brazil_map()
        
        # Dicionário com posicionamentos otimizados para evitar sobreposição
        label_positions = {
            "São Paulo": ("right", "bottom"),
            "Rio de Janeiro": ("right", "top"), 
            "Brasília": ("center", "bottom"),
            "Salvador": ("right", "center"),
            "Manaus": ("center", "bottom"),
            "Porto Alegre": ("center", "bottom"),
            "Recife": ("right", "center"),
            "Belém": ("right", "bottom"),
            "Fortaleza": ("right", "bottom"),
            "Belo Horizonte": ("left", "bottom"),
            "Curitiba": ("left", "bottom"),
            "Goiânia": ("center", "bottom"),
            "Vitória": ("right", "bottom"),
            "Florianópolis": ("center", "bottom"),
            "Campo Grande": ("center", "top"),
            "Cuiabá": ("center", "top"),
            "João Pessoa": ("left", "bottom"),
            "Natal": ("center", "bottom"),
            "Aracaju": ("left", "center"),
            "Maceió": ("center", "top"),
            "Teresina": ("center", "top"),
            "São Luís": ("left", "bottom"),
            "Palmas": ("right", "bottom"),
            "Macapá": ("center", "bottom"),
            "Boa Vista": ("left", "bottom"),
            "Rio Branco": ("center", "bottom"),
            "Porto Velho": ("center", "bottom")
        }
        
        # Plota todas as capitais com estilo melhorado
        for city_name, (lat, lon) in CAPITAL_COORDINATES.items():
            if city_name in [city.name for city in self.graph.cities]:
                self.ax.plot(lon, lat, 'o', markersize=8, color='#1E90FF', alpha=0.9,
                           markeredgecolor='white', markeredgewidth=1.5)
                
                # Adiciona nomes de todas as capitais com posicionamento inteligente
                ha, va = label_positions.get(city_name, ("center", "bottom"))
                
                # Ajusta offset baseado na posição com espaçamento maior
                offset_x = 0.6 if ha == "left" else (-0.6 if ha == "right" else 0)
                offset_y = 0.4 if va == "bottom" else (-0.4 if va == "top" else 0)
                
                self.ax.annotate(city_name, (lon + offset_x, lat + offset_y), 
                               fontsize=8, ha=ha, va=va,
                               bbox=dict(boxstyle="round,pad=0.2", facecolor='white', 
                                        alpha=0.9, edgecolor='#1E90FF', linewidth=0.5))
        
        # Adiciona título com melhor formatação
        self.ax.set_title("Mapa do Brasil - Capitais dos Estados", fontsize=14, 
                         fontweight='bold', pad=20)
        
        # Adiciona informação sobre o número de capitais (posição ajustada para o zoom)
        num_capitals = len([name for name in CAPITAL_COORDINATES.keys() 
                           if name in [city.name for city in self.graph.cities]])
        self.ax.text(-72, -30, f"Total: {num_capitals} capitais", fontsize=10, 
                    bbox=dict(boxstyle="round,pad=0.3", facecolor='lightgray', alpha=0.8))
        
        # Atualiza o canvas
        self.canvas.draw()

if __name__ == "__main__":
    app = RouteFinderApp()
    app.mainloop()
