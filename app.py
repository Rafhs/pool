import streamlit as st
import time

# Importando nossos módulos personalizados
from modules import sheets_connector, ai_handler

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Rotas & Transportes",
    page_icon="🚌",
    layout="centered",
    initial_sidebar_state="expanded"
)

# --- FUNÇÕES DE INTERFACE (UI) ---
def init_session_state():
    """Inicializa o histórico do chat se ele não existir."""
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Olá! 👋 Para onde você deseja ir hoje?"}
        ]
    if "gemini_history" not in st.session_state:
        st.session_state.gemini_history = []

def render_sidebar():
    """Renderiza a barra lateral simplificada."""
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/3448/3448339.png", width=60)
        st.title("Central de Rotas")
        st.markdown("---")

        # Tenta carregar os dados e mostra status simples
        df = sheets_connector.load_data()

        if not df.empty:
            st.success("🟢 Sistema Online")
            st.caption(f"{len(df)} rotas disponíveis.")
        else:
            st.error("🔴 Sistema Offline")
            st.caption("Verifique a conexão.")

        st.markdown("---")
        # Botão para resetar a conversa
        if st.button("🗑️ Nova Pesquisa", use_container_width=True):
            st.session_state.messages = []
            st.session_state.gemini_history = []
            st.rerun()

        return df

def type_writer_effect(text: str, placeholder):
    """Efeito visual de digitação para a resposta da IA."""
    text_buffer = ""
    for chunk in text.split(' '): # Divide por espaços para manter palavras inteiras
        text_buffer += chunk + " "
        placeholder.markdown(text_buffer + "▌")
        time.sleep(0.02)
    placeholder.markdown(text_buffer) # Remove o cursor final

# --- FLUXO PRINCIPAL ---
def main():
    init_session_state()
    df_transportes = render_sidebar()

    st.title("🚌 Agente de Viagens")
    st.caption("Pergunte sobre linhas, ruas ou pontos de referência.")

    # Se a planilha não carregou, interrompe aqui para não quebrar o resto
    if df_transportes.empty:
        st.warning("⚠️ O sistema está temporariamente indisponível.")
        st.stop()

    # Prepara o texto base para a IA
    contexto_dados = sheets_connector.get_formatted_context(df_transportes)

    # Exibe o histórico da conversa na tela
    for msg in st.session_state.messages:
        avatar = "🚍" if msg["role"] == "assistant" else "🧑‍💼"
        st.chat_message(msg["role"], avatar=avatar).write(msg["content"])

    # Captura a nova pergunta do usuário
    if prompt := st.chat_input("Digite sua dúvida..."):
        # Mostra a pergunta do usuário
        st.chat_message("user", avatar="🧑‍💼").write(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Gera e mostra a resposta da IA
        with st.chat_message("assistant", avatar="🚍"):
            placeholder = st.empty()
            placeholder.markdown("🔍 *Buscando informações...*")

            # Chama o Gemini
            full_response = ai_handler.get_gemini_response(
                st.session_state.gemini_history,
                contexto_dados,
                prompt
            )

            # Exibe com efeito
            type_writer_effect(full_response, placeholder)

            # Salva no histórico
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            st.session_state.gemini_history.append({"role": "user", "parts": [prompt]})
            st.session_state.gemini_history.append({"role": "model", "parts": [full_response]})

if __name__ == "__main__":
    main()