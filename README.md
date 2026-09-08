# WebStore ETL & Analytics

Este projeto foi desenvolvido no âmbito da minha formação em **Data & Business Analysis** com o objetivo de demonstrar um processo completo de **ETL (Extract, Transform, Load)** através da integração de uma API REST, armazenamento dos dados numa base de dados **MySQL** e respetiva análise através de um dashboard interativo desenvolvido em **Python** e **Streamlit**.

Ao longo do desenvolvimento procurei aplicar boas práticas de organização de código, modelação de bases de dados relacionais, consumo de APIs e visualização de informação, criando uma aplicação que permite importar, gerir, consultar e analisar dados de produtos de forma simples e intuitiva.

---

# Funcionalidades

A aplicação inclui várias funcionalidades, entre elas:

- Importação automática de produtos através da API DummyJSON
- Criação automática da base de dados e respetivas tabelas em MySQL
- Gestão de produtos, categorias, marcas e reviews (CRUD)
- Pesquisa de produtos por nome
- Filtros por categoria, marca e intervalo de preços
- Consulta de ratings médios dos produtos
- Exportação de dados para ficheiros JSON e CSV
- Dashboard interativo em Streamlit com análise visual dos dados

Cada funcionalidade foi desenvolvida para demonstrar um fluxo completo de tratamento e análise de dados, desde a extração até à visualização.

---

# Tecnologias utilizadas

- Python
- MySQL
- Streamlit
- Pandas
- Plotly
- Requests
- mysql-connector-python
- DummyJSON API
- Beaupy

---

# Estrutura do projeto

```text
webstore-etl-mysql/
│
├── webstore.py               # Aplicação principal (ETL + CRUD)
├── webstore_dashboard.py     # Dashboard interativo
├── config.py                 # Configuração da ligação MySQL
├── requirements.txt
├── .gitignore
└── README.md
```

---

# Pré-requisitos

- Python 3.10+
- Servidor MySQL ativo localmente (ex: via **XAMPP**, WAMP ou instalação standalone do MySQL)
  - Por defeito, a aplicação liga-se com utilizador `root`, sem password, em `localhost` — a configuração padrão do XAMPP
  - Se usares outras credenciais, define as variáveis de ambiente `DB_USER`, `DB_PASSWORD`, `DB_HOST` e `DB_NAME` antes de executar (ver abaixo)

---

# Como executar

## Clonar o repositório

```bash
git clone https://github.com/ufylva2/webstore-etl-mysql.git
```

## Instalar as dependências

```bash
pip install -r requirements.txt
```

## Garantir que o MySQL está ativo

Inicia o servidor MySQL (por exemplo, no XAMPP Control Panel, clica em **Start** no módulo MySQL) antes de executar a aplicação.

Se as tuas credenciais forem diferentes das predefinições (`root`, sem password, `localhost`, base `webstore`), define as variáveis de ambiente antes de correr o script:

```bash
export DB_USER=root
export DB_PASSWORD="a_tua_password"
export DB_HOST=localhost
export DB_NAME=webstore
```

(no Windows CMD: `set DB_PASSWORD=a_tua_password`; no PowerShell: `$env:DB_PASSWORD="a_tua_password"`)

## Executar a aplicação

```bash
python webstore.py
```

Na primeira execução, a aplicação cria automaticamente a base de dados e todas as tabelas necessárias.

Depois de importar os dados através da opção **Importar API**, é possível iniciar o dashboard com:

```bash
streamlit run webstore_dashboard.py
```

---

# O que procurei desenvolver neste projeto

Mais do que criar uma aplicação de gestão de produtos, este projeto permitiu-me consolidar competências em:

- Consumo de APIs REST
- Processos ETL (Extract, Transform & Load)
- Modelação de bases de dados relacionais
- SQL e MySQL
- Operações CRUD
- Limpeza e preparação de dados
- Desenvolvimento de dashboards interativos
- Visualização de dados
- Organização e reutilização de código
- Estruturação de projetos em Python

---

# Próximos passos

Pretendo continuar a evoluir este projeto com novas funcionalidades, como:

- Atualização automática de produtos existentes
- Paginação nas consultas
- Dashboard com novos indicadores de negócio
- Estatísticas mais detalhadas sobre produtos e categorias
- Testes automatizados
- Modelos preditivos utilizando Machine Learning


---

## Autor

**Luís Fernandes**
