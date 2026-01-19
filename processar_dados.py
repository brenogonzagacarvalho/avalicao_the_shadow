import pandas as pd
import json
from collections import Counter
import re

def carregar_dados():
    """Carrega os dados do arquivo Excel de avaliações"""
    try:
        df = pd.read_excel('steam_reviews_the_vale_shadow_of_the_crown.xlsx')
        return df
    except FileNotFoundError:
        print("Arquivo não encontrado. Tentando arquivo CSV...")
        df = pd.read_csv('The Vale - Shadow of the Crown  - reviews - Sheet1.csv')
        return df

def calcular_estatisticas(df):
    """Calcula estatísticas gerais das avaliações"""
    stats = {
        'totalReviews': int(len(df)),
        'positiveReviews': int(df['Recomendado'].sum()) if 'Recomendado' in df.columns else 0,
        'negativeReviews': int(len(df) - (df['Recomendado'].sum() if 'Recomendado' in df.columns else 0)),
        'avgPlaytime': float(round(df['Horas Jogadas'].mean() / 60, 2)) if 'Horas Jogadas' in df.columns else 0,
        'languages': {k: int(v) for k, v in df['Idioma'].value_counts().to_dict().items()} if 'Idioma' in df.columns else {}
    }
    return stats

def analisar_tempo_jogado(df):
    """Analisa a distribuição de tempo jogado"""
    if 'Horas Jogadas' not in df.columns:
        return {}
    
    horas = df['Horas Jogadas'] / 60
    distribuicao = {
        '0-2h': len(horas[horas <= 2]),
        '2-5h': len(horas[(horas > 2) & (horas <= 5)]),
        '5-10h': len(horas[(horas > 5) & (horas <= 10)]),
        '10+h': len(horas[horas > 10])
    }
    return distribuicao

def extrair_conceitos(df):
    """Extrai conceitos relevantes das reviews usando palavras-chave"""
    if 'Review' not in df.columns:
        return []
    
    # Palavras-chave relacionadas ao jogo de áudio/acessibilidade
    keywords = {
        'acessibilidade': ['accessibility', 'accessible', 'acessibilidade', 'accesibilidad', 'blind', 'cego', 'visual'],
        'audio_espacial': ['spatial audio', 'sound design', 'áudio espacial', 'audio', 'som', 'sonido'],
        'narrativa': ['story', 'narrative', 'história', 'narrativa', 'historia', 'plot'],
        'imersao': ['immersive', 'immersion', 'imersivo', 'envolvente', 'inmersivo'],
        'combate': ['combat', 'fight', 'battle', 'combate', 'luta'],
        'exploracao': ['exploration', 'explore', 'exploração', 'explorar'],
        'gameplay': ['gameplay', 'mechanics', 'jogabilidade', 'mecânica'],
        'qualidade': ['quality', 'qualidade', 'calidad', 'excellent', 'excelente']
    }
    
    concept_counts = Counter()
    
    # Converte todas as reviews para lowercase para análise
    reviews_text = ' '.join(df['Review'].astype(str).str.lower())
    
    for concept, terms in keywords.items():
        count = sum(reviews_text.count(term.lower()) for term in terms)
        if count > 0:
            concept_counts[concept] = count
    
    # Retorna os conceitos ordenados por frequência
    concepts = [
        {'name': name.replace('_', ' ').title(), 'count': count}
        for name, count in concept_counts.most_common(10)
    ]
    
    return concepts

def analisar_opiniao_aspectos(df):
    """Analisa a opinião sobre aspectos específicos do jogo"""
    if 'Review' not in df.columns or 'Recomendado' not in df.columns:
        return {}
    
    aspectos = {
        'Qualidade do Áudio': ['audio', 'sound', 'áudio', 'som', 'sonido'],
        'História': ['story', 'narrative', 'história', 'narrativa', 'historia'],
        'Jogabilidade': ['gameplay', 'mechanics', 'jogabilidade', 'mecânica'],
        'Acessibilidade': ['accessibility', 'accessible', 'acessibilidade', 'accesibilidad'],
        'Duração': ['length', 'duration', 'short', 'long', 'duração', 'curto'],
        'Replay Value': ['replay', 'replayability', 'rejogabilidade']
    }
    
    resultados = {}
    
    for aspecto, keywords in aspectos.items():
        # Filtra reviews que mencionam o aspecto
        mentions = df[df['Review'].str.lower().str.contains('|'.join(keywords), na=False)]
        
        if len(mentions) > 0:
            # Calcula a porcentagem de reviews positivas que mencionam esse aspecto
            positive_mentions = mentions[mentions['Recomendado'] == True]
            score = int((len(positive_mentions) / len(mentions)) * 100)
            resultados[aspecto] = score
        else:
            resultados[aspecto] = 50  # Valor neutro se não houver menções
    
    return resultados

def gerar_json_dados(df):
    """Gera um arquivo JSON com todos os dados processados"""
    dados = {
        'estatisticas': calcular_estatisticas(df),
        'playtimeDistribution': analisar_tempo_jogado(df),
        'concepts': extrair_conceitos(df),
        'opinions': analisar_opiniao_aspectos(df)
    }
    
    with open('dados_processados.json', 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
    
    print("Dados processados salvos em 'dados_processados.json'")
    return dados

if __name__ == '__main__':
    print("Carregando dados...")
    df = carregar_dados()
    print(f"Total de reviews carregadas: {len(df)}")
    
    print("\nProcessando dados...")
    dados = gerar_json_dados(df)
    
    print("\n=== ESTATÍSTICAS GERAIS ===")
    print(f"Total de Reviews: {dados['estatisticas']['totalReviews']}")
    print(f"Reviews Positivas: {dados['estatisticas']['positiveReviews']}")
    print(f"Reviews Negativas: {dados['estatisticas']['negativeReviews']}")
    print(f"Tempo Médio Jogado: {dados['estatisticas']['avgPlaytime']}h")
    
    print("\n=== CONCEITOS MAIS RELEVANTES ===")
    for conceito in dados['concepts'][:5]:
        print(f"- {conceito['name']}: {conceito['count']} menções")
    
    print("\n=== AVALIAÇÃO DE ASPECTOS ===")
    for aspecto, score in dados['opinions'].items():
        print(f"- {aspecto}: {score}%")
    
    print("\nProcessamento concluído! Abra 'relatorio_avaliacoes.html' no navegador.")
