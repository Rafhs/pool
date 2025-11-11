import streamlit as st
import pandas as pd
import gspread

@st.cache_data(ttl=600, show_spinner=False)
def load_data() -> pd.DataFrame:
    try:
        service_account = st.secrets.get("gcp_service_account")
        sheet_url = st.secrets.get("SHEET_URL")

        if not service_account or not sheet_url:
            return pd.DataFrame()

        gc = gspread.service_account_from_dict(service_account)
        sh = gc.open_by_url(sheet_url)
        worksheet = sh.get_worksheet(0)

        df = pd.DataFrame(worksheet.get_all_records())
        df = df.astype(str)
        df = df.map(lambda x: x.strip() if isinstance(x, str) else x)
        df = df.replace(['', 'nan', 'None'], 'N/A')

        return df
    except Exception as e:
        print(f"Erro planilha: {e}")
        return pd.DataFrame()

def get_formatted_context(df: pd.DataFrame) -> str:
    if df.empty: return ""

    text = "BASE DE DADOS (LINHA POR LINHA):\n"
    for row in df.itertuples(index=False):
        roteiro = getattr(row, 'ROTEIRO', 'N/A')
        bairro = getattr(row, 'BAIRRO', 'N/A')
        rua = getattr(row, 'RUA', 'N/A')
        # Garante que pega a referência independente de pequena variação no nome da coluna
        ref = getattr(row, 'PONTO_DE_REFERÊNCIA', getattr(row, 'PONTO_DE_REFERENCIA', 'N/A'))
        cidade = getattr(row, 'CIDADE', 'N/A')

        # AQUI ESTÁ A MUDANÇA CRÍTICA: Mudamos os rótulos de Prioridade
        text += f"| ROTEIRO: {roteiro} | PRIORIDADE 1 (REF): {ref} | PRIORIDADE 2 (RUA): {rua} | PRIORIDADE 3 (BAIRRO): {bairro} | CIDADE: {cidade} |\n"

    return text