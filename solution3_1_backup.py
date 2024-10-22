import search
import numpy as np

class BAProblem(search.Problem):
    
    def __init__(self):
        """Inicia a classe BAProblem"""
        self.initial = None
        self.S = None
        self.N = None
        self.vessels = np.empty((0, 4), dtype=int)

        # Debug
        self.state_count = 0

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
        # Debug
        self.state_count += 1

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
                    if v + si <= self.S:
                        berth_is_free = all(berth_occupation[sec] <= t for sec in range(v, v + si))
                        if berth_is_free:
                            actions.append((i, t, v))
                            break

                    if v + si < self.S:
                        v += 1
                    else:
                        t += 1
                        v = 0

        return actions

    def goal_test(self, state):
        """Retorna True se todos os navios foram atracados corretamente"""
        return not any(vessel == () for vessel in state)

    def path_cost(self, c, state1, action, state2):
        """Retorna o custo do caminho que leva de state1 a state2"""
        i, mooring_time, berth_section = action
        ai, pi, si, wi = self.vessels[i]
        ci = mooring_time + pi
        fi = ci - ai
        return c + (wi * fi)

    def solve(self):
        """Chama o algoritmo de busca de custo uniforme (Uniform Cost Search) para resolver o problema"""
        # solution_node = search.uniform_cost_search(self)

        # Chama o algoritmo de busca A* para resolver o problema
        solution_node = search.astar_search(self)

        # Debug
        # print(f"Estados visitados: {self.state_count}")

        if solution_node is not None:
            return list(solution_node.state)
        return None

    def h(self, node):
        """
        Função heurística para estimar o tempo de fluxo total ponderado.
        A heurística calcula o tempo de fluxo total estimado para os navios
        que ainda não foram atracados, com base na ocupação atual do cais.
        Também calcula uma penalidade para o tempo de inatividade do cais
        e uma penalidade para seções vazias.
        """
        state = node.state
        total_weighted_flow_time = 0
        idle_time_penalty_weight = 0.075  # Peso da penalidade para o tempo ocioso do cais (ajustável)
        empty_sections_penalty_weight = 0.1  # Peso da penalidade para seções vazias (ajustável)

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
        
        # Inicializa o próximo tempo disponível para cada seção do cais
        next_available_time = berth_occupation[:]

        # Estimar o tempo de fluxo e o tempo ocioso (penalidade) para os navios que ainda não foram atracados
        for i in range(self.N):
            if state[i] == ():  # Se o navio i ainda não foi atracado
                ai, pi, si, wi = self.vessels[i]  # Tempo de chegada, tempo de processamento, tamanho, peso
                t, v = ai, 0  # Começar a verificar o tempo a partir do tempo de chegada do navio

                # Encontrar o tempo mais cedo possível para atracar o navio
                while True:
                    if v + si <= self.S:  # Verifica se há espaço suficiente para o navio
                        berth_is_free = all(berth_occupation[sec] <= t for sec in range(v, v + si))
                        if berth_is_free:
                            # Encontramos o tempo mais cedo possível para atracar o navio
                            earliest_start_time = t
                            break

                    if v + si < self.S:
                        v += 1  # Tentar na próxima seção do cais
                    else:
                        t += 1  # Tentar no próximo intervalo de tempo
                        v = 0  # Reiniciar a verificação das seções do cais

                # Calcula o tempo de fluxo para este navio
                ci = earliest_start_time + pi  # Tempo de partida (fim do processamento)
                fi = ci - ai  # Tempo de fluxo = tempo de partida - tempo de chegada

                # Adiciona o tempo de fluxo ponderado ao total
                total_weighted_flow_time += wi * fi

                # Calcula a penalidade de tempo ocioso para o cais
                idle_time_penalty = max(0, next_available_time[v] - earliest_start_time)  # Penalidade pelo tempo ocioso
                total_weighted_flow_time += idle_time_penalty_weight * idle_time_penalty
                
                # Atualiza o tempo disponível para as seções de cais após atracar o navio
                for sec in range(v, v + si):
                    next_available_time[sec] = earliest_start_time + pi

        ### Penalidade por Seções Vazias ###
        empty_sections = berth_occupation.count(0)  # Contar quantas seções estão vazias
        total_weighted_flow_time += empty_sections_penalty_weight * empty_sections  # Aplicar penalidade

        return total_weighted_flow_time

