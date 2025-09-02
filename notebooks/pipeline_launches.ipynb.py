# Databricks notebook source
# Célula 1: Instalação de Dependências
%pip install -r ../requirements.txt

# COMMAND ----------

# Célula 2: Importações
import requests
import json
from pyspark.sql.functions import col, to_timestamp, year, month, when
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType, BooleanType

# COMMAND ----------

# Célula 3: Passo 1 - Extração (E)
import requests
import json
import pandas as pd
from pyspark.sql.functions import col, to_timestamp, year, month, when

print("Iniciando extração de dados...")

# URLs das APIs
launches_url = "https://api.spacexdata.com/v4/launches"
launchpads_url = "https://api.spacexdata.com/v4/launchpads"
countries_url = "https://restcountries.com/v3.1/all?fields=name,cca3,region,population,currencies"

try:
    # --- Requisição 1: Launches ---
    print("Tentando extrair dados de: Lançamentos (SpaceX)")
    launches_response = requests.get(launches_url, timeout=30)
    launches_response.raise_for_status()
    launches_data = launches_response.json()
    print("1/3 - Dados da SpaceX (Lançamentos) extraídos com sucesso.")

    # --- Requisição 2: Launchpads ---
    print("Tentando extrair dados de: Bases de Lançamento (SpaceX)")
    launchpads_response = requests.get(launchpads_url, timeout=30)
    launchpads_response.raise_for_status()
    launchpads_data = launchpads_response.json()
    print("2/3 - Dados da SpaceX (Bases de Lançamento) extraídos com sucesso.")

    # --- Requisição 3: Countries ---
    print("Tentando extrair dados de: Países (REST Countries)")
    countries_response = requests.get(countries_url, timeout=30)
    countries_response.raise_for_status()
    countries_data = countries_response.json()
    print("3/3 - Dados da REST Countries extraídos com sucesso.")

    # --- Verificação de tipo de dados ---
    if not isinstance(launches_data, list) or not isinstance(launchpads_data, list) or not isinstance(countries_data, list):
        raise TypeError("Uma das APIs não retornou uma lista de dados como esperado.")

    print("\nExtração concluída. Convertendo para DataFrames Spark...")
    
    launches_df = spark.createDataFrame(pd.DataFrame(launches_data))
    launchpads_df = spark.createDataFrame(pd.DataFrame(launchpads_data))
    countries_df = spark.createDataFrame(pd.DataFrame(countries_data))
    
    print("DataFrames criados com sucesso!")
    countries_df.printSchema()

except requests.exceptions.HTTPError as err:
    print("========================= ERRO DE API DETECTADO =========================")
    print(f"A extração de dados falhou na URL: {err.request.url}")
    print(f"Código de Status HTTP: {err.response.status_code}")
    print(f"Resposta da API: {err.response.text}")
    print("=======================================================================")
    dbutils.notebook.exit("Falha na extração de dados da API. Verifique a saída de erro acima para detalhes.")
except requests.exceptions.RequestException as e:
    print(f"ERRO DE CONEXÃO: Não foi possível conectar à API. Detalhes: {e}")
    dbutils.notebook.exit("Falha de conexão com a API.")
except Exception as e:
    print(f"Ocorreu um erro inesperado: {e}")
    dbutils.notebook.exit("Ocorreu um erro inesperado.")

# COMMAND ----------

# Célula 4: Passo 2 - Transformação (T)
from pyspark.sql.functions import col, to_timestamp, year, month, when, lower

print("Iniciando transformações...")

# 1. Seleção de colunas
launches_selected_df = launches_df.select("id", "name", "date_utc", "launchpad", "success", "rocket")
launchpads_selected_df = launchpads_df.select(
    col("id").alias("launchpad_id"), 
    col("name").alias("launchpad_name"), 
    col("locality")
)
countries_selected_df = countries_df.select(col("name.common").alias("country_name"), "cca3", "region", "population", "currencies")

# Criação da coluna de país da base
launchpads_with_country_df = launchpads_selected_df.withColumn("launchpad_country",
    when(lower(col("locality")).like("%vandenberg%"), "United States")
    .when(lower(col("locality")).like("%cape canaveral%"), "United States")
    .when(lower(col("locality")).like("%starbase%"), "United States")
    .when(lower(col("locality")).like("%kennedy space center%"), "United States")
    .when(lower(col("locality")).like("%kwajalein atoll%"), "Marshall Islands")
    .otherwise("Unknown")
)

# 2. Padronização de datas
launches_typed_df = launches_selected_df \
    .withColumn("launch_date", to_timestamp(col("date_utc"))) \
    .withColumn("launch_year", year(col("launch_date"))) \
    .withColumn("launch_month", month(col("launch_date")))

# 3. Limpeza de dados nulos
launches_cleaned_df = launches_typed_df.withColumn("success", when(col("success").isNull(), False).otherwise(col("success")))

# 4. Enriquecimento com dados das bases de lançamento (Join 1) 
launches_with_launchpad_df = launches_cleaned_df.join(
    launchpads_with_country_df,
    launches_cleaned_df.launchpad == launchpads_with_country_df.launchpad_id,
    "left"
)

# 5. Enriquecimento com dados dos países (Join 2)
final_df = launches_with_launchpad_df.join(
    countries_selected_df,
    launches_with_launchpad_df.launchpad_country == countries_selected_df.country_name, # A condição do join foi simplificada
    "left"
)

# Seleção final de colunas
output_df = final_df.select(
    "id",
    "name",
    "launch_date",
    "success",
    "rocket",
    "launchpad_name",
    "locality",
    col("launchpad_country").alias("country_name"),
    "region",
    "population",
    "currencies",
    "launch_year",
    "launch_month"
)

print("Transformações concluídas.")
output_df.printSchema()

# COMMAND ----------

# Célula 5: Passo 3 - Relatório de Qualidade de Dados (DQ)
import json
import os
from pyspark.sql.functions import col, count, when

print("Gerando relatório de qualidade...")

total_rows = output_df.count()
dq_report_list = []

for c in output_df.columns:
    null_count = output_df.filter(col(c).isNull()).count()
    null_ratio = (null_count / total_rows) * 100 if total_rows > 0 else 0
    dq_report_list.append({"column": c, "null_count": null_count, "null_ratio_percent": round(null_ratio, 2)})

dq_final_report = {"total_rows": total_rows, "columns_check": dq_report_list}

# Obter o caminho raiz do repositório clonado no Databricks
repo_root = os.getcwd()
output_dir = os.path.join(repo_root, "output/dq_report")

# Criar o diretório, se não existir
os.makedirs(output_dir, exist_ok=True)

# Escrever o arquivo JSON usando Python padrão
file_path = os.path.join(output_dir, "dq_report.json")
with open(file_path, "w") as f:
    json.dump(dq_final_report, f, indent=4)

print(f"Relatório salvo com sucesso em: {file_path}")
print(json.dumps(dq_final_report, indent=4))

# COMMAND ----------

# Célula 5.1: Visualização do Relatório de Qualidade
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

print("Gerando visualização do relatório de qualidade...")

# --- Carregar os dados do relatório JSON ---
repo_root = os.getcwd()
json_path = os.path.join(repo_root, "output/dq_report/dq_report.json")

with open(json_path, 'r') as f:
    dq_data = json.load(f)

# Converter a parte de checagem de colunas para um DataFrame pandas
dq_df = pd.DataFrame(dq_data['columns_check'])

# --- Gerar o Gráfico ---
plt.figure(figsize=(12, 8))
sns.set_style("whitegrid")

# Criar o gráfico de barras horizontais
barplot = sns.barplot(
    x="null_ratio_percent", 
    y="column", 
    data=dq_df, 
    palette="coolwarm"
)

# Adicionar os valores exatos nas barras para clareza
for index, value in enumerate(dq_df['null_ratio_percent']):
    if value > 0:
        plt.text(value + 0.1, index, f'{value:.2f}%', color='black', ha="left", va="center")

plt.title("Percentual de Valores Nulos por Coluna", fontsize=16)
plt.xlabel("Percentual de Nulos (%)", fontsize=12)
plt.ylabel("Coluna", fontsize=12)
plt.xlim(0, max(dq_df['null_ratio_percent']) * 1.2 + 1) # Ajustar o limite do eixo x

# --- Salvar o Gráfico ---
output_images_dir = os.path.join(repo_root, "output/images")
os.makedirs(output_images_dir, exist_ok=True) # Garantir que a pasta existe

file_path_dq = os.path.join(output_images_dir, "data_quality_null_ratio.png")
plt.savefig(file_path_dq, bbox_inches='tight')
plt.close()

print(f"Gráfico de qualidade de dados salvo em: {file_path_dq}")

# Exibir o DataFrame no notebook
display(dq_df)

# COMMAND ----------

# Célula 6: Passo 4 - Carga (L)
print("Salvando dados finais como uma tabela Delta gerenciada...")
table_name = "launches_enriched"

output_df.write \
    .format("delta") \
    .mode("overwrite") \
    .partitionBy("launch_year", "launch_month") \
    .saveAsTable(table_name)

print(f"Dados salvos com sucesso na tabela: '{table_name}'")
print("Você pode navegar até a aba 'Data' na interface do Databricks para ver a nova tabela.")

# COMMAND ----------

# Célula 7: Passo 5 - Análise e Dashboard de Lançamentos
from pyspark.sql.functions import col, count, when, sum, format_number

print("Iniciando a análise aprofundada da tabela 'launches_enriched'...")

# ------------------------------------------------------------------------------------
# 1. CARREGAMENTO DOS DADOS
# ------------------------------------------------------------------------------------
# Carregamos a tabela final que foi salva na Célula 6.
table_name = "launches_enriched"
launches_final_table = spark.read.table(table_name)
print(f"Tabela '{table_name}' carregada com sucesso.")

# COMMAND ----------

# Célula de Setup para os Gráficos
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Definir um estilo visual mais agradável para os gráficos
sns.set_style("whitegrid")

# Obter o caminho raiz do repositório
repo_root = os.getcwd()
output_images_dir = os.path.join(repo_root, "output/images")

# Criar o diretório para salvar as imagens, se não existir
os.makedirs(output_images_dir, exist_ok=True)

print(f"Gráficos serão salvos em: {output_images_dir}")

# COMMAND ----------

# MAGIC %md
# MAGIC ### Análise 1: Evolução dos Lançamentos ao Longo do Tempo
# MAGIC
# MAGIC Vamos analisar o número de lançamentos por ano para entender a cadência e o crescimento das operações da SpaceX.

# COMMAND ----------

# Análise 1: Evolução dos Lançamentos ao Longo do Tempo

# Agregação com PySpark
launches_per_year_df = launches_final_table.groupBy("launch_year").count().orderBy("launch_year")

# 1. Converter para Pandas
pandas_df_year = launches_per_year_df.toPandas()

# 2. Criar o gráfico
plt.figure(figsize=(12, 7))
sns.lineplot(x="launch_year", y="count", data=pandas_df_year, marker='o', markersize=8)
plt.title("Evolução do Número de Lançamentos da SpaceX por Ano", fontsize=16)
plt.xlabel("Ano", fontsize=12)
plt.ylabel("Número de Lançamentos", fontsize=12)
plt.xticks(pandas_df_year["launch_year"])
plt.grid(True)

# 3. Salvar a imagem
file_path_year = os.path.join(output_images_dir, "launches_per_year.png")
plt.savefig(file_path_year, bbox_inches='tight')
plt.close()

print(f"Gráfico de lançamentos por ano salvo em: {file_path_year}")

display(launches_per_year_df)

# COMMAND ----------

# MAGIC %md
# MAGIC ### Análise 2: Desempenho por País (Taxa de Sucesso)
# MAGIC
# MAGIC Agora, vamos aprofundar a análise geográfica, não apenas contando os lançamentos, mas também calculando a taxa de sucesso em cada país.

# COMMAND ----------

# Análise 2: Desempenho por País (Taxa de Sucesso)

# Agregação com PySpark
success_rate_df = launches_final_table.groupBy("country_name") \
    .agg(
        count("*").alias("total_launches"),
        sum(when(col("success") == True, 1).otherwise(0)).alias("successful_launches")
    ) \
    .withColumn("failure_launches", col("total_launches") - col("successful_launches")) \
    .withColumn("success_rate_percent", 
        format_number((col("successful_launches") / col("total_launches") * 100), 2)
    ) \
    .orderBy(col("total_launches").desc())

# 1. Converter para Pandas
pandas_df_country = success_rate_df.toPandas()

# 2. Criar o gráfico de barras
plt.figure(figsize=(10, 6))
sns.barplot(x="total_launches", y="country_name", data=pandas_df_country, palette="viridis")
plt.title("Número Total de Lançamentos por País", fontsize=16)
plt.xlabel("Número Total de Lançamentos", fontsize=12)
plt.ylabel("País", fontsize=12)

# 3. Salvar a imagem
file_path_country = os.path.join(output_images_dir, "launches_per_country.png")
plt.savefig(file_path_country, bbox_inches='tight')
plt.close()

print(f"Gráfico de lançamentos por país salvo em: {file_path_country}")

display(success_rate_df)

# COMMAND ----------

# MAGIC %md
# MAGIC ### Análise 3: Bases de Lançamento Mais Ativas
# MAGIC
# MAGIC Qual base de lançamento (Launchpad) é a mais utilizada? Esta análise nos dá uma visão mais granular do que a análise por país.

# COMMAND ----------

# Análise 3: Bases de Lançamento Mais Ativas

# Agregação com PySpark
launches_per_launchpad_df = launches_final_table.groupBy("launchpad_name") \
    .count() \
    .orderBy(col("count").desc())

# 1. Converter para Pandas
pandas_df_launchpad = launches_per_launchpad_df.toPandas()

# 2. Criar o gráfico de barras horizontais
plt.figure(figsize=(12, 8))
sns.barplot(x="count", y="launchpad_name", data=pandas_df_launchpad, palette="plasma")
plt.title("Bases de Lançamento Mais Ativas da SpaceX", fontsize=16)
plt.xlabel("Número de Lançamentos", fontsize=12)
plt.ylabel("Base de Lançamento", fontsize=12)

# 3. Salvar a imagem
file_path_launchpad = os.path.join(output_images_dir, "launches_per_launchpad.png")
plt.savefig(file_path_launchpad, bbox_inches='tight')
plt.close()

print(f"Gráfico de lançamentos por base salvo em: {file_path_launchpad}")

display(launches_per_launchpad_df)
