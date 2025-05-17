# python-telegram-bot-22.1

from telegram import Update
import os
from dotenv import load_dotenv
import asyncio
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from agente_pergunta_reciclavel import agente_reciclagem, agente_validador  # importe seus agentes aqui

load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM\_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Oi! Sou seu assistente de reciclagem. Me pergunte se um item é reciclável.")

#async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
 #   pergunta = update.message.text
  #  await update.message.reply_text(f"Você perguntou: {pergunta}")
  #  print(f"Mensagem recebida: {pergunta}")


async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pergunta = update.message.text
    loop = asyncio.get_event_loop()
    resposta = await loop.run_in_executor(None, agente_reciclagem, pergunta)
    validacao = await loop.run_in_executor(None, agente_validador, pergunta, resposta)
    resposta_final = f"♻️🔍 Resultado \n{validacao.strip()}"
    await update.message.reply_text(resposta_final)
    #print(pergunta)
    #print(validacao)

app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder))
app.run_polling()
