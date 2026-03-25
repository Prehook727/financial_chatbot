import os
import asyncio
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackContext, ContextTypes
from llm_client import call_llm_api  
from db_client import write_bot_log  # write logs
from bot_functions import get_realtime_risk_data,get_industry

load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
LLM_MODEL = os.getenv("LLM_MODEL", "chatgpt_hkbu")  

# start command
async def start(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    response = "Hello,I am a financial AI assistant.\nSupported Commands:\n/risk - market risk analysis\n/industry - industry configuration recommendation\nSend any text to get financial questions answered"
    await update.message.reply_text(response)   
    asyncio.create_task(log_async(user_id, "/start", response, LLM_MODEL))

# risk analysis
async def risk_analysis(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    user_message = "/risk"
    prompt = get_realtime_risk_data()
    bot_response = call_llm_api(prompt, model=LLM_MODEL)
    await update.message.reply_text(bot_response)
    
    asyncio.create_task(log_async(user_id, user_message, bot_response, LLM_MODEL))

# industry configuration recommendation
async def industry_recommend(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    user_message = "/industry"
    prompt = await get_industry()
    bot_response = call_llm_api(prompt, model=LLM_MODEL)
    await update.message.reply_text(bot_response)
    
    asyncio.create_task(log_async(user_id, user_message, bot_response, LLM_MODEL))

#新闻信息
async def news(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    user_message = "/news"
    prompt = "Analyze global market sentiment (BULLISH/BEARISH/NEUTRAL) + score 0-10, 1 sentence."
    bot_response = call_llm_api(prompt, model=LLM_MODEL)
    await update.message.reply_text(bot_response)
    
    asyncio.create_task(log_async(user_id, user_message, bot_response, LLM_MODEL))


#NLP 
async def handle_message(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    user_message = update.message.text
    prompt = f"As a financial AI agent, answer the following question in simple:  {user_message}"
    temp_msg = await update.message.reply_text("Processing...")
    bot_response = call_llm_api(prompt, model=LLM_MODEL)
    await temp_msg.edit_text(bot_response)
    
    
    asyncio.create_task(log_async(user_id, user_message, bot_response, LLM_MODEL))

# async logs
async def log_async(user_id, user_message, bot_response, llm_model):
    try:
        write_bot_log(user_id, user_message, bot_response, llm_model)
    except Exception as e:
        print(f"log_async failed:{e}")


def main():
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    # register commands
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("risk", risk_analysis))
    application.add_handler(CommandHandler("industry", industry_recommend))
    application.add_handler(CommandHandler("news", news))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    # start bot
    application.run_polling()

if __name__ == "__main__":
    main()