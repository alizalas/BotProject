import logging
import os

from telegram.ext import Application, MessageHandler, filters, CommandHandler, ConversationHandler, CallbackQueryHandler
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from config import BOT_TOKEN
from data import db_session
from data.users import User
from data.books import Book
from data.films import Film
from functions import format_item_message

# Запускаем логгирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)


reply_keyboard = [['/address', '/phone'],
                  ['/site', '/work_time']]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)


async def start(update, context):
    await update.message.reply_text(
        """
        📚🎬 Добро пожаловать в каталогизатор книг и фильмов!
        
        Доступные команды:
        /add - добавить книгу или фильм
        /list - показать весь каталог
        /search - поиск по каталогу
        /export - экспорт в CSV
        /import - импорт из CSV
        /help - справка по командам
        """,
        reply_markup=markup
    )


async def help(update, context):
    await update.message.reply_text(
        """
        ℹ️ Справка по командам:
        
        <b>Добавление</b>
        /add - начать добавление нового элемента
        (после запуска бот будет запрашивать данные шаг за шагом)
        
        <b>Просмотр</b>
        /list - показать весь каталог
        /search - поиск по каталогу
        
        <b>Управление</b>
        /export - экспортировать каталог в CSV
        /import - импортировать каталог из CSV (отправьте CSV файл после команды)
        """,
        parse_mode='HTML')


async def list(update, context):
    session = db_session.create_session()
    books = session.query(Book).filter_by(Book.user_id == update.effective_user.id).all()
    films = session.query(Film).filter_by(Film.user_id == update.effective_user.id).all()

    if not books:
        update.message.reply_text("😌 Ваш каталог книг пуст.")

    for item in books:
        message = format_item_message(item, "book")
        if item.cover and os.path.exists(item.cover):
            update.message.reply_photo(
                photo=open(item.cover, 'rb'),
                caption=message
            )
        else:
            update.message.reply_text(message)

    if not films:
        update.message.reply_text("😌 Ваш каталог фильмов пуст.")

    for item in books:
        message = format_item_message(item, "film")
        if item.cover and os.path.exists(item.cover):
            update.message.reply_photo(
                photo=open(item.cover, 'rb'),
                caption=message
            )
        else:
            update.message.reply_text(message)



TYPE, BOOK_TITLE, BOOK_AUTHOR, BOOK_YEAR, BOOK_GENRE, BOOK_LINK, FILM_TITLE, FILM_DIRECTOR, FILM_YEAR, FILM_GENRE, FILM_DURATION, FILM_RATING, FILM_LINK = range(13)


async def first_step(update, context):
    keyboard = [
        [InlineKeyboardButton("Книга", callback_data='book')],
        [InlineKeyboardButton("Фильм", callback_data='film')]
    ]
    update.message.reply_text(
        "🏷️ Выберите тип элемента, который хотите добавить в каталог:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return TYPE


async def second_step(update, context):
    query = update.callback_query
    query.answer()

    choice = query.data
    context.user_data['type'] = choice

    if choice == 'book':
        query.edit_message_text('📖 Хорошо, введите название книги:')
        return BOOK_TITLE
    elif choice == 'movie':
        query.edit_message_text('🎬 Хорошо, введите название фильма:')
        return FILM_TITLE


async def third_step_books(update, context):
    context.user_data['book_title'] = update.message.text
    update.message.reply_text('✏️ Введите автора книги:')
    return BOOK_AUTHOR


async def third_step_films(update, context):
    context.user_data['film_title'] = update.message.text
    update.message.reply_text('📽️ Введите режиссёра фильма:')
    return FILM_DIRECTOR


async def fourth_step_books(update, context):
    context.user_data['books_author'] = update.message.text
    update.message.reply_text('📅 Теперь введите год написания книги:')
    return BOOK_YEAR


async def fourth_step_films(update, context):
    context.user_data['film_director'] = update.message.text
    update.message.reply_text('📅 Теперь введите год выпуска фильма:')
    return FILM_YEAR


async def fifth_step_books(update, context):
    context.user_data['book_year'] = update.message.text
    update.message.reply_text('🏷️ Введите жанр книги:')
    return BOOK_GENRE


async def fifth_step_films(update, context):
    context.user_data['film_year'] = update.message.text
    update.message.reply_text('🏷️ Введите жанр фильма:')
    return FILM_GENRE

async def sixth_step_films(update, context):
    context.user_data['film_genre'] = update.message.text
    update.message.reply_text('🕔 Введите продолжительность фильма (в минутах):')
    return FILM_DURATION


async def seventh_step_films(update, context):
    context.user_data['film_duration'] = update.message.text

    keyboard = [
        [InlineKeyboardButton("1", callback_data='1')],
        [InlineKeyboardButton("2", callback_data='2')],
        [InlineKeyboardButton("3", callback_data='3')],
        [InlineKeyboardButton("4", callback_data='4')],
        [InlineKeyboardButton("5", callback_data='5')]
    ]

    update.message.reply_text('🏆 Выберите рейтинг фильма (по пятибалльной шкале):',
                              reply_markup=InlineKeyboardMarkup(keyboard))
    return FILM_RATING


async def sixth_step_books(update, context):
    context.user_data['book_genre'] = update.message.text
    update.message.reply_text('🔗 Введите ссылку на книгу:')
    return BOOK_LINK


async def eighth_step_films(update, context):
    query = update.callback_query
    query.answer()

    context.user_data['film_rating'] = query.data
    update.message.reply_text('🔗 Введите ссылку на фильм:')
    return FILM_LINK


async def seventh_step_books(update, context):
    context.user_data['book_link'] = update.message.text
    return finish_step(update, context)


async def ninth_step_films(update, context):
    context.user_data['film_link'] = update.message.text
    return finish_step(update, context)


async def finish_step(update, context):
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
                user_id = update.effective_user.id
            )
        else:
            item = Film(
                title=context.user_data['title'],
                director=context.user_data.get('author_director'),
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

        update.message.reply_text('⚠️ Произошла ошибка. Попробуйте еще раз.')

    except Exception as e:
        update.message.reply_text("✅ Элемент успешно добавлен в каталог!")

    return ConversationHandler.END


async def cancel(update, context):
    update.message.reply_text(
        "❌ Вы отменили добавление элемента в каталог",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END




def main():
    db_session.global_init("db/films_books.db")
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))

    application.add_handler(CommandHandler("list", list))

    application.add_handler(CommandHandler("start", start))

    application.add_handler(CommandHandler("help", help))
    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler('add', first_step)],
        states={
            TYPE: [CallbackQueryHandler(second_step)],
            BOOK_TITLE: [MessageHandler(filters.TEXT, first_step)],
            BOOK_AUTHOR: [MessageHandler(filters.TEXT, second_step)],
            BOOK_YEAR: [MessageHandler(filters.TEXT, third_step_books)],
            BOOK_GENRE: [MessageHandler(filters.TEXT, fourth_step_books)],
            BOOK_LINK: [MessageHandler(filters.TEXT, fifth_step_books)],
            FILM_TITLE: [MessageHandler(filters.TEXT, sixth_step_books())]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    application.add_handler(conversation_handler)
    application.add_handler(CallbackQueryHandler(button_click))
    application.run_polling()


if __name__ == '__main__':
    main()