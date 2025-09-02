# Projeto de Pipeline de Dados: Análise Geopolítica de Lançamentos da SpaceX

## 1. Objetivo do Projeto

Este projeto implementa um pipeline de dados completo para extrair, tratar e enriquecer informações sobre os lançamentos de foguetes da SpaceX. Os dados de lançamentos são cruzados com dados demográficos e geográficos de nações, obtidos da API REST Countries, com o objetivo de criar um dataset analítico para estudos sobre a distribuição global de atividades espaciais.

O pipeline é desenvolvido para ser executado no ambiente Databricks, utilizando PySpark para transformações e Delta Lake para persistência.

## 2. APIs Utilizadas

- **SpaceX API v4**: Fornece dados detalhados sobre lançamentos, foguetes e bases de lançamento (launchpads).
  - Endpoint de Lançamentos: `https://api.spacexdata.com/v4/launches`
  - Endpoint de Bases de Lançamento: `https://api.spacexdata.com/v4/launchpads`
- **REST Countries v3.1**: Fornece dados detalhados sobre países.
  - Endpoint de Países: `https://restcountries.com/v3.1/all`

## 3. Como Executar no Databricks

1.  **Configurar o Cluster**: Crie ou utilize um cluster Databricks (qualquer versão recente do Databricks Runtime é suficiente).
2.  **Clonar o Repositório**:
    - Na interface do Databricks, vá para a seção **Repos**.
    - Clique em **"Add Repo"**.
    - Cole a URL do seu repositório GitHub e confirme.
3.  **Abrir o Notebook**: Navegue até `notebooks/pipeline_launches.ipynb` e abra-o.
4.  **Executar o Pipeline**: Anexe o notebook ao seu cluster e execute todas as células em ordem (`Run All`). A primeira célula de código instalará as dependências listadas no `requirements.txt`.

## 4. Decisões de Arquitetura e Persistência

### Formato de Dados: Delta Lake

O dataset final é armazenado no formato **Delta Lake**. A escolha se baseia nos seguintes benefícios:
- **Transações ACID**: Garante a confiabilidade e a integridade dos dados, mesmo com falhas ou escritas concorrentes.
- **Performance**: O Delta Lake utiliza arquivos Parquet otimizados com compressão e indexing, acelerando as consultas.
- **Time Travel**: Permite versionar os dados e consultar snapshots anteriores, facilitando auditorias e a recuperação de dados.

### Estratégia de Particionamento

Os dados foram particionados por `launch_year` (ano do lançamento) e `launch_month` (mês do lançamento). Esta estratégia foi escolhida para:
- **Otimizar Consultas Temporais**: Análises que filtram por períodos específicos (ex: "todos os lançamentos de 2023") se tornam extremamente rápidas, pois o Spark lê apenas as partições relevantes, ignorando o resto dos dados.
- **Gerenciamento de Dados**: Facilita operações de manutenção, como apagar ou arquivar dados de um determinado período.