import random
import math
import numpy as np
import os

class Individuo:
    def __init__(self, sequencia, aptidao = 0) -> None:
        self.sequencia = sequencia
        self.aptidao = aptidao

class MonteCarlo:
    def __init__(self, ponto_reposicao, tamanho_lote, media_demanda=50, desvio_demanda=10, media_lead=5, desvio_lead=1, estoque_inicial=15):
        
        if ponto_reposicao > 10 * media_demanda:
            print('Ponto de reposição superou expectativas: ', ponto_reposicao)
            self.ponto_reposicao = 10 * media_demanda
        else:
            print('Ponto de reposição: ', ponto_reposicao)
            self.ponto_reposicao = ponto_reposicao

        if tamanho_lote > 10 * media_demanda:
            print('Tam lote superou expectativas: ', tamanho_lote)
            self.tamanho_lote = 10 * media_demanda
        else:
            print('Tam lote: ', tamanho_lote)
            self.tamanho_lote = tamanho_lote

        self.media_demanda = media_demanda
        self.desvio_demanda = desvio_demanda
        self.media_lead = media_lead
        self.desvio_lead = desvio_lead
        self.estoque = estoque_inicial
    
    _estoque_dias = []
    _dias_ate_entrega = None
    _tam_prox_lote = 0

    _demanda_atendida = 0
    _total_demanda = 0
    _media_estoque = 0

    def realizar_previsao(self, n_dias=30):
        for _ in range(n_dias):
            if self._dias_ate_entrega == 0:
                self._dias_ate_entrega = None
                self.receber_entrega()
            self._estoque_dias.append(self.estoque)
            self.retirar_do_estoque(int(np.random.normal(self.media_demanda, self.desvio_demanda)))
            if self.estoque <= self.ponto_reposicao and type(self._dias_ate_entrega) == None:
                self.realiza_compra()
            if type(self._dias_ate_entrega) == int:
                self._dias_ate_entrega -= 1
        media_estoque = np.mean(self._estoque_dias)
        return self._demanda_atendida, self._total_demanda, self.media_demanda, media_estoque

    def retirar_do_estoque(self, quantidade):
        estoque_antes = self.estoque
        self.estoque -= quantidade
        self._total_demanda += quantidade
        self._demanda_atendida += quantidade
        if self.estoque < 0:
            self._demanda_atendida -= self.estoque + estoque_antes
            self.estoque = 0

    def realiza_compra(self):
        self._dias_ate_entrega = int(np.random.normal(self.media_lead, self.desvio_lead))

    def receber_entrega(self):
        print(f'Tamanho do lote a ser adicionado: {self.tamanho_lote}')
        self.estoque += self.tamanho_lote


# gera a população (100 indivíduos que são 22 bits)

def pedacos_individuo(individuo: Individuo):
    ponto_reposicao = int(''.join(map(str, individuo.sequencia[:10])), 2)
    tamanho_lote = int(''.join(map(str, individuo.sequencia[10:])), 2)
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
def avaliar_individuos(populacao, a = 0.5, b = 0.5):
    for individuo in populacao:
        ponto_reposicao, tamanho_lote = pedacos_individuo(individuo)
        mt = MonteCarlo(tamanho_lote=tamanho_lote, ponto_reposicao=ponto_reposicao, estoque_inicial=15)
        demanda_atendida, total_demanda, media_demanda, media_estoque = mt.realizar_previsao()
        individuo.aptidao = func_objetivo(
                    a=a, 
                    b=b, 
                    demanda_atendida=demanda_atendida, 
                    demanda_total=total_demanda, 
                    media_estoque=media_estoque, 
                    media_demanda=media_demanda
                )
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
    print(len(nova_pop))
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

def alg_gen(tam_populacao, n_geracoes, tam_cromossomo, taxa_mutacao):
    populacao = gerar_populacao(tam_populacao, tam_cromossomo)
    avaliar_individuos(populacao)

    for i in range(n_geracoes):
        # os.system('cls' if os.name == 'nt' else 'clear')
        print(f'Calculando geração: {i}', )
        pais = selecao_por_torneio(populacao, len(populacao))
        filhos = gerar_filhos(pais, tam_populacao)
        mutacao(filhos, taxa_mutacao)
        avaliar_individuos(filhos)
        populacao = filhos
        melhor_individuo = max(populacao, key=sort_function)
    
    melhor_individuo = max(populacao, key=sort_function)
    return melhor_individuo

if __name__ == "__main__":
    print('Irei rodar o algoritmo genético com os determinados parâmetros: ')
    print('Tamanho da população: 100')
    print('Número de gerações: 2')
    print('Tamanho do Cromossomo: 22')
    print('Taxa de mutação: 10%')
    resp = input('Prosseguir? Y/n')
    if resp == 'y' or resp == 'Y':
        ind = alg_gen(3, 10, 22, 0.1)
        ponto_reposicao, tamanho_lote = pedacos_individuo(ind)
        print(f'O melhor indivíduo diz que o ponto de reposição deve ser: {ponto_reposicao}')
        print(f'O melhor indivíduo diz que o tamanho do lote deve ser: {tamanho_lote}')
        print(f'Sua aptidão: {ind.aptidao}')