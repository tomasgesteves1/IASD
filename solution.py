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

            # Ignora linhas que começam com #
            if line.startswith("#"):
                continue

            # Verifica se a linha está vazia
            if line == "":
                break

            # Se a linha contém dois inteiros (S e N)
            numbers = line.split()
            if len(numbers) == 2 and self.S is None and self.N is None:
                self.S = int(numbers[0])
                self.N = int(numbers[1])
               
            # Se a linha contém 4 inteiros, armazena-os na matriz
            elif len(numbers) == 4:
                new_row = np.array([[int(x) for x in numbers]])  
                self.vessels = np.vstack((self.vessels, new_row))  

        return

    def cost(self, sol):
        """Calcula o custo da solução fornecida"""
                  
        total_cost = 0
        for i, (ui, vi) in enumerate(sol):
            ai, pi, si, wi = self.vessels[i]
            ci = ui + pi  # Tempo de partida do navio
            fi = ci - ai  # Flow time
            total_cost += wi * fi
            
        return total_cost

    def check(self, sol):
        """Verifica se a solução fornecida é viável"""
        
        max_processing = int(np.max(self.vessels[:, 1]))

        sol = np.array(sol).reshape(-1,2)
        max_arriving = np.max(sol[:, 0])
        
        # Cria a matriz de ocupação do cais (berth occupation)
        berth_occupation = np.zeros(( max_arriving + max_processing, self.S), dtype=int)

        # Verifica e preenche a matriz de ocupação do cais
        for i, (ui, vi) in  enumerate(sol):
            
            #Verifica se o barco já chegou à hora de descarregar
            if ui < self.vessels[i][0]:
                return False
            
            #Verifica se o barco cabe no cais
            if vi + self.vessels[i][2] > self.S:
                return False
            
            #Preenche a matriz de ocupação
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
        A ação é atracar um navio específico num tempo e local específicos.
        """
        # Fazer uma cópia do estado atual para não modificar o original
        new_state = state.copy()
        
        # Desempacotar a ação (i, mooring_time, berth_section)
        i, mooring_time, berth_section = action
        
        # Atualizar o estado do navio i com a nova ação (tempo e seção de atracação)
        new_state[i] = (mooring_time, berth_section)
        
        # Retornar o novo estado
        return new_state
    
    def actions(self, state):
        """
        Retorna a lista de ações possíveis para os navios que ainda não foram atracados.
        Gera combinações de tempo de atracação e seção do cais.
        O tempo de atracação é limitado a um valor máximo baseado no tempo de chegada e processamento.
        """
        actions = []
        
        # Definir o tempo máximo como o maior tempo de chegada + maior tempo de processamento
        max_arrival = max(self.vessels[:, 0])  # Maior tempo de chegada
        max_processing = max(self.vessels[:, 1])  # Maior tempo de processamento
        max_time = max_arrival + max_processing  # Tempo máximo permitido

        for i in range(self.N):  # Para cada navio
            if state[i] is None:  # Se o navio ainda não foi atracado
                ai, pi, si, wi = self.vessels[i]  # Dados do navio

                # Verificar tempos de atracação válidos a partir do tempo de chegada (ai)
                # Limitando até o max_time
                for mooring_time in range(ai, max_time + 1):  # Gera tempos de atracação válidos >= ai e <= max_time
                    # Verificar seções do cais onde o navio pode ser alocado
                    for berth_section in range(self.S - si + 1):  # Verifica se o navio cabe
                        actions.append((i, mooring_time, berth_section))

        return actions

    def goal_test(self, state):
        """
        Retorna True se o estado fornecido é um estado de objetivo,
        ou seja, se todos os navios foram alocados e ancorados corretamente.
        """
        # Verifica se algum navio ainda está como None (não atracado)
        for navio in state:
            if navio is None:
                return False
        return True

    def path_cost(self, c, state1, action, state2):
        """
        Retorna o custo do caminho que leva de state1 a state2 após aplicar a ação.
        O custo é o total weighted flow time.
        """
        # Desempacotar a ação (i, mooring_time, berth_section)
        i, mooring_time, berth_section = action

        # Obter os dados do navio i
        ai, pi, si, wi = self.vessels[i]

        # Calcular o tempo de partida do navio i (c_i = u_i + p_i)
        ci = mooring_time + pi

        # Calcular o flow time (f_i = c_i - a_i)
        fi = ci - ai

        # Calcular o flow time ponderado (w_i * f_i)
        weighted_flow_time = wi * fi

        # Retornar o custo atualizado (custo anterior + flow time ponderado)
        return c + weighted_flow_time

    def solve(self):
        """
        Chama o algoritmo de busca de custo uniforme (Uniform Cost Search) para resolver o problema.
        Retorna a solução na forma de uma lista de tuplas (ui, vi).
        """
        # Estado inicial: todos os navios ainda não atracados
        initial_state = [None] * self.N

        # Criar uma instância do problema, passando o estado inicial e, opcionalmente, o goal
        problem = search.Problem(initial_state)

        # Usar a busca de custo uniforme para encontrar a solução
        solution_node = search.uniform_cost_search(problem)

        # Verificar se a solução foi encontrada
        if solution_node is not None:
            return solution_node.state  # O estado final contém a alocação dos navios
        else:
            return None  # Caso não encontre solução