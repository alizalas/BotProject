import logging
from telegram.ext import Application, MessageHandler, filters, CommandHandler, CallbackQueryHandler, ConversationHandler
from telegram import ReplyKeyboardMarkup
from MyProject.data.books import Book
from MyProject.data.films import Film
from MyProject.config import BOT_TOKEN, PAGINATION_CNT
from MyProject.functions import first_result_format, pagination
from MyProject import add
from MyProject import search
from MyProject.data import db_session

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)

reply_keyboard = [['/book_catalog', '/film_catalog'],
                  ['/add', '/search'],
                  ['/start', '/help'], ]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)


async def start(update, context):
    await update.message.reply_text(
        """
        📚🎬 Добро пожаловать в каталогизатор книг и фильмов!

        Доступные команды:
        /book_catalog - показать каталог книг
        /film_catalog - показать каталог фильмов
        /add - добавить книгу или фильм
        /search - поиск по каталогу
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

        <b>Просмотр</b>
        /book_catalog - показать каталог книг
        /film_catalog - показать каталог фильмов
        /search - поиск по каталогу

        <b>Добавление</b>
        /add - добавление нового элемента в каталог

        После запуска команд /search, /add бот будет запрашивать данные шаг за шагом,
        выйти из диалога можно командой /cancel
        """,
        parse_mode='HTML')


async def catalog_books(update, context):
    session = db_session.create_session()
    results = session.query(Book).filter(Book.user_id == update.effective_user.id).all()
    context.user_data['results'] = results
    context.user_data['type'] = "book"

    if not results:
        await update.message.reply_text("😔 Ваш каталог книг пуст.")
        return

    await update.message.reply_text(
        f"🔍 В Вашем каталоге {len(results)} книг ({(len(results) + PAGINATION_CNT - 1) // PAGINATION_CNT} страниц):")
    await first_result_format(update, context, update.message.chat_id)
    # if item.cover and os.path.exists(item.cover):
    #     await update.message.reply_photo(
    #         photo=open(item.cover, 'rb'),
    #         caption=message
    #     )


async def catalog_films(update, context):
    session = db_session.create_session()
    results = session.query(Film).filter(Film.user_id == update.effective_user.id).all()
    context.user_data['results'] = results
    context.user_data['type'] = "film"

    if not results:
        await update.message.reply_text("😔 Ваш каталог фильмов пуст.")
        return

    await update.message.reply_text(
        f"🔍 В Вашем каталоге {len(results)} фильмов ({(len(results) + PAGINATION_CNT - 1) // PAGINATION_CNT} страниц):")
    await first_result_format(update, context, update.message.chat_id)


def main():
    db_session.global_init("../db/films_books.db")
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))

    application.add_handler(CommandHandler("book_catalog", catalog_books))

    application.add_handler(CommandHandler("film_catalog", catalog_films))

    application.add_handler(CommandHandler("help", help))

    add_conversation = ConversationHandler(
        entry_points=[CommandHandler('add', add.first_step)],
        states={
            add.TYPE: [CallbackQueryHandler(add.second_step)],
            add.BOOK_TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, add.third_step_books)],
            add.BOOK_AUTHOR: [MessageHandler(filters.TEXT & ~filters.COMMAND, add.fourth_step_books)],
            add.BOOK_YEAR: [MessageHandler(filters.TEXT & ~filters.COMMAND, add.fifth_step_books)],
            add.BOOK_GENRE: [MessageHandler(filters.TEXT & ~filters.COMMAND, add.sixth_step_books)],
            add.BOOK_LINK: [MessageHandler(filters.TEXT& ~filters.COMMAND, add.seventh_step_books)],
            add.FILM_TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, add.third_step_films)],
            add.FILM_DIRECTOR: [MessageHandler(filters.TEXT & ~filters.COMMAND, add.fourth_step_films)],
            add.FILM_YEAR: [MessageHandler(filters.TEXT & ~filters.COMMAND, add.fifth_step_films)],
            add.FILM_GENRE: [MessageHandler(filters.TEXT & ~filters.COMMAND, add.sixth_step_films)],
            add.FILM_DURATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, add.seventh_step_films)],
            add.FILM_RATING: [CallbackQueryHandler(add.eighth_step_films)],
            add.FILM_LINK: [MessageHandler(filters.TEXT & ~filters.COMMAND, add.ninth_step_films)],
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
            search.SEARCH_QUERY: [MessageHandler(filters.TEXT & ~filters.COMMAND, search.third_step)]
        },
        fallbacks=[CommandHandler('cancel', search.cancel)]
    )
    application.add_handler(search_conversation)

    application.add_handler(CallbackQueryHandler(pagination, pattern=r"^(next|prev)$"))

    application.run_polling()


if __name__ == '__main__':
    main()
