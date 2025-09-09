import io
import unicodedata
import requests
import pandas as pd
import streamlit as st

# =========================
# CONFIG GERAL + TEMA
# =========================
st.set_page_config(
    page_title="Super Preços", 
    page_icon="🛒", 
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
ECONOMY = "#4CAF50"      # Verde para melhor preço

# URL da planilha atualizada
DATA_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTQuWn9iSZkiuiaA5--9CSqfJ6NBxrCK_ClWfKH_es49sSWQkVEvkIB0h6Ow0EKZkHBwhN7IveSW7LR/pub?gid=1059501700&single=true&output=csv"

# CSS com a mesma identidade visual do TOP Preços
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

.stTextInput > div > div > input:focus {{
  border-color: var(--accent) !important;
  box-shadow: 0 0 0 3px rgba(107, 182, 255, 0.2) !important;
  outline: none !important;
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

.best-price-badge {{
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
                <span class="best-price-badge">🏆 Melhor Preço</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

# =========================
# INTERFACE PRINCIPAL
# =========================

st.markdown("""
<div class="main-header">
    <h1>🛒 Super Preços</h1>
    <div class="subtitle">Compare preços entre supermercados e economize</div>
</div>
""", unsafe_allow_html=True)

# Carrega dados
try:
    df_raw = load_from_google_sheets(DATA_URL)
    if df_raw.empty:
        st.error("Nenhum dado encontrado na planilha.")
        st.stop()
        
    df = padronizar_colunas(df_raw)
    if df.empty:
        st.error("Erro ao processar dados da planilha.")
        st.stop()
        
    st.success("✅ Dados carregados com sucesso!")
    
except Exception as e:
    st.error(f"❌ Erro ao carregar dados: {e}")
    st.stop()

# Container de busca
st.markdown('<div class="search-container">', unsafe_allow_html=True)
busca = st.text_input("🔍 Pesquisar produto", placeholder="Digite o nome do produto (ex: Arroz, Feijão, Óleo...)")
st.markdown('</div>', unsafe_allow_html=True)

# Filtra resultados
if busca:
    resultado = df[df["produto_norm"].str.contains(norm(busca), na=False)]
else:
    resultado = df.copy()

# Exibição dos resultados
if resultado.empty:
    st.markdown("""
    <div style="text-align: center; padding: 40px; background: var(--card); border-radius: 15px; margin: 20px 0;">
        <h3 style="color: var(--muted);">🔍 Nenhum produto encontrado</h3>
        <p style="color: var(--muted);">Tente buscar por outro termo ou verifique a ortografia.</p>
    </div>
    """, unsafe_allow_html=True)
else:
    # Ordenar por produto e depois por preço
    resultado = resultado.sort_values(['Produto', 'Valor'])
    
    st.markdown(f"### 📋 Melhores Preços ({len(resultado)} produtos)")
    render_cards_mobile(resultado[["Produto", "Mercado", "Valor", "produto_norm"]])

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: var(--muted); padding: 20px;">
    📊 Dados atualizados automaticamente do Google Sheets<br>
    🔄 Última atualização em cache: 2 minutos<br>
    📱 Interface otimizada para dispositivos móveis
</div>
""", unsafe_allow_html=True)