import pandas as pd
import json
import re
from collections import Counter
import itertools
import os

def exportar_para_gephi(caminho_csv_input='The Vale - Shadow of the Crown  - reviews - Sheet1.csv'):
    print(f"Lendo dados de {caminho_csv_input}...")
    
    # Carregar dados
    if not os.path.exists(caminho_csv_input):
        print(f"Erro: Arquivo {caminho_csv_input} não encontrado.")
        return

    df = pd.read_csv(caminho_csv_input)
    
    if 'Review' not in df.columns:
        print("Erro: Coluna 'Review' não encontrada no CSV.")
        return

    # Stopwords para limpeza
    stopwords = {'a', 'o', 'e', 'de', 'do', 'da', 'em', 'um', 'uma', 'que', 'é', 'com', 'não', 'os', 'as', 'para', 'se', 'na', 'no', 'por', 'mais', 'foi', 'ao', 'dos', 'das', 'seu', 'sua', 'ou', 'ser', 'quando', 'muito', 'nos', 'já', 'está', 'eu', 'também', 'só', 'pelo', 'pela', 'até', 'isso', 'ela', 'entre', 'era', 'depois', 'sem', 'mesmo', 'aos', 'ter', 'seus', 'quem', 'nas', 'me', 'esse', 'eles', 'estão', 'você', 'tinha', 'foram', 'essa', 'num', 'nem', 'suas', 'meu', 'às', 'minha', 'têm', 'numa', 'pelos', 'elas', 'havia', 'seja', 'qual', 'será', 'nós', 'tenho', 'lhe', 'deles', 'essas', 'esses', 'pelas', 'este', 'fosse', 'dele', 'tu', 'te', 'vocês', 'vos', 'lhes', 'meus', 'minhas', 'teu', 'tua', 'teus', 'tuas', 'nosso', 'nossa', 'nossos', 'nossas', 'dela', 'delas', 'esta', 'estes', 'estas', 'aquele', 'aquela', 'aqueles', 'aquelas', 'isto', 'aquilo', 'estou', 'está', 'estamos', 'estão', 'estive', 'esteve', 'estivemos', 'estiveram', 'estava', 'estávamos', 'estavam', 'estivera', 'estivéramos', 'esteja', 'ejamos', 'estejam', 'estivesse', 'estivéssemos', 'estivessem', 'estiver', 'estivermos', 'estiverem', 'hei', 'há', 'havemos', 'hão', 'houve', 'houvemos', 'houveram', 'houvera', 'houvéramos', 'haja', 'hajamos', 'hajam', 'houvesse', 'houvéssemos', 'houvessem', 'houver', 'houvermos', 'houverem', 'houverei', 'houverá', 'houveremos', 'houverão', 'houveria', 'houveríamos', 'houveriam', 'sou', 'somos', 'são', 'era', 'éramos', 'eram', 'fui', 'foi', 'fomos', 'foram', 'fora', 'foramos', 'seja', 'sejamos', 'sejam', 'fosse', 'fôssemos', 'fossem', 'for', 'formos', 'forem', 'serei', 'será', 'seremos', 'serão', 'seria', 'seríamos', 'seriam', 'tenho', 'tem', 'temos', 'tém', 'tinha', 'tínhamos', 'tinham', 'tive', 'teve', 'tivemos', 'tiveram', 'tivera', 'tivéramos', 'tenha', 'tenhamos', 'tenham', 'tivesse', 'tivéssemos', 'tivessem', 'tiver', 'tivermos', 'tiverem', 'terei', 'terá', 'teremos', 'terão', 'teria', 'teríamos', 'teriam', 'the', 'and', 'of', 'to', 'a', 'in', 'is', 'it', 'you', 'that', 'for', 'on', 'with', 'as', 'was', 'are', 'this', 'but', 'be', 'have', 'not', 'an', 'at', 'or', 'if', 'from', 'my', 'all', 'so', 'me', 'by', 'one', 'can', 'just', 'like', 'about', 'very', 'out', 'what', 'game', 'play', 'really'}

    # Definir conceitos de interesse (nós principais)
    keywords_map = {
        'Acessibilidade': ['accessibility', 'accessible', 'acessibilidade', 'blind', 'cego', 'visual'],
        'Audio_Espacial': ['spatial audio', 'sound design', 'áudio espacial', 'audio', 'som', 'binaural', 'hearing', 'headphones'],
        'Narrativa': ['story', 'narrative', 'história', 'plot', 'writing', 'voice acting'],
        'Imersao': ['immersive', 'immersion', 'imersivo', 'atmosphere'],
        'Combate': ['combat', 'fight', 'battle', 'combate', 'luta'],
        'Exploracao': ['exploration', 'explore', 'exploração', 'world'],
        'Jogabilidade': ['gameplay', 'mechanics', 'jogabilidade', 'play'],
        'Acessivel': ['accessible', 'barrier-free', 'inclusive']
    }

    # 1. Preparar lista de palavras e co-ocorrências
    all_terms_freq = Counter()
    edges_counter = Counter()

    print("Processando reviews para extrair conexões...")
    for review in df['Review'].astype(str).str.lower():
        # Limpar texto
        words = re.findall(r'\b[a-z]{4,}\b', review)
        words = [w for w in words if w not in stopwords]
        
        # Identificar quais das nossas palavras-chave estão presentes
        present_concepts = set()
        for concept, terms in keywords_map.items():
            if any(term in review for term in terms):
                present_concepts.add(concept)
        
        # Também adicionar palavras frequentes que não são keywords mas são importantes
        # (Para o Gephi, focamos nos conceitos para não poluir o grafo)
        
        nodes_list = sorted(list(present_concepts))
        
        # Contar frequências dos nós
        for node in nodes_list:
            all_terms_freq[node] += 1
            
        # Calcular co-ocorrências (Edges)
        if len(nodes_list) >= 2:
            for pair in itertools.combinations(nodes_list, 2):
                edges_counter[tuple(sorted(pair))] += 1

    # 2. Gerar Arquivo de NÓS (Nodes)
    nodes_df = pd.DataFrame([
        {'Id': node, 'Label': node, 'Weight': freq}
        for node, freq in all_terms_freq.items()
    ])
    nodes_df.to_csv('gephi_nodes.csv', index=False)
    print(f"✓ Arquivo 'gephi_nodes.csv' gerado ({len(nodes_df)} nós)")

    # 3. Gerar Arquivo de ARESTAS (Edges)
    edges_list = []
    for (source, target), weight in edges_counter.items():
        edges_list.append({
            'Source': source,
            'Target': target,
            'Weight': weight,
            'Type': 'Undirected'
        })
    
    edges_df = pd.DataFrame(edges_list)
    edges_df.to_csv('gephi_edges.csv', index=False)
    print(f"✓ Arquivo 'gephi_edges.csv' gerado ({len(edges_df)} conexões)")

    print("\nInstruções para o Gephi:")
    print("1. Abra o Gephi e vá em 'Data Laboratory' > 'Import Spreadsheet'.")
    print("2. Importe 'gephi_nodes.csv' como 'Nodes table'.")
    print("3. Importe 'gephi_edges.csv' como 'Edges table' (certifique-se de marcar como 'Append to existing workspace').")
    print("4. Vá em 'Overview', use o layout 'ForceAtlas 2' e ajuste o tamanho dos nós pelo atributo 'Weight'.")

if __name__ == "__main__":
    exportar_para_gephi()
