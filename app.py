import io
import unicodedata
import requests
import pandas as pd
import streamlit as st

# =========================
# CONFIG GERAL + TEMA
# =========================
st.set_page_config(
    page_title="TOP Preços", 
    page_icon="🏆", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Paleta baseada no TOP Preços: azuis e verdes
PRIMARY = "#4A90A4"      # Azul principal
SECONDARY = "#5BA05B"    # Verde
ACCENT = "#6BB6FF"       # Azul mais claro
BG = "#1C1C1C"           # Fundo escuro
CARD = "#2A2A2A"         # Cards em cinza escuro
TEXT = "#FFFFFF"         # Texto branco
MUTED = "#B0B0B0"        # Texto mais suave
ECONOMY = "#4CAF50"      # Verde para disponível

# URL da planilha
DATA_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTQuWn9iSZkiuiaA5--9CSqfJ6NBxrCK_ClWfKH_es49sSWQkVEvkIB0h6Ow0EKZkHBwhN7IveSW7LR/pub?gid=1059501700&single=true&output=csv"

# CSS
st.markdown(f"""
<style>
:root {{
  --primary: {PRIMARY};
  --secondary: {SECONDARY};
  --accent: {ACCENT};
  --bg: {BG};
  --card: {CARD};
  --text: {TEXT};
  --muted: {MUTED};
  --economy: {ECONOMY};
}}

* {{ box-sizing: border-box; }}

html, body, [data-testid="stAppViewContainer"] {{
  background: var(--bg) !important; 
  color: var(--text) !important;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
}}

.main-header {{
  background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
  padding: 20px;
  border-radius: 15px;
  margin-bottom: 25px;
  text-align: center;
  box-shadow: 0 2px 15px rgba(74, 144, 164, 0.15);
}}

.main-header h1 {{
  color: white !important;
  font-size: 2.5rem !important;
  font-weight: 800 !important;
  margin: 0 !important;
  text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
}}

.main-header .subtitle {{
  color: rgba(255,255,255,0.9);
  font-size: 1.1rem;
  margin-top: 8px;
  font-weight: 400;
}}

.search-container {{
  background: var(--card);
  padding: 20px;
  border-radius: 15px;
  margin-bottom: 25px;
  border: 1px solid rgba(74, 144, 164, 0.15);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}}

.stTextInput > div > div > input {{
  background: var(--bg) !important;
  color: var(--text) !important;
  border: 2px solid var(--primary) !important;
  border-radius: 25px !important;
  padding: 15px 20px !important;
  font-size: 1.1rem !important;
  font-weight: 500 !important;
}}

.product-card {{
  background: var(--card);
  border-radius: 12px;
  padding: 20px;
  margin: 15px 0;
  border: 1px solid rgba(74, 144, 164, 0.2);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}}

.product-card::before {{
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, var(--primary), var(--secondary));
}}

.product-card:hover {{
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(74, 144, 164, 0.4);
  border-color: var(--primary);
}}

.product-name {{
  font-size: 1.3rem;
  font-weight: 700;
  color: var(--text);
  margin-bottom: 12px;
  line-height: 1.4;
}}

.supplier-info {{
  display: flex;
  align-items: center;
  margin-bottom: 15px;
}}

.supplier-label {{
  background: rgba(74, 144, 164, 0.15);
  color: var(--primary);
  padding: 5px 12px;
  border-radius: 15px;
  font-size: 0.85rem;
  font-weight: 600;
  margin-right: 10px;
  border: 1px solid rgba(74, 144, 164, 0.3);
}}

.available-badge {{
  background: var(--economy);
  color: white;
  padding: 5px 10px;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 4px;
}}

.price-container {{
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(74, 144, 164, 0.1);
  padding: 15px;
  border-radius: 12px;
  margin-top: 15px;
}}

.price-value {{
  font-size: 1.8rem;
  font-weight: 800;
  color: var(--primary);
  text-shadow: 1px 1px 2px rgba(0,0,0,0.2);
}}

.total-card {{
  background: var(--card);
  padding: 30px;
  border-radius: 20px;
  text-align: center;
  border: 2px solid var(--economy);
  box-shadow: 0 8px 25px rgba(76, 175, 80, 0.15);
  margin: 30px auto;
  max-width: 400px;
}}

.total-value {{
  font-size: 3rem;
  font-weight: 900;
  color: var(--economy);
  display: block;
  margin-bottom: 10px;
}}

.total-label {{
  color: var(--muted);
  font-size: 1.2rem;
  font-weight: 600;
  text-transform: uppercase;
}}

.supplier-header {{
  background: var(--primary);
  color: white;
  padding: 15px 20px;
  border-radius: 12px;
  margin: 25px 0 15px 0;
  font-size: 1.2rem;
  font-weight: 700;
  text-align: center;
}}

.quantity-controls {{
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 10px;
}}

.block-container {{
  padding: 20px !important;
  max-width: 100% !important;
}}

@media (max-width: 768px) {{
  .main-header h1 {{
    font-size: 2rem !important;
  }}
  .product-card {{
    margin: 10px 0;
    padding: 15px;
  }}
  .price-value {{
    font-size: 1.5rem;
  }}
}}
</style>
""", unsafe_allow_html=True)

# =========================
# FUNÇÕES
# =========================
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

def format_brl(x):
    if pd.isna(x):
        return "-"
    s = f"{float(x):,.2f}"
    return "R$ " + s.replace(",", "X").replace(".", ",").replace("X", ".")

def norm(s: str) -> str:
    s = str(s or "").strip().lower()
    s = "".join(ch for ch in unicodedata.normalize("NFD", s) if unicodedata.category(ch) != "Mn")
    s = " ".join(s.split())
    return s

@st.cache_data(ttl=120)
def load_from_google_sheets(url: str) -> pd.DataFrame:
    try:
        r = requests.get(url, headers=HEADERS, timeout=25, allow_redirects=True)
        r.raise_for_status()
        return pd.read_csv(io.BytesIO(r.content))
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return pd.DataFrame()

def padronizar_colunas(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
        
    colmap = {c.strip().lower(): c for c in df.columns}

    def pick(*ops):
        for o in ops:
            if o in colmap:
                return colmap[o]
        return None

    c_prod = pick("produto", "item", "descrição", "descricao", "nome")
    c_mkt = pick("mercado", "supermercado", "fornecedor", "loja")
    c_val = pick("valor unitário", "valor unitario", "preço", "preco", "valor", "price")
    
    if not all([c_prod, c_mkt, c_val]):
        st.error("Colunas esperadas não encontradas. Esperado: Produto, Mercado, Valor")
        return pd.DataFrame()

    df = df[[c_prod, c_mkt, c_val]].copy()
    df.columns = ["Produto", "Mercado", "Valor"]
    
    # Limpa valores monetários
    df["Valor"] = (
        df["Valor"].astype(str)
        .str.replace("R$", "", regex=False)
        .str.replace("\u00A0", " ", regex=False)
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
    )
    df["Valor"] = pd.to_numeric(df["Valor"], errors="coerce")
    df = df.dropna(subset=["Produto", "Mercado", "Valor"])
    
    df["produto_norm"] = df["Produto"].apply(norm)
    return df

def render_cards_mobile(df_view: pd.DataFrame):
    for _, row in df_view.iterrows():
        st.markdown(f"""
        <div class="product-card">
            <div class="product-name">{row['Produto']}</div>
            <div class="supplier-info">
                <span class="supplier-label">Supermercado</span>
                <span style="color: var(--muted); font-size: 1.05rem; font-weight: 500;">{row['Mercado']}</span>
            </div>
            <div class="price-container">
                <span class="price-value">{format_brl(row['Valor'])}</span>
                <span class="available-badge">✅ Disponível</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

def render_cards_with_selection(df_view: pd.DataFrame):
    for idx, row in df_view.iterrows():
        with st.container():
            col1, col2 = st.columns([0.1, 0.9])
            
            with col1:
                # Verifica se produto já está selecionado
                product_key = f"{row['Produto']}_{row['Mercado']}"
                selected = st.checkbox("", key=f"product_{idx}", label_visibility="collapsed")
                
            with col2:
                st.markdown(f"""
                <div class="product-card">
                    <div class="product-name">{row['Produto']}</div>
                    <div class="supplier-info">
                        <span class="supplier-label">Supermercado</span>
                        <span style="color: var(--muted); font-size: 1.05rem; font-weight: 500;">{row['Mercado']}</span>
                    </div>
                    <div class="price-container">
                        <span class="price-value">{format_brl(row['Valor'])}</span>
                        <span class="available-badge">✅ Disponível</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            # Gerencia seleção no session state
            if selected:
                if 'selected_products' not in st.session_state:
                    st.session_state.selected_products = {}
                
                st.session_state.selected_products[product_key] = {
                    'Produto': row['Produto'],
                    'Mercado': row['Mercado'],
                    'Valor': row['Valor'],
                    'Quantidade': 1
                }
            else:
                if 'selected_products' in st.session_state and product_key in st.session_state.selected_products:
                    del st.session_state.selected_products[product_key]

# =========================
# CARREGAMENTO DE DADOS
# =========================
try:
    df_raw = load_from_google_sheets(DATA_URL)
    if df_raw.empty:
        st.error("Nenhum dado encontrado na planilha.")
        st.stop()
        
    df = padronizar_colunas(df_raw)
    if df.empty:
        st.error("Erro ao processar dados da planilha.")
        st.stop()
        
except Exception as e:
    st.error(f"❌ Erro ao carregar dados: {e}")
    st.stop()

# =========================
# INTERFACE PRINCIPAL
# =========================

st.markdown("""
<div class="main-header">
    <h1>🏆 TOP Preços</h1>
    <div class="subtitle">Compare preços entre supermercados e economize</div>
</div>
""", unsafe_allow_html=True)

# Navegação por abas
tab1, tab2, tab3 = st.tabs(["🏠 Página Principal", "📝 Minha Lista", "🛒 Lista de Compras"])

with tab1:
    st.success("✅ Dados carregados com sucesso!")
    
    # Container de busca
    st.markdown('<div class="search-container">', unsafe_allow_html=True)
    busca_principal = st.text_input("🔍 Pesquisar produto", placeholder="Digite o nome do produto (ex: Arroz, Feijão, Óleo...)", key="search_main")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Filtra resultados
    if busca_principal:
        resultado_principal = df[df["produto_norm"].str.contains(norm(busca_principal), na=False)]
    else:
        resultado_principal = df.copy()
    
    # Exibição dos resultados
    if resultado_principal.empty:
        st.markdown("""
        <div style="text-align: center; padding: 40px; background: var(--card); border-radius: 15px; margin: 20px 0;">
            <h3 style="color: var(--muted);">🔍 Nenhum produto encontrado</h3>
            <p style="color: var(--muted);">Tente buscar por outro termo ou verifique a ortografia.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        resultado_principal = resultado_principal.sort_values(['Produto', 'Valor'])
        st.markdown(f"### 📋 Lista de Preços ({len(resultado_principal)} produtos)")
        render_cards_mobile(resultado_principal[["Produto", "Mercado", "Valor", "produto_norm"]])

with tab2:
    st.success("✅ Dados carregados com sucesso!")
    st.info("💡 Selecione os produtos que deseja comprar marcando as caixas ao lado de cada item.")
    
    # Container de busca
    st.markdown('<div class="search-container">', unsafe_allow_html=True)
    busca_lista = st.text_input("🔍 Pesquisar produto", placeholder="Digite o nome do produto (ex: Arroz, Feijão, Óleo...)", key="search_list")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Filtra resultados
    if busca_lista:
        resultado_lista = df[df["produto_norm"].str.contains(norm(busca_lista), na=False)]
    else:
        resultado_lista = df.copy()
    
    # Exibição dos resultados com seleção
    if resultado_lista.empty:
        st.markdown("""
        <div style="text-align: center; padding: 40px; background: var(--card); border-radius: 15px; margin: 20px 0;">
            <h3 style="color: var(--muted);">🔍 Nenhum produto encontrado</h3>
            <p style="color: var(--muted);">Tente buscar por outro termo ou verifique a ortografia.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        resultado_lista = resultado_lista.sort_values(['Produto', 'Valor'])
        st.markdown(f"### 📝 Selecionar Produtos ({len(resultado_lista)} produtos)")
        render_cards_with_selection(resultado_lista[["Produto", "Mercado", "Valor", "produto_norm"]])

with tab3:
    if 'selected_products' not in st.session_state or not st.session_state.selected_products:
        st.markdown("""
        <div style="text-align: center; padding: 40px; background: var(--card); border-radius: 15px; margin: 20px 0;">
            <h3 style="color: var(--muted);">🛒 Sua lista está vazia</h3>
            <p style="color: var(--muted);">Vá para "Minha Lista" e selecione os produtos que deseja comprar.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        selected_products = st.session_state.selected_products
        
        # Calcula valor total considerando quantidades
        total_value = sum(item['Valor'] * item['Quantidade'] for item in selected_products.values())
        
        # Card com valor total
        st.markdown(f"""
        <div class="total-card">
            <span class="total-value">{format_brl(total_value)}</span>
            <div class="total-label">Total da Compra</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Agrupa por fornecedor
        produtos_por_fornecedor = {}
        for key, item in selected_products.items():
            fornecedor = item['Mercado']
            if fornecedor not in produtos_por_fornecedor:
                produtos_por_fornecedor[fornecedor] = []
            produtos_por_fornecedor[fornecedor].append((key, item))
        
        # Exibe produtos agrupados por fornecedor
        st.markdown(f"### 🛒 Seus Produtos ({len(selected_products)} itens)")
        
        for fornecedor, produtos in produtos_por_fornecedor.items():
            # Header do fornecedor
            st.markdown(f'<div class="supplier-header">🏪 {fornecedor}</div>', unsafe_allow_html=True)
            
            for product_key, item in produtos:
                col1, col2 = st.columns([0.85, 0.15])
                
                with col1:
                    # Calcula subtotal
                    subtotal = item['Valor'] * item['Quantidade']
                    
                    st.markdown(f"""
                    <div class="product-card">
                        <div class="product-name">{item['Produto']}</div>
                        <div class="supplier-info">
                            <span class="supplier-label">Valor Unit.</span>
                            <span style="color: var(--muted); font-size: 1.05rem; font-weight: 500;">{format_brl(item['Valor'])}</span>
                        </div>
                        <div class="price-container">
                            <span class="price-value">{format_brl(subtotal)}</span>
                            <span class="available-badge">✅ Selecionado</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Controles de quantidade
                    col_qty1, col_qty2, col_qty3, col_qty4 = st.columns([1, 1, 1, 1])
                    
                    with col_qty1:
                        if st.button("➖", key=f"minus_{product_key}"):
                            if item['Quantidade'] > 1:
                                st.session_state.selected_products[product_key]['Quantidade'] -= 1
                                st.rerun()
                    
                    with col_qty2:
                        st.write(f"*Qtd: {item['Quantidade']}*")
                    
                    with col_qty3:
                        if st.button("➕", key=f"plus_{product_key}"):
                            st.session_state.selected_products[product_key]['Quantidade'] += 1
                            st.rerun()
                
                with col2:
                    if st.button("🗑", key=f"remove_{product_key}", help="Remover item"):
                        del st.session_state.selected_products[product_key]
                        st.rerun()

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: var(--muted); padding: 20px;">
    📊 Dados atualizados automaticamente do Google Sheets<br>
    🔄 Última atualização em cache: 2 minutos<br>
    📱 Interface otimizada para dispositivos móveis
</div>
""", unsafe_allow_html=True)