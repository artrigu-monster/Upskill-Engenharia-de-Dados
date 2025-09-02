# Pipeline de Dados: Análise de Lançamentos da SpaceX

![Databricks](https://img.shields.io/badge/Databricks-FF3621?style=for-the-badge&logo=databricks&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![PySpark](https://img.shields.io/badge/PySpark-002D5E?style=for-the-badge&logo=apache-spark&logoColor=white)
![Delta Lake](https://img.shields.io/badge/Delta_Lake-00435A?style=for-the-badge&logo=linux&logoColor=white)

## 🎯 Objetivo do Projeto

Este projeto implementa um pipeline de dados ETL (Extração, Transformação e Carga) de ponta a ponta, desenvolvido como parte do programa **Upskill Tiller | Engenharia de Dados**.

O objetivo principal é consumir dados de duas APIs públicas distintas, enriquecê-los e modelá-los para criar um dataset analítico de alta qualidade. O caso de uso escolhido foi a **análise de lançamentos de foguetes da SpaceX**, enriquecendo os dados brutos com informações demográficas e geográficas dos países onde as bases de lançamento estão localizadas.

O resultado final é uma tabela Delta Lake limpa e otimizada, pronta para análises e visualizações.

## 🛠️ Tecnologias Utilizadas

* **Plataforma Cloud:** Databricks Community Edition
* **Linguagem:** Python
* **Processamento de Dados:** PySpark
* **Formato de Armazenamento:** Delta Lake (Tabela Gerenciada)
* **Bibliotecas Python:** `requests` para consumo de APIs e `pandas` para conversão de dados.
* **Versionamento:** Git & GitHub

## 📂 Estrutura do Repositório

```
/
├── README.md           # Documentação do projeto
├── requirements.txt    # Dependências Python
└── notebooks/
    └── pipeline_launches.ipynb # Notebook Databricks com o código do pipeline
```

## 📈 Etapas do Pipeline

O pipeline foi desenvolvido no notebook `pipeline_launches.ipynb` e segue as seguintes etapas:

1.  **Extração (E):**
    * Consumo de dados da **SpaceX API** para obter informações sobre lançamentos e bases de lançamento.
    * Consumo de dados da **REST Countries API** para obter dados demográficos e geográficos dos países.
    * Implementado tratamento de erros robusto para garantir a resiliência do pipeline contra falhas de API.

2.  **Transformação (T):**
    * Limpeza de dados nulos e seleção de colunas relevantes.
    * Conversão e padronização de tipos de dados (ex: `string` para `timestamp`).
    * **Enriquecimento de Dados:** Criação da coluna `country` (país) para as bases de lançamento, que não era fornecida pela API.
    * **Join Estratégico:** Cruzamento dos dados de lançamentos com os dados dos países para criar um dataset unificado.

3.  **Carga (L):**
    * **Relatório de Qualidade:** Geração de um arquivo `dq_report.json` com métricas essenciais sobre a qualidade dos dados finais.
    * **Persistência Otimizada:** Salvamento do DataFrame final como uma **tabela Delta gerenciada** no Databricks, particionada por ano e mês (`launch_year`, `launch_month`) para otimizar consultas temporais.

## 🚀 Como Executar no Databricks

1.  **Configurar o Cluster:** Crie ou utilize um cluster Databricks.
2.  **Clonar o Repositório:**
    * Na interface do Databricks, vá para a seção **Repos**.
    * Clique em **"Add Repo"** e cole a URL deste repositório.
3.  **Abrir o Notebook:** Navegue até `notebooks/pipeline_launches.ipynb` e anexe-o ao seu cluster.
4.  **Executar o Pipeline:** Execute todas as células em ordem (`Run All`). A primeira célula instalará as dependências listadas no `requirements.txt` e as demais executarão o pipeline completo.

## 📊 Demonstração dos Resultados

A última etapa do notebook realiza uma série de análises sobre a tabela final para demonstrar o seu valor. Os insights extraídos incluem:

#### 1. Crescimento Exponencial de Lançamentos da SpaceX
O gráfico de linhas mostra a evolução do número de lançamentos por ano, evidenciando o rápido crescimento das operações.

*(**SUGESTÃO:** Tire um print do gráfico de linhas gerado no Databricks e coloque a imagem aqui!)*
`![Gráfico de Lançamentos por Ano](caminho/para/sua/imagem.png)`

#### 2. Desempenho e Distribuição por País
A análise da taxa de sucesso revela a confiabilidade das operações em diferentes localidades.

*(**SUGESTÃO:** Tire um print da tabela de taxa de sucesso e coloque aqui!)*
`![Tabela de Taxa de Sucesso](caminho/para/sua/imagem2.png)`

#### 3. Bases de Lançamento Mais Ativas
O gráfico de barras mostra quais bases de lançamento são mais estratégicas para a SpaceX, concentrando a maior parte das operações.

---

*Projeto desenvolvido por Arthur Rodrigues.*