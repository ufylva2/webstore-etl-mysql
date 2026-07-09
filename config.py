"""Configurações da aplicação WebStore CLI.

As credenciais da base de dados são lidas de variáveis de ambiente,
com valores por defeito para facilitar a execução em desenvolvimento local.
Para produção, define as variáveis de ambiente correspondentes em vez de
alterar os valores por defeito abaixo.
"""

import os

DB_CONFIG = {
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "host": os.getenv("DB_HOST", "localhost"),
    "database": os.getenv("DB_NAME", "webstore"),
}
