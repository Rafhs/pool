import streamlit as st
import google.generativeai as genai

try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    MODEL_NAME = 'gemini-pro-latest'
except Exception:
    pass

def get_gemini_response(history_gemini: list, data_context: str, user_question: str) -> str:
    if not data_context:
        return "⚠️ Erro: Base de dados vazia."

    model = genai.GenerativeModel(MODEL_NAME)

    # --- PROMPT COM NOVA HIERARQUIA ---
    system_prompt = f"""
    VOCÊ É: Um assistente de transportes.
    
    NOVA ORDEM DE PRIORIDADE DE BUSCA (Siga estritamente):
    1. PONTO DE REFERÊNCIA (Comece procurando aqui)
    2. RUA
    3. BAIRRO
    (Ignore acentos na comparação)

    MODELO OBRIGATÓRIO DE RESPOSTA:
    Para cada correspondência encontrada, você DEVE estruturar a resposta nesta ordem exata:
    
    * 📍 **PONTO DE REFERÊNCIA:** [Informe a referência encontrada na linha]
      * 🛣️ **Rua:** [Informe a Rua da mesma linha]
      * 🏘️ **Bairro:** [Informe o Bairro da mesma linha]
      * 🚌 **ROTEIRO:** [Número/Nome do Roteiro]

    OBSERVAÇÃO: Mesmo que a busca tenha sido por bairro, mantenha o formato acima, preenchendo os campos com os dados da linha encontrada.

    SE NÃO ENCONTRAR NADA: "Não encontrei informações correspondentes na base de dados."

    --- BASE DE DADOS OFICIAL ---
    {data_context}
    -----------------------------
    """

    chat = model.start_chat(history=history_gemini)

    try:
        response = chat.send_message(f"{system_prompt}\nPERGUNTA DO USUÁRIO: {user_question}")
        return response.text
    except Exception:
        return "Instabilidade momentânea na IA. Tente novamente."