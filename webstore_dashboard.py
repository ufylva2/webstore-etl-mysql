import mysql.connector
import pandas as pd
import plotly.express as px
import streamlit as st

from config import DB_CONFIG

# Configuração inicial da página do Streamlit
st.set_page_config(
    page_title="WebStore Analytics",
    page_icon="📦",
    layout="wide"
)


# ---------------------------------------------------------------------------
# Acesso a dados
# ---------------------------------------------------------------------------

def executar_query(query: str) -> pd.DataFrame:
    """Abre uma ligação à BD, executa uma query SELECT e devolve o resultado."""
    conn = mysql.connector.connect(**DB_CONFIG)
    try:
        return pd.read_sql(query, conn)
    finally:
        conn.close()


@st.cache_data(ttl=300, show_spinner="A carregar catálogo de produtos...")
def carregar_produtos() -> pd.DataFrame:
    """Produtos com categoria e marca associadas, e rating médio (se existir)."""
    query = """
        SELECT p.id, p.title, p.price, c.name AS categoria, b.name AS marca,
               AVG(r.rating) AS rating_medio, COUNT(r.id) AS total_reviews
        FROM products p
        JOIN categories c ON p.category_id = c.id
        JOIN brands b ON p.brand_id = b.id
        LEFT JOIN reviews r ON r.product_id = p.id
        GROUP BY p.id, p.title, p.price, c.name, b.name
    """
    return executar_query(query)


@st.cache_data(ttl=300, show_spinner="A carregar reviews...")
def carregar_reviews() -> pd.DataFrame:
    """Todas as reviews, com o título do produto associado."""
    query = """
        SELECT p.title AS produto, r.reviewerName, r.rating, r.comment
        FROM reviews r
        JOIN products p ON p.id = r.product_id
    """
    return executar_query(query)


# ---------------------------------------------------------------------------
# Carregamento dos dados (com tratamento de erro de ligação à BD)
# ---------------------------------------------------------------------------

try:
    df_produtos = carregar_produtos()
    df_reviews = carregar_reviews()
except mysql.connector.Error as erro:
    st.error(f"❌ Não foi possível ligar à base de dados: {erro}")
    st.info("Confirma que o MySQL está a correr e que já correste 'Importar API' no PL_LUIS.py.")
    st.stop()

if df_produtos.empty:
    st.warning("⚠️ Ainda não existem produtos na base de dados. Corre o PL_LUIS.py e escolhe 'Importar API'.")
    st.stop()

# Sidebar: filtros
st.sidebar.title("📦 WebStore Analytics")
st.sidebar.markdown("Filtros")

categorias_sel = st.sidebar.multiselect(
    "Categorias:",
    options=sorted(df_produtos['categoria'].unique()),
    default=sorted(df_produtos['categoria'].unique())
)
marcas_sel = st.sidebar.multiselect(
    "Marcas:",
    options=sorted(df_produtos['marca'].unique()),
    default=sorted(df_produtos['marca'].unique())
)
preco_min, preco_max = st.sidebar.slider(
    "Intervalo de preço (€):",
    min_value=float(df_produtos['price'].min()),
    max_value=float(df_produtos['price'].max()),
    value=(float(df_produtos['price'].min()), float(df_produtos['price'].max()))
)

if st.sidebar.button("🔄 Atualizar dados"):
    st.cache_data.clear()
    st.sidebar.success("Dados atualizados com sucesso!")
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("Desenvolvido por Luís Fernandes")

# Aplicar filtros
df_filtrado = df_produtos[
    df_produtos['categoria'].isin(categorias_sel)
    & df_produtos['marca'].isin(marcas_sel)
    & df_produtos['price'].between(preco_min, preco_max)
]

# Título principal
st.title("📊 WebStore Product Analytics")
st.caption("Relatório interativo sobre o catálogo importado da API (DummyJSON) para a base de dados.")

if df_filtrado.empty:
    st.warning("⚠️ Nenhum produto corresponde aos filtros selecionados.")
    st.stop()

# KPIs principais
st.subheader("📌 Métricas Globais")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Produtos", f"{len(df_filtrado):,}")
with col2:
    st.metric("Marcas", df_filtrado['marca'].nunique())
with col3:
    st.metric("Preço Médio", f"€{df_filtrado['price'].mean():,.2f}")
with col4:
    rating_medio_geral = df_filtrado['rating_medio'].mean()
    st.metric("Rating Médio", f"{rating_medio_geral:.1f} ⭐" if pd.notna(rating_medio_geral) else "N/D")

st.markdown("---")

tab1, tab2, tab3, tab4 = st.tabs(
    ["🏷️ Categorias & Marcas", "💶 Preços", "⭐ Ratings", "📋 Catálogo"]
)

# Aba 1: Categorias & Marcas
with tab1:
    col1, col2 = st.columns(2)
    with col1:
        contagem_cat = df_filtrado['categoria'].value_counts().reset_index()
        contagem_cat.columns = ['categoria', 'quantidade']
        fig = px.bar(
            contagem_cat, x='quantidade', y='categoria', orientation='h',
            color='quantidade', color_continuous_scale='tealrose',
            title="Nº de Produtos por Categoria"
        )
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        contagem_marca = df_filtrado['marca'].value_counts().reset_index()
        contagem_marca.columns = ['marca', 'quantidade']
        fig = px.pie(
            contagem_marca, values='quantidade', names='marca',
            color_discrete_sequence=px.colors.qualitative.Pastel,
            title="Distribuição de Produtos por Marca"
        )
        st.plotly_chart(fig, use_container_width=True)

# Aba 2: Preços
with tab2:
    col1, col2 = st.columns(2)
    with col1:
        fig = px.histogram(
            df_filtrado, x='price', nbins=20,
            title="Distribuição de Preços",
            labels={'price': 'Preço (€)'}
        )
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        preco_por_cat = df_filtrado.groupby('categoria')['price'].mean().reset_index()
        preco_por_cat = preco_por_cat.sort_values('price', ascending=False)
        fig = px.bar(
            preco_por_cat, x='price', y='categoria', orientation='h',
            color='price', color_continuous_scale='oranges',
            title="Preço Médio por Categoria",
            labels={'price': 'Preço médio (€)'}
        )
        st.plotly_chart(fig, use_container_width=True)

# Aba 3: Ratings
with tab3:
    df_com_rating = df_filtrado.dropna(subset=['rating_medio'])
    if df_com_rating.empty:
        st.info("Ainda não existem reviews para os produtos filtrados.")
    else:
        col1, col2 = st.columns(2)
        with col1:
            top_rating = df_com_rating.sort_values('rating_medio', ascending=False).head(10)
            fig = px.bar(
                top_rating, x='rating_medio', y='title', orientation='h',
                color='rating_medio', color_continuous_scale='blues',
                title="Top 10 Produtos por Rating Médio",
                labels={'rating_medio': 'Rating médio', 'title': 'Produto'}
            )
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            fig = px.scatter(
                df_com_rating, x='price', y='rating_medio', color='categoria',
                size='total_reviews', hover_name='title',
                title="Preço vs. Rating Médio",
                labels={'price': 'Preço (€)', 'rating_medio': 'Rating médio'}
            )
            st.plotly_chart(fig, use_container_width=True)

    if not df_reviews.empty:
        st.subheader("📝 Reviews mais recentes")
        st.dataframe(df_reviews.tail(10), use_container_width=True)

# Aba 4: Catálogo completo (tabela filtrável)
with tab4:
    st.dataframe(
        df_filtrado[['title', 'categoria', 'marca', 'price', 'rating_medio', 'total_reviews']]
        .rename(columns={
            'title': 'Produto', 'categoria': 'Categoria', 'marca': 'Marca',
            'price': 'Preço (€)', 'rating_medio': 'Rating Médio', 'total_reviews': 'Nº Reviews'
        })
        .sort_values('Produto'),
        use_container_width=True
    )
