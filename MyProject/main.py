import logging
from telegram.ext import Application, MessageHandler, filters, CommandHandler, CallbackQueryHandler, ConversationHandler
from telegram import ReplyKeyboardMarkup
from config import BOT_TOKEN
from functions import format_item_message
from . import add
from . import search
from .data import db_session

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
    books = session.query(Book).filter(Book.user_id == update.effective_user.id)
    films = session.query(Film).filter(Film.user_id == update.effective_user.id)

    if not books:
        await update.message.reply_text("😔 Ваш каталог книг пуст.")

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
        await update.message.reply_text("😔 Ваш каталог фильмов пуст.")

    for item in books:
        message = format_item_message(item, "film")
        if item.cover and os.path.exists(item.cover):
            await update.message.reply_photo(
                photo=open(item.cover, 'rb'),
                caption=message
            )
        else:
            await update.message.reply_text(message)


def main():
    db_session.global_init("db/films_books.db")
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))

    application.add_handler(CommandHandler("catalog", catalog))

    application.add_handler(CommandHandler("help", help))

    add_conversation = ConversationHandler(
        entry_points=[CommandHandler('add', add.first_step)],
        states={
            add.TYPE: [CallbackQueryHandler(add.second_step)],
            add.BOOK_TITLE: [MessageHandler(filters.TEXT, add.third_step_books)],
            add.BOOK_AUTHOR: [MessageHandler(filters.TEXT, add.fourth_step_books)],
            add.BOOK_YEAR: [MessageHandler(filters.TEXT, add.fifth_step_books)],
            add.BOOK_GENRE: [MessageHandler(filters.TEXT, add.sixth_step_books)],
            add.BOOK_LINK: [MessageHandler(filters.TEXT, add.seventh_step_books)],
            add.FILM_TITLE: [MessageHandler(filters.TEXT, add.third_step_films)],
            add.FILM_DIRECTOR: [MessageHandler(filters.TEXT, add.fourth_step_films)],
            add.FILM_YEAR: [MessageHandler(filters.TEXT, add.fifth_step_films)],
            add.FILM_GENRE: [MessageHandler(filters.TEXT, add.sixth_step_films)],
            add.FILM_DURATION: [MessageHandler(filters.TEXT, add.seventh_step_films)],
            add.FILM_RATING: [CallbackQueryHandler(add.eighth_step_films)],
            add.FILM_LINK: [MessageHandler(filters.TEXT, add.ninth_step_films)],
            add.COVER: [CallbackQueryHandler(add.skip_cover, pattern='^skip_upload$'),
                    MessageHandler(filters.PHOTO, add.penultimate_step)]
        },
        fallbacks=[CommandHandler('cancel', add.cancel)],
        allow_reentry=True
    )
    application.add_handler(add_conversation)

    search_conversation = ConversationHandler(
        entry_points=[CommandHandler('search', search.first_step)],
        states={
            search.TYPE: [CallbackQueryHandler(search.second_step)],
            search.SEARCH_QUERY: [MessageHandler(filters.TEXT, search.third_step)]
        },
        fallbacks=[CommandHandler('cancel', cancel_search)]
    )
    application.add_handler(search_conversation)

    # Кнопки пагинации
    dispatcher.add_handler(CallbackQueryHandler(handle_pagination, pattern="^search:"))

    application.run_polling()


if __name__ == '__main__':
    main()