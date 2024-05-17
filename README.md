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

### Clonar o Repositório

1. Abra o terminal ou o prompt de comando.

2. Navegue até o diretório onde deseja clonar o repositório.

3. Execute o seguinte comando:

    ```
    git clone https://github.com/cristianefleal/dataint.git
    ```

### Configurar e executar o docker compose

1. Navegue até o diretório raiz do projeto após clonar o repositório:

    ```
    cd dataint
    ```
2. Crie um arquivo .env de acordo com a estrutura de .env.local:

    ```
    cp .env.local .env
    ```
3. Edite o arquivo .env informando o valor das variáveis:

    ```
    AIRFLOW_UID=${AIRFLOW_UID}
    POSTGRES_USER=${POSTGRES_USER}
    POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    POSTGRES_DB=${POSTGRES_DB}

    ```

4. Execute o seguinte comando para inicializar os serviços:

    ```
    docker compose up -d
    ```

### Acessar o airflow

6. Após iniciar todos os serviços a aplicação pode ser acessada através do endereço: http://localhost:8080
