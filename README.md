# Pipeline On-premises 

!(./img/dataint.png)

## Links das aplicações

- **Airbyte:**  - http://localhost:8000/
- **Airflow:**  - http://localhost:8080/
- **Minio:**    - http://localhost:9000/

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
- **url:** http://localhost:9000
- **iip interno:** docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' <CONTAINER_ID>
- **porta:** 9000

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
- **external_port:** 5454
- **internal_host:** `postgres_prod`
- **interal_port:** `5432`

### Airbyte
 - **url:** `http://localhost:8000`
 - **user:** `airbyte`
 - **password:** `password`
 - **ip interno:** docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' <CONTAINER_ID>


## Instruções Resumo
1. Clonar o repositório.
2. Navegar até a pasta `data-int\airbyte`
3. Executar ./run=ab.plataform.sh
4. Voltar para o diretório do projeto `data-int\`
5. Executar `docker compose up -d`. A ordem é importante porque o Airbyte cria a rede que será usado pelo airflow, postgres e minio.
6. Configurar o MinIO criando os buckets (tmp, lake)
7. Acessar o Airflow para criar a conexão com o MinIO.
8. Executar DAG 1_copy_cvs_to_s3
9. Acessar o Airbyte para configurar o souce, destination e connection.
10. Acessar o Airflow para criar a conexão com o Airbyte.
11. Configurar o ID da connection criada no Airbyte na DAG 2_s3_etl_dbstage
12. Executar DAG 2_s3_etl_dbstage

## Como usar - passo a passo

### Inicializar os serviços

1. Abra o terminal ou o prompt de comando.
2. Navegue até o diretório onde deseja clonar o repositório.
3. Execute o seguinte comando:

    ```
    git clone https://github.com/cristianefleal/dataint.git
    ```
4. Navegue até o diretório do Airbyte do projeto após clonar o repositório:
    ```
    cd dataint/airbyte
    ```
5. Execute o seguinte comando para inicializar os serviços:
    ```
    ./run-ab-plataform.sh
    ```
6. Volte para o diretório raiz, execute o comando para subir o restantes dos serviços.
    ```
    docker composer up -d
    ```

## Criação dos Buckets

1. Acessar o MinIO através da URL: http://localhost/9000
2. Informar as credenciais fornecidas acima
3. Crie dois buckets de nomes: tmp e lake.

## Executar DAG 1_copy_cvs_to_s3

1. Acessar o Airflow através da URL: http://localhost:8080/home
2. Informar as credenciais fornecidas acima
3. Criar a conexão com o MinIO:
    - Abrir o terminal para recuperar o IP interno do serviço minio.
    - Executar docker ps, identificar o container_id do serviço.
    - Executar docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' <CONTAINER_ID>
    - Abrir o Menu: Admin/Connections.
    - Criar uma nova conexão:
        - Name:
        - Type:

## Airflow Configurations
1. Open Airflow
2. Go to connections
3. Create the Minio S3 connection with the below configuration:
*If you test this connection it will fail, just ignore it.*
    - **Connection Type:** `Amazon Web Services`
    - **Connection Id:** `aws_default`
    - **IP interno do container**: docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' <CONTAINER_ID>
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
    - **Host:** docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' <CONTAINER_ID> (airbyte-server)
    - **Username:** `airbyte`
    - **Password:** `password`
    - **Port:** `8001`

---

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

---

# Documentação do Projeto

Este repositório contém o projeto da disciplina de Data Integration.

Os seguintes serviços são instalados pelo Docker compose:

- Airflow
- MinIO

## Pré-requisitos

Antes de começar, certifique-se de ter o Git e o Docker instalados no seu sistema.

- [Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)
- [Docker](https://docs.docker.com/engine/install/)
- [Docker Composer](https://docs.docker.com/compose/install/)

Requisitos mínimos de memória

- Memória RAM: 4GB
- Número de CPUs: 2
- Espaço em disco: 10 GBs


## Como Usar

