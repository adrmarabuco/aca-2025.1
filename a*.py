# %%
# %pip install pandas networkx matplotlib

# %%
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from time import sleep
import logging
from datetime import datetime

# Setup logging to file with timestamp
log_filename = datetime.now().strftime("%Y-%m-%dT%H-%M-%S.log")
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    handlers=[logging.FileHandler(log_filename), logging.StreamHandler()]
)

# %%
dfd = pd.read_excel('metro_distancias_diretas.xlsx', sheet_name='metro_tempos_diretos', index_col=0)
dfr = pd.read_excel('metro_distancias_reais.xlsx', sheet_name='metro_tempos_reais', index_col=0)
linhas = pd.read_csv('conexoes_metro.csv', index_col=0)

# %%
GD = nx.from_pandas_adjacency(dfd) 
GR = nx.from_pandas_adjacency(dfr)

# %%
# criar classe com o grafo para o problema de busca
class Mapa:
    def __init__(self, estacoes, distancias, conexoes, linhas):
        self.estacoes = estacoes
        self.distancias = distancias
        self.conexoes = conexoes
        self.linhas = linhas
        self.tempo_baldeacao = 3
        self.volta = False
        

    def backtrack(self, memoria, estacao):
        for i in memoria[-1]:
            print(i['fim'], estacao, i['custo_historico'])
            if i['fim'] == estacao:
                return round(i['custo_historico'],2)
        
    def t(self, inicio, fim):
        return round(self.conexoes.get_edge_data(inicio, fim)['weight'],2) 

    def g(self, inicio, fim, memoria, numero, baldeacao):
        if len(memoria) == 0:
            return round(self.conexoes.get_edge_data(inicio, fim)['weight'], 2)
        if self.volta:
            return round(self.conexoes.get_edge_data(inicio, fim)['weight'] + self.backtrack(memoria, fim) + (self.tempo_baldeacao * baldeacao),2)
        return round(self.conexoes.get_edge_data(inicio, fim)['weight'] + memoria[-1][0]["custo_historico"] + (self.tempo_baldeacao * baldeacao),2)
    
    def h(self, inicio, fim):
        if inicio == fim:
            return 0
        return round(self.distancias.get_edge_data(inicio, fim)['weight'],2)

    def f(self, h, g):
        return round(h + g, 2)
   
    def get_fronteira(self, estacao):
        return self.conexoes.neighbors(estacao)
    
    def a_star(self, origem, destino):

        self.origem = origem
        logging.info(f"Origem: {origem}")
        self.destino = destino
        logging.info(f"Destino: {destino}")

        self.estacao = self.origem
        self.memoria = []
                
        self.numero = 0
        h0 = self.h(self.origem, self.destino)
        logging.info(f"h({self.origem}, {self.destino}): {h0}")   
        logging.info(f"*" * 50)
            
            
        while self.estacao != self.destino and self.numero <= 10:        

            logging.info(f"Rodada: {self.numero}")
            logging.info(f"Estação atual: {self.estacao}")

            # fronteira
            fronteira = self.get_fronteira(self.estacao)

            self.candidatos = self.get_fronteira(self.estacao)
            logging.info(f"Candidatos: {list(self.candidatos)}")


            self.rodada = []
            for i in fronteira:
                
                if len(self.memoria) != 0:
                    # logging.info(self.memoria[-1][0]["linha"])
                    # logging.info(self.linhas.at[self.estacao, i])
                    self.baldeacao = self.memoria[-1][0]["linha_fim"] != self.linhas.at[self.estacao, i]
                else:
                    self.baldeacao = False

                # Cálculo custo
                # logging.info(f"{self.estacao}, {i}, {self.memoria}, {self.numero}, {self.baldeacao}")
                g = self.g(self.estacao, i, self.memoria, self.numero, self.baldeacao)
                t = self.t(self.estacao, i)
                h = self.h(i, self.destino)
                f = self.f(h, g)

                candidato = {
                    "inicio": self.estacao,
                    "fim": i,
                    "linha_inicio": self.memoria[-1][0]["linha_fim"] if len(self.memoria) > 0 else None,
                    "linha_fim": self.linhas.at[self.estacao, i],
                    "baldeacao": self.baldeacao,
                    "custo_historico": g,
                    "custo_trecho": t,
                    "custo_estimado": h,
                    "custo_total": f
                }
                
                self.rodada.append(candidato)
                log_str = f"Candidato {i}:\n"
                for k, v in candidato.items():
                    log_str += f"  {k:<15}: {v}\n"
                logging.info(log_str)
            
            # ordena fronteira
            self.rodada.sort(key=lambda x: x["custo_total"])

            # seleciona o melhor destino                
            self.estacao = self.rodada[0]["fim"]

            ## verifica se vai voltar para inicio da rodada anterior, e se for altera o custo histórico da estação de origem
            if len(self.memoria) > 0 and self.rodada[0]["fim"] == self.memoria[-1][0]["inicio"]:
                self.volta = True
                # logging.info("Voltando para inicio da rodada anterior")
                # logging.info(f'antes: {self.memoria[-1][0]["custo_historico"]}')
                self.memoria[-1][0]["custo_historico"] += (2 * self.rodada[0]["custo_trecho"])
                # logging.info(f'agora: {self.memoria[-1][0]["custo_historico"]}')
                # logging.info(f'antes: {self.memoria[-1][0]["custo_total"]}')
                self.memoria[-1][0]["custo_total"] += (2 * self.rodada[0]["custo_trecho"])
                # logging.info(f'agora: {self.memoria[-1][0]["custo_total"]}')
            else:
                # caso contrário salva nova rodada na memoria 
                self.volta = False
                self.memoria.append(self.rodada)
                
            resultado = {i+1: r['fim'] for i, r in enumerate(self.rodada)}
            logging.info(f"Ordem: {resultado}")
            self.numero += 1
            
            logging.info(f"Próxima estação: {self.estacao}")
            
            logging.info(f"*" * 50)
            logging.info(f" " )
            with open('tmp.json', 'w') as f:
                import json
                f.write(f"{json.dumps(self.memoria)}\n")
            
            sleep(2)

        trajeto = []
        trajeto.append((self.origem, self.memoria[0][0]['linha_fim'], 0))   
        for r in self.memoria:
            trajeto.append((r[0]['fim'],r[0]['linha_fim'], r[0]['custo_historico']))
        # trajeto.append((self.destino, self.memoria[-1][0]['linha'], self.memoria[-1][0]['custo_historico']))
        
        path = ' -> '.join([p[0]+' ('+p[1]+'): ' + str(p[2]) + ' min' for p in trajeto])
        # tempo = ' '.join([str(p[2]) for p in trajeto])

        logging.info(f"Trajeto: {path}")
        logging.info(f" ")

        # logging.info(f"Tempo: {tempo}")
        
        for i, p in enumerate(trajeto):
            logging.info(f"{i+1}: {p}")
        
        logging.info(f" ")
        logging.info(f"Custo total: {self.memoria[-1][0]['custo_total']} minutos")

        return self.memoria


# %%
metro = Mapa(GD.nodes, GD, GR, linhas)

if __name__ == "__main__":
    ei = str(input("Estação de origem: ")).upper()
    ef = str(input("Estação de destino: ")).upper()
    arvore = metro.a_star(ei, ef)