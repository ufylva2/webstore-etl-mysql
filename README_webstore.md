# Webstore.py — WebStore CLI (ETL + MySQL)

Aplicação de linha de comandos que consome a API pública [DummyJSON](https://dummyjson.com/)
e carrega produtos, categorias, marcas e reviews para uma base de dados
MySQL, disponibilizando um menu interativo para consultar, filtrar, gerir e
exportar os dados.

## Objetivo

Demonstrar um pequeno pipeline de ETL (Extract, Transform, Load): extração de
dados de uma API REST, transformação/normalização em tabelas relacionais, e
carregamento numa base de dados MySQL, seguido de operações de consulta,
gestão (CRUD) e exportação de dados.

## Tecnologias utilizadas

- Python 3
- MySQL / mysql-connector-python
- API REST (requests)
- beaupy (menus interativos de consola)
- JSON / CSV (exportação de dados)

## Funcionalidades

- **Importar API**: importa até 100 produtos da DummyJSON, criando automaticamente
  categorias e marcas associadas
- **Consultar Produtos**: listar todos, pesquisar por nome, ver ratings médios
- **Filtrar Produtos**: por marca, por categoria e por intervalo de preço
- **Reviews**: consulta de reviews por produto e por utilizador (nome/email)
- **Gestão de Registos**: inserir/remover produtos, categorias, marcas e reviews
- **Exportar Dados**: para JSON (`produtos.json`) e CSV (`produtos.csv`)
- **Dashboard interativo** (`webstore_dashboard.py`): relatório visual em
  Streamlit com KPIs, distribuição por categoria/marca, análise de preços,
  ratings e catálogo filtrável

O menu principal está organizado em submenus temáticos para não sobrecarregar
o utilizador com demasiadas opções de uma só vez.

## Estrutura do projeto

```
webstore/
├── webstore.py             # Aplicação principal (menu, ETL, CRUD, exportações)
├── webstore_dashboard.py  # Dashboard interativo (Streamlit) sobre os dados importados
├── config.py               # Configuração da ligação à base de dados MySQL
├── requirements.txt
├── .gitignore
└── README.md
```

A base de dados (`webstore`, por defeito) e as respetivas tabelas são criadas
automaticamente na primeira execução, desde que o servidor MySQL esteja
acessível com as credenciais configuradas.

## Como instalar

1. Cria e ativa um ambiente virtual (opcional, mas recomendado):
   ```bash
   python -m venv .venv
   source .venv/bin/activate   # Windows: .venv\Scripts\activate
   ```
2. Instala as dependências:
   ```bash
   pip install -r requirements.txt
   ```
3. Garante que tens um servidor MySQL/MariaDB acessível (local ou remoto).
4. (Opcional) Define as credenciais da base de dados através de variáveis de
   ambiente, caso sejam diferentes das predefinições (`root` sem password,
   `localhost`, base de dados `webstore`):
   ```bash
   export DB_USER=root
   export DB_PASSWORD=""
   export DB_HOST=localhost
   export DB_NAME=webstore
   ```

## Como executar

```bash
python webstore.py
```

Na primeira execução, a base de dados e as tabelas são criadas
automaticamente. Depois, escolhe a opção **"Importar API"** no menu para
carregar os dados de exemplo.

Para visualizar o dashboard interativo com os dados já importados:

```bash
streamlit run webstore_dashboard.py
```



## Competências demonstradas

- Consumo de APIs REST e tratamento de erros de rede
- Modelação de uma base de dados relacional (MySQL) com chaves estrangeiras
- Processo de ETL simples (extração, normalização, carregamento)
- Operações CRUD com validação básica de dados
- Configuração de credenciais fora do código-fonte (variáveis de ambiente)
- Exportação de dados para JSON e CSV

## Melhorias futuras

- Paginação nas listagens para bases de dados maiores
- Testes automatizados para as funções de acesso a dados
- Suporte para atualizar produtos/reviews existentes
- Pool de ligações (`mysql.connector.pooling`) para reduzir overhead de conexão
