import datetime
import os
from telegram.ext import ConversationHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from MyProject.config import COVERS_DIR
from MyProject.data import db_session
from MyProject.data.books import Book
from MyProject.data.films import Film


TYPE, BOOK_TITLE, BOOK_AUTHOR, BOOK_YEAR, BOOK_GENRE, BOOK_LINK, FILM_TITLE, FILM_DIRECTOR, FILM_YEAR, \
    FILM_GENRE, FILM_DURATION, FILM_RATING, FILM_LINK, COVER, END = range(15)


async def first_step(update, context):
    keyboard = [
        [InlineKeyboardButton("Книга", callback_data='book')],
        [InlineKeyboardButton("Фильм", callback_data='film')]
    ]
    await update.message.reply_text(
        "🏷️ Выберите тип элемента, который хотите добавить в каталог:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return TYPE


async def second_step(update, context):
    query = update.callback_query
    await query.answer()

    choice = query.data
    context.user_data['type'] = choice

    if choice == 'book':
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=f'📖 Хорошо, введите название книги:'
        )
        return BOOK_TITLE
    else:
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=f'🎬 Хорошо, введите название фильма:'
        )
        return FILM_TITLE


async def third_step_books(update, context):
    context.user_data['title'] = update.message.text
    await update.message.reply_text('✏️ Введите автора:')
    return BOOK_AUTHOR


async def third_step_films(update, context):
    context.user_data['title'] = update.message.text
    await update.message.reply_text('📽️ Введите режиссёра:')
    return FILM_DIRECTOR


async def fourth_step_books(update, context):
    context.user_data['author'] = update.message.text
    await update.message.reply_text('📅 Теперь введите год написания книги:')
    return BOOK_YEAR


async def fourth_step_films(update, context):
    context.user_data['director'] = update.message.text
    await update.message.reply_text('📅 Теперь введите год выпуска фильма:')
    return FILM_YEAR


async def fifth_step_books(update, context):
    context.user_data['year'] = update.message.text
    await update.message.reply_text('🏷️ Введите жанр книги:')
    return BOOK_GENRE


async def fifth_step_films(update, context):
    context.user_data['year'] = update.message.text
    await update.message.reply_text('🏷️ Введите жанр фильма:')
    return FILM_GENRE


async def sixth_step_films(update, context):
    context.user_data['genre'] = update.message.text
    await update.message.reply_text('🕔 Введите продолжительность фильма (в минутах):')
    return FILM_DURATION


async def seventh_step_films(update, context):
    context.user_data['duration'] = update.message.text

    keyboard = [
        [InlineKeyboardButton("1", callback_data='1'),
         InlineKeyboardButton("2", callback_data='2'),
         InlineKeyboardButton("3", callback_data='3'),
         InlineKeyboardButton("4", callback_data='4'),
         InlineKeyboardButton("5", callback_data='5')],
        [InlineKeyboardButton("6", callback_data='6'),
         InlineKeyboardButton("7", callback_data='7'),
         InlineKeyboardButton("8", callback_data='8'),
         InlineKeyboardButton("9", callback_data='9'),
         InlineKeyboardButton("10", callback_data='10')]
    ]

    await update.message.reply_text('🏆 Выберите рейтинг фильма (по десятибалльной шкале):',
                              reply_markup=InlineKeyboardMarkup(keyboard))
    return FILM_RATING


async def sixth_step_books(update, context):
    context.user_data['genre'] = update.message.text
    await update.message.reply_text('🔗 Введите ссылку на книгу:')
    return BOOK_LINK


async def eighth_step_films(update, context):
    query = update.callback_query
    await query.answer()

    context.user_data['rating'] = query.data

    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text=f'🔗 Введите ссылку на фильм:'
    )
    return FILM_LINK


async def seventh_step_books(update, context):
    context.user_data['link'] = update.message.text

    keyboard = [
        [InlineKeyboardButton("Не загружать изображение", callback_data='skip_upload')]
    ]

    await update.message.reply_text(' Добавьте обложку к книге:',
                              reply_markup=InlineKeyboardMarkup(keyboard))
    return COVER


async def ninth_step_films(update, context):
    context.user_data['link'] = update.message.text

    keyboard = [
        [InlineKeyboardButton("Не загружать изображение", callback_data='skip_upload')]
    ]

    await update.message.reply_text(' Добавьте постер к фильму:',
                              reply_markup=InlineKeyboardMarkup(keyboard))
    return COVER


async def penultimate_step(update, context):
    try:
        file_id = update.message.photo[-1].file_id
        photo_file = await context.bot.get_file(file_id)

        user_id = update.effective_user.id
        item_type = context.user_data['type']
        timestamp = int(datetime.datetime.now().timestamp())
        filename = f"cover_{item_type}{user_id}_{timestamp}.jpg"
        filepath = os.path.join(COVERS_DIR, filename)

        await photo_file.download_to_drive(filepath)

        context.user_data['cover'] = filepath
        await update.message.reply_text("✅ Изображение сохранено!")

    except Exception as e:
        context.user_data['cover'] = None
        await update.message.reply_text(f"❌ Возникла ошибка при сохранении изображения: {str(e)}")
        await update.message.reply_text(f"Добавим запись в каталог без него")

    await finish_step(update, context, update.message.chat_id)


async def finish_step(update, context, chat_id):
    session = db_session.create_session()

    try:
        if context.user_data['type'] == "book":
            item = Book(
                title=context.user_data['title'],
                author=context.user_data.get('author'),
                year=int(context.user_data.get('year')),
                genre=context.user_data.get('genre'),
                link=context.user_data.get('link'),
                cover=context.user_data.get('cover'),
                user_id=update.effective_user.id
            )
        else:
            item = Film(
                title=context.user_data['title'],
                director=context.user_data.get('director'),
                year=int(context.user_data.get('year')),
                genre=context.user_data.get('genre'),
                duration=int(context.user_data.get('duration')),
                rating=context.user_data.get('rating'),
                link=context.user_data.get('link'),
                cover=context.user_data.get('cover'),
                user_id=update.effective_user.id,
            )

        session.add(item)
        session.commit()

        await context.bot.send_message(
            chat_id=chat_id,
            text=f'✅ Элемент успешно добавлен в каталог!'
        )

    except Exception as e:
        await context.bot.send_message(
            chat_id=chat_id,
            text=f'⚠️ Произошла ошибка: {str(e)}'
        )
        await context.bot.send_message(
            chat_id=chat_id,
            text=f'Попробуйте еще раз.'
        )
        session.rollback()

    finally:
        session.close()

    return ConversationHandler.END


async def skip_cover(update, context):
    query = update.callback_query
    await query.answer()

    context.user_data['cover'] = None
    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text=f'Пропускаем добавление изображения'
    )
    await finish_step(update, context, query.message.chat_id)


async def cancel(update, context):
    await update.message.reply_text(
        "❌ Вы отменили добавление элемента в каталог",
    )
    return ConversationHandler.END
