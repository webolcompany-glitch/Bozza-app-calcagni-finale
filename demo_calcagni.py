import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configurazione della pagina
st.set_page_config(page_title="Gestionale E-commerce 2026", layout="wide")
st.title("📊 Dashboard Gestionale E-commerce 2026")
st.markdown("---")

# 2. Caricamento e pulizia dei dati
@st.cache_data
def load_data():
    # Carica ordini
    df_ordini = pd.read_csv("Gestionale 2026.xlsx - Ordini.csv")
    # Gestione formati data misti nel tuo file (YYYY-MM-DD e DD/MM/YYYY)
    df_ordini['Data ordine'] = pd.to_datetime(df_ordini['Data ordine'], errors='coerce', dayfirst=True)
    
    # Rimuove gli spazi extra dai nomi delle colonne (es. 'Utile ')
    df_ordini.columns = df_ordini.columns.str.strip()
    
    # Carica magazzino
    df_magazzino = pd.read_csv("Gestionale 2026.xlsx - Prodotti Magazzino.csv")
    df_magazzino.columns = df_magazzino.columns.str.strip()
    
    return df_ordini, df_magazzino

try:
    df_ordini, df_magazzino = load_data()
except Exception as e:
    st.error(f"Errore nel caricamento dei file CSV. Verifica i nomi. Dettaglio: {e}")
    st.stop()

# 3. Sidebar per i Filtri
st.sidebar.header("🔍 Filtri Avanzati")

marketplace_list = ["Tutti"] + list(df_ordini['Marketplace'].dropna().unique())
selected_marketplace = st.sidebar.selectbox("Seleziona Marketplace", marketplace_list)

paese_list = ["Tutti"] + list(df_ordini['Paese (Mercato)'].dropna().unique())
selected_paese = st.sidebar.selectbox("Seleziona Paese", paese_list)

stato_list = ["Tutti"] + list(df_ordini['Stato ordine'].dropna().unique())
selected_stato = st.sidebar.selectbox("Stato dell'ordine", stato_list)

# Applicazione filtri al dataframe ordini
df_filtered = df_ordini.copy()
if selected_marketplace != "Tutti":
    df_filtered = df_filtered[df_filtered['Marketplace'] == selected_marketplace]
if selected_paese != "Tutti":
    df_filtered = df_filtered[df_filtered['Paese (Mercato)'] == selected_paese]
if selected_stato != "Tutti":
    df_filtered = df_filtered[df_filtered['Stato ordine'] == selected_stato]

# 4. Creazione dei Tab principali
tab1, tab2, tab3 = st.tabs(["💰 Performance Finanziarie", "📦 Analisi Prodotti", "🚨 Allert Riordino Magazzino"])

# ---- TAB 1: PERFORMANCE FINANZIARIE ----
with tab1:
    st.subheader("Metriche Chiave (Periodo Selezionato)")
    
    # Calcolo metriche
    fatturato_lordo = df_filtered['Fatturato (Lordo)'].sum()
    costo_totale = df_filtered['Costo totale'].sum()
    utile_totale = df_filtered['Utile'].sum()
    margine = (utile_totale / fatturato_lordo * 100) if fatturato_lordo > 0 else 0
    
    # Visualizzazione KPI in colonne
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Fatturato Lordo", f"€ {fatturato_lordo:,.2f}")
    col2.metric("Costo Totale", f"€ {costo_totale:,.2f}", delta_color="inverse")
    col3.metric("Utile Netto stimato", f"€ {utile_totale:,.2f}")
    col4.metric("Margine Medio", f"{margine:.2f}%")
    
    st.markdown("### Analisi Canali di Vendita")
    g1, g2 = st.columns(2)
    
    # Grafico 1: Fatturato per Marketplace
    fig_market = px.pie(df_filtered, values='Fatturato (Lordo)', names='Marketplace', 
                        title="Quota di Fatturato per Marketplace", hole=0.4,
                        color_discrete_sequence=px.colors.qualitative.Pastel)
    g1.plotly_chart(fig_market, use_container_width=True)
    
    # Grafico 2: Trend temporale fatturato
    df_trend = df_filtered.groupby('Data ordine')['Fatturato (Lordo)'].sum().reset_index()
    fig_trend = px.line(df_trend, x='Data ordine', y='Fatturato (Lordo)', 
                        title="Andamento delle Vendite nel Tempo",
                        labels={'Fatturato (Lordo)': 'Fatturato (€)', 'Data ordine': 'Data'})
    g2.plotly_chart(fig_trend, use_container_width=True)

# ---- TAB 2: ANALISI PRODOTTI ----
with tab2:
    st.subheader("Performance dei Prodotti")
    
    # Top prodotti per utile
    df_prod = df_filtered.groupby('Prodotto (SKU o nome)')[['Quantità ordinata', 'Fatturato (Lordo)', 'Utile']].sum().reset_index()
    df_top_utile = df_prod.sort_values(by='Utile', ascending=False).head(10)
    
    fig_prod = px.bar(df_top_utile, x='Utile', y='Prodotto (SKU o nome)', orientation='h',
                      title="Top 10 Prodotti per Utile Generato",
                      labels={'Utile': 'Utile Netto (€)'},
                      color='Utile', color_continuous_scale='Greens')
    st.plotly_chart(fig_prod, use_container_width=True)
    
    # Focus sui prodotti "DA EVITARE"
    st.markdown("### ⚠️ Prodotti Critici (Segnalati come DA EVITARE)")
    df_evitare = df_filtered[df_filtered['Decisione'] == 'DA EVITARE'][['Data ordine', 'Marketplace', 'Prodotto (SKU o nome)', 'Utile', 'Note']].dropna(subset=['Prodotto (SKU o nome)'])
    if not df_evitare.empty:
        st.dataframe(df_evitare, use_container_width=True)
    else:
        st.success("Nessun prodotto critico o in perdita nel filtro selezionato!")

# ---- TAB 3: ALLERT RIORDINO MAGAZZINO ----
with tab3:
    st.subheader("🚨 Prodotti in Esaurimento - Ordini Fornitore Immediati")
    st.markdown("Filtro estratto direttamente dal foglio di calcolo del magazzino.")
    
    # Mostra solo i prodotti che richiedono azione immediata
    df_riordino = df_magazzino[df_magazzino['Allert Riordino'] == 'ORDINA SUBITO'][
        ['Prodotto (SKU o nome)', 'Stock (A magazzino)', 'Punto di riordino (Stock minimo da avere)', 'Quantità da ordinare', 'Copertura stock (Giorni)']
    ]
    
    if not df_riordino.empty:
        st.warning(f"Ci sono {len(df_riordino)} prodotti sotto la soglia minima critica!")
        st.dataframe(df_riordino.style.background_gradient(subset=['Stock (A magazzino)'], cmap='Reds'), use_container_width=True)
    else:
        st.success("Tutti i prodotti a magazzino hanno una copertura stock ottimale!")
