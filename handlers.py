from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
import database
import utils
from datetime import datetime
import os

# Состояния диалога (машина состояний)
CHOOSING_CATEGORY, ENTERING_AMOUNT = range(2)

CATEGORIES = ["Еда", "Транспорт", "Развлечения", "Здоровье", "Коммунальные услуги", "Другое"]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Команда /start"""
    keyboard = [
        [InlineKeyboardButton("➕ Добавить расход", callback_data='add_expense')],
        [InlineKeyboardButton("📊 Статистика за месяц", callback_data='show_stats')],
        [InlineKeyboardButton("📋 Список категорий", callback_data='show_categories')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        f"Привет, {update.effective_user.first_name}! 👋\n"
        "Я помогу тебе контролировать бюджет. Выбери действие:",
        reply_markup=reply_markup
    )
    return CHOOSING_CATEGORY

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка нажатий на кнопки главного меню"""
    query = update.callback_query
    await query.answer()

    if query.data == 'add_expense':
        context.user_data.clear() # Очищаем старые данные
        keyboard = [[InlineKeyboardButton(cat, callback_data=cat)] for cat in CATEGORIES]
        keyboard.append([InlineKeyboardButton("❌ Отмена", callback_data='cancel')])
        
        await query.edit_message_text("Выберите категорию расхода:", reply_markup=InlineKeyboardMarkup(keyboard))
        return CHOOSING_CATEGORY

    elif query.data == 'show_stats':
        user_id = update.effective_user.id
        stats = database.get_monthly_stats(user_id)
        
        if not stats:
            await query.edit_message_text("📭 У вас пока нет записанных расходов.")
            return ConversationHandler.END
            
        total = sum(amount for _, amount in stats)
        text = f"💰 **Общие расходы:** {total} руб.\n\n"
        text += "**По категориям:**\n"
        for category, amount in stats:
            text += f"• {category}: {amount} руб.\n"
            
        await query.edit_message_text(text, parse_mode='Markdown')
        
        # Генерируем и отправляем график
        categories = [row[0] for row in stats]
        amounts = [row[1] for row in stats]
        chart_file = utils.generate_pie_chart(categories, amounts)
        
        with open(chart_file, 'rb') as f:
            await update.effective_user.send_document(document=f, filename="stats.png")
        
        # Удаляем временный файл
        if os.path.exists(chart_file):
            os.remove(chart_file)
            
        return ConversationHandler.END

    elif query.data == 'show_categories':
        text = "📋 Доступные категории:\n" + "\n".join([f"• {cat}" for cat in CATEGORIES])
        await query.edit_message_text(text)
        return ConversationHandler.END

    elif query.data == 'cancel':
        await query.edit_message_text("Действие отменено. Введите /start для начала.")
        return ConversationHandler.END

async def category_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Сохраняем категорию и просим сумму"""
    query = update.callback_query
    await query.answer()
    
    context.user_data['category'] = query.data
    context.user_data['date'] = datetime.now().strftime("%Y-%m-%d")
    
    await query.edit_message_text(f"Вы выбрали: *{query.data}*.\n\nВведите сумму расхода (например, 500 или 150.50):", parse_mode='Markdown')
    return ENTERING_AMOUNT

async def amount_entered(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Проверяем сумму и сохраняем в БД"""
    user_input = update.message.text.strip().replace(',', '.')
    
    try:
        amount = float(user_input)
        if amount <= 0:
            await update.message.reply_text("❌ Сумма должна быть больше нуля. Попробуйте еще раз:")
            return ENTERING_AMOUNT
            
        # Сохраняем в БД
        success = database.add_expense(
            user_id=update.effective_user.id,
            amount=amount,
            category=context.user_data['category'],
            date=context.user_data['date']
        )
        
        if success:
            await update.message.reply_text(
                f"✅ Успешно добавлено: *{amount}* руб. в категорию '*{context.user_data['category']}*'.",
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text("❌ Произошла ошибка при сохранении.")
            
        context.user_data.clear()
        
        # Возвращаем в главное меню
        keyboard = [[InlineKeyboardButton("➕ Добавить еще", callback_data='add_expense')],
                    [InlineKeyboardButton("📊 Статистика", callback_data='show_stats')]]
        await update.message.reply_text("Что делаем дальше?", reply_markup=InlineKeyboardMarkup(keyboard))
        return CHOOSING_CATEGORY
        
    except ValueError:
        await update.message.reply_text("❌ Неверный формат. Пожалуйста, введите число (например, 500):")
        return ENTERING_AMOUNT

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Отмена диалога"""
    await update.message.reply_text("Действие отменено. Введите /start.")
    context.user_data.clear()
    return ConversationHandler.END