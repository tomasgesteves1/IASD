import search
import numpy as np
import ast
import io

class BAProblem(search.Problem):
    
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
            with fh as arquivo:
                for linha in arquivo:
                    linha = linha.strip()

                    # Ignora linhas que começam com #
                    if linha.startswith("#"):
                        continue

                    # Verifica se a linha está vazia
                    if linha == "":
                    
                        break

                    # Se a linha contém dois inteiros (S e N)
                    numeros = linha.split()
                    if len(numeros) == 2 and self.S is None and self.N is None:
                        try:
                            self.S = int(numeros[0])
                            self.N = int(numeros[1])
                            #print(f"Variáveis S: {self.S} e N: {self.N} foram definidas")
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

            return

        except FileNotFoundError:
            #print(f"Erro: O ficheiro '{fh}' não foi encontrado.")
            return None
        except IOError:
            #print(f"Erro: Não foi possível ler o ficheiro '{fh}'.")
            return None


    def cost(self, sol):
        """Calcula o custo da solução fornecida"""
        
        lista = sol
        
        final_cost = 0
        
        for i in range(len(lista)):
            final_cost += self.matriz[i][3] * ((lista[i][0] - self.matriz[i][0]) + self.matriz[i][1])  # soma + wi*((vi-ai)+pi)
        
        return final_cost

    def check(self, sol):
        """Verifica se a solução fornecida é viável"""

        # Inicializa max_val e max_idx

        max_processing = 0
            
        for linha in self.matriz:
            if linha[1] > max_processing:
                max_processing = linha[1]


        max_arriving = 0
        for i in range(len(sol)):
            if sol[i][0] > max_arriving:
                max_arriving = sol[i][0]
                
        # Cria a matriz de ocupação do cais (berth occupation)
        berth_occupation = np.zeros(( max_arriving + max_processing, self.S), dtype=int)

        # Verifica e preenche a matriz de ocupação do cais
        for i in range(len(sol)):
            
            #Verifica se o barco cabe no cais
            if sol[i][1] + self.matriz[i][2] > self.S:
                return False
            
            #Verifica se o barco já chegou à hora de descarregar
            if sol[i][0] < self.matriz[i][0]:
                return False
            
            for j in range(self.matriz[i][2]):
                a = sol[i][0]
                b = sol[i][1] + j
                
                for k in range(self.matriz[i][1]):
                    c = a + k
                    berth_occupation[c][b] += 1

        # Verifica se algum cais está ocupado por mais de um navio ao mesmo tempo
        for linha in berth_occupation:
            if np.any(linha > 1):  # Verifica se há valores maiores que 1
                return False
        
        return True