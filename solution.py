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
    