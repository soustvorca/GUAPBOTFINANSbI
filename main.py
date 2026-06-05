import os
# Очищаем переменные окружения, чтобы httpx не пытался использовать несовместимый socks4 прокси
os.environ.pop('HTTP_PROXY', None)
os.environ.pop('HTTPS_PROXY', None)
os.environ.pop('ALL_PROXY', None)
os.environ.pop('http_proxy', None)
os.environ.pop('https_proxy', None)
os.environ.pop('all_proxy', None)
import logging
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ConversationHandler
import database
import handlers

# ================= НАСТРОЙКИ =================
BOT_TOKEN = "токенбота,свой не дам"

# Настройка логирования (чтобы видеть, что происходит, в черном окошке)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def main() -> None:
    """Запуск бота."""
    # 1. Инициализируем базу данных
    database.init_db()
    
    # 2. Создаем приложение
    application = Application.builder().token(BOT_TOKEN).build()
    
    # 3. Настраиваем машину состояний (ConversationHandler)
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler('start', handlers.start),
            CallbackQueryHandler(handlers.button_handler, pattern='^(add_expense|show_stats|show_categories|cancel)$')
        ],
        states={
            handlers.CHOOSING_CATEGORY: [
                CallbackQueryHandler(handlers.category_selected, pattern='^(' + '|'.join(handlers.CATEGORIES) + ')$')
            ],
            handlers.ENTERING_AMOUNT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.amount_entered)
            ],
        },
        fallbacks=[CommandHandler('cancel', handlers.cancel)],
        allow_reentry=True
    )
    
    # 4. Добавляем обработчики в приложение
    application.add_handler(conv_handler)
    
    # 5. Запускаем бота
    logger.info("Бот успешно запущен! Ожидаю сообщений...")
    application.run_polling()

if __name__ == '__main__':
    main()