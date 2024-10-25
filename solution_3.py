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
        for i, (ui, _) in enumerate(sol):
            ai, pi, _, wi = self.vessels[i]
            ci = ui + pi
            fi = ci - ai
            total_cost += wi * fi
        return total_cost

    def check(self, sol):
        """Verifica se a solução fornecida é viável"""
        max_processing = int(np.max(self.vessels[:, 1]))
        sol = np.array(sol).reshape(-1, 2)
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
        i, mooring_time, berth_section = action
        return state[:i] + ((mooring_time, berth_section),) + state[i+1:]

    def actions(self, state):
        """
        Retorna a lista de ações possíveis para os navios que ainda não foram atracados,
        tentando sempre o canto mais à esquerda possível, ou seja, t = ai e v = mínimo possível.
        Se não for possível, incrementamos t ou v.
        """
        actions = []
        berth_occupation = [0] * self.S  # Inicializa com 0, indicando que o cais está livre no tempo 0

        # Atualiza a ocupação do cais com base nos navios já atracados no estado atual
        for i in range(self.N):
            if state[i] != ():
                mooring_time, berth_section = state[i]
                pi = self.vessels[i][1]
                si = self.vessels[i][2]
                for sec in range(berth_section, berth_section + si):
                    berth_occupation[sec] = max(berth_occupation[sec], mooring_time + pi)

        # Gerar ações para os navios que ainda não foram atracados
        for i in range(self.N):
            if state[i] == ():
                ai, pi, si, wi = self.vessels[i]
                t, v = ai, 0

                while True:
                    for v in range (self.S - si + 1): # Verifica se o navio cabe no cais na seção `v` ao longo do cais
                        if all(berth_occupation[sec] <= t for sec in range(v, v + si)): 
                            actions.append((i, t, v))
                            break
                    else: 
                        t += 1 # Pular para o próximo intervalo de tempo
                        continue
                    break               

        return actions

    def goal_test(self, state):
        """Retorna True se todos os navios foram atracados corretamente"""
        return not any(vessel == () for vessel in state)

    def path_cost(self, c, state1, action, state2):
        """Retorna o custo do caminho que leva de state1 a state2"""
        i, mooring_time, _ = action
        ai, pi, _, wi = self.vessels[i]
        ci = mooring_time + pi
        fi = ci - ai
        return c + (wi * fi)

    def solve(self):
        """Chama o algoritmo de busca de custo uniforme (Uniform Cost Search) para resolver o problema"""
        # Chama o algoritmo de busca A* para resolver o problema
        solution_node = search.astar_search(self)

        if solution_node is not None:
            return list(solution_node.state)
        return None

    def h(self, node):
        """
        Função heurística para estimar o tempo de fluxo total ponderado.
        A heurística calcula o tempo de fluxo total estimado para os navios
        que ainda não foram atracados, com base na ocupação atual do cais.
        É adicionado uma constante a todos os valores calculados de 0.000001 para
        otimizar a resolução de empates pela heurística.
        """
        state = node.state
        total_weighted_flow_time = 0

        # Inicializa a ocupação do cais (0 = livre no tempo 0)
        berth_occupation = [0] * self.S

        # Atualiza a ocupação do cais com base nos navios já atracados no estado atual
        for i in range(self.N):
            if state[i] != ():  # Se o navio i já foi atracado
                mooring_time, berth_section = state[i]
                pi = self.vessels[i][1]  # Tempo de processamento
                si = self.vessels[i][2]  # Tamanho do navio (seções ocupadas)
                for sec in range(berth_section, berth_section + si):
                    berth_occupation[sec] = max(berth_occupation[sec], mooring_time + pi)
                

        # Estimar o tempo de fluxo e o tempo ocioso (penalidade) para os navios que ainda não foram atracados
        for i in range(self.N):
            if state[i] == ():  # Se o navio i ainda não foi atracado
                ai, pi, si, wi = self.vessels[i]  # Tempo de chegada, tempo de processamento, tamanho, peso
                t, v = ai, 0  # Começar a verificar o tempo a partir do tempo de chegada do navio

                # Encontrar o tempo mais cedo possível para atracar o navio
                while True:
                    for v in range (self.S - si + 1): # Verifica se o navio cabe no cais na seção `v` ao longo do cais
                        if all(berth_occupation[sec] <= t for sec in range(v, v + si)):
                            earliest_start_time = t
                            break
                    else: 
                        t += 1 # Pular para o próximo intervalo de tempo
                        continue
                    break

                # Calcula o tempo de fluxo para este navio
                ci = earliest_start_time + pi  # Tempo de partida (fim do processamento)
                fi = ci - ai  # Tempo de fluxo = tempo de partida - tempo de chegada

                # Adiciona o tempo de fluxo ponderado ao total 
                # Nota: Adicionamos o 0.000001 para facilitar o desempate da heuristica em situações em que chegam muitos barcos ao mesmo tempo e com o mesmo peso para não ter que
                # andar a experimentar as permutações todas dos barcos ao longo do cais 
                total_weighted_flow_time += wi * fi + 0.000001

        return total_weighted_flow_time