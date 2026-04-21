import streamlit as st
import pandas as pd
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

st.set_page_config(page_title="Fuel SaaS", layout="wide")

# =========================
# 🏢 AZIENDA
# =========================
azienda = st.query_params.get("azienda", "demo")
if isinstance(azienda, list):
    azienda = azienda[0]

FILE = f"clienti_{azienda}.csv"

st.markdown(f"## 🏢 Azienda: {azienda.upper()}")

# =========================
# 📧 EMAIL
# =========================
EMAIL_MITTENTE = st.secrets["EMAIL_MITTENTE"]
PASSWORD_APP = st.secrets["PASSWORD_APP"]

def invia_email(destinatari, prezzo, template, nome=""):
    try:
        data = datetime.now().strftime("%d/%m/%Y")

        testo = template \
            .replace("{prezzo}", f"{prezzo:.3f}") \
            .replace("{nome}", nome) \
            .replace("{data}", data)

        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"OFFERTA CARBURANTE - {data}"
        msg["From"] = EMAIL_MITTENTE

        # 👉 lista email
        lista_email = [e.strip() for e in destinatari.split(",") if e.strip()]

        if not lista_email:
            return

        msg["To"] = lista_email[0]

        if len(lista_email) > 1:
            msg["Cc"] = ", ".join(lista_email[1:])

        msg.attach(MIMEText(testo, "html", "utf-8"))

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL_MITTENTE, PASSWORD_APP)

        server.sendmail(
            EMAIL_MITTENTE,
            lista_email,
            msg.as_string()
        )

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
if "clienti" not in st.session_state:
    st.session_state.clienti = load_data()

if "page" not in st.session_state:
    st.session_state.page = "dashboard"

if "edit_id" not in st.session_state:
    st.session_state.edit_id = None

if "prezzo_base" not in st.session_state:
    st.session_state.prezzo_base = 1.000

if "email_template" not in st.session_state:
    st.session_state.email_template = """<div style="font-family: Tahoma, Arial, sans-serif; font-size:13px; line-height:1.5; color:#000000;">

Gentile cliente,<br><br>

con la presente le formuliamo la nostra migliore offerta sui prodotti utilizzati dalla Vostra azienda ''ipotizzando'' un presunto scarico per la giornata in oggetto.<br><br>

<b>Gasolio per autotrazione = {prezzo}/litro + Iva</b><br><br>

Per via delle attuali fluttuazioni di mercato i prezzi in elenco avranno una validità giornaliera.<br><br>

Le consegne dei prodotti avverranno entro il giorno dopo alla data di effettuazione dell'ordine.<br><br>

<b>ATTENZIONE!!!</b> GLI ORDINI DOVRANNO PERVENIRE ENTRO LE ORE 14:00 RISPONDENDO ALLA PRESENTE OPPURE CHIAMANDO AL NUMERO DI TELEFONO<br><br>

Rag. Silvio Calcagni - 335/6145323 &nbsp;&nbsp;&nbsp; Luigi Calcagni - 3209364267
<br>
<br>
<br>
<!-- FIRMA -->
<div style="font-family: Arial, sans-serif; font-size:13px; line-height:1.4; color:#2F5496; margin-top:10px;">

<p><b>Long Life Consulting</b></p>

<p>
Luigi Calcagni<br>
<br>
Corso Italia, 46 – 80011 Acerra (NA)
</p>

<p>
Mob: 3209364267<br>
<br>
Info: info@longlifecons.com
</p>
<br>
<br>
<br>
<p>
Wholeses Fuels - Fuel Cards - Coupons<br>
<br>
<b>Agente di</b><br><br>

<img src="https://longlifecons.com/wp-content/Prodotti/Tamoil.svg.png" width="90">
</p>

<p>
Via Andrea Costa, 17 20131 Milano, ITALIA
</p>

<p>
Tel: 800 11 33 30
</p>

</div>

<br>

<!-- DISCLAIMER -->
<div style="font-family: Tahoma, Arial, sans-serif; font-size:10px; color:#000000; line-height:1.4;">
<i>
La presente comunicazione, con le informazioni in essa contenute e ogni documento o file allegato, e' strettamente riservata e soggetta alle garanzie che legano i rapporti tra le parti interessate. E' rivolta unicamente alla/e persona/e cui e' indirizzata ed alle altre da questa autorizzata/e a riceverla. Se non siete i destinatari/autorizzati siete avvisati che qualsiasi azione, copia, comunicazione, divulgazione o simili basate sul contenuto di tali informazioni e' vietata e potrebbe essere contro la legge (art. 616 e seguenti C.P., regolamento UE 2016/679). Se avete ricevuto questa comunicazione per errore, vi preghiamo di darne immediata notizia al mittente a mezzo telefono, fax o e-mail e di distruggere il messaggio originale e ogni file allegato senza farne copia alcuna o riprodurne in alcun modo il contenuto. Grazie. Long Life Consulting.
<br><br>
This e-mail and its attachments are intended for the addressee(s) only and are confidential and/or may contain legally privileged information. If you have received this message by mistake or are not one of the addressees above, you may take no action based on it, and you may not copy or show it to anyone; please reply to this e-mail and point out the error which has occurred. Thank you. Long Life Consulting.
</i>
</div>

</div>
"""
if "wa_template" not in st.session_state:
    st.session_state.wa_template = """Gentile cliente {nome},

con la presente le formuliamo la nostra migliore offerta sui prodotti utilizzati dalla Vostra azienda ''ipotizzando'' un presunto scarico per la giornata di seguito indicata.

Data: {data}

Gasolio per autotrazione = {prezzo}/litro + Iva

Per via delle attuali fluttuazioni di mercato i prezzi in elenco avranno una validità giornaliera.

Le consegne dei prodotti avverranno entro il giorno dopo alla data di effettuazione dell'ordine.

ATTENZIONE!!! GLI ORDINI DOVRANNO PERVENIRE ENTRO LE ORE 14:00 RISPONDENDO ALLA PRESENTE OPPURE CHIAMANDO AL NUMERO DI TELEFONO
Rag. Silvio Calcagni -335/6145323                 Luigi Calcagni - 3209364267

Cordiali saluti
Long Life Consulting
Luigi Calcagni
Corso Italia, 46 – 80011 Acerra (NA)
Mob: 3209364267
Info : info@longlifecons.com
Wholeses Fuels - Fuel Cards - Coupons
Agente di TAMOIL ITALIA S.P.A
"""
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
# CARD
# =========================
def card(title, value):
    return f"""
    <div style="padding:14px;border-radius:14px;background:#111827;
    color:white;text-align:center;margin:6px 0;">
        <div style="font-size:12px;opacity:0.7;">{title}</div>
        <div style="font-size:20px;font-weight:600">{value}</div>
    </div>
    """

# =========================================================
# 📊 DASHBOARD
# =========================================================
if st.session_state.page == "dashboard":

    st.markdown("## ⛽ Dashboard operativa")

    prezzo_base = st.number_input(
        "⛽ Prezzo base",
        value=float(st.session_state.prezzo_base),
        step=0.001,
        format="%.3f"
    )

    st.session_state.prezzo_base = prezzo_base

    clienti_count = len(df)
    media_margine = round(df["Margine"].mean(), 3) if not df.empty else 0

    prezzo_medio = (
        calc_price(prezzo_base, df["Margine"].mean(), df["Trasporto"].mean())
        if not df.empty else prezzo_base
    )

    c1, c2 = st.columns(2)
    c3, c4 = st.columns(2)

    with c1:
        st.markdown(card("⛽ Base", format_euro(prezzo_base)), unsafe_allow_html=True)

    with c2:
        st.markdown(card("👤 Clienti", clienti_count), unsafe_allow_html=True)

    with c3:
        st.markdown(card("📊 Margine medio", format_euro(media_margine)), unsafe_allow_html=True)

    with c4:
        st.markdown(card("💰 Prezzo medio", format_euro(prezzo_medio)), unsafe_allow_html=True)

    st.divider()

    st.markdown("### ✉️ Messaggio Email")
    st.info("""
    ⚠️ ATTENZIONE
    Modifica solo il contenuto del messaggio.
    NON modificare:
    - i tag HTML (es. <b>, <br>, <hr>)
    - le variabili tra parentesi graffe (es. {prezzo}, {nome}, {data})
    
    ✔ Puoi cambiare le frasi liberamente
    ❌ Non cancellare o modificare i simboli tecnici
    """)
        
    template = st.text_area(
        "Modifica il messaggio",
        value=st.session_state.email_template,
        height=300
    )

    st.session_state.email_template = template

    st.divider()

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
        st.success(f"Email inviate: {count}")

    st.markdown("### 👤 Clienti")

    search_dash = st.text_input("🔍 Cerca", key="search_dashboard")
    df_view = filtra_clienti(df, search_dash)

    for _, c in df_view.iterrows():

        prezzo = calc_price(prezzo_base, c["Margine"], c["Trasporto"])

        ultimo = c["UltimoPrezzo"]
        ultimo_txt = "Nessun invio" if pd.isna(ultimo) else format_euro(ultimo) + " €/L"

        st.markdown(f"""
        ### 👤 {c['Nome']}
        📄 P.IVA: {c['PIVA']}  
        💰 Oggi: {format_euro(prezzo)} €/L  
        📌 Ultimo: **{ultimo_txt}**
        """)

        col1, col2, col3 = st.columns(3)

        with col1:
            import urllib.parse

            tel = str(c["Telefono"]).replace("+", "").replace(" ", "")
            data = datetime.now().strftime("%d/%m/%Y")

            msg = st.session_state.wa_template \
                .replace("{prezzo}", format_euro(prezzo)) \
                .replace("{nome}", c["Nome"]) \
                .replace("{data}", data)

            msg_encoded = urllib.parse.quote(msg)

            wa = f"https://wa.me/{tel}?text={msg_encoded}"

            st.link_button("📲 WhatsApp", wa)

        with col2:
            if c["Email"] and pd.notna(c["Email"]):
                if st.button("📧 Email", key=f"mail_{c['ID']}"):

                    prezzo_send = calc_price(prezzo_base, c["Margine"], c["Trasporto"])

                    invia_email(c["Email"], prezzo_send, template, c["Nome"])

                    st.session_state.clienti.loc[
                        st.session_state.clienti["ID"] == c["ID"],
                        "UltimoPrezzo"
                    ] = prezzo_send

                    save_data(st.session_state.clienti)
                    st.success("Email inviata")

        with col3:
            if st.button("🗑️ Elimina", key=f"del_{c['ID']}"):
                st.session_state.clienti = df[df["ID"] != c["ID"]]
                save_data(st.session_state.clienti)
                st.rerun()

# =========================================================
# 👤 CLIENTI PAGE
# =========================================================
elif st.session_state.page == "clienti":

    st.markdown("## 👤 Clienti")

    search = st.text_input("🔍 Cerca cliente")
    df_view = filtra_clienti(df, search)

    for _, c in df_view.iterrows():

        ultimo_txt = "Nessun invio" if pd.isna(c["UltimoPrezzo"]) else format_euro(c["UltimoPrezzo"]) + " €/L"

        st.markdown(f"""
        ### 👤 {c['Nome']}
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
            if st.button("🗑️ Elimina", key=f"del_list_{c['ID']}"):
                st.session_state.clienti = df[df["ID"] != c["ID"]]
                save_data(st.session_state.clienti)
                st.rerun()

        st.divider()

# =========================================================
# ➕ CLIENTE PAGE
# =========================================================
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

    margine = st.number_input("Margine", value=float(c["Margine"]), step=0.001, format="%.3f")
    trasporto = st.number_input("Trasporto", value=float(c["Trasporto"]), step=0.001, format="%.3f")

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
