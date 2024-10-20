import search
import numpy as np

class BAProblem(search.Problem):
    
    def __init__(self):
        """Inicia a classe BAProblem"""
        self.initial = None
        self.S = None
        self.N = None
        self.vessels = np.empty((0, 4), dtype=int)


    def load(self, fh):
        """Carrega o problema BAP a partir de um arquivo de entrada"""
        for line in fh:
            line = line.strip()
            # Ignora linhas que começam com # ou se a linha está vazia
            if line.startswith("#") or line == "":
                continue
            numbers = line.split()
            # Se a linha contém dois inteiros (S e N)
            if len(numbers) == 2 and self.S is None and self.N is None:
                self.S = int(numbers[0])
                self.N = int(numbers[1])
                self.initial = tuple([() for _ in range(self.N)])
            # Se a linha contém 4 inteiros, armazena-os na matriz
            elif len(numbers) == 4:
                new_row = np.array([[int(x) for x in numbers]])  
                self.vessels = np.vstack((self.vessels, new_row))

    def actions(self, state):
        """
        Retorna a lista de ações possíveis para os navios que ainda não foram atracados,
        tentando sempre o canto mais à esquerda possível, ou seja, t = ai e v = mínimo possível.
        Se não for possível, incrementamos t ou v.
        """
        actions = []

        # Criar uma lista para armazenar os tempos de atracação ocupados para cada seção do cais
        berth_occupation = [0] * self.S  # Inicializa com 0, indicando que o cais está livre no tempo 0

        # Atualiza a ocupação do cais com base nos navios já atracados no estado atual
        for i in range(self.N):
            if state[i] != ():  # Se o navio já foi atracado
                mooring_time, berth_section = state[i]
                pi = self.vessels[i][1]  # Tempo de processamento
                si = self.vessels[i][2]  # Tamanho do navio
                # Marcar as seções ocupadas durante o tempo de processamento do navio
                for sec in range(berth_section, berth_section + si):
                    berth_occupation[sec] = max(berth_occupation[sec], mooring_time + pi)

        # Gerar ações para os navios que ainda não foram atracados
        for i in range(self.N):
            if state[i] == ():  # Se o navio ainda não foi atracado
                ai, pi, si, _ = self.vessels[i]  # Dados do navio  
                
                # Começar sempre com t = ai (tempo de chegada) e v = 0 (primeira seção)
                t, v = ai, 0

                while True:
                    # Verifica se o navio cabe no cais na seção `v`
                    if v + si <= self.S:
                        berth_is_free = all(berth_occupation[sec] <= t for sec in range(v, v + si))
                        if berth_is_free:
                            # Se a seção está livre no tempo `t`, adiciona a ação
                            actions.append((i, t, v))
                            break   # Parar após encontrar o primeiro slot válido
                    
                    # Se não couber ou a seção não estiver livre, tenta aumentar `v`
                    if v + si < self.S:
                        v += 1  # Incrementa `v` para tentar a próxima seção
                    else:
                        # Se não houver mais seções, incrementa `t` e reinicia `v`
                        t += 1
                        v = 0

        return actions

    def result(self, state, action):
        """
        Retorna o novo estado após aplicar a ação dada no estado atual.
        A ação é atracar um navio num tempo e seção específicos.
        """
        # Desempacotar a ação (i, mooring_time, berth_section)
        i, mooring_time, berth_section = action

        # Atualizar o estado
        return state[:i] + ((mooring_time, berth_section),) + state[i+1:]


    def goal_test(self, state):
        """Retorna True se todos os navios foram atracados corretamente"""
        # Retorna False assim que encontra o primeiro navio não atracado
        return not any(vessel == () for vessel in state)

    def path_cost(self, c, state1, action, state2):
        """Retorna o custo do caminho que leva de state1 a state2"""
        i, mooring_time, _= action
        ai, pi, _, wi = self.vessels[i]
        ci = mooring_time + pi
        fi = ci - ai
        return c + (wi * fi)

    def h(self, node):
        """Heurística usando custo ponderado pelo peso."""
        state = node.state
        total_weighted_cost = 0
        
        for i, vessel in enumerate(state):
            if vessel == ():  # Se o navio ainda não foi atracado
                ai, pi, _, wi = self.vessels[i]
                total_weighted_cost += wi * pi  # Estima o custo ponderado pelo peso e tempo de processamento
        
        return total_weighted_cost

    def solve(self):
        """Chama o algoritmo de busca de custo uniforme (Uniform Cost Search) para resolver o problema"""
        # Usar Uniform Cost Search
        solution_node = search.uniform_cost_search(self)
        
        # Verificar se existe solução (se não, retorna None)
        if solution_node is not None:
            return list(solution_node.state)
        return None
    
     
import timeit
# Função para resolver o problema
def resolver_problema():
    solution = problem.solve()
    if solution:
        print("Solução encontrada:", solution.solution())
    else:
        print("Nenhuma solução foi encontrada.")
# Converter a solução para inteiros
def converter_solucao(solution):
    return [(int(t), int(v)) for t, v in solution]

# Exemplo de uso:
if __name__ == "__main__":
    problem = BAProblem()
    
    # Carregar o problema de um arquivo
    with open("example1.dat") as fh:
        problem.load(fh)
    
    # Resolver o problema
    solution = problem.solve()
    if solution:
        # Converter a solução para inteiros
        solution_convertida = converter_solucao(solution)
        print("Solução encontrada:", solution_convertida)
    else:
        print("Nenhuma solução foi encontrada.")
    tempo_execucao = timeit.timeit("problem.solve()", globals=globals(), number=1)
    print(f"A função demorou {tempo_execucao:.4f} segundos a correr.")


