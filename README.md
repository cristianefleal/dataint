# Data Integration 

![alt text](img/dataint.png)

## Links das aplicações

- **Airbyte:**  - `http://localhost:8000/`
- **Airflow:**  - `http://localhost:8080/`
- **Minio:**    - `http://localhost:9000/`

## Caso de Uso

## Requisitos
- Linux Ubuntu (WSL)
- Docker
- Docker Compose
- Python 3.10+
- Recomendado 8GB+ RAM 

## Credenciais

### Airflow
- **username:** `airflow`
- **password:** `airflow`

### Minio
- **access_key:** `minio_admin`
- **secret_key:** `minio_password`
- **url:** `http://localhost:9000`
- **ip interno:** 
    ```
    docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' <CONTAINER_ID>
    ```
- **porta:** `9000`

### Postgres Stage
- **username:** `impacta`
- **password:** `impacta`
- **external_host:** `localhost`
- **external_port:** 5455
- **internal_host:** `postgres_stage`
- **interal_port:** `5432`

### Postgres Prod
- **username:** `impacta`
- **password:** `impacta`
- **external_host:** `localhost`
- **external_port:** `5454`
- **internal_host:** `postgres_prod`
- **interal_port:** `5432`

### Airbyte
 - **url:** `http://localhost:8000`
 - **user:** `airbyte`
 - **password:** `password`
- **ip interno:** 
    ```
    docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' <CONTAINER_ID>
    ```

## Resumo
1. Instalar e subir o Airbyte conforme instruções: `https://docs.airbyte.com/deploying-airbyte/docker-compose`
2. Clonar o repositório.
3. Acessar o diretório raiz `dataint\`
4. Executar `docker compose up -d`. 
5. Importante: O Airbyte deve ser executado primeiro porque ele cria a rede que será usada pelo Airflow, Postgres e MinIO.
6. Configurar o MinIO criando os buckets (tmp, lake)
7. Acessar o Airflow para criar a conexão com o MinIO.
8. Executar DAG 1_copy_cvs_to_s3
9. Acessar o Airbyte para configurar o Souce (S3), Destination (Stage) e Connection.
10. Acessar o Airflow para criar a conexão com o Airbyte.
11. Configurar o ID da connection (connection_id) criada no Airbyte na DAG 2_s3_etl_dbstage
12. Executar DAG 2_s3_etl_dbstage
13. Acessar o Airbyte para configurar o Souce (Stage), Destination (Prod) e Connection.
14. Após verificações executar DAG 3_dbstage_to_dbprod

## Como usar - passo a passo

### Inicializar o Airbyte

1. Conforme instruções em: `https://docs.airbyte.com/deploying-airbyte/docker-compose`

### Inicializar o Airflow, Postgres e MinIO

1. Abra o terminal ou o prompt de comando.
2. Navegue até o diretório onde deseja clonar o repositório.
3. Execute o seguinte comando:

    ```
    git clone https://github.com/cristianefleal/dataint.git
    ```
4. Volte para o diretório raiz, execute o comando para subir o restantes dos serviços.
    ```
    docker composer up -d
    ```

## Criação dos Buckets

1. Acessar o MinIO através da URL: `http://localhost/9000`
2. Informar as credenciais fornecidas acima
3. Crie dois buckets de nomes: tmp e lake.

## Executar DAG 1_copy_cvs_to_s3

1. Acessar o Airflow através da URL: `http://localhost:8080/home`
2. Informar as credenciais fornecidas acima
3. Criar a conexão com o MinIO:
    - Abrir o terminal para recuperar o IP interno do serviço minio.
    - Executar docker ps, identificar o container_id do serviço e depois:
        ```
        docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' <CONTAINER_ID>
        ```
    - Abrir o Menu: Admin/Connections.
    - Criar uma nova conexão:
        - Name:
        - Type:
4. Executar DAG 1_copy_cvs_to_s3

## Configuração do Airbyte
1. Acessar o Airbyte através da URL:
2. Fornecer as credenciais:
2. Em Sources (*menu esquerdo*), busque e selecione S3. 
3. Configuração:
    - **Source_name:** `S3`
    - **Output_stream_name:** `dauly_coffeeshop`
    - **Pattern_of_files_to_replicate:** `coffeeshopsales.csv`
    - **Bucket:** `tmp`
    - **Aws_access_key_id:** `minio_admin`
    - **Aws_secret_access_key:** `minio_password`
    - **Path_prefix:** `customer/`
    - **Endpoint:** `http://<IP_INTERNO_CONTAINER>:9000`
    - ***Selecione `set up source`***
5. Em Destinations (*menu esquerdo*), busque e selecione Postgres.
6. Configuração Postgres Stage:
    - **Destination_name:** `Postgres_Stage`
    - **Host: (IP interno)** `localhost`
    - **Port:** `5453`
    - **Db_name:** `impacta`
    - **Default_Schema**: `airbyte`
    - **user:** `impacta`
    - **password:** `impacta`
    - ***Selecione `set up destination`***
7. Crie um novo destino e configure o Postgres Prod.
8. Configuração:
    - **Destination_name:** `Postgres_Prod`
    - **Host: (IP interno)** `localhost`
    - **Port:** `5453`
    - **Db_name:** `impacta`
    - **Default_Schema**: `public`
    - **user:** `impacta`
    - **password:** `impacta`
    - ***Selecione `set up destination`***
7. Em Connections (*menu esquerdo*)
    - Selecione o source `S3`
    - Selecione `Use existing destination` e **Postgres_Stage**
    - Altere `Replication frequency` para `Manual`
    - E o modo de sincronização deve ser `Full refresh overwrite` 
    - Selecione`set up connection`

## Airflow Configurations
1. Open Airflow
2. Go to connections
3. Create the Minio S3 connection with the below configuration:
*If you test this connection it will fail, just ignore it.*
    - **Connection Type:** `Amazon Web Services`
    - **Connection Id:** `aws_default`
    - **IP interno do container**: 
        ```
        docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' <CONTAINER_ID>
        ```
    - **Extra:** `{"aws_access_key_id": "minio_admin", "aws_secret_access_key": "minio_password", "endpoint_url": "http://<IP_INTERNO_CONTAINER>:9000"}`
4. Create the Postgres connection
    - **Connection Type:** `Postgres`
    - **Connection Id:** `postgres_default`
    - **Host:** `postgres_dw`
    - **Database:** `impacta`
    - **Login:** `impacta`
    - **Password:** `impacta`
    - **Port:** `5432`
5. Create the Airbyte connection (Optional, in case you want to use the stack for your own development)
    - **Connection Type:** `Airbyte`
    - **Connection Id:** `airbyte_default`
    - **Host:**  `IP interno do serviço airbyte-server`
        ```
        docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' <CONTAINER_ID>
        ```
    - **Username:** `airbyte`
    - **Password:** `password`
    - **Port:** `8001`

## Airbyte Configurations
1. Open Airbyte, enter an email and select `Get started`
2. Select sources (*left sidebar*) , in the search bar write `S3` and select it 
3. Create the S3 connection for customer data
    - **Source_name:** `S3`
    - **Output_stream_name:** `dauly_coffeeshop`
    - **Pattern_of_files_to_replicate:** `coffeeshopsales.csv`
    - **Bucket:** `landing`
    - **Aws_access_key_id:** `minio_admin`
    - **Aws_secret_access_key:** `minio_password`
    - **Path_prefix:** `customer/`
    - **Endpoint:** `http://<IP_INTERNO_CONTAINER>:9000`
    - ***Scroll until the end and select `set up source`***
5. Select Destinations (*left sidebar*), search for Postgres and select it.
6. Create the Postgres connection as destination
    - **Destination_name:** `Postgres_DW`
    - **Host:** `localhost`
    - **Port:** `5455`
    - **Db_name:** `impacta`
    - **Default_Schema**: `airbyte`
    - **user:** `impacta`
    - **password:** `impacta`
    - ***Scroll until the end and select `set up destination`***
7. Select Connections (*left sidebar*)
    - Select the `S3` source
    - Select `Use existing destination`
    - In the destination tab select **Postgres_DW** and select `Use existing destination`
    - In the new screen view, change the `Replication frequency` to `Manual`
    - Sync mode should be `Full refresh overwrite` 
    - Select `set up connection`

