'''
This program requires the following modules:
- python-telegram-bot==22.5
- urllib3==2.6.2
'''
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
import configparser
import logging
from llm_client import call_llm_api  # 修改：使用新的LLM客户端

def main():
    # Configure logging so you can see initialization and error messages
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)
    
    # Load the configuration data from file
    logging.info('INIT: Loading configuration...')
    config = configparser.ConfigParser()
    config.read('config.ini')

    # Create an Application for your bot
    logging.info('INIT: Connecting the Telegram bot...')
    app = ApplicationBuilder().token(config['TELEGRAM']['ACCESS_TOKEN']).build()

    # Register a message handler
    logging.info('INIT: Registering the message handler...')
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, callback))

    # Start the bot
    logging.info('INIT: Initialization done!')
    app.run_polling()


async def callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # await update.message.reply_text(response)
    logging.info("UPDATE: " + str(update))
    loading_message = await update.message.reply_text('Thinking...')

    # send the user message to the LLM client with FinGPT model
    # 修改：使用新的LLM客户端调用FinGPT模型
    response = call_llm_api(prompt=update.message.text, model="fingpt")

    # send the response to the Telegram box client
    await loading_message.edit_text(response)
if __name__ == '__main__':
    main()