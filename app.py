
import streamlit as st
import pandas as pd
import re, unicodedata
from difflib import SequenceMatcher

st.set_page_config(page_title="Benedito | Prefeitura de Macaé", page_icon="💬", layout="centered")

ARQUIVO = "Base_Oficial_Benedito_1_1_Piloto.xlsx"

@st.cache_data
def carregar_base():
    df = pd.read_excel(ARQUIVO, sheet_name="Base_Oficial", dtype=str).fillna("")
    return df

def norm(txt):
    txt = unicodedata.normalize("NFKD", str(txt)).encode("ascii","ignore").decode("ascii").lower()
    return re.sub(r"[^a-z0-9\s]", " ", txt)

def tokens(txt):
    return {x for x in norm(txt).split() if len(x) > 2}

def pontuar(pergunta, row):
    q = norm(pergunta)
    qt = tokens(pergunta)
    campos = " ".join([
        row["Órgão / Unidade"], row["Órgão superior / área"],
        row["Palavras-chave / intenções"], row["Bairro"]
    ])
    ct = tokens(campos)
    inter = len(qt & ct)
    score = inter * 4
    # correspondência por frases/palavras-chave
    for kw in str(row["Palavras-chave / intenções"]).split(";"):
        kw = norm(kw).strip()
        if kw and kw in q:
            score += 8
    # similaridade do texto com o nome da unidade
    score += 3 * SequenceMatcher(None, q, norm(row["Órgão / Unidade"])).ratio()
    return score

def campo_pedido(q):
    q = norm(q)
    if any(x in q for x in ["telefone","tel ","numero","ligar","contato"]): return "telefone"
    if any(x in q for x in ["email","e mail","correio eletronico"]): return "email"
    if any(x in q for x in ["horario","abre","fecha","funciona"]): return "horario"
    if any(x in q for x in ["onde fica","endereco","localizacao","localizado"]): return "endereco"
    return "geral"

def resposta(row, pergunta):
    pedido = campo_pedido(pergunta)
    status = row["Status"].strip().lower()
    nome = row["Órgão / Unidade"]
    obs = row["Observações"].strip()

    # Nunca completar campo ausente.
    campos = {
        "telefone": row["Telefone"].strip(),
        "email": row["E-mail"].strip(),
        "horario": row["Horário de atendimento"].strip(),
        "endereco": row["Endereço"].strip()
    }
    if pedido in campos and (not campos[pedido] or "não informado" in norm(campos[pedido]) or "truncad" in norm(campos[pedido])):
        return f"Encontrei **{nome}**, mas a fonte oficial não traz uma informação confiável sobre {pedido}. Para evitar informar algo incorreto, não vou completar esse dado por inferência. Posso informar os outros contatos cadastrados ou encaminhar você à Ouvidoria Geral."

    partes = [f"**{nome}**"]
    if row["Endereço"]: partes.append(f"📍 {row['Endereço']}" + (f", {row['Bairro']}" if row["Bairro"] else ""))
    if row["Horário de atendimento"] and "truncad" not in norm(row["Horário de atendimento"]): partes.append(f"🕒 {row['Horário de atendimento']}")
    if row["Telefone"]: partes.append(f"☎️ {row['Telefone']}")
    if row["WhatsApp"]: partes.append(f"💬 WhatsApp: {row['WhatsApp']}")
    if row["E-mail"]: partes.append(f"✉️ {row['E-mail']}")
    if obs and ("provis" in norm(obs) or "manutenc" in norm(obs)):
        partes.append(f"⚠️ {obs}")
    partes.append(f"Fonte oficial: {row['Fonte oficial']}")
    return "\n\n".join(partes)

df = carregar_base()

st.title("Benedito")
st.caption("Protótipo de assistente virtual da Prefeitura de Macaé — MVP informacional")
st.info("Nesta versão, Benedito responde apenas sobre endereços, horários, telefones, WhatsApp, e-mails e identificação de órgãos/unidades cadastrados na base oficial.")

if "historico" not in st.session_state:
    st.session_state.historico = []

for papel, msg in st.session_state.historico:
    with st.chat_message(papel):
        st.markdown(msg)

pergunta = st.chat_input("Ex.: Onde resolvo problema de ônibus?")
if pergunta:
    st.session_state.historico.append(("user", pergunta))
    with st.chat_message("user"):
        st.markdown(pergunta)

    scores = [(pontuar(pergunta, r), i) for i, r in df.iterrows()]
    scores.sort(reverse=True)
    melhor_score, idx = scores[0]
    row = df.loc[idx]

    # limiar conservador; se não souber, Ouvidoria.
    if melhor_score < 4:
        ouv = df[df["ID"] == "BEN-002"].iloc[0]
        resp = ("Não encontrei uma unidade com segurança suficiente na base do piloto. "
                "Para não direcionar você incorretamente, sugiro a **Ouvidoria Geral do Município**.\n\n"
                + resposta(ouv, pergunta))
    else:
        resp = resposta(row, pergunta)

    st.session_state.historico.append(("assistant", resp))
    with st.chat_message("assistant"):
        st.markdown(resp)

with st.sidebar:
    st.subheader("Sobre o protótipo")
    st.write(f"Base carregada: {len(df)} registros.")
    st.write("Sem IA generativa nesta primeira prova técnica: a recuperação é controlada e auditável.")
    st.write("Isso permite validar intenções, dados e regras de segurança sem custo de API.")
