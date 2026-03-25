import os
import asyncio
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackContext
from llm_client import call_llm_api  
from db_client import write_bot_log  # write logs
from bot_functions import get_realtime_risk_data

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

# 消息处理（自然语言问答，满足作业"接受自然语言输入"要求）
async def handle_message(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    user_message = update.message.text
    # 构造Prompt，加入金融场景约束
    prompt = f"As a financial AI agent, answer the following question in simple:  {user_message}"
    
    # 先发送一个临时响应，告知用户正在处理
    temp_msg = await update.message.reply_text("Processing...")
    
    # 调用LLM API
    bot_response = call_llm_api(prompt, model=LLM_MODEL)
    
    # 编辑之前的消息，替换为实际响应
    await temp_msg.edit_text(bot_response)
    
    
    asyncio.create_task(log_async(user_id, user_message, bot_response, LLM_MODEL))

# 异步日志记录
async def log_async(user_id, user_message, bot_response, llm_model):
    try:
        write_bot_log(user_id, user_message, bot_response, llm_model)
    except Exception as e:
        print(f"log_async failed:{e}")

# 主函数
def main():
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    # 注册指令和消息处理器
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("risk", risk_analysis))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    # 直接启动，内部自动管理事件循环
    application.run_polling()

if __name__ == "__main__":
    main()