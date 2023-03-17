import random
import math

class Individuo:
    def __init__(self, sequencia, aptidao = 0) -> None:
        self.sequencia = sequencia
        self.aptidao = aptidao

# gera a população (100 indivíduos que são 22 bits)

def gerar_populacao(n_individuos, tam_individuo):
    """
    Retorna uma lista de 'Individuo' com sequências aleatórias e não repetidas
    """
    populacao = []
    sequencias = []
    i = 0
    while i < n_individuos:
        sequencia_novo_individuo = []
        for _ in range(tam_individuo):
            bit = random.randint(0, 1)
            sequencia_novo_individuo.append(bit)
        novo_individuo = Individuo(sequencia_novo_individuo)
        if novo_individuo.sequencia not in sequencias:
            sequencias += [novo_individuo.sequencia]
            populacao.append(novo_individuo)
        else:
            n_individuos += 1
        i += 1
    return populacao

# obtem de cada indivíduo o ponto de reposição e tamanho do lote
def avaliar_individuos(populacao):
    pass
# gera observações de 5000 dias

# função objetivo

def func_objetivo(a, b, demanda_atendida, demanda_total, media_estoque, media_demanda):
    """
    Retorna a aptidão de um indivíduo, com base nos parâmetros listados.
    """
    na = demanda_atendida / demanda_total
    A = math.log(10 ** -3 / 10 ** media_demanda)
    ce = math.e ** (A * media_estoque)
    res = (na * a) + (ce * b)
    return res

def sort_function(individuo: Individuo):
        return individuo.aptidao

def selecao_por_torneio(pais, tam_pop_pais):
    nova_populacao = []
    while len(nova_populacao) < tam_pop_pais:
        torneio = random.sample(pais, 2)
        melhor_individuo = max(torneio, key=sort_function)
        nova_populacao.append(melhor_individuo)
    return nova_populacao

def crossover(pai: Individuo, mae: Individuo):
    corte1 = random.randint(0, len(pai) - 1)
    corte2 = random.randint(0, len(pai) - 1)

    # Garante que corte2 é maior ou igual a corte1
    if corte2 < corte1:
        corte1, corte2 = corte2, corte1

    # Realiza o crossover
    filho1 = Individuo(pai.sequencia[:corte1] + mae.sequencia[corte1:corte2] + pai.sequencia[corte2:])
    filho2 = Individuo(mae.sequencia[:corte1] + pai.sequencia[corte1:corte2] + mae.sequencia[corte2:])

    return filho1, filho2

def gerar_filhos(pais, tam_nova_pop):
    nova_pop = []
    for _ in range(tam_nova_pop):
        pai1 = pais[random.randint(0, len(pais) - 1)]
        pai2 = pais[random.randint(0, len(pais) - 1)]
        filho_1, filho_2 = crossover(pai1, pai2)
        nova_pop.append(filho_1)
        nova_pop.append(filho_2)
    if len(nova_pop) > tam_nova_pop:
        nova_pop.pop()
    return nova_pop

def mutacao(pop_filhos, taxa_mutacao):
    for filho in pop_filhos:
        for i, value in enumerate(filho.sequencia):
            if random.random() <= taxa_mutacao:
                if value == 0:
                    filho.sequencia[i] = 1
                else: filho.sequencia[i] = 0

def alg_gen(tam_populacao, n_geracoes, tam_cromossomo, taxa_mutacao):
    populacao = gerar_populacao(tam_populacao, tam_cromossomo)
    avaliar_individuos(populacao)

    for _ in range(n_geracoes):
        pais = selecao_por_torneio(populacao)
        filhos = gerar_filhos(pais, tam_populacao)
        mutacao(filhos, taxa_mutacao)
        avaliar_individuos(filhos)
        populacao = filhos
    
    melhor_individuo = max(populacao, key=sort_function)
    return melhor_individuo
