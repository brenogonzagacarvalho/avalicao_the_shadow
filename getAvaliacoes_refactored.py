import requests
import pandas as pd
import time
from typing import List, Dict, Any, Optional

# Passo 3: Função para obter reviews da Steam com retry
def get_steam_reviews(appid: int, cursor: str = '*', language: str = 'english', num_per_page: int = 100, max_retries: int = 5) -> Optional[Dict[str, Any]]:
    """
    Obtém uma página de reviews da Steam para um determinado appid.
    Implementa um mecanismo de retry simples para lidar com falhas de rede ou rate limiting.
    """
    url = f"https://store.steampowered.com/appreviews/{appid}?json=1"
    params = {
        # Alterado de 'recent' para 'all' para garantir a coleta completa
        'filter': 'all',
        'language': language,
        # Mantido o day_range máximo para não filtrar por data
        'day_range': '9223372036854775807',
        'review_type': 'all',
        'purchase_type': 'all',
        'num_per_page': num_per_page,
        'cursor': cursor
    }
    
    for attempt in range(max_retries):
        try:
            response = requests.get(url, params=params, timeout=15)
            
            if response.status_code == 200:
                return response.json()
            
            elif response.status_code == 429:
                # Rate limit: espera mais tempo
                wait_time = 2 ** attempt * 5  # Backoff exponencial: 5s, 10s, 20s, ...
                print(f"Rate limit (429) atingido. Tentando novamente em {wait_time} segundos...")
                time.sleep(wait_time)
                continue
            
            else:
                print(f"Erro ao acessar a API (Status {response.status_code}) na tentativa {attempt + 1}/{max_retries}.")
                if attempt < max_retries - 1:
                    time.sleep(2)
                
        except requests.exceptions.RequestException as e:
            print(f"Erro de conexão na tentativa {attempt + 1}/{max_retries}: {e}")
            if attempt < max_retries - 1:
                time.sleep(2)
                
    print(f"Falha ao obter reviews após {max_retries} tentativas.")
    return None

# Passo 4: Função para processar os dados e criar um DataFrame
def process_reviews(reviews_list: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Processa uma lista de dicionários de reviews e retorna um DataFrame.
    """
    data = []
    for review in reviews_list:
        data.append({
            'Horas Jogadas': review['author']['playtime_forever'],
            'Idioma': review['language'],
            'Review': review['review'],
            'Recomendado': review['voted_up'],
            'Votos Úteis': review['votes_up'],
            # Converte o timestamp Unix para datetime
            'Data da Review': pd.to_datetime(review['timestamp_created'], unit='s')
        })
    return pd.DataFrame(data)

# Passo 5: Função principal para coletar reviews em múltiplos idiomas
def scrape_reviews_multiple_languages(appid: int, languages: List[str], filename: str) -> Optional[pd.DataFrame]:
    """
    Coleta reviews para um appid em múltiplos idiomas e salva em um arquivo Excel.
    """
    all_dfs = []
    
    for language in languages:
        print(f"--- Coletando reviews em {language.upper()} (App ID: {appid}) ---")
        cursor = '*'
        reviews_count = 0
        
        while True:
            reviews_data = get_steam_reviews(appid, cursor=cursor, language=language)
            
            if reviews_data and 'reviews' in reviews_data:
                new_reviews = reviews_data['reviews']
                
                if not new_reviews:
                    print(f"Não há mais reviews para o idioma {language}.")
                    break
                
                # Processa o chunk de reviews e adiciona ao DataFrame
                df_chunk = process_reviews(new_reviews)
                all_dfs.append(df_chunk)
                reviews_count += len(new_reviews)
                
                # Obtém o novo cursor para a próxima página
                new_cursor = reviews_data.get('cursor')
                
                # A API da Steam pode retornar o mesmo cursor na última página.
                # Se o cursor não mudou ou se não houver mais cursor, encerra o loop.
                if new_cursor == cursor or not new_cursor:
                    print(f"Fim da coleta para o idioma {language}. Total de reviews: {reviews_count}")
                    break
                else:
                    cursor = new_cursor
                    print(f"Coletadas {reviews_count} reviews em {language}. Próximo cursor: {cursor[:20]}...")
            else:
                print(f"Não foi possível coletar mais reviews em {language}. Passando para o próximo idioma.")
                break
    
    if all_dfs:
        # Concatena todos os DataFrames de todos os idiomas
        final_df = pd.concat(all_dfs, ignore_index=True)
        
        # Remove duplicatas que podem ocorrer devido a falhas de cursor na API
        final_df.drop_duplicates(subset=['Review', 'Data da Review'], inplace=True)
        
        final_df.to_excel(filename, index=False)
        print(f"\nColeta concluída. Total de reviews salvas: {len(final_df)}")
        print(f"Arquivo salvo com sucesso: {filename}")
        return final_df
    else:
        print("\nNenhuma review foi coletada.")
        return None

# Passo 6: Configurações específicas para o jogo
# O jogo é "The Vale - Shadow of the Crown" (confirmado via pesquisa)
appid = 989790
languages = ['brazilian', 'english', 'spanish']
filename = 'steam_reviews_the_vale_shadow_of_the_crown.xlsx'

# Executar o scraper e salvar os dados
print(f"Iniciando coleta de reviews para o jogo com App ID {appid}...")
df = scrape_reviews_multiple_languages(appid, languages, filename)

# Exibir as primeiras linhas do DataFrame (opcional)
if df is not None:
    print("\nPrimeiras 5 linhas do DataFrame final:")
    print(df.head())
