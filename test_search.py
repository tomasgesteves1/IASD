import search  # Importa o algoritmo de busca
from solution import BAProblem  # Importa o problema de exemplo

# Teste para verificar o funcionamento de métodos chave no algoritmo de busca
def test_expand_node():
    # Inicializar o problema
    problem = BAProblem()

    # Definir os navios antes de expandir o nó
    problem.S = 5  # Número de seções no cais
    problem.N = 4  # Número de navios
    
    # Exemplo de navios
    problem.vessels = [
        [0, 3, 2, 1],  # [tempo de chegada, tempo de processamento, tamanho, peso]
        [2, 2, 1, 2],
        [4, 1, 1, 3],
        [6, 2, 2, 1]
    ]

    # Estado inicial de teste (com None para navios não atracados)
    initial_state = (None, None, None, None)
    problem.initial = initial_state

    # Criar um nó inicial com este estado
    node = search.Node(problem.initial)
    
    # Expandir o nó e verificar o que acontece
    try:
        children = node.expand(problem)
        print(f"Estados filhos gerados na expansão: {[child.state for child in children]}")
    except Exception as e:
        print(f"Erro ao expandir o nó: {e}")

def test_result_method():
    # Inicializar o problema
    problem = BAProblem()

    # Estado inicial de teste
    problem.S = 5
    problem.N = 4
    problem.vessels = [
        [0, 3, 2, 1],
        [2, 2, 1, 2],
        [4, 1, 1, 3],
        [6, 2, 2, 1]
    ]
    state = (None, None, None, None)
    action = (0, 0, 1)  # Exemplo de ação (atracar o primeiro navio no tempo 0, seção 1)
    
    # Testar o método result() diretamente
    try:
        new_state = problem.result(state, action)
        print(f"Novo estado após aplicar ação: {new_state}")
    except Exception as e:
        print(f"Erro no método result(): {e}")

def test_actions_method():
    # Inicializar o problema
    problem = BAProblem()

    # Estado inicial de teste
    state = (None, None, None, None)
    problem.S = 5  # Definir o número de seções do cais
    problem.N = 4  # Definir o número de navios
    
    # Exemplo de navios
    problem.vessels = [
        [0, 3, 2, 1],  # [tempo de chegada, tempo de processamento, tamanho, peso]
        [2, 2, 1, 2],
        [4, 1, 1, 3],
        [6, 2, 2, 1]
    ]
    
    # Testar o método actions() diretamente
    try:
        actions = problem.actions(state)
        print(f"Ações possíveis geradas: {actions}")
    except Exception as e:
        print(f"Erro no método actions(): {e}")

if __name__ == "__main__":
    print("Testando o método expand()")
    test_expand_node()
    
    print("\nTestando o método result()")
    test_result_method()
    
    print("\nTestando o método actions()")
    test_actions_method()
