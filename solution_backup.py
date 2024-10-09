import search
import numpy as np
import os

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
            if line.startswith("#") or line == "":
                continue
            numbers = line.split()
            if len(numbers) == 2 and self.S is None and self.N is None:
                self.S = int(numbers[0])
                self.N = int(numbers[1])
                self.initial = tuple([() for _ in range(self.N)])

            elif len(numbers) == 4:
                new_row = np.array([[int(x) for x in numbers]])  
                self.vessels = np.vstack((self.vessels, new_row))

    def cost(self, sol):
        """Calcula o custo da solução fornecida"""
        total_cost = 0
        for i, (ui, vi) in enumerate(sol):
            ai, pi, si, wi = self.vessels[i]
            ci = ui + pi
            fi = ci - ai
            total_cost += wi * fi
        return total_cost

    def check(self, sol):
        """Verifica se a solução fornecida é viável"""
        max_processing = int(np.max(self.vessels[:, 1]))
        sol = np.array(sol).reshape(-1,2)
        max_arriving = np.max(sol[:, 0])
        berth_occupation = np.zeros((max_arriving + max_processing, self.S), dtype=int)
        for i, (ui, vi) in enumerate(sol):
            if ui < self.vessels[i][0]:
                return False
            if vi + self.vessels[i][2] > self.S:
                return False
            for j in range(self.vessels[i][2]):                
                for k in range(self.vessels[i][1]):
                    if berth_occupation[ui+k][vi+j] == 1:
                        return False
                    else:
                        berth_occupation[ui+k][vi+j] += 1
        return True
    
    def result(self, state, action):
        """
        Retorna o novo estado após aplicar a ação dada no estado atual.
        A ação é atracar um navio num tempo e seção específicos.
        """

        # Desempacotar a ação (i, mooring_time, berth_section)
        i, mooring_time, berth_section = action

        # Atualizar o estado diretamente sem conversão desnecessária
        return state[:i] + ((mooring_time, berth_section),) + state[i+1:]

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
                ai, pi, si, wi = self.vessels[i]  # Dados do navio

                # Começar sempre com t = ai (tempo de chegada) e v = 0 (primeira seção)
                t = ai
                v = 0

                while True:
                    # Verifica se o navio cabe no cais na seção `v`
                    if v + si <= self.S:
                        berth_is_free = all(
                            berth_occupation[sec] <= t
                            for sec in range(v, v + si)
                        )

                        if berth_is_free:
                            # Se a seção está livre no tempo `t`, adiciona a ação
                            actions.append((i, t, v))
                            break  # Parar após encontrar o primeiro slot válido

                    # Se não couber ou a seção não estiver livre, tenta aumentar `v`
                    if v + si < self.S:
                        v += 1  # Incrementa `v` para tentar a próxima seção
                    else:
                        # Se não houver mais seções, incrementa `t` e reinicia `v`
                        t += 1
                        v = 0

        return actions



    def goal_test(self, state):
        """
        Retorna True se o estado fornecido é um estado de objetivo,
        ou seja, se todos os navios foram atracados corretamente (nenhum navio está vazio).
        """
        # Retorna False assim que encontra o primeiro navio não atracado
        return not any(vessel == () for vessel in state)

    def path_cost(self, c, state1, action, state2):
        """Retorna o custo do caminho que leva de state1 a state2"""
        i, mooring_time, berth_section = action
        ai, pi, si, wi = self.vessels[i]
        ci = mooring_time + pi
        fi = ci - ai
        return c + (wi * fi)

    def solve(self):
        """
        Chama o algoritmo de busca de custo uniforme (Uniform Cost Search) para resolver o problema.
        Retorna a solução na forma de uma lista de tuplas (ui, vi).
        """
        # Usar Uniform Cost Search passando `self` como o problema
        solution_node = search.uniform_cost_search(self)
        # solution_node = search.breadth_first_tree_search(self)
        # solution_node = search.depth_first_tree_search(self)
        # solution_node = search.depth_first_graph_search(self)
        # solution_node = search.breadth_first_graph_search(self)
        # solution_node = search.iterative_deepening_search(self)
        # solution_node = search.depth_limited_search(self)
        # solution_node = search.best_first_graph_search(self, lambda node: node.path_cost)


        




        if solution_node is not None:
            solution = list(solution_node.state)
            return solution
        else:
            return None
