class BAProblem:
    def __init__(self):
        """Instancia a classe BAProblem."""
        self.initial = None
        self.S = 0  # tamanho do espaço de atracação
        self.N = 0  # número de navios
        self.vessels = []  # lista que contém os dados dos navios [(ai, pi, si, wi), ...]

    def load(self, fh):
        """Carrega um problema BAP a partir de um arquivo de entrada."""
        self.vessels = []
        for line in fh:
            line = line.strip()
            if line.startswith('#') or not line:  # ignora comentários e linhas vazias
                continue
            data = list(map(int, line.split()))
            if len(data) == 2:
                self.S, self.N = data  # Lê S (tamanho do espaço de atracação) e N (número de navios)
            elif len(data) == 4:
                self.vessels.append(tuple(data))  # Lê os dados de cada navio (ai, pi, si, wi)

    def cost(self, sol):
        """
        Calcula o custo da solução dada.
        :param sol: Lista de tuplas [(ui, vi), ...], onde ui é o tempo de início e vi é a seção inicial do cais.
        :return: Custo total da solução (soma dos tempos ponderados de fluxo).
        """
        total_cost = 0
        for i, (ui, vi) in enumerate(sol):
            ai, pi, si, wi = self.vessels[i]
            ci = ui + pi  # Tempo de partida do navio
            flow_time = ci - ai  # Tempo de fluxo (fi)
            total_cost += wi * flow_time
        return total_cost

    def check(self, sol):
        """
        Verifica se a solução dada é viável.
        :param sol: Lista de tuplas [(ui, vi), ...], onde ui é o tempo de início e vi é a seção inicial do cais.
        :return: True se a solução for viável, False caso contrário.
        """
        # Verifica se não há conflitos de atracação e se os navios estão dentro dos limites de tempo e espaço.
        berth_occupancy = [[False] * self.S for _ in range(max(ui + pi for ui, _ in sol))]  # Matriz de ocupação do cais

        for i, (ui, vi) in enumerate(sol):
            ai, pi, si, wi = self.vessels[i]
            
            # Verifica se o navio está dentro dos limites do espaço de atracação
            if vi < 0 or vi + si > self.S:
                return False  # Fora do limite do cais

            # Verifica se o tempo de início é pelo menos o tempo de chegada
            if ui < ai:
                return False  # O tempo de início é menor que o tempo de chegada

            # Verifica se o navio ocupa seções do cais já ocupadas
            for t in range(ui, ui + pi):  # Para cada unidade de tempo durante o processamento
                for s in range(vi, vi + si):  # Para cada seção do cais ocupada pelo navio
                    if berth_occupancy[t][s]:  # Verifica se já está ocupada
                        return False  # Conflito de atracação
                    berth_occupancy[t][s] = True  # Marca como ocupada

        return True  # Se não houve conflitos, a solução é viável


# Exemplo de uso
if __name__ == '__main__':
    # Abre o arquivo de exemplo
    with open('example1.dat', 'r') as fh:
        bap = BAProblem()
        bap.load(fh)

        # Exemplo de solução para o arquivo de entrada
        solution = [(10, 0), (11, 2), (3, 4), (0, 0)]

        # Verifica a solução
        if bap.check(solution):
            print("Solução é viável.")
            print("Custo total da solução:", bap.cost(solution))
        else:
            print("Solução não é viável.")
