import random
import time
from math import sqrt

random.seed(999)

def ler_entrada(arquivo):
    pontos_de_entrega = []
    ponto_de_partida = ()
    with open(arquivo) as arquivo:
        for i, linha in enumerate(arquivo):
            lista = linha.split()
            for j, element in enumerate(lista):
                if element != '0':
                    if element == 'R':
                        ponto_de_partida = (i, j, element)
                    else:
                        pontos_de_entrega.append((i, j, element))
    return ponto_de_partida, pontos_de_entrega

def gerar_populacao(pontos_de_entrega, n_individuos):
    populacao = []
    i = 0
    while i < n_individuos:
        novo_individuo = pontos_de_entrega.copy()
        random.shuffle(novo_individuo)
        
        if novo_individuo not in populacao:
            populacao += [novo_individuo]
        else:
            n_individuos += 1
        i += 1
    return populacao

def distancia_entre_pontos(tupla_1, tupla_2):
    return int(sqrt((tupla_1[0] - tupla_2[0]) ** 2 + (tupla_1[1] - tupla_2[1]) ** 2))

def avaliar_individuo(ponto_inicial, rota):
    inicial_para_segundo = distancia_entre_pontos(ponto_inicial, rota[0])
    ultimo_para_inicial = 0

    dist_rota = 0
    for i, ponto in enumerate(rota):
        if ponto != rota[-1]:   
            dist_rota += distancia_entre_pontos(ponto, rota[i+1])
        else:
            ultimo_para_inicial = distancia_entre_pontos(ponto_inicial, rota[-1])
    return inicial_para_segundo + ultimo_para_inicial + dist_rota
    
def avaliar_populacao(populacao, ponto_inicial):
    aptidoes = []

    for individuo in populacao:
        aptidao_individuo = avaliar_individuo(ponto_inicial, individuo)
        aptidoes.append(aptidao_individuo)
    return aptidoes

def torneio(dados):
    populacao = dados["populacao"]
    aptidoes = dados["aptidoes"]
    i_pais = []
    n_individuos = len(populacao)

    for _ in range(n_individuos):
        i_pai1 = random.randint(0, n_individuos - 1)
        i_pai2 = random.randint(0, n_individuos - 1)
        if aptidoes[i_pai2] < aptidoes[i_pai1]:
            i_pais.append(i_pai2)
        else: i_pais.append(i_pai1)
    return i_pais

def crossover(i_pais, dados, taxa_crossover):
    
    def pmx(p1, p2):
        corte = random.randint(1, len(p1) - 2)

        nova_permutacao = p1.copy()
        nova_permutacao = nova_permutacao[:corte]

        for item in p2:
            if item not in nova_permutacao:
                nova_permutacao.append(item)    
        return nova_permutacao

    n_pais = len(i_pais)
    filhos = []
    n_filhos = 0

    while n_filhos < n_pais:
        pai1 = dados["populacao"][i_pais[random.randint(0, n_pais - 1)]]
        pai2 = dados["populacao"][i_pais[random.randint(0, n_pais - 1)]]

        if random.random() <= taxa_crossover:
            filho = pmx(pai1, pai2)
            filho2 = pmx(pai2, pai1)
            filhos.append(filho)
            filhos.append(filho2)

            n_filhos += 2

    if n_filhos > n_pais:
        filhos.pop()

    return filhos 

def mutacao(filhos, taxa_mutacao):
    for filho in filhos:
        for i, _ in enumerate(filho):
            if random.random() <= taxa_mutacao:
                if filho[i] != filho[-1]:
                    filho[i], filho[i+1] = filho[i+1], filho[i]
                else: filho[i], filho[0] = filho[0], filho[i]
    

def selecionar_sobreviventes(dados, filhos, aptidoes_filhos,elitismo : bool):
    
    nova_populacao = []
    novas_aptidoes = []

    if elitismo == True:
        index_melhor_pai = dados["aptidoes"].index(min(dados["aptidoes"]))
        melhor_pai = dados["populacao"][index_melhor_pai]
        aptidao_melhor_pai = dados["aptidoes"][index_melhor_pai]

        index_pior_filho = aptidoes_filhos.index(max(aptidoes_filhos))
        filhos.pop(index_pior_filho)
        aptidoes_filhos.pop(index_pior_filho)

        nova_populacao = filhos + [melhor_pai]
        novas_aptidoes = aptidoes_filhos + [aptidao_melhor_pai]
        return nova_populacao, novas_aptidoes
    else: 
        nova_populacao = filhos
        return nova_populacao, aptidoes_filhos

def algoritmo_genetico(tam_populacao, taxa_crossover, taxa_mutacao, n_geracoes, elitismo, arquivo):

    ponto_inicial, pontos_entrega = ler_entrada(arquivo)
    populacao = gerar_populacao(pontos_entrega, tam_populacao)
    aptidoes = avaliar_populacao(populacao, ponto_inicial)
    dados = { "populacao": populacao, "aptidoes": aptidoes }

    melhor_individuo = (0, [])

    for _ in range(n_geracoes):
        pais_selecionados = torneio(dados)
        filhos = crossover(pais_selecionados, dados, taxa_crossover)
        mutacao(filhos, taxa_mutacao)
        aptidoes_filhos = avaliar_populacao(filhos, ponto_inicial)
        dados["populacao"], dados["aptidoes"] = selecionar_sobreviventes(dados, filhos, aptidoes_filhos, elitismo)     
    
    index_melhor_individuo = dados["aptidoes"].index(min(dados["aptidoes"]))
    melhor_individuo = dados["populacao"][index_melhor_individuo]

    return avaliar_individuo(ponto_inicial, melhor_individuo), melhor_individuo
    
if __name__ == "__main__":
    print('iniciou')
    start = time.perf_counter()
    melhor_distancia, melhor_individuo = algoritmo_genetico(100, 0.8, 0.05, 1000, False, "entrada.txt")
    print(melhor_distancia)
    print(melhor_individuo)
    end = time.perf_counter()
    print(f"Solução encontrada em {end - start} segundos")
