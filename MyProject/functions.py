from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from MyProject.config import PAGINATION_CNT


async def first_result_format(update, context, chat_id):
    context.user_data['current_page'] = 0
    results = context.user_data['results']
    context.user_data['total_pages'] = (len(results) + PAGINATION_CNT - 1) // PAGINATION_CNT

    await finish_result_format(update, context, chat_id)


async def finish_result_format(update, context, chat_id):
    """Отображение результатов на странице"""

    kind = context.user_data['type']
    current_page = context.user_data['current_page']
    total_pages = context.user_data['total_pages']
    results = context.user_data['results']
    start_idx = current_page * PAGINATION_CNT
    page_results = results[start_idx:start_idx + PAGINATION_CNT] if start_idx + PAGINATION_CNT <= len(
        results) else results[start_idx:]
    message = f"стр. {current_page + 1}/{total_pages}\n\n"
    keyboard = []

    if kind == "book":
        format_str = "📌 {title}, {author}, {year} год, жанр: {genre}, ссылка: <a href='{link}'>перейти</a>\n"
        for item in page_results:
            message += format_str.format(title=item.title,
                                         author=item.author,
                                         year=item.year,
                                         genre=item.genre,
                                         link=item.link)
    else:
        format_str = "📌 {title}, {director}, {year} год, жанр: {genre}, продолжительность: {duration} мин, рейтинг: {rating}, ссылка: <a href='{link}'>перейти</a>\n"
        for item in page_results:
            message += format_str.format(title=item.title,
                                         director=item.director,
                                         year=item.year,
                                         genre=item.genre,
                                         duration=item.duration,
                                         rating=item.rating,
                                         link=item.link)

    if current_page + 1 < total_pages:
        keyboard.append([InlineKeyboardButton("▶️ Далее", callback_data="next")])
    if current_page > 0:
        if keyboard:
            keyboard[-1].append(InlineKeyboardButton("◀️ Назад", callback_data="prev"))
        else:
            keyboard.append([InlineKeyboardButton("◀️ Назад", callback_data="prev")])

    await context.bot.send_message(
        chat_id=chat_id,
        text=message,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
    )


async def pagination(update, context):
    """Переключение страниц результатов"""

    query = update.callback_query
    await query.answer()

    action = query.data

    if action == 'next':
        context.user_data['current_page'] += 1
    elif action == 'prev':
        context.user_data['current_page'] -= 1

    await finish_result_format(update, context, query.message.chat_id)
