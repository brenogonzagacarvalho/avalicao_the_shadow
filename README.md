# Análise de Sentimento e Interações: The Vale - Shadow of the Crown

Este projeto realiza uma análise técnica e semântica profunda das avaliações do jogo **"The Vale: Shadow of the Crown"**, um RPG de áudio acessível. O objetivo é compreender como jogadores (videntes e deficientes visuais) interagem com o jogo e como a ausência de feedback visual influencia a percepção de mecânicas e narrativa.

## 🚀 Funcionalidades

*   **Coleta Multi-Plataforma**: Consolidação de dados de reviews da Steam, Metacritic, Xbox Store, PlayStation Store, Nintendo eShop e Epic Games Store.
*   **Processamento de Linguagem Natural (PLN)**:
    *   Limpeza e normalização de texto.
    *   Análise de N-Gramas (Bigramas e Trigramas) para identificar expressões recorrentes.
    *   Matriz de Co-ocorrência para mapear a rede de assuntos conectados.
    *   Análise de Sentimentos baseada em aspectos (Combate, Narrativa, Acessibilidade).
*   **Dashboard Interativo**: Interface Web (`index.html`) com gráficos dinâmicos de distribuição de jogadores, rede de conceitos e análise de sentimentos.
*   **Exportação para Gephi**: Ferramenta para gerar grafos complexos de conexões semânticas.

## 📂 Estrutura do Projeto

*   `processar_dados.py`: Script principal de NLP. Processa o CSV/Excel de reviews, gera estatísticas e extrai n-gramas. Geia `dados_processados.json`.
*   `coletar_multiplataforma.py`: Simula a coleta e consolida dados de todas as plataformas. Consome `dados_processados.json` e gera `dados_consolidados.json`.
*   `exportar_gephi.py`: Gera arquivos `.csv` (Nodes e Edges) para visualização de grafos de rede no software Gephi.
*   `index.html`: Dashboard interativo para visualização dos resultados no navegador.
*   `RELATORIO.md`: Relatório técnico científico detalhado com metodologia, diagramas e conclusões da análise.

## 🛠️ Como Executar

### Pré-requisitos
*   Python 3.8+
*   Bibliotecas Python: `pandas`, `numpy`, `beautifulsoup4`, `requests`

### Instalação das Dependências
```bash
pip install pandas numpy beautifulsoup4 requests
```

### Executando a Pipeline de Dados
1.  **Processar Reviews da Steam e NLP**:
    ```bash
    python processar_dados.py
    ```
2.  **Consolidar Dados Multi-Plataforma**:
    ```bash
    python coletar_multiplataforma.py
    ```
3.  **Gerar Arquivos para Gephi (Opcional)**:
    ```bash
    python exportar_gephi.py
    ```

### Visualizando o Dashboard
Basta abrir o arquivo `index.html` em qualquer navegador moderno. O dashboard carregará automaticamente os dados de `dados_consolidados.json`.

### Deploy
O projeto está configurado para deploy na **Vercel**:
```bash
npx vercel deploy --prod
```

## 📊 Relatório Final
Para uma leitura detalhada da metodologia científica, taxonomia de usuários e conclusões, consulte o arquivo [RELATORIO.md](./RELATORIO.md).
