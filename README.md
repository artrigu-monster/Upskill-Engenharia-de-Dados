# Pipeline de Dados: Análise de Lançamentos da SpaceX

![Databricks](https://img.shields.io/badge/Databricks-FF3621?style=for-the-badge&logo=databricks&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![PySpark](https://img.shields.io/badge/PySpark-002D5E?style=for-the-badge&logo=apache-spark&logoColor=white)
![Delta Lake](https://img.shields.io/badge/Delta_Lake-00435A?style=for-the-badge&logo=linux&logoColor=white)

## 🎯 Objetivo do Projeto

Este projeto implementa um pipeline de dados ETL (Extração, Transformação e Carga) de ponta a ponta, desenvolvido como parte do programa **Upskill Tiller | Engenharia de Dados**.

O objetivo principal é consumir dados de duas APIs públicas distintas, enriquecê-los e modelá-los para criar um dataset analítico de alta qualidade. O caso de uso escolhido foi a **análise de lançamentos de foguetes da SpaceX**, enriquecendo os dados brutos com informações demográficas e geográficas dos países onde as bases de lançamento estão localizadas.

O resultado final é uma tabela Delta Lake limpa e otimizada, além de todos os artefatos de análise (relatório de qualidade e gráficos) gerados de forma 100% automatizada pelo pipeline.

## 🛠️ Tecnologias Utilizadas

* **Plataforma Cloud:** Databricks Community Edition
* **Linguagem:** Python
* **Processamento de Dados:** PySpark
* **Formato de Armazenamento:** Delta Lake (Tabela Gerenciada)
* **Bibliotecas Python:** `requests`, `pandas`, `matplotlib`, `seaborn`
* **Versionamento:** Git & GitHub

## 📂 Estrutura do Repositório

Ao executar o pipeline, a seguinte estrutura de artefatos é gerada dentro do repositório no Databricks, pronta para ser sincronizada com o GitHub.

```
/
├── README.md           # Documentação do projeto
├── requirements.txt    # Dependências Python
├── notebooks/
│   └── pipeline_launches.ipynb # Notebook com o código do pipeline
└── output/
    ├── dq_report/
    │   └── dq_report.json  # Relatório de qualidade dos dados (gerado)
    └── images/
        ├── launches_per_year.png       # Gráfico de lançamentos por ano (gerado)
        ├── launches_per_country.png    # Gráfico de lançamentos por país (gerado)
        └── launches_per_launchpad.png  # Gráfico de lançamentos por base (gerado)
```

## 📈 Etapas do Pipeline

O pipeline foi desenvolvido no notebook `pipeline_launches.ipynb` e segue as seguintes etapas:

1.  **Extração (E):**
    * Consumo de dados da **SpaceX API** e da **REST Countries API**.
    * Implementado tratamento de erros robusto para garantir a resiliência do pipeline contra falhas de API (timeouts, erros HTTP).

2.  **Transformação (T):**
    * Limpeza, padronização de tipos e seleção de colunas relevantes.
    * **Enriquecimento de Dados:** Criação da coluna `country` (país) para as bases de lançamento, que não era fornecida pela API.
    * **Join Estratégico:** Cruzamento dos dados de lançamentos com os dados dos países para criar um dataset unificado.

3.  **Carga (L) e Geração de Artefatos:**
    * **Relatório de Qualidade:** Geração automática de um arquivo `dq_report.json` com métricas essenciais.
    * **Persistência Otimizada:** Salvamento do DataFrame final como uma **tabela Delta gerenciada** no Databricks, particionada por ano e mês para otimizar consultas.
    * **Geração de Gráficos:** Criação e salvamento automático de todas as visualizações de análise como arquivos `.png` usando Matplotlib e Seaborn.

## 🚀 Como Executar no Databricks

1.  **Configurar o Cluster:** Crie ou utilize um cluster Databricks.
2.  **Clonar o Repositório:**
    * Na interface do Databricks, vá para a seção **Repos**.
    * Clique em **"Add Repo"** e cole a URL deste repositório.
3.  **Abrir o Notebook:** Navegue até `notebooks/pipeline_launches.ipynb` e anexe-o ao seu cluster.
4.  **Executar o Pipeline:** Execute todas as células em ordem (`Run All`). O notebook instalará as dependências, executará o ETL completo e gerará todos os relatórios e gráficos na pasta `output/`.

## 📊 Resultados e Análises Geradas

A última etapa do notebook realiza uma série de análises sobre a tabela final para demonstrar o seu valor. Os insights extraídos incluem:

#### 1. Crescimento Exponencial de Lançamentos da SpaceX
O gráfico de linhas mostra a evolução do número de lançamentos por ano, evidenciando o rápido crescimento das operações.

![Gráfico de Lançamentos por Ano](output/images/launches_per_year.png)

#### 2. Desempenho e Distribuição por País
A análise do número de lançamentos por país mostra a concentração das operações nos Estados Unidos, com um altíssimo índice de sucesso.

![Gráfico de Lançamentos por País](output/images/launches_per_country.png)

#### 3. Bases de Lançamento Mais Ativas
O gráfico de barras horizontais identifica as bases de lançamento mais estratégicas para a SpaceX, destacando os principais centros operacionais.

![Gráfico de Lançamentos por Base](output/images/launches_per_launchpad.png)

---

*Projeto desenvolvido por Arthur Rodrigues.*