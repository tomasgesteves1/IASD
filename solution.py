import numpy as np
import ast

matriz = []
S = None
N = None

def load(fh):
    global matriz 
    global S
    global N
    
    S = None
    N = None
    
    with open(fh, 'r') as arquivo:
        for linha in arquivo:
            linha = linha.strip()

            # Ignora linhas que começam com #
            if linha.startswith("#"):
                continue

            # Verifica se a linha está vazia
            if linha == "":
                print("Terminou a leitura")
                break

            # Se a linha contém dois inteiros (S e N)
            numeros = linha.split()
            if len(numeros) == 2 and S is None and N is None:
                S = int(numeros[0])
                N = int(numeros[1])
                print(f"Variáveis S: {S} e N: {N} foram definidas")
                continue

            # Se a linha contém 4 inteiros, armazena-os na matriz
            if len(numeros) == 4:
                matriz.append([int(x) for x in numeros])

    # Ajusta o tamanho da matriz para N x 4
    if len(matriz) != N:
        print(f"Atenção: Existe informação em falta sobre os navios")

    return S, N, matriz


def cost(sol):
    
    global matriz 
    
    with open(sol, 'r') as f:
        # Ler o conteúdo do ficheiro
        linha = f.readline().strip()
        # Usar ast.literal_eval para converter a string da linha em uma lista de tuplas
        lista = ast.literal_eval(linha)
        
    n_vessels = len(lista)
    
    final_cost = 0
    
    for i in range(len(lista)):
        final_cost += matriz[i][3] * ((lista[i][0] - matriz[i][0]) + matriz[i][1])  # soma + wi*((vi-ai)+pi)
    
    return final_cost


def check(sol):
    global S
    
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

    aux = max_val + matriz[max_idx][1] + 1

    # Cria a matriz de ocupação do cais (berth occupation)
    berth_occupation = np.zeros((S, aux), dtype=int)


    # Verifica e preenche a matriz de ocupação do cais
    for i in range(len(lista)):
        
        if lista[i][1] + matriz[i][2] > S:
            return False
        
        for j in range(matriz[i][1]):
            a = lista[i][0]
            b = lista[i][1] + j
            if a < S and b < aux:  # Verifica se os índices são válidos
                berth_occupation[a][b] += 1
    
    print("Matriz de ocupação inicial:")
    print(berth_occupation)
    # Verifica se algum cais está ocupado por mais de um navio ao mesmo tempo
    for linha in berth_occupation:
        if np.any(linha > 1):  # Verifica se há valores maiores que 1
            return False
    
    return True
    
    
def main():
    

    fh = 'test.dat'
    S, N, matriz = load(fh)
    
    print("Matriz lida:")
    for linha in matriz:
        print(linha)
        
    sol = 'sol.dat'
    custo = cost(sol)
    print(f"Custo final: {custo}")
    
    
    valid = check(sol)
    print(f"RESULTADO: {valid}")

        
if __name__ == '__main__':
    main()
