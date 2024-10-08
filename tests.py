import os
from solution import BAProblem
import numpy as np

def test_load():
    """Testa o método load da classe BAProblem para verificar se os dados são carregados corretamente a partir de um ficheiro real."""
    
    # Criar instância da classe BAProblem
    problem = BAProblem()
    
    # Definir o caminho do ficheiro de entrada
    file_path = "test_data/assign2/ey100.dat"
    
    # Carregar os dados dos navios a partir do ficheiro real
    with open(file_path, 'r') as file:
        problem.load(file)

    # Verificar se o estado inicial foi corretamente definido
    if problem.initial is not None:
        print(f"Estado inicial corretamente definido: {problem.initial}")
    else:
        print("Erro: O estado inicial não foi definido corretamente.")

    # Verificar se os dados dos navios foram corretamente carregados
    print(f"Vessels: {problem.vessels}")
    expected_vessels = np.array([
        [1, 1, 4, 1],
        [0, 2, 2, 1],
        [2, 4, 2, 1],
        [2, 4, 2, 1]
    ])
    
    if np.array_equal(problem.vessels, expected_vessels):
        print("Os dados dos navios foram carregados corretamente.")
    else:
        print(f"Erro ao carregar os dados dos navios. Vessels esperado: {expected_vessels}, Vessels carregado: {problem.vessels}")

def test_actions(folder_path):
    """Testa o método actions da classe BAProblem para todos os arquivos .dat e salva as ações possíveis."""
    # Pega todos os arquivos .dat na pasta e os ordena
    for file_name in sorted(os.listdir(folder_path)):
        if file_name.endswith(".dat"):  # Apenas arquivos .dat
            file_path = os.path.join(folder_path, file_name)
            print(f"\nCarregando arquivo: {file_name}")

            # Criar instância da classe BAProblem
            problem = BAProblem()

            # Abrir e carregar o arquivo de teste
            with open(file_path, 'r') as f:
                problem.load(f)

            # Estado inicial (todos os navios ainda não atracados)
            initial_state = [None] * problem.N

            # Testar o método actions e salvar as ações possíveis
            actions_possiveis = problem.actions(initial_state)

            # Criar o nome do arquivo de saída (mesmo nome do arquivo de entrada, mas com extensão .out)
            output_file_name = file_name.replace(".dat", ".out")
            output_file_path = os.path.join(folder_path, output_file_name)

            # Salvar as ações no arquivo de saída
            with open(output_file_path, 'w') as out_file:
                for action in actions_possiveis:
                    out_file.write(f"{action}\n")

            print(f"Ações possíveis salvas em: {output_file_name}")

def test_result():
    """Testa o método result da classe BAProblem sem usar arquivos, apenas com um exemplo simples."""
    # Criar instância da classe BAProblem com um exemplo fictício
    problem = BAProblem()
    problem.N = 3
    problem.S = 5
    problem.vessels = [
        [0, 3, 2, 1],  # Navio 0: chega no tempo 0, processo 3, tamanho 2, peso 1
        [2, 2, 1, 1],  # Navio 1: chega no tempo 2, processo 2, tamanho 1, peso 1
        [4, 1, 1, 1],  # Navio 2: chega no tempo 4, processo 1, tamanho 1, peso 1
    ]

    # Estado inicial (todos os navios ainda não atracados)
    initial_state = [None] * problem.N

    # Exemplo de ação: atracar o navio 0 no tempo 0 na seção 0
    action = (0, 0, 0)

    # Testar o método result
    new_state = problem.result(initial_state, action)
    print(f"\nEstado após aplicar a ação {action}: {new_state}")

    # Aplicar outra ação: atracar o navio 1 no tempo 2 na seção 2
    action2 = (1, 2, 2)
    new_state = problem.result(new_state, action2)
    print(f"Estado após aplicar a ação {action2}: {new_state}")

def test_goal_test():
    """Testa o método goal_test da classe BAProblem"""
    # Criar instância da classe BAProblem com um exemplo fictício
    problem = BAProblem()
    problem.N = 3
    problem.S = 5
    problem.vessels = [
        [0, 3, 2, 1],  # Navio 0: chega no tempo 0, processo 3, tamanho 2, peso 1
        [2, 2, 1, 1],  # Navio 1: chega no tempo 2, processo 2, tamanho 1, peso 1
        [4, 1, 1, 1],  # Navio 2: chega no tempo 4, processo 1, tamanho 1, peso 1
    ]

    # Estado inicial: todos os navios ainda não atracados (não é objetivo)
    initial_state = [None, None, None]
    print(f"\nTestando estado inicial (esperado False): {problem.goal_test(initial_state)}")

    # Estado parcialmente preenchido: apenas um navio atracado (não é objetivo)
    partial_state = [(3, 1), None, None]
    print(f"Testando estado parcial (esperado False): {problem.goal_test(partial_state)}")

    # Estado final: todos os navios atracados (é objetivo)
    final_state = [(3, 1), (5, 2), (6, 0)]
    print(f"Testando estado final (esperado True): {problem.goal_test(final_state)}")

def test_path_cost():
    """Testa o método path_cost da classe BAProblem"""
    # Criar instância da classe BAProblem com um exemplo fictício
    problem = BAProblem()
    problem.N = 3
    problem.S = 5
    problem.vessels = [
        [0, 3, 2, 2],  # Navio 0: chega no tempo 0, processo 3, tamanho 2, peso 2
        [2, 2, 1, 1],  # Navio 1: chega no tempo 2, processo 2, tamanho 1, peso 1
        [4, 1, 1, 3],  # Navio 2: chega no tempo 4, processo 1, tamanho 1, peso 3
    ]

    # Estado inicial (todos os navios ainda não atracados)
    initial_state = [None] * problem.N

    # Custo inicial
    initial_cost = 0

    # Aplicar a primeira ação: atracar o navio 0 no tempo 0, seção 0
    action1 = (0, 0, 0)
    new_state1 = problem.result(initial_state, action1)
    new_cost1 = problem.path_cost(initial_cost, initial_state, action1, new_state1)
    print(f"\nCusto após atracar o navio 0: {new_cost1}")

    # Aplicar a segunda ação: atrcar o navio 1 no tempo 2, seção 2
    action2 = (1, 2, 2)
    new_state2 = problem.result(new_state1, action2)
    new_cost2 = problem.path_cost(new_cost1, new_state1, action2, new_state2)
    print(f"Custo após atracar o navio 1: {new_cost2}")

    # Aplicar a terceira ação: atracar o navio 2 no tempo 5, seção 3
    action3 = (2, 5, 3)
    new_state3 = problem.result(new_state2, action3)
    new_cost3 = problem.path_cost(new_cost2, new_state2, action3, new_state3)
    print(f"Custo após atracar o navio 2: {new_cost3}")

def test_solve():
    """Testa o método solve da classe BAProblem para verificar se encontra a solução ótima."""
    
    # Criar instância da classe BAProblem
    problem = BAProblem()
    
    # Definir o caminho do ficheiro de entrada
    file_path = "test_data/assign2/ey100.dat"
    
    # Carregar os dados dos navios a partir do ficheiro real
    with open(file_path, 'r') as file:
        problem.load(file)

    # Verificar se o estado inicial foi corretamente definido
    if problem.initial is not None:
        print(f"Estado inicial corretamente definido: {problem.initial}")
    else:
        print("Erro: O estado inicial não foi definido corretamente.")
        return
    
    # Resolver o problema
    solution = problem.solve()

    # Mostrar a solução encontrada
    if solution is not None:
        print(f"Solução encontrada: {solution}")
    else:
        print("Nenhuma solução foi encontrada.")

    # Verificação de consistência da solução
    expected_solution = [(0, 0), (2, 2), (5, 3)]

    # Verifica se a solução encontrada corresponde à solução esperada
    if solution == expected_solution:
        print("Teste bem-sucedido! A solução encontrada é a esperada.")
    else:
        print(f"Erro no teste! Solução esperada: {expected_solution}, Solução encontrada: {solution}")

def test_solve_simple():
    """Testa o método solve da classe BAProblem para um exemplo simples."""
    
    # Criar instância da classe BAProblem
    problem = BAProblem()
    
    # Definir o estado inicial manualmente para o exemplo simples com 2 navios
    problem.S = 2  # Número de seções
    problem.N = 2  # Número de navios
    problem.vessels = np.array([[0, 4, 2, 1],  # (chegada, tempo de processamento, tamanho, peso)
                                [1, 2, 2, 1]])  # Navio 2
    problem.initial = tuple([() for _ in range(problem.N)])  # Estado inicial com tuplos vazios

    # Verificar se o estado inicial foi corretamente definido
    if problem.initial is not None:
        print(f"Estado inicial corretamente definido: {problem.initial}")
    else:
        print("Erro: O estado inicial não foi definido corretamente.")
        return
    
    # Resolver o problema
    solution = problem.solve()

    # Mostrar a solução encontrada
    if solution is not None:
        print(f"Solução encontrada: {solution}")
    else:
        print("Nenhuma solução foi encontrada.")

    # Verificação de consistência da solução
    expected_solution = [(0, 0), (4, 0)]  # Exemplo simples com 2 navios

    # Converter a solução encontrada para lista de tuplas
    solution_list = list(solution)

    # Verifica se a solução encontrada corresponde à solução esperada
    if solution_list == expected_solution:
        print("Teste bem-sucedido! A solução encontrada é a esperada.")
    else:
        print(f"Erro no teste! Solução esperada: {expected_solution}, Solução encontrada: {solution_list}")


if __name__ == "__main__":
    # Chamar os testes isoladamente
    folder_path = "test_data/assign2"
    
    # test_load()
    # test_actions(folder_path)
    # test_result()
    # test_goal_test()
    # test_path_cost()
    # test_solve()
    test_solve_simple()
