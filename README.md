# Projeto de Algoritmos de Busca - Rotas entre Capitais Brasileiras

Este projeto implementa diferentes algoritmos de busca para encontrar rotas entre capitais brasileiras, tanto por via aérea quanto terrestre.

## Algoritmos Implementados

1. Busca em Largura (BFS)
2. Busca em Profundidade (DFS)
3. Busca de Custo Uniforme (UCS)
4. Busca Gulosa (Greedy)
5. Busca A* (A-Star)

## Requisitos

- Python 3.6+
- Pacotes:
  - requests

## Instalação

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/rotas-capitais.git
cd rotas-capitais

# Instale as dependências
pip install requests
```

## Uso

### Executar o programa principal

```bash
python main.py
```

O programa oferece as seguintes opções:
1. Encontrar rota entre duas capitais
2. Comparar algoritmos para uma rota
3. Analisar cenários de teste
0. Sair

### Exemplo de análise de cenário

Cenário: São Paulo -> Rio de Janeiro
- Algoritmo: BFS
  - Caminho: São Paulo -> Rio de Janeiro
  - Distância: 400 km
  - Nós expandidos: 2

- Algoritmo: DFS
  - Caminho: São Paulo -> Rio de Janeiro
  - Distância: 400 km
  - Nós expandidos: 2

- Algoritmo: UCS
  - Caminho: São Paulo -> Rio de Janeiro
  - Distância: 400 km
  - Nós expandidos: 2

- Algoritmo: GREEDY
  - Caminho: São Paulo -> Rio de Janeiro
  - Distância: 400 km
  - Nós expandidos: 2

- Algoritmo: ASTAR
  - Caminho: São Paulo -> Rio de Janeiro
  - Distância: 400 km
  - Nós expandidos: 2

## Estrutura do Projeto

- **models/**: Classes para representar cidades e grafo
- **search/**: Implementações dos algoritmos de busca
- **utils/**: Utilitários para carregar dados
- **main.py**: Ponto de entrada da aplicação

## Princípios SOLID Aplicados

1. **S - Single Responsibility Principle**: Cada classe tem uma única responsabilidade.
   - Exemplo: `City` gerencia informações de uma cidade, `Graph` gerencia conexões.

2. **O - Open/Closed Principle**: As classes são abertas para extensão, fechadas para modificação.
   - Exemplo: Novos algoritmos podem ser adicionados sem modificar a interface.

3. **L - Liskov Substitution Principle**: Algoritmos derivados podem substituir a classe base.
   - Exemplo: Todos os algoritmos implementam a interface `SearchAlgorithm`.

4. **I - Interface Segregation Principle**: Interfaces específicas para necessidades específicas.
   - Exemplo: A interface `SearchAlgorithm` contém apenas o método necessário.

5. **D - Dependency Inversion Principle**: Depender de abstrações, não implementações.
   - Exemplo: `PathFinder` depende da interface `SearchAlgorithm`, não de implementações concretas.

## Geração do Relatório

Para gerar o relatório comparativo, execute o programa e escolha a opção 3 para analisar os cenários predefinidos. Use as saídas para compor o relatório final.

## Criação do Vídeo

Para o vídeo de demonstração, recomenda-se:
1. Apresentar o problema e a estrutura da solução
2. Demonstrar a execução do programa
3. Analisar os resultados dos diferentes algoritmos
4. Comparar eficiência e otimalidade das soluções

## Contribuição

Desenvolvido por Gabriel Felipe Guarnieri para a disciplina de Fundamentos de Sistemas Inteligentes - UTFPR Campus Dois Vizinhos.