from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder



votes = {"like": 0, "dislike": 0, "love": 0}

def get_main_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.button(text="📝Добавить задачу")
    builder.button(text="ℹ️Помощь")
    builder.button(text="💭Обратная связь")
    builder.adjust(2, 1) # Расположения кнопок в ряду

    return builder.as_markup(
        resize_keyboard=True,
        input_field_placeholder="Выбери раздел..."
    )

def get_vote_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text=f"👍{votes['like']}", callback_data="vote_like")
    builder.button(text=f"👎{votes['dislike']}", callback_data="vote_dislike")
    builder.button(text=f"❤️{votes['love']}", callback_data="vote_love")
    
    return builder.as_markup()