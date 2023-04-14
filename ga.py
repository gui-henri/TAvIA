import random
import numpy as np
import os

class Individuo:
    def __init__(self, sequencia, aptidao = 0) -> None:
        self.sequencia = sequencia
        self.aptidao = aptidao

def simular(ponto_corte, tamanho_lote, media_demanda=50, desvio_demanda=10, media_lead=5, desvio_lead=1, estoque_inicial=15):
    estoque = estoque_inicial
    estoque_dias = []
    dias_ate_entrega = -1
    demanda_atendida = 0
    total_demanda = 0
    for _ in range(365):
        if dias_ate_entrega > 0:
            dias_ate_entrega -= 1
        elif dias_ate_entrega == 0:
            dias_ate_entrega = -1
            estoque += tamanho_lote
        estoque_dias.append(estoque)
        demanda = int(round(np.random.normal(media_demanda, desvio_demanda)))
        if demanda > estoque:
            demanda_atendida += estoque
            total_demanda += demanda
            estoque = 0
        else:
            estoque -= demanda
            total_demanda += demanda
            demanda_atendida += demanda
        if estoque <= ponto_corte and dias_ate_entrega == -1:
            dias_ate_entrega = int(round(np.random.normal(media_lead, desvio_lead)))
    media_estoque = np.mean(estoque_dias)
    return demanda_atendida, total_demanda, media_demanda, media_estoque

# gera a população (100 indivíduos que são 22 bits)

def pedacos_individuo(individuo: Individuo):
    divisa = int((len(individuo.sequencia) / 2) - 1)
    ponto_reposicao = int(''.join(map(str, individuo.sequencia[:divisa])), 2)
    tamanho_lote = int(''.join(map(str, individuo.sequencia[divisa:])), 2)
    return ponto_reposicao, tamanho_lote

def gerar_populacao(n_individuos, tam_individuo, media_demanda=50):
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
        ponto_reposicao, tamanho_lote = pedacos_individuo(novo_individuo)
        if (ponto_reposicao <= 10 * media_demanda) and (tamanho_lote <= 10 * media_demanda) and (ponto_reposicao >= 2 * media_demanda) and (tamanho_lote >= 2 * media_demanda) and (novo_individuo.sequencia not in sequencias):
            sequencias += [novo_individuo.sequencia]
            populacao.append(novo_individuo)
        else:
            n_individuos += 1
        i += 1
    return populacao

# obtem de cada indivíduo o ponto de reposição e tamanho do lote
def avaliar_individuos(populacao, a = 0.5, b = 0.5, media_demanda=50, desvio_demanda=10, media_lead=5, desvio_lead=1, estoque_inicial=15):
    for individuo in populacao:
        ponto_reposicao, tamanho_lote = pedacos_individuo(individuo)
        demanda_atendida, total_demanda, media_demanda, media_estoque = simular(ponto_reposicao, tamanho_lote, media_demanda, desvio_demanda, media_lead, desvio_lead, estoque_inicial)
        individuo.aptidao = func_objetivo(
                    a=a, 
                    b=b, 
                    demanda_atendida=demanda_atendida, 
                    demanda_total=total_demanda, 
                    media_estoque=media_estoque, 
                    media_demanda=media_demanda
                )

def func_objetivo(a, b, demanda_atendida, demanda_total, media_estoque, media_demanda):
    """
    Retorna a aptidão de um indivíduo, com base nos parâmetros listados.
    """
    na = demanda_atendida / demanda_total
    razao_excesso = (media_estoque - media_demanda) / media_demanda
    ce = 1 / (1 + np.exp(razao_excesso * 7))
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

def crossover(pai: Individuo, mae: Individuo, media_demanda=50):
    corte1 = random.randint(0, len(pai.sequencia) - 1)
    corte2 = random.randint(0, len(pai.sequencia) - 1)

    # Garante que corte2 é maior ou igual a corte1
    if corte2 < corte1:
        corte1, corte2 = corte2, corte1

    # Realiza o crossover
    filho1 = Individuo(pai.sequencia[:corte1] + mae.sequencia[corte1:corte2] + pai.sequencia[corte2:])
    filho2 = Individuo(mae.sequencia[:corte1] + pai.sequencia[corte1:corte2] + mae.sequencia[corte2:])

    reposicao_f1, lote_f1 = pedacos_individuo(filho1)
    reposicao_f2, lote_f2 = pedacos_individuo(filho2)

    if reposicao_f1 > media_demanda * 10 or lote_f1 > media_demanda * 10:
        filho1 = pai
    if reposicao_f2 > media_demanda * 10 or lote_f2 > media_demanda * 10:
        filho2 = mae

    return filho1, filho2

def gerar_filhos(pais, tam_nova_pop):
    nova_pop = []
    while len(nova_pop) < tam_nova_pop:
        pai1 = pais[random.randint(0, len(pais) - 1)]
        pai2 = pais[random.randint(0, len(pais) - 1)]
        filho_1, filho_2 = crossover(pai1, pai2)
        nova_pop.append(filho_1)
        nova_pop.append(filho_2)
    if len(nova_pop) > tam_nova_pop:
        nova_pop.pop()
    return nova_pop

def mutacao(pop_filhos, taxa_mutacao, media_demanda=50):
    for filho in pop_filhos:
        sequencia_antiga = filho.sequencia.copy()
        for i, value in enumerate(filho.sequencia):
            if random.random() <= taxa_mutacao:
                if value == 0:
                    filho.sequencia[i] = 1
                else: filho.sequencia[i] = 0
        ponto_reposicao, tamanho_lote = pedacos_individuo(filho)
        if ponto_reposicao > 10 * media_demanda or tamanho_lote > 10 * media_demanda:
            filho.sequencia = sequencia_antiga

def elitismo(populacao, filhos):
    melhor_individuo = max(populacao, key=sort_function)
    pior_individuo = min(filhos, key=sort_function)
    filhos.remove(pior_individuo)
    filhos.append(melhor_individuo)
    populacao = filhos


def alg_gen(tam_populacao, n_geracoes, tam_cromossomo, taxa_mutacao, a=0.5, b=0.5, media_demanda=50, desvio_demanda=10, media_lead=5, desvio_lead=2, estoque_inicial=15):
    populacao = gerar_populacao(tam_populacao, tam_cromossomo)
    avaliar_individuos(populacao)

    for i in range(n_geracoes):
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f'Geração {i}')
        pais = selecao_por_torneio(populacao, len(populacao))
        filhos = gerar_filhos(pais, tam_populacao)
        mutacao(filhos, taxa_mutacao)
        avaliar_individuos(filhos)
        elitismo(populacao, filhos)
        melhor_individuo = max(populacao, key=sort_function)
    
    melhor_individuo = max(populacao, key=sort_function)
    return melhor_individuo

if __name__ == "__main__":
    parametros = []
    with open('dados.txt', 'r') as f:
        linhas = f.readlines()

        # Processar as linhas do arquivo
        for linha in linhas:
            parametros.append(linha.strip())
        # Fechar o arquivo
        f.close()

    print('Irei rodar o algoritmo genético com os determinados parâmetros: ')
    pop_size = int(parametros[0])
    print(f'Tamanho da população: {pop_size}')
    n_geracoes = int(parametros[1])
    print(f'Número de gerações: {n_geracoes}')
    tam_cromossomo = int(parametros[2])
    print(f'Tamanho do Cromossomo: {tam_cromossomo}')
    taxa_mutacao = float(parametros[3])
    print(f'Taxa de mutação: {taxa_mutacao * 100}%')
    a = float(parametros[4])
    print(f'a: {a}')
    b = float(parametros[5])
    print(f'b: {b}')
    media_demanda = int(parametros[6])
    print(f'Media demanda: {media_demanda}')
    desvio_demanda = int(parametros[7])
    print(f'Desvio demanda: {desvio_demanda}')
    media_lead = int(parametros[8])
    print(f'Media lead: {media_lead}')
    desvio_lead = int(parametros[9])
    print(f'Desvio lead: {desvio_lead}')
    estoque_inicial = int(parametros[10])
    print(f'Estoque inicial: {estoque_inicial}')
    resp = input('Prosseguir? Y/n')
    if resp == 'y' or resp == 'Y':
        ind = alg_gen(pop_size, n_geracoes, tam_cromossomo, taxa_mutacao, a, b, media_demanda, desvio_demanda, media_lead, desvio_lead, estoque_inicial)
        ponto_reposicao, tamanho_lote = pedacos_individuo(ind)
        print(f'O melhor indivíduo diz que o ponto de reposição deve ser: {ponto_reposicao}')
        print(f'O melhor indivíduo diz que o tamanho do lote deve ser: {tamanho_lote}')
        print(f'Sua aptidao: {ind.aptidao}')