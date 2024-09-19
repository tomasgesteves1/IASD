import numpy as np
import ast

class BAProblem:
    def __init__(self):
        self.matriz = []
        self.S = None
        self.N = None

    def load(self, fh):
        """Carrega o problema BAP a partir de um ficheiro de entrada com tratamento de exceções"""
        self.matriz = []
        self.S = None
        self.N = None

        try:
            with open(fh, 'r') as arquivo:
                for linha in arquivo:
                    linha = linha.strip()

                    # Ignora linhas que começam com #
                    if linha.startswith("#"):
                        continue

                    # Verifica se a linha está vazia
                    if linha == "":
                        print("Terminou a leitura.")
                        break

                    # Se a linha contém dois inteiros (S e N)
                    numeros = linha.split()
                    if len(numeros) == 2 and self.S is None and self.N is None:
                        try:
                            self.S = int(numeros[0])
                            self.N = int(numeros[1])
                            print(f"Variáveis S: {self.S} e N: {self.N} foram definidas")
                        except ValueError:
                            raise ValueError("Erro: A linha contendo S e N não é composta por dois inteiros válidos.")
                        continue

                    # Se a linha contém 4 inteiros, armazena-os na matriz
                    if len(numeros) == 4:
                        try:
                            # Converte cada valor da linha em um inteiro
                            self.matriz.append([int(x) for x in numeros])
                        except ValueError:
                            raise ValueError(f"Erro: A linha {linha} contém valores não inteiros.")

            # Verifica se o número de navios lido corresponde ao esperado
            if len(self.matriz) != self.N:
                raise ValueError(f"Atenção: Existem informações faltantes ou em excesso sobre os navios. Esperado {self.N}, mas encontrado {len(self.matriz)}.")

            return self.S, self.N, self.matriz

        except FileNotFoundError:
            print(f"Erro: O ficheiro '{fh}' não foi encontrado.")
            return None
        except IOError:
            print(f"Erro: Não foi possível ler o ficheiro '{fh}'.")
            return None


    def cost(self, sol):
        """Calcula o custo da solução fornecida"""
        with open(sol, 'r') as f:
            # Ler o conteúdo do ficheiro
            linha = f.readline().strip()
            # Usar ast.literal_eval para converter a string da linha em uma lista de tuplas
            lista = ast.literal_eval(linha)
        
        n_vessels = len(lista)
        
        final_cost = 0
        
        for i in range(len(lista)):
            final_cost += self.matriz[i][3] * ((lista[i][0] - self.matriz[i][0]) + self.matriz[i][1])  # soma + wi*((vi-ai)+pi)
        
        return final_cost

    def check(self, sol):
        """Verifica se a solução fornecida é viável"""
        with open(sol, 'r') as f:
            linha = f.readline().strip()
            lista = ast.literal_eval(linha)

        # Inicializa max_val e max_idx
        max_val = 0
        max_idx = 0

        # Encontra o maior valor e o índice correspondente
        for i in range(len(lista)):
            if lista[i][0] > max_val:
                max_val = lista[i][0]
                max_idx = i

        aux = max_val + self.matriz[max_idx][1] + 1

        # Cria a matriz de ocupação do cais (berth occupation)
        berth_occupation = np.zeros((self.S, aux), dtype=int)

        # Verifica e preenche a matriz de ocupação do cais
        for i in range(len(lista)):
            
            if lista[i][1] + self.matriz[i][2] > self.S:
                return False
            
            for j in range(self.matriz[i][1]):
                a = lista[i][0]
                b = lista[i][1] + j
                if a < self.S and b < aux:  # Verifica se os índices são válidos
                    berth_occupation[a][b] += 1
        
        print("Matriz de ocupação inicial:")
        print(berth_occupation)
        # Verifica se algum cais está ocupado por mais de um navio ao mesmo tempo
        for linha in berth_occupation:
            if np.any(linha > 1):  # Verifica se há valores maiores que 1
                return False
        
        return True

# Função principal
def main():
    problem = BAProblem()

    fh = 'test.dat'
    S, N, matriz = problem.load(fh)
    
    print("Matriz lida:")
    for linha in matriz:
        print(linha)
        
    sol = 'sol.dat'
    custo = problem.cost(sol)
    print(f"Custo final: {custo}")
    
    valid = problem.check(sol)
    print(f"RESULTADO: {valid}")

if __name__ == '__main__':
    main()
