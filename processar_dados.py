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

def gerar_ngrams(textos, n=2, top_k=10):
    """Gera N-Grams mais frequentes (bigramas, trigramas)"""
    ngrams_list = []
    
    # Stopwords básicas para limpeza (hardcoded para evitar dependências externas)
    stopwords = {'a', 'o', 'e', 'de', 'do', 'da', 'em', 'um', 'uma', 'que', 'é', 'com', 'não', 'os', 'as', 'para', 'se', 'na', 'no', 'por', 'mais', 'foi', 'ao', 'dos', 'das', 'seu', 'sua', 'ou', 'ser', 'quando', 'muito', 'nos', 'já', 'está', 'eu', 'também', 'só', 'pelo', 'pela', 'até', 'isso', 'ela', 'entre', 'era', 'depois', 'sem', 'mesmo', 'aos', 'ter', 'seus', 'quem', 'nas', 'me', 'esse', 'eles', 'estão', 'você', 'tinha', 'foram', 'essa', 'num', 'nem', 'suas', 'meu', 'às', 'minha', 'têm', 'numa', 'pelos', 'elas', 'havia', 'seja', 'qual', 'será', 'nós', 'tenho', 'lhe', 'deles', 'essas', 'esses', 'pelas', 'este', 'fosse', 'dele', 'tu', 'te', 'vocês', 'vos', 'lhes', 'meus', 'minhas', 'teu', 'tua', 'teus', 'tuas', 'nosso', 'nossa', 'nossos', 'nossas', 'dela', 'delas', 'esta', 'estes', 'estas', 'aquele', 'aquela', 'aqueles', 'aquelas', 'isto', 'aquilo', 'estou', 'está', 'estamos', 'estão', 'estive', 'esteve', 'estivemos', 'estiveram', 'estava', 'estávamos', 'estavam', 'estivera', 'estivéramos', 'esteja', 'ejamos', 'estejam', 'estivesse', 'estivéssemos', 'estivessem', 'estiver', 'estivermos', 'estiverem', 'hei', 'há', 'havemos', 'hão', 'houve', 'houvemos', 'houveram', 'houvera', 'houvéramos', 'haja', 'hajamos', 'hajam', 'houvesse', 'houvéssemos', 'houvessem', 'houver', 'houvermos', 'houverem', 'houverei', 'houverá', 'houveremos', 'houverão', 'houveria', 'houveríamos', 'houveriam', 'sou', 'somos', 'são', 'era', 'éramos', 'eram', 'fui', 'foi', 'fomos', 'foram', 'fora', 'foramos', 'seja', 'sejamos', 'sejam', 'fosse', 'fôssemos', 'fossem', 'for', 'formos', 'forem', 'serei', 'será', 'seremos', 'serão', 'seria', 'seríamos', 'seriam', 'tenho', 'tem', 'temos', 'tém', 'tinha', 'tínhamos', 'tinham', 'tive', 'teve', 'tivemos', 'tiveram', 'tivera', 'tivéramos', 'tenha', 'tenhamos', 'tenham', 'tivesse', 'tivéssemos', 'tivessem', 'tiver', 'tivermos', 'tiverem', 'terei', 'terá', 'teremos', 'terão', 'teria', 'teríamos', 'teriam', 'the', 'and', 'of', 'to', 'a', 'in', 'is', 'it', 'you', 'that', 'for', 'on', 'with', 'as', 'was', 'are', 'this', 'but', 'be', 'have', 'not', 'an', 'at', 'or', 'if', 'from', 'my', 'all', 'so', 'me', 'by', 'one', 'can', 'just', 'like', 'about', 'very', 'out', 'what', 'game'}

    for texto in textos:
        if not isinstance(texto, str): continue
        # Limpeza básica
        palavras = re.findall(r'\b[a-z]{3,}\b', texto.lower())
        palavras = [p for p in palavras if p not in stopwords]
        
        # Gerar n-grams
        for i in range(len(palavras) - n + 1):
            ngram = ' '.join(palavras[i:i+n])
            ngrams_list.append(ngram)
            
    counts = Counter(ngrams_list)
    return [{'text': gram, 'value': count} for gram, count in counts.most_common(top_k)]

def analisar_coocorrencia(df, keywords):
    """
    Analisa quais conceitos aparecem juntos nas mesmas reviews.
    Retorna uma matriz de adjacência (lista de arestas para grafo).
    """
    if 'Review' not in df.columns: return []
    
    coocorrencias = Counter()
    
    for review in df['Review'].astype(str).str.lower():
        conceitos_presentes = []
        for concept, terms in keywords.items():
            if any(term in review for term in terms):
                conceitos_presentes.append(concept)
        
        # Se houver mais de um conceito, gera pares
        if len(conceitos_presentes) > 1:
            # Ordena para garantir que (A, B) seja igual a (B, A)
            conceitos_presentes.sort()
            for i in range(len(conceitos_presentes)):
                for j in range(i + 1, len(conceitos_presentes)):
                    pair = f"{conceitos_presentes[i]}|{conceitos_presentes[j]}"
                    coocorrencias[pair] += 1
                    
    # Formata para visualização de grafo
    edges = []
    for pair, weight in coocorrencias.most_common(15):
        source, target = pair.split('|')
        edges.append({
            'source': source.replace('_', ' ').title(),
            'target': target.replace('_', ' ').title(),
            'weight': weight
        })
        
    return edges

def gerar_json_dados(df):
    """Gera um arquivo JSON com todos os dados processados"""
    
    # Palavras-chave centralizadas
    keywords = {
        'acessibilidade': ['accessibility', 'accessible', 'acessibilidade', 'accesibilidad', 'blind', 'cego', 'visual'],
        'audio_espacial': ['spatial audio', 'sound design', 'áudio espacial', 'audio', 'som', 'sonido', 'binaural', 'hearing'],
        'narrativa': ['story', 'narrative', 'história', 'narrativa', 'historia', 'plot', 'writing'],
        'imersao': ['immersive', 'immersion', 'imersivo', 'envolvente', 'inmersivo', 'atmosphere'],
        'combate': ['combat', 'fight', 'battle', 'combate', 'luta', 'fighting'],
        'exploracao': ['exploration', 'explore', 'exploração', 'explorar', 'world', 'walking'],
        'gameplay': ['gameplay', 'mechanics', 'jogabilidade', 'mecânica', 'play'],
        'qualidade': ['quality', 'qualidade', 'calidad', 'excellent', 'excelente', 'great', 'good', 'best']
    }

    raw_reviews = df['Review'].astype(str).tolist() if 'Review' in df.columns else []

    dados = {
        'estatisticas': calcular_estatisticas(df),
        'playtimeDistribution': analisar_tempo_jogado(df),
        'concepts': extrair_conceitos(df), # Reutiliza a lógica existente mas poderia ser atualizada para usar 'keywords' local se desejado
        'opinions': analisar_opiniao_aspectos(df),
        # Novos campos de análise aprofundada
        'ngramas': {
            'bigramas': gerar_ngrams(raw_reviews, n=2, top_k=15),
            'trigramas': gerar_ngrams(raw_reviews, n=3, top_k=10)
        },
        'coocorrencia': analisar_coocorrencia(df, keywords)
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
    
    print("\nProcessamento concluído! Abra 'index.html' no navegador.")
