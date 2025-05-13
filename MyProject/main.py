import datetime
import logging
import os

from telegram.ext import Application, MessageHandler, filters, CommandHandler, ConversationHandler, CallbackQueryHandler
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from config import BOT_TOKEN, COVERS_DIR
from data import db_session
from data.users import User
from data.books import Book
from data.films import Film
from functions import format_item_message

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)


reply_keyboard = [['/add', '/catalog'],
                  ['/search', '/help'],
                  ['/export', '/import']]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)


async def start(update, context):
    await update.message.reply_text(
        """
        📚🎬 Добро пожаловать в каталогизатор книг и фильмов!
        
        Доступные команды:
        /add - добавить книгу или фильм
        /list - показать весь каталог
        /catalog - поиск по каталогу
        /export - экспорт в CSV
        /import - импорт из CSV
        /help - справка по командам
        """,
        reply_markup=markup
    )
    # user = User(telegram_id=update.effective_user.id, name=,lastnametitle="Первая новость", content="Привет блог!",
    #             user_id=1, is_private=False)
    # db_sess.add(news)



async def help(update, context):
    await update.message.reply_text(
        """
        ℹ️ Справка по командам:
        
        <b>Добавление</b>
        /add - начать добавление нового элемента
        (после запуска бот будет запрашивать данные шаг за шагом)
        
        <b>Просмотр</b>
        /catalog - показать все каталоги книг и фильмов
        /search - поиск по каталогу
        
        <b>Управление</b>
        /export - экспортировать каталог в CSV
        /import - импортировать каталог из CSV (отправьте CSV файл после команды)
        """,
        parse_mode='HTML')


async def catalog(update, context):
    session = db_session.create_session()
    books = session.query(Book).filter(Book.user_id == update.effective_user.id).all()
    films = session.query(Film).filter(Film.user_id == update.effective_user.id).all()

    if not books:
        await update.message.reply_text("😌 Ваш каталог книг пуст.")

    for item in books:
        message = format_item_message(item, "book")
        if item.cover and os.path.exists(item.cover):
            await update.message.reply_photo(
                photo=open(item.cover, 'rb'),
                caption=message
            )
        else:
            await update.message.reply_text(message)

    if not films:
        await update.message.reply_text("😌 Ваш каталог фильмов пуст.")

    for item in books:
        message = format_item_message(item, "film")
        if item.cover and os.path.exists(item.cover):
            await update.message.reply_photo(
                photo=open(item.cover, 'rb'),
                caption=message
            )
        else:
            await update.message.reply_text(message)


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

    query.edit_message_reply_markup(reply_markup=None)

    if choice == 'book':
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=f'📖 Хорошо, введите название книги:'
        )
        return BOOK_TITLE
    elif choice == 'film':
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=f'🎬 Хорошо, введите название фильма:'
        )
        return FILM_TITLE


async def third_step_books(update, context):
    context.user_data['title'] = update.message.text
    await update.message.reply_text('✏️ Введите автора книги:')
    return BOOK_AUTHOR


async def third_step_films(update, context):
    context.user_data['title'] = update.message.text
    await update.message.reply_text('📽️ Введите режиссёра фильма:')
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
        photo_file = update.message.photo[-1].get_file()
        print(type(photo_file))
        user_id = update.effective_user.id
        item_type = context.user_data['type']
        timestamp = int(datetime.datetime.now().timestamp())
        filename = f"cover_{item_type}{user_id}_{timestamp}.jpg"
        filepath = os.path.join(COVERS_DIR, filename)

        photo_file.download(filepath)

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
        if context.user_data['type'] == "Книга":
            item = Book(
                title=context.user_data['title'],
                author=context.user_data.get('author'),
                year=context.user_data.get('year'),
                genre=context.user_data.get('genre'),
                link=context.user_data.get('link'),
                cover=context.user_data.get('cover'),
                user_id=update.effective_user.id
            )
        else:
            item = Film(
                title=context.user_data['title'],
                director=context.user_data.get('director'),
                year=context.user_data.get('year'),
                genre=context.user_data.get('genre'),
                duration=context.user_data.get('duration'),
                rating=context.user_data.get('rating'),
                link=context.user_data.get('link'),
                cover=context.user_data.get('cover'),
                user_id=update.effective_user.id,
            )

        session.add(item)
        session.commit()

        await context.bot.send_message(
            chat_id=chat_id,
            text=f'⚠️ Произошла ошибка. Попробуйте еще раз.'
        )

    except Exception as e:
        await context.bot.send_message(
            chat_id=chat_id,
            text=f'✅ Элемент успешно добавлен в каталог!'
        )

    return ConversationHandler.END


async def skip_cover(update, context):
    query = update.callback_query
    await query.answer()

    context.user_data['cover'] = None
    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text=f'Пропускаем добавление зображения'
    )
    await finish_step(update, context, query.message.chat_id)


async def cancel(update, context):
    await update.message.reply_text(
        "❌ Вы отменили добавление элемента в каталог",
    )
    return ConversationHandler.END


def main():
    db_session.global_init("db/films_books.db")
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))

    application.add_handler(CommandHandler("catalog", catalog))

    application.add_handler(CommandHandler("help", help))
    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler('add', first_step)],
        states={
            TYPE: [CallbackQueryHandler(second_step)],
            BOOK_TITLE: [MessageHandler(filters.TEXT, third_step_books)],
            BOOK_AUTHOR: [MessageHandler(filters.TEXT, fourth_step_books)],
            BOOK_YEAR: [MessageHandler(filters.TEXT, fifth_step_books)],
            BOOK_GENRE: [MessageHandler(filters.TEXT, sixth_step_books)],
            BOOK_LINK: [MessageHandler(filters.TEXT, seventh_step_books)],
            FILM_TITLE: [MessageHandler(filters.TEXT, third_step_films)],
            FILM_DIRECTOR: [MessageHandler(filters.TEXT, fourth_step_films)],
            FILM_YEAR: [MessageHandler(filters.TEXT, fifth_step_films)],
            FILM_GENRE: [MessageHandler(filters.TEXT, sixth_step_films)],
            FILM_DURATION: [MessageHandler(filters.TEXT, seventh_step_films)],
            FILM_RATING: [CallbackQueryHandler(eighth_step_films)],
            FILM_LINK: [MessageHandler(filters.TEXT, ninth_step_films)],
            COVER: [CallbackQueryHandler(skip_cover, pattern='^skip_upload$'),
                    MessageHandler(filters.PHOTO, penultimate_step)]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        allow_reentry=True
    )
    application.add_handler(conversation_handler)

    application.run_polling()


if __name__ == '__main__':
    main()