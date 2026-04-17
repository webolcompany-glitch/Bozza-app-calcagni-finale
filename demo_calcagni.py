import streamlit as st
import pandas as pd
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import urllib.parse

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="Fuel SaaS", layout="wide", initial_sidebar_state="collapsed")

# =========================
# 🏢 AZIENDA
# =========================
azienda = st.query_params.get("azienda", "demo")
if isinstance(azienda, list):
    azienda = azienda[0]

FILE = f"clienti_{azienda}.csv"

st.markdown(f"""
# ⛽ Fuel SaaS
### 🏢 Azienda: `{azienda.upper()}`
""")

# =========================
# 📧 EMAIL
# =========================
EMAIL_MITTENTE = "webolcompany@gmail.com"
PASSWORD_APP = "neqr ewtb bdkr lmca"

def invia_email(destinatario, prezzo, template, nome=""):
    try:
        data = datetime.now().strftime("%d/%m/%Y")

        testo = template \
            .replace("{prezzo}", f"{prezzo:.3f}") \
            .replace("{nome}", nome) \
            .replace("{data}", data)

        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"OFFERTA CARBURANTE - {data}"
        msg["From"] = EMAIL_MITTENTE
        msg["To"] = destinatario

        msg.attach(MIMEText(testo, "html", "utf-8"))

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL_MITTENTE, PASSWORD_APP)
        server.send_message(msg)
        server.quit()

    except Exception as e:
        st.error(f"Errore email: {e}")

# =========================
# UTILS
# =========================
def format_euro(x):
    if x is None or pd.isna(x):
        return "0,000"
    return f"{round(float(x), 3):.3f}".replace(".", ",")

def calc_price(base, margine, trasporto):
    return round(float(base) + float(margine) + float(trasporto), 3)

def filtra_clienti(df, search):
    if not search:
        return df
    return df[
        df["Nome"].astype(str).str.contains(search, case=False, na=False) |
        df["PIVA"].astype(str).str.contains(search, case=False, na=False) |
        df["Telefono"].astype(str).str.contains(search, case=False, na=False)
    ]

# =========================
# DATA
# =========================
def load_data():
    if os.path.exists(FILE):
        df = pd.read_csv(FILE)

        for col in ["Nome","PIVA","Telefono","Email"]:
            df[col] = df[col].astype(str)

        for col in ["Margine","Trasporto"]:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

        if "UltimoPrezzo" not in df.columns:
            df["UltimoPrezzo"] = None

        return df

    return pd.DataFrame(columns=[
        "ID","Nome","PIVA","Telefono","Email",
        "Margine","Trasporto","UltimoPrezzo"
    ])

def save_data(df):
    df.to_csv(FILE, index=False)

# =========================
# SESSION STATE
# =========================
if "clienti" not in st.session_state:
    st.session_state.clienti = load_data()

if "prezzo_base" not in st.session_state:
    st.session_state.prezzo_base = 1.000

if "email_template" not in st.session_state:
    st.session_state.email_template = """Gentile cliente,<br><br>

<b>Gasolio = {prezzo}/L + IVA</b><br><br>

Offerta valida per la giornata odierna.<br><br>

Cordiali saluti<br>
Long Life Consulting
"""

df = st.session_state.clienti

# =========================
# TABS (UI PULITA)
# =========================
tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "👤 Clienti", "➕ Nuovo"])

# =========================================================
# 📊 DASHBOARD
# =========================================================
with tab1:

    st.markdown("## 📊 Dashboard")

    prezzo_base = st.number_input(
        "⛽ Prezzo base",
        value=float(st.session_state.prezzo_base),
        step=0.001,
        format="%.3f"
    )

    st.session_state.prezzo_base = prezzo_base

    clienti_count = len(df)
    media_margine = round(df["Margine"].mean(), 3) if not df.empty else 0

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("⛽ Base", format_euro(prezzo_base))

    with col2:
        st.metric("👤 Clienti", clienti_count)

    with col3:
        st.metric("📊 Margine medio", format_euro(media_margine))

    st.divider()

    st.markdown("## ✉️ Email")

    with st.expander("⚙️ Modifica template email"):

        st.warning("Non modificare {prezzo}, {nome}, {data} o HTML")

        st.code("{nome} {prezzo} {data}")

        template = st.text_area(
            "Template email",
            value=st.session_state.email_template,
            height=300
        )

        st.session_state.email_template = template

    if st.button("📧 Invia email a tutti"):

        count = 0

        for _, c in df.iterrows():

            if c["Email"] and pd.notna(c["Email"]):

                prezzo = calc_price(prezzo_base, c["Margine"], c["Trasporto"])

                invia_email(c["Email"], prezzo, template, c["Nome"])

                st.session_state.clienti.loc[
                    st.session_state.clienti["ID"] == c["ID"],
                    "UltimoPrezzo"
                ] = prezzo

                count += 1

        save_data(st.session_state.clienti)
        st.success(f"Inviate {count} email")

# =========================================================
# 👤 CLIENTI
# =========================================================
with tab2:

    st.markdown("## 👤 Clienti")

    search = st.text_input("🔍 Cerca cliente")
    df_view = filtra_clienti(df, search)

    for _, c in df_view.iterrows():

        prezzo = calc_price(prezzo_base, c["Margine"], c["Trasporto"])
        ultimo_txt = "Nessun invio" if pd.isna(c["UltimoPrezzo"]) else format_euro(c["UltimoPrezzo"])

        st.markdown(f"""
        ### 👤 {c['Nome']}
        📄 {c['PIVA']}  
        📞 {c['Telefono']}  
        💰 Oggi: **{format_euro(prezzo)} €/L**  
        📌 Ultimo: **{ultimo_txt}**
        """)

        col1, col2, col3 = st.columns(3)

        with col1:

            tel = str(c["Telefono"]).replace("+", "").replace(" ", "")
            data = datetime.now().strftime("%d/%m/%Y")

            msg = st.session_state.email_template \
                .replace("{prezzo}", format_euro(prezzo)) \
                .replace("{nome}", c["Nome"]) \
                .replace("{data}", data)

            wa = f"https://wa.me/{tel}?text={urllib.parse.quote(msg)}"

            st.link_button("📲 WhatsApp", wa)

        with col2:
            if st.button("📧 Email", key=f"mail_{c['ID']}"):
                prezzo_send = calc_price(prezzo_base, c["Margine"], c["Trasporto"])
                invia_email(c["Email"], prezzo_send, template, c["Nome"])
                st.success("Email inviata")

        with col3:
            if st.button("🗑️ Elimina", key=f"del_{c['ID']}"):
                st.session_state.clienti = df[df["ID"] != c["ID"]]
                save_data(st.session_state.clienti)
                st.rerun()

# =========================================================
# ➕ CLIENTE
# =========================================================
with tab3:

    st.markdown("## ➕ Nuovo cliente")

    nome = st.text_input("Nome")
    piva = st.text_input("P.IVA")
    tel = st.text_input("Telefono")
    email = st.text_input("Email")

    margine = st.number_input("Margine", value=0.0)
    trasporto = st.number_input("Trasporto", value=0.0)

    if st.button("💾 Salva"):

        new_id = 1 if df.empty else int(df["ID"].max()) + 1

        new = pd.DataFrame([{
            "ID": new_id,
            "Nome": nome,
            "PIVA": piva,
            "Telefono": tel,
            "Email": email,
            "Margine": margine,
            "Trasporto": trasporto,
            "UltimoPrezzo": None
        }])

        st.session_state.clienti = pd.concat([df, new], ignore_index=True)
        save_data(st.session_state.clienti)

        st.success("Cliente salvato")
        st.rerun()
