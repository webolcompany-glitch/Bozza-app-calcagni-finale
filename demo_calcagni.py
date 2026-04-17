import streamlit as st
import pandas as pd
import os
import smtplib
import re
import json
from email.mime.text import MIMEText
from datetime import datetime

st.set_page_config(page_title="Fuel SaaS", layout="wide")

# =========================
# 🏢 AZIENDA
# =========================
azienda = st.query_params.get("azienda", "demo")
if isinstance(azienda, list):
    azienda = azienda[0]

FILE = f"clienti_{azienda}.csv"
CONFIG_FILE = f"config_{azienda}.json"

st.markdown(f"## 🏢 Azienda: {azienda.upper()}")

# =========================
# 📧 EMAIL CREDENZIALI
# =========================
EMAIL_MITTENTE = "webolcompany@gmail.com"
PASSWORD_APP = "neqr ewtb bdkr lmca"

# =========================
# 📧 EMAIL INVIO
# =========================
def invia_email(destinatario, prezzo, cc=None):
    try:
        data = datetime.now().strftime("%d/%m/%Y")

        prezzo_txt = f"{prezzo:.3f}".replace(".", ",")

        testo = st.session_state.email_template.replace("{prezzo}", prezzo_txt)

        msg = MIMEText(testo)
        msg["Subject"] = f"OFFERTA CARBURANTE - {data}"
        msg["From"] = EMAIL_MITTENTE
        msg["To"] = destinatario

        destinatari = [destinatario]

        if cc:
            msg["Cc"] = cc
            destinatari.append(cc)

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL_MITTENTE, PASSWORD_APP)
        server.send_message(msg, to_addrs=destinatari)
        server.quit()

    except Exception as e:
        st.error(f"Errore email: {e}")

# =========================
# 🔒 UTIL
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
# 💾 CONFIG
# =========================
def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {}

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f)

# =========================
# 💾 DATA
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
# INIT
# =========================
config = load_config()

if "clienti" not in st.session_state:
    st.session_state.clienti = load_data()

if "page" not in st.session_state:
    st.session_state.page = "dashboard"

if "edit_id" not in st.session_state:
    st.session_state.edit_id = None

if "prezzo_base" not in st.session_state:
    st.session_state.prezzo_base = 1.000

if "email_template" not in st.session_state:
    st.session_state.email_template = config.get("email_template", """Gentile cliente,

con la presente le formuliamo la nostra migliore offerta.

Gasolio per autotrazione = {prezzo}/litro + IVA

Cordiali saluti
""")

df = st.session_state.clienti

# =========================
# NAV
# =========================
c1, c2, c3 = st.columns(3)

with c1:
    if st.button("📊 Dashboard", use_container_width=True):
        st.session_state.page = "dashboard"

with c2:
    if st.button("👤 Clienti", use_container_width=True):
        st.session_state.page = "clienti"

with c3:
    if st.button("➕ Nuovo", use_container_width=True):
        st.session_state.page = "cliente"

st.divider()

# =========================
# 📊 DASHBOARD
# =========================
if st.session_state.page == "dashboard":

    st.markdown("## ⛽ Dashboard operativa")

    prezzo_base = st.number_input(
        "⛽ Prezzo base",
        value=float(st.session_state.prezzo_base),
        step=0.001,
        format="%.3f"
    )

    st.session_state.prezzo_base = prezzo_base

    # =========================
    # TEMPLATE EMAIL
    # =========================
    st.markdown("### ✉️ Template Email")

    email_template = st.text_area(
        "Scrivi email (usa {prezzo})",
        value=st.session_state.email_template,
        height=300
    )

    st.session_state.email_template = email_template
    config["email_template"] = email_template
    save_config(config)

    st.info("Usa {prezzo} per inserire il prezzo automaticamente")

    # =========================
    # VALIDAZIONE TEMPLATE
    # =========================
    pattern_numero = r"\b\d+[.,]\d+\b"
    template_senza = email_template.replace("{prezzo}", "")
    numeri = re.findall(pattern_numero, template_senza)

    manca = "{prezzo}" not in email_template

    if manca:
        st.error("❌ Inserire {prezzo}")

    if numeri:
        st.error(f"❌ Rimuovi prezzi manuali: {', '.join(numeri)}")

    blocca = manca or len(numeri) > 0

    # CC EMAIL
    cc_email = st.text_input("📧 CC Email (opzionale)")

    # =========================
    # INVIO MASSIVO
    # =========================
    if st.button("📧 Invia email a tutti", disabled=blocca):

        count = 0

        for _, c in df.iterrows():
            if c["Email"] and pd.notna(c["Email"]):

                prezzo = calc_price(prezzo_base, c["Margine"], c["Trasporto"])

                invia_email(c["Email"], prezzo, cc=cc_email)

                st.session_state.clienti.loc[
                    st.session_state.clienti["ID"] == c["ID"],
                    "UltimoPrezzo"
                ] = prezzo

                count += 1

        save_data(st.session_state.clienti)
        st.success(f"Email inviate: {count}")

# =========================
# 👤 CLIENTI PAGE
# =========================
elif st.session_state.page == "clienti":

    st.markdown("## 👤 Clienti")

    search = st.text_input("🔍 Cerca")
    df_view = filtra_clienti(df, search)

    for _, c in df_view.iterrows():

        ultimo = c["UltimoPrezzo"]
        ultimo_txt = "Nessun invio" if pd.isna(ultimo) else format_euro(ultimo) + " €/L"

        st.markdown(f"""
        ### {c['Nome']}
        📄 {c['PIVA']}  
        📞 {c['Telefono']}  
        💰 Ultimo: {ultimo_txt}
        """)

        col1, col2 = st.columns(2)

        with col1:
            if st.button("✏️ Modifica", key=f"edit_{c['ID']}"):
                st.session_state.edit_id = c["ID"]
                st.session_state.page = "cliente"

        with col2:
            if st.button("🗑️ Elimina", key=f"del_{c['ID']}"):
                st.session_state.clienti = df[df["ID"] != c["ID"]]
                save_data(st.session_state.clienti)
                st.rerun()

# =========================
# ➕ CLIENTE
# =========================
elif st.session_state.page == "cliente":

    st.markdown("## ➕ Cliente")

    editing = st.session_state.edit_id is not None

    if editing:
        c = df[df["ID"] == st.session_state.edit_id].iloc[0]
    else:
        c = {"Nome":"","PIVA":"","Telefono":"","Email":"","Margine":0.0,"Trasporto":0.0}

    nome = st.text_input("Nome", value=c["Nome"])
    piva = st.text_input("P.IVA", value=c["PIVA"])
    tel = st.text_input("Telefono", value=c["Telefono"])
    email = st.text_input("Email", value=c["Email"])

    margine = st.number_input("Margine", value=float(c["Margine"]), step=0.001)
    trasporto = st.number_input("Trasporto", value=float(c["Trasporto"]), step=0.001)

    if st.button("💾 Salva"):

        if editing:
            idx = st.session_state.clienti["ID"] == st.session_state.edit_id

            st.session_state.clienti.loc[idx, "Nome"] = nome
            st.session_state.clienti.loc[idx, "PIVA"] = piva
            st.session_state.clienti.loc[idx, "Telefono"] = tel
            st.session_state.clienti.loc[idx, "Email"] = email
            st.session_state.clienti.loc[idx, "Margine"] = margine
            st.session_state.clienti.loc[idx, "Trasporto"] = trasporto

            st.session_state.edit_id = None

        else:
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
        st.success("Salvato")
        st.session_state.page = "clienti"
        st.rerun()
