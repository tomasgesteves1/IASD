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
        if state is None:
            raise ValueError("Erro: O estado não pode ser None.")

        # Converter o estado de tuplo para lista, para permitir modificações
        new_state = list(state)
        
        # Desempacotar a ação (i, mooring_time, berth_section)
        i, mooring_time, berth_section = action
        
        # Verificar se o índice da ação está dentro dos limites do estado
        if i >= len(new_state):
            raise IndexError(f"Erro: O índice {i} está fora do intervalo dos navios.")

        # Atualizar o estado do navio no índice correto
        new_state[i] = (mooring_time, berth_section)
        
        # Retornar o novo estado como tuplo
        new_state_tuple = tuple(new_state)
        
        return new_state_tuple

    def actions(self, state):
        """
        Retorna a lista de ações possíveis para os navios que ainda não foram atracados,
        verificando diretamente no state se o espaço está disponível.
        """

        actions = []
        
        # Definir o tempo máximo como o maior tempo de chegada + maior tempo de processamento
        max_arrival = max(self.vessels[:, 0])  # Maior tempo de chegada
        max_processing = max(self.vessels[:, 1])  # Maior tempo de processamento
        max_time = max_arrival + max_processing  # Tempo máximo permitido

        # Gerar ações possíveis para os navios que ainda não foram atracados
        for i in range(self.N):
            if state[i] == ():  # Se o navio ainda não foi atracado
                ai, pi, si, wi = self.vessels[i]  # Dados do navio

                # Gerar tempos de atracação válidos a partir do tempo de chegada (ai)
                for mooring_time in range(ai, max_time + 1):  
                    for berth_section in range(self.S - si + 1):  # Verifica se o navio cabe no cais
                        # Verificar se esta posição já está ocupada no state
                        is_valid = True
                        for j in range(self.N):
                            if state[j] != ():  # Verifica se este navio já foi atracado
                                other_time, other_section = state[j]
                                # Verifica se há sobreposição
                                if not (
                                    (mooring_time + pi <= other_time or other_time + self.vessels[j][1] <= mooring_time) or
                                    (berth_section + si <= other_section or other_section + self.vessels[j][2] <= berth_section)
                                ):
                                    is_valid = False
                                    break
                        
                        if is_valid:
                            actions.append((i, mooring_time, berth_section))
        print(f"Ações possíveis geradas: {actions}")  # Verificação das ações
        return actions

    def goal_test(self, state):
        """
        Retorna True se o estado fornecido é um estado de objetivo,
        ou seja, se todos os navios foram atracados corretamente (nenhum navio está vazio).
        """
        if state is None:
            return False  # Se o estado for None, não é um estado de objetivo

        # Verifica se todos os elementos do estado são válidos (não estão vazios)
        return all(vessel != () for vessel in state)

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
        # Verificar se o estado inicial foi corretamente definido
        if self.initial is None:
            raise ValueError("O estado inicial não foi definido corretamente.")
        
        # Verificar o conteúdo do estado inicial antes de iniciar a busca
        print(f"Estado inicial utilizado no solve: {self.initial}")  # Verificação de debug

        # Usar Uniform Cost Search passando `self` como o problema
        solution_node = search.uniform_cost_search(self, True)

        if solution_node is not None:
            print(f"Solução encontrada: {solution_node.state}")  # Verificação do estado final
            print(f"Número de nós expandidos: {solution_node}")
            return solution_node.state  # Retorna o estado final (solução)
        else:
            print("Nenhuma solução foi encontrada.")
            return None
