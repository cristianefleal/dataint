import pendulum
from airflow.models.dag import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.empty import EmptyOperator
from airflow.hooks.base import BaseHook
import snowflake.connector as sc
from airflow.providers.snowflake.operators.snowflake import SnowflakeOperator

minha_conexao = "snowflake_default"
meu_arquivo = ["data/coffeeshopsales1.csv","data/coffeeshopsales2.csv","data/coffeeshopsales3.csv"]

with DAG(
    dag_id="02_snowflake_put_and_copy",
    schedule=None,
    start_date=pendulum.datetime(2024, 5, 10, tz="UTC"),
):

    # Obtém a conexão do banco de dados do Airflow
    def obter_credenciais_conexao(conn_id):
        conexao = BaseHook.get_connection(f"{conn_id}")

        if conexao:
            login = conexao.login
            senha = conexao.password
            conta = conexao.extra.split('"account": "')[1].split('"')[0]
            regiao = conexao.extra.split('"region": "')[1].split('"')[0]
            return login, senha, conta, regiao
        else:
            print(f"A conexão com o ID '{conn_id}' não foi encontrada.")
            return None, None

    def envia_arquivo(arquivos):
        login, senha, conta, regiao = obter_credenciais_conexao(minha_conexao)
        conn = sc.connect(user=login, password=senha, account=f"{conta}.{regiao}")
        for arquivo in arquivos:
            conn.cursor().execute(
                f"""
                PUT file://dags/{arquivo} @impacta.public.stg_coffee AUTO_COMPRESS=FALSE OVERWRITE = TRUE;
                """
            )
        return f"arquivo {arquivo} enviado para a STAGE @impacta.public.stg_coffee"

    start = EmptyOperator(task_id="start")
    envia_arquivo_para_nuvem = PythonOperator(
        task_id="envia_arquivo_para_nuvem",
        python_callable=envia_arquivo,
        op_args=[meu_arquivo],
    )
    # Executar a consulta usando SnowflakeOperator
    sql = """
CREATE or replace TABLE coffeeshop_raw ( transaction_id NUMBER(10),
                                    transaction_date DATE,
                                    transaction_time TIME,
                                    store_id NUMBER(10),
                                    store_location VARCHAR,
                                    product_id NUMBER(10),
                                    transaction_qty NUMBER(10),
                                    unit_price NUMBER(10,2),
                                    product_category VARCHAR(50),
                                    product_type VARCHAR(50),
                                    product_detail VARCHAR(50),
                                    size VARCHAR(50),
                                    total_bill NUMBER(10,2),
                                    month_name VARCHAR(50),
                                    day_name VARCHAR(50),
                                    hour NUMBER(2),
                                    day_of_week NUMBER(2),
                                    month NUMBER(2));

CREATE FILE FORMAT tmp_coffeeshop
	TYPE=CSV
    SKIP_HEADER=1
    FIELD_DELIMITER=';'
    TRIM_SPACE=TRUE
    FIELD_OPTIONALLY_ENCLOSED_BY='"'
    REPLACE_INVALID_CHARACTERS=TRUE
    DATE_FORMAT=AUTO
    TIME_FORMAT=AUTO
    TIMESTAMP_FORMAT=AUTO;

COPY INTO coffeeshop_raw
FROM (SELECT DISTINCT $1, 
             TO_DATE($2,'DD/MM/YYYY'),
             $3,
             $4,
             $5,
             $6,
             $7,
             $8,
             $9,
             $10,
             $11,
             $12,
             $13,
             $14,
             $15,
             $16,
             $17,
             $18    
      FROM @stg_coffee)
FILES = ('coffeeshopsales1.csv','coffeeshopsales2.csv','coffeeshopsales3.csv') 
FILE_FORMAT = ( FORMAT_NAME = tmp_coffeeshop)
ON_ERROR=ABORT_STATEMENT;
"""
    copy_file = SnowflakeOperator(
        task_id="copy_file",
        sql=sql,
        snowflake_conn_id=minha_conexao,  # Nome da conexão configurada no Airflow para o Snowflake
        autocommit=True,
        split_statements=True,
    )

    sql = """
            CREATE TABLE impacta.public.dim_date (
    full_date DATE,
    day_of_week VARCHAR(20),
    day int,
    month int,
    year INT,
    quarter INT,
    is_holiday BOOLEAN
);

SET total_time = (SELECT DATEDIFF(DAY, '2023-01-01', '2024-01-01'));

INSERT INTO impacta.public.dim_date (full_date, day_of_week, day, month, year, quarter, is_holiday)
WITH dates_cte AS (
    SELECT DATEADD(DAY, seq8(), TO_DATE('2023-01-01')) AS full_date
    FROM TABLE(GENERATOR(ROWCOUNT => $total_time))
)
SELECT
    full_date,
    DAYNAME(full_date) AS day_of_week,
    DAY(full_date),
    month(full_date) AS month,
    YEAR(full_date) AS year,
    CEIL(TO_NUMBER(TO_CHAR(full_date, 'MM')) / 3) AS quarter,
    CASE WHEN full_date IN ('2023-01-01', '2023-12-25') THEN TRUE ELSE FALSE END AS is_holiday
FROM dates_cte;

-- Verificação dos dados inseridos
SELECT * FROM impacta.public.dim_date ORDER BY full_date LIMIT 100;
    """

    cria_dim_date = SnowflakeOperator(
        task_id="cria_dim_date",
        sql=sql,
        snowflake_conn_id=minha_conexao,  # Nome da conexão configurada no Airflow para o Snowflake
        autocommit=True,
        split_statements=True,
    )

    sql = """
            CREATE or replace TABLE dim_produto AS SELECT DISTINCT product_id, product_category, product_type, product_detail, size, unit_price FROM coffeeshop_raw;
    """

    cria_dim_produto = SnowflakeOperator(
        task_id="cria_dim_produto",
        sql=sql,
        snowflake_conn_id=minha_conexao,  # Nome da conexão configurada no Airflow para o Snowflake
        autocommit=True,
        split_statements=True,
    )

    sql = """
            CREATE or replace TABLE dim_store AS SELECT DISTINCT store_id, store_location FROM coffeeshop_raw;
    """

    cria_dim_store = SnowflakeOperator(
        task_id="cria_dim_store",
        sql=sql,
        snowflake_conn_id=minha_conexao,  # Nome da conexão configurada no Airflow para o Snowflake
        autocommit=True,
        split_statements=True,
    )

    sql = """
            CREATE or replace TABLE ft_coffeeshop AS SELECT DISTINCT transaction_id, transaction_date, transaction_time, store_id, product_id, transaction_qty, total_bill  FROM coffeeshop_raw;
    """

    cria_fato = SnowflakeOperator(
        task_id="cria_fato",
        sql=sql,
        snowflake_conn_id=minha_conexao,  # Nome da conexão configurada no Airflow para o Snowflake
        autocommit=True,
        split_statements=True,
    )    


    end = EmptyOperator(task_id="end")


start >> envia_arquivo_para_nuvem >> copy_file >> [cria_dim_date,cria_dim_produto,cria_dim_store] >> cria_fato >> end