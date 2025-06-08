#!/usr/bin/env python3
"""
Script para executar a interface gráfica do mapa de rotas entre capitais brasileiras.
Este script verifica as dependências e inicia a aplicação.
"""

import sys
import os

def check_dependencies():
    """Verifica se todas as dependências estão instaladas"""
    required_modules = [
        'tkinter',
        'matplotlib',
        'networkx', 
        'numpy',
        'geopandas',
        'shapely'
    ]
    
    missing_modules = []
    
    for module in required_modules:
        try:
            if module == 'tkinter':
                import tkinter
            elif module == 'matplotlib':
                import matplotlib.pyplot
            elif module == 'networkx':
                import networkx
            elif module == 'numpy':
                import numpy
            elif module == 'geopandas':
                import geopandas
            elif module == 'shapely':
                import shapely.geometry
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        print("❌ Dependências faltando:")
        for module in missing_modules:
            print(f"  - {module}")
        print("\n📦 Para instalar as dependências:")
        if 'tkinter' in missing_modules:
            print("  sudo apt-get install python3-tk  # Para tkinter no Ubuntu/Debian")
        print("  pip install -r requirements.txt")
        return False
    
    print("✅ Todas as dependências estão instaladas!")
    return True

def main():
    """Função principal"""
    print("🇧🇷 Mapa de Rotas entre Capitais Brasileiras")
    print("=" * 50)
    
    # Verifica dependências
    if not check_dependencies():
        sys.exit(1)
    
    # Verifica se os arquivos principais existem
    required_files = [
        'main_gui_maps.py',
        'geo_coordinates.py',
        'models/city.py',
        'models/graph.py'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print("❌ Arquivos faltando:")
        for file in missing_files:
            print(f"  - {file}")
        sys.exit(1)
    
    print("🚀 Iniciando aplicação...")
    
    try:
        # Importa e executa a aplicação
        from main_gui_maps import RouteFinderApp
        app = RouteFinderApp()
        print("✅ Aplicação iniciada com sucesso!")
        print("📍 Use a interface para buscar rotas entre capitais brasileiras")
        app.mainloop()
    except Exception as e:
        print(f"❌ Erro ao iniciar a aplicação: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()