"""Agente de Reciclagem Inteligente com Gemini e Google Search (via Telegram)
"""

from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    raise ValueError("A chave GOOGLE_API_KEY não foi carregada. Verifique seu arquivo .env.")

os.environ["GOOGLE_API_KEY"] = api_key

# SDKs principais
from google import genai
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import google_search
from google.genai import types

# Extras
from IPython.display import Markdown, display
from datetime import date
import textwrap
import warnings
warnings.filterwarnings("ignore")

# Função auxiliar que envia uma mensagem para um agente via Runner e retorna a resposta final
def call_agent(agent: Agent, message_text: str) -> str:
    # Cria um serviço de sessão em memória
    session_service = InMemorySessionService()
    # Cria uma nova sessão (você pode personalizar os IDs conforme necessário)
    session = session_service.create_session(app_name=agent.name, user_id="user1", session_id="session1")
    # Cria um Runner para o agente
    runner = Runner(agent=agent, app_name=agent.name, session_service=session_service)
    # Cria o conteúdo da mensagem de entrada
    content = types.Content(role="user", parts=[types.Part(text=message_text)])

    final_response = ""
    # Itera assincronamente pelos eventos retornados durante a execução do agente
    for event in runner.run(user_id="user1", session_id="session1", new_message=content):
        if event.is_final_response():
          for part in event.content.parts:
            if part.text is not None:
              final_response += part.text
              final_response += "\n"
    return final_response


# Função auxiliar para exibir texto formatado em Markdown no Colab
def to_markdown(text):
  text = text.replace('•', '  *')
  return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))

# Agente de Reciclagem
def agente_reciclagem(pergunta):
    reciclagem = Agent(
        name="agente_reciclagem",
        model="gemini-2.0-flash",
        instruction="""
        Você é um assistente de sustentabilidade. Sua tarefa é responder se um item pode ou não ser reciclado,
        com base em dados atualizados de sites confiáveis e com notório sabers. Use a ferramenta google_search
        para isso.Sua resposta deve ser curta, clara e incluir instruções de descarte no Brasil, se possível.
        Dê a resposta em no máximo 2 frases
        """,
        description="Agente que responde se um item é reciclável ou não.",
        tools=[google_search]
    )

    entrada_do_agente_reciclagem = f"Tópico: {pergunta}"
    item_perguntado = call_agent(reciclagem, entrada_do_agente_reciclagem)
    return item_perguntado

# Agente validador
def agente_validador(pergunta, resposta_reciclagem):
    validador = Agent(
        name="agente_validador",
        model="gemini-2.0-flash",
        instruction="""
        Você é um Revisor Técnico e Especialista em Sustentabilidade.
        Avalie a resposta fornecida por outro agente sobre se um item pode ou não ser reciclado.
        Verifique se a resposta está correta, clara e alinhada com as práticas de descarte no Brasil.
        Se estiver adequada, apenas repita a resposta.
        Caso contrário, corrija e apresente a nova versão da resposta final.
        Não explique o motivo. Apenas retorne a versão final da resposta que o usuário verá.
        """,
        description="Agente que valida a resposta do agente de reciclagem."
    )
    entrada_do_agente_validador = f"Tópico: {pergunta}\nRascunho: {resposta_reciclagem}"
    texto_revisado = call_agent(validador, entrada_do_agente_validador)
    return texto_revisado

# --- Obter o Tópico do Usuário ---
pergunta = input("❓ Por favor, digite o ITEM sobre o qual você quer saber de reciclagem: ")

# Inserir lógica do sistema de agentes ################################################
if not pergunta:
    print("Você esqueceu de digitar um item!")
else:
    print(f"Maravilha! Vamos então avaliar a recilagem de {pergunta}")

    resposta = agente_reciclagem(pergunta)
    #print(f"\n --- ✅ 📝 Resultado do Agente 1 (Reciclagem) --- : {pergunta}\n")
    #display(to_markdown(resposta))
    print("--------------------------------------------------------------")

    validacao = agente_validador(pergunta, resposta)
    print(f"\n🔎📝 Resultado: {validacao} \n")
    #display(to_markdown(validacao))
    print("--------------------------------------------------------------")


