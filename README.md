# Documentação do Projeto

Este repositório contém o projeto da disciplina de DataOps.

Os seguintes serviços são instalados pelo Docker compose:

- Suite Airflow
    - Webserver
    - Worker
    - Schedule
    - Postgres
    - Redis
    - Triggerer

- Destino dos dados tratados
    - MySQL

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

### Clonar o Repositório

1. Abra o terminal ou o prompt de comando.

2. Navegue até o diretório onde deseja clonar o repositório.

3. Execute o seguinte comando:

    ```
    git clone https://github.com/cristianefleal/dataops.git
    ```

### Configurar e executar o docker compose

1. Navegue até o diretório raiz do projeto após clonar o repositório:

    ```
    cd dataops
    ```
2. Crie um arquivo .env de acordo com a estrutura de .env.local:

    ```
    cp .env.local .env
    ```
3. Edite o arquivo .env informando o valor das variáveis:

    ```
    AIRFLOW_UID=${AIRFLOW_UID}
    MYSQL_ROOT_PASSWORD=${MYSQL_ROOT_PASSWORD}
    MYSQL_DATABASE=${MYSQL_DATABASE}
    MYSQL_USER=${MYSQL_USER}
    MYSQL_PASSWORD=${MYSQL_PASSWORD}
    POSTGRES_USER=${POSTGRES_USER}
    POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    POSTGRES_DB=${POSTGRES_DB}
    URL=${URL}
    _PIP_ADDITIONAL_REQUIREMENTS=openpyxl
    ```

4. Execute o seguinte comando para inicializar os serviços:

    ```
    docker compose up -d
    ```

5. Buscar o IP do container do Mysql, para que seja configurada a conexão no Airflow

    ```
    docker  ps

    docker inspect <container_id_mysql> | grep IPAddress
    ```


### Acessar o airflow

6. Após iniciar todos os serviços a aplicação pode ser acessada através do endereço: http://localhost:8080

7. Crie uma conexão para o Mysql em Admin/Conections

![Alt text](images/airflow1.png?raw=true "Title")

8. No campo Host informe o IP do Mysql (passo 5), assim como connection_id (mysql_con), Login e Password configurados no .env

![Alt text](images/airflow2.png?raw=true "Title")

9. No menu DAGS, executar a dag de04-dataops

![Alt text](images/airflow3.png?raw=true "Title")
