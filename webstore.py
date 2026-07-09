import csv      # Para exportar para ficheiro CSV
import json     # Para exportar para ficheiro JSON
import os       # Para comandos do sistema (como limpar ecrã)

import mysql.connector  # Para ligação à base de dados MySQL
from mysql.connector.connection import MySQLConnection
import requests # Para consumir a API externa
from beaupy import select  # Para menus interativos no terminal

from config import DB_CONFIG

# LUIS FERNANDES


# CONFIGURAÇÃO DA API


API_URL = "https://dummyjson.com/products?limit=100"


# FUNÇÃO LIMPAR TERMINAL


def limpar() -> None:
    """Limpa o ecrã do terminal (compatível com Windows e Unix)."""
    os.system('cls' if os.name == 'nt' else 'clear')


# LIGAR À BASE DE DADOS


def conectar(usar_bd: bool = True) -> MySQLConnection:
    """Abre e devolve uma ligação à base de dados MySQL do projeto.

    Com usar_bd=False, liga ao servidor sem selecionar a base de dados
    (usado apenas para a criar automaticamente, caso ainda não exista).
    """
    config = DB_CONFIG if usar_bd else {k: v for k, v in DB_CONFIG.items() if k != "database"}
    return mysql.connector.connect(**config)


def garantir_bd() -> None:
    """Cria a base de dados configurada no servidor MySQL, caso ainda não exista."""
    con = conectar(usar_bd=False)
    cur = con.cursor()
    cur.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']} DEFAULT CHARACTER SET utf8mb4")
    con.commit()
    con.close()


# CRIAR TABELAS NA BD


def criar_tabelas() -> None:
    """Cria as tabelas da base de dados (categorias, marcas, produtos, reviews) se não existirem."""
    garantir_bd()
    con = conectar()
    cur = con.cursor()

    # Criar tabela de categorias
    cur.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) UNIQUE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)

    # Criar tabela de marcas
    cur.execute("""
        CREATE TABLE IF NOT EXISTS brands (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) UNIQUE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)

    # Criar tabela de produtos
    cur.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(255),
            description TEXT,
            price DECIMAL(10,2),
            category_id INT,
            brand_id INT,
            FOREIGN KEY (category_id) REFERENCES categories(id),
            FOREIGN KEY (brand_id) REFERENCES brands(id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)

    # Criar tabela de reviews
    cur.execute("""
        CREATE TABLE IF NOT EXISTS reviews (
            id INT AUTO_INCREMENT PRIMARY KEY,
            product_id INT,
            reviewerName VARCHAR(255),
            reviewerEmail VARCHAR(255),
            rating DECIMAL(3,2),
            comment TEXT,
            FOREIGN KEY (product_id) REFERENCES products(id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)

    con.commit()
    con.close()


# IMPORTAR PRODUTOS DA API PARA A BD


def importar_api() -> None:
    """Importa produtos, categorias, marcas e reviews a partir da API DummyJSON para a BD local."""
    try:
        resposta = requests.get(API_URL, timeout=10)
        resposta.raise_for_status()
        dados = resposta.json()["products"]
    except requests.exceptions.RequestException as erro:
        print(f"Erro ao aceder à API: {erro}")
        return
    except (KeyError, ValueError) as erro:
        print(f"Resposta inesperada da API: {erro}")
        return

    con = conectar()
    cur = con.cursor()

    for p in dados:
        # Obter ou criar categoria
        categoria = p.get('category', 'Desconhecida')
        cur.execute("INSERT IGNORE INTO categories(name) VALUES (%s)", (categoria,))
        cur.execute("SELECT id FROM categories WHERE name=%s", (categoria,))
        cat_id = cur.fetchone()[0]

        # Obter ou criar marca
        brand = p.get('brand', 'Desconhecida')
        cur.execute("INSERT IGNORE INTO brands(name) VALUES (%s)", (brand,))
        cur.execute("SELECT id FROM brands WHERE name=%s", (brand,))
        brand_id = cur.fetchone()[0]

        # Inserir produto
        cur.execute("""
            INSERT IGNORE INTO products(id, title, description, price, category_id, brand_id)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (p['id'], p['title'], p['description'], p['price'], cat_id, brand_id))

        # Inserir reviews (se existirem)
        for r in p.get("reviews", []):
            cur.execute("""
                INSERT INTO reviews(product_id, reviewerName, reviewerEmail, rating, comment)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                p['id'],
                r.get("reviewerName", "Anônimo"),
                r.get("reviewerEmail", "sememail@dominio.com"),
                r.get("rating", 0),
                r.get("comment", "")
            ))

    con.commit()
    con.close()
    print("\nImportação concluída com sucesso!\n")


# LISTAR TODOS OS PRODUTOS


def listar_produtos() -> None:
    """Lista todos os produtos com categoria e marca associadas."""
    con = conectar()
    cur = con.cursor()
    cur.execute("""
        SELECT p.title, p.description, p.price, c.name, b.name
        FROM products p
        JOIN categories c ON p.category_id = c.id
        JOIN brands b ON p.brand_id = b.id
    """)
    for row in cur.fetchall():
        print(f"\nProduto: {row[0]}\nDescricao: {row[1]}\nPreco: {row[2]} €\nCategoria: {row[3]}\nMarca: {row[4]}\n")
    input("ENTER para continuar...")
    con.close()


# CONSULTAR PRODUTO POR NOME


def consulta_produto() -> None:
    """Pesquisa produtos pelo nome (título) informado pelo utilizador."""
    nome = input("Nome do produto: ")
    con = conectar()
    cur = con.cursor()
    cur.execute("""
        SELECT p.title, p.description, p.price, c.name, b.name
        FROM products p
        JOIN categories c ON p.category_id = c.id
        JOIN brands b ON p.brand_id = b.id
        WHERE LOWER(p.title) LIKE %s
    """, (f"%{nome.lower()}%",))
    for row in cur.fetchall():
        print(f"\nProduto: {row[0]}\nDescricao: {row[1]}\nPreco: {row[2]} €\nCategoria: {row[3]}\nMarca: {row[4]}\n")
    input("ENTER para continuar...")
    con.close()


# VER REVIEWS DE UM PRODUTO


def reviews_produto() -> None:
    """Mostra as reviews de um produto pesquisado pelo nome."""
    nome = input("Nome do produto: ")
    con = conectar()
    cur = con.cursor()
    cur.execute("SELECT id FROM products WHERE LOWER(title) LIKE %s", (f"%{nome.lower()}%",))
    row = cur.fetchone()
    if row:
        cur.execute("SELECT reviewerName, rating, comment FROM reviews WHERE product_id = %s", (row[0],))
        for r in cur.fetchall():
            print(f"\n{r[0]} deu nota {r[1]}\nComentário: {r[2]}")
    else:
        print("Produto não encontrado.")
    input("ENTER para continuar...")
    con.close()


# FILTRAR PRODUTOS POR MARCA


def listar_por_marca() -> None:
    """Lista produtos filtrados por marca."""
    marca = input("Nome da marca: ")
    con = conectar()
    cur = con.cursor()
    cur.execute("""
        SELECT p.title, p.price FROM products p
        JOIN brands b ON p.brand_id = b.id
        WHERE LOWER(b.name) = %s
    """, (marca.lower(),))
    for r in cur.fetchall():
        print(f"{r[0]} - {r[1]} €")
    input("ENTER para continuar...")
    con.close()


# FILTRAR PRODUTOS POR CATEGORIA


def listar_por_categoria() -> None:
    """Lista produtos filtrados por categoria."""
    cat = input("Nome da categoria: ")
    con = conectar()
    cur = con.cursor()
    cur.execute("""
        SELECT p.title, p.price FROM products p
        JOIN categories c ON p.category_id = c.id
        WHERE LOWER(c.name) = %s
    """, (cat.lower(),))
    for r in cur.fetchall():
        print(f"{r[0]} - {r[1]} €")
    input("ENTER para continuar...")
    con.close()


# FILTRAR PRODUTOS POR INTERVALO DE PREÇO


def listar_por_preco() -> None:
    """Lista produtos cujo preço está dentro do intervalo indicado."""
    min_p = float(input("Preco minimo: "))
    max_p = float(input("Preco maximo: "))
    con = conectar()
    cur = con.cursor()
    cur.execute("SELECT title, price FROM products WHERE price BETWEEN %s AND %s", (min_p, max_p))
    for p in cur.fetchall():
        print(f"{p[0]} - {p[1]} €")
    input("ENTER para continuar...")
    con.close()


# MÉDIA DE RATING POR PRODUTO


def listar_rating() -> None:
    """Lista a média de rating (avaliação) de cada produto com reviews."""
    con = conectar()
    cur = con.cursor()
    cur.execute("""
        SELECT p.title, AVG(r.rating)
        FROM products p
        JOIN reviews r ON p.id = r.product_id
        GROUP BY p.id
    """)
    for r in cur.fetchall():
        print(f"{r[0]} - Rating: {round(r[1],1)}")
    input("ENTER para continuar...")
    con.close()


# VER REVIEWS DE UM UTILIZADOR


def reviews_por_user() -> None:
    """Lista as reviews feitas por um utilizador (nome ou email)."""
    user = input("Nome ou email do utilizador: ").lower()
    con = conectar()
    cur = con.cursor()
    cur.execute("""
        SELECT p.title, r.rating, r.comment
        FROM reviews r
        JOIN products p ON p.id = r.product_id
        WHERE LOWER(r.reviewerName) = %s OR LOWER(r.reviewerEmail) = %s
    """, (user, user))
    for r in cur.fetchall():
        print(f"Produto: {r[0]} | Nota: {r[1]}\nComentário: {r[2]}\n")
    input("ENTER para continuar...")
    con.close()


# EXPORTAR PRODUTOS PARA JSON


def exportar_json() -> None:
    """Exporta todos os produtos da BD para um ficheiro JSON, com nomes de coluna."""
    con = conectar()
    cur = con.cursor()
    cur.execute("SELECT id, title, description, price, category_id, brand_id FROM products")
    colunas = [c[0] for c in cur.description]
    produtos = [dict(zip(colunas, linha)) for linha in cur.fetchall()]
    with open("produtos.json", "w", encoding="utf-8") as f:
        json.dump(produtos, f, indent=4, ensure_ascii=False)
    con.close()
    print("Exportação JSON feita com sucesso: produtos.json")


def exportar_csv() -> None:
    """Exporta todos os produtos, com categoria e marca, para um ficheiro CSV."""
    con = conectar()
    cur = con.cursor()
    cur.execute("""
        SELECT p.id, p.title, p.description, p.price, c.name, b.name
        FROM products p
        JOIN categories c ON p.category_id = c.id
        JOIN brands b ON p.brand_id = b.id
    """)
    linhas = cur.fetchall()
    con.close()
    with open("produtos.csv", "w", newline="", encoding="utf-8") as f:
        escritor = csv.writer(f)
        escritor.writerow(["id", "titulo", "descricao", "preco", "categoria", "marca"])
        escritor.writerows(linhas)
    print("Exportação CSV feita com sucesso: produtos.csv")

# inserir categoria

def inserir_categoria() -> None:
    """Insere uma nova categoria na base de dados."""
    nome = input("Nome da nova categoria: ")
    con = conectar()
    cur = con.cursor()
    cur.execute("INSERT IGNORE INTO categories(name) VALUES (%s)", (nome,))
    con.commit()
    con.close()
    print("Categoria inserida com sucesso!")
 
#inseir marcar 

def inserir_marca() -> None:
    """Insere uma nova marca na base de dados."""
    
    
    nome = input("Nome da nova marca: ")
    con = conectar()
    cur = con.cursor()
    cur.execute("INSERT IGNORE INTO brands(name) VALUES (%s)", (nome,))
    con.commit()
    con.close()
    print("Marca inserida com sucesso!")
 

#INSERIR PRODUTO

def inserir_produto() -> None:
    """Regista um novo produto, criando categoria/marca se necessário."""
    try:
     
       title = input("Título do produto: ")
       description = input("Descrição: ")
       while True:  
            price = input("Preço: ").strip()
            if price.isdigit() and float(price) > 0: 
                price = int(price)
                break
            print("Insira apenas Numeros")
      
       categoria = input("Categoria: ")
       marca = input("Marca: ")
    
       con = conectar()
       cur = con.cursor()
       cur.execute("INSERT IGNORE INTO categories(name) VALUES (%s)", (categoria,))
       cur.execute("SELECT id FROM categories WHERE name=%s", (categoria,))
       categoria_id = cur.fetchone()[0]
       cur.execute("INSERT IGNORE INTO brands(name) VALUES (%s)", (marca,))
       cur.execute("SELECT id FROM brands WHERE name=%s", (marca,))
       marca_id = cur.fetchone()[0]
 
       cur.execute("INSERT INTO products(title, description, price, category_id, brand_id) VALUES (%s, %s, %s, %s, %s)",
                (title, description, price, categoria_id, marca_id))
       con.commit()
       con.close()
       print("Produto inserido com sucesso!")
    except Exception as erro:
        print(f"❌ Erro ao inserir produto: {erro}")
        
        
    

#iNSERIR REVIEW

def inserir_review() -> None:
    """Regista uma nova review associada a um produto existente."""
    try:
        produto = input("Nome do produto para a review: ")
        con = conectar()
        cur = con.cursor()
        cur.execute("SELECT id FROM products WHERE LOWER(title)=%s", (produto.lower(),))
        prod = cur.fetchone()

        if not prod:
            print("Produto não encontrado.")
            con.close()
            return

        reviewer = input("Nome do utilizador: ")
        email = input("Email do utilizador: ")

        while True:
            rating = input("Rating (0 a 5): ")
            if rating.replace(".", "", 1).isdigit() and 0 <= float(rating) <= 5:
                rating = float(rating)
                break
            else:
                print("Insira um número válido entre 0 e 5.")

        comment = input("Comentário: ")

        cur.execute("""INSERT INTO reviews(product_id, reviewerName, reviewerEmail, rating, comment)
                       VALUES (%s, %s, %s, %s, %s)""", (prod[0], reviewer, email, rating, comment))

        con.commit()
        con.close()
        print("Review adicionada com sucesso!")

    except Exception as erro:
        print(f"Ocorreu um erro ao adicionar a review: {erro}")

#REMOVER PRODUTO

def remover_produto() -> None:
    """Remove um produto pelo nome (título)."""
    nome = input("Nome do produto a remover: ")
    con = conectar()
    cur = con.cursor()
    cur.execute("DELETE FROM products WHERE LOWER(title)=%s", (nome.lower(),))
    con.commit()
    con.close()
    print("Produto removido com sucesso!")
 

#remover categoria


def remover_categoria() -> None:
    """Remove uma categoria pelo nome."""
    nome = input("Nome da categoria a remover: ")
    con = conectar()
    cur = con.cursor()
    cur.execute("DELETE FROM categories WHERE LOWER(name)=%s", (nome.lower(),))
    con.commit()
    con.close()
    print("Categoria removida com sucesso!")
 
# remover marca 
 
def remover_marca() -> None:
    """Remove uma marca pelo nome."""
    nome = input("Nome da marca a remover: ")
    con = conectar()
    cur = con.cursor()
    cur.execute("DELETE FROM brands WHERE LOWER(name)=%s", (nome.lower(),))
    con.commit()
    con.close()
    print("Marca removida com sucesso!")
 

#remover review



def remover_review() -> None:
    """Remove review(s) pelo email do autor."""
    email = input("Email do utilizador da review: ")
    con = conectar()
    cur = con.cursor()
    cur.execute("DELETE FROM reviews WHERE LOWER(reviewerEmail)=%s", (email.lower(),))
    con.commit()
    con.close()
    print("Review(s) removida(s) com sucesso!")
 
# MENU PRINCIPAL
 
def submenu_consultar() -> None:
    """Submenu de consultas gerais sobre produtos (listagem, pesquisa e ratings)."""
    opcao = select([
        "Listar todos os produtos", "Consultar produto por nome",
        "Listar ratings", "Voltar"
    ], cursor="👉 ", return_index=True)
    match opcao:
        case 0: listar_produtos()
        case 1: consulta_produto()
        case 2: listar_rating()
        case 3: pass


def submenu_filtrar() -> None:
    """Submenu de filtragem de produtos (marca, categoria e preço)."""
    opcao = select([
        "Por marca", "Por categoria", "Por intervalo de preço", "Voltar"
    ], cursor="👉 ", return_index=True)
    match opcao:
        case 0: listar_por_marca()
        case 1: listar_por_categoria()
        case 2: listar_por_preco()
        case 3: pass


def submenu_reviews() -> None:
    """Submenu de consulta de reviews (por produto e por utilizador)."""
    opcao = select([
        "Reviews de um produto", "Reviews de um utilizador", "Voltar"
    ], cursor="👉 ", return_index=True)
    match opcao:
        case 0: reviews_produto()
        case 1: reviews_por_user()
        case 2: pass


def submenu_gestao() -> None:
    """Submenu de gestão de registos (inserir/remover produtos, categorias, marcas e reviews)."""
    opcao = select([
        "Inserir Produto", "Inserir Categoria", "Inserir Marca", "Inserir Review",
        "Remover Produto", "Remover Categoria", "Remover Marca", "Remover Review", "Voltar"
    ], cursor="👉 ", return_index=True)
    match opcao:
        case 0: inserir_produto()
        case 1: inserir_categoria()
        case 2: inserir_marca()
        case 3: inserir_review()
        case 4: remover_produto()
        case 5: remover_categoria()
        case 6: remover_marca()
        case 7: remover_review()
        case 8: pass


def submenu_exportar() -> None:
    """Submenu de exportação de dados (JSON e CSV)."""
    opcao = select([
        "Exportar JSON", "Exportar CSV", "Voltar"
    ], cursor="👉 ", return_index=True)
    match opcao:
        case 0: exportar_json()
        case 1: exportar_csv()
        case 2: pass


def menu() -> None:
    """Ciclo principal do menu interativo da aplicação."""
    criar_tabelas()
    while True:
        limpar()
        print("=== WebStore 🛒 ===")
        escolha = select([
            "Importar API", "Consultar Produtos", "Filtrar Produtos",
            "Reviews", "Gestão de Registos", "Exportar Dados", "Sair"
        ], cursor="👉 ", return_index=True)

        match escolha:
            case 0: importar_api()
            case 1: submenu_consultar()
            case 2: submenu_filtrar()
            case 3: submenu_reviews()
            case 4: submenu_gestao()
            case 5: submenu_exportar()
            case 6:
                print("Programa encerrado.")
                break
if __name__ == "__main__":
    menu()            
