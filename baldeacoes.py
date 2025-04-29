# Reimportar bibliotecas após reinício
import pandas as pd

# Reconstruir os dados manuais
data = [
    ("E1", "E2", "vermelha"),
    ("E2", "E3", "vermelha"),
    ("E3", "E4", "vermelha"),
    ("E4", "E14", "vermelha"),
    ("E11", "E9", "amarela"),
    ("E9", "E8", "amarela"),
    ("E8", "E4", "amarela"),
    ("E4", "E5", "amarela"),
    ("E6", "E7", "azul"),
    ("E7", "E3", "azul"),
    ("E3", "E8", "azul"),
    ("E8", "E10", "azul"),
    ("E10", "E12", "azul"),
    ("E7", "E2", "verde"),    
    ("E10", "E13", "verde"),
    ("E2", "E9", "verde"),
    ("E9", "E10", "verde"),
    ("E10", "E13", "verde")
]

df = pd.DataFrame(data, columns=["origem", "destino", "cor"])

lista_ordenada = ["E1", "E2", "E3", "E4", "E5", "E6", "E7", "E8", "E9", "E10", "E11", "E12", "E13", "E14"]

# Criar a matriz de adjacência
stations = sorted(set(df['origem']).union(df['destino']))
adj_matrix = pd.DataFrame('-', index=stations, columns=stations)

# Preencher a matriz
for _, row in df.iterrows():
    adj_matrix.loc[row['origem'], row['destino']] = row['cor']
    adj_matrix.loc[row['destino'], row['origem']] = row['cor']  # grafo não direcionado

adj_matrix = adj_matrix.reindex(lista_ordenada, axis=0)
adj_matrix = adj_matrix.reindex(lista_ordenada, axis=1)

adj_matrix_path = "conexoes_metro.csv"
adj_matrix.to_csv(adj_matrix_path)
