from telegram.ext import ConversationHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from MyProject.data.authors import Author
from MyProject.data.books_genres import BooksGenre
from MyProject.data.directors import Director
from MyProject.data.films_genres import FilmsGenre
from MyProject.functions import first_result_format
from MyProject.config import COVERS_DIR, PAGINATION_CNT
from MyProject.data import db_session
from MyProject.data.books import Book
from MyProject.data.films import Film

TYPE, SEARCH_QUERY = range(2)


async def first_step(update, context):
    keyboard = [
        [InlineKeyboardButton("Книги", callback_data="book")],
        [InlineKeyboardButton("Фильмы", callback_data="film")],
    ]
    await update.message.reply_text(
        "🔍 Выберите тип для поиска:",
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
            text="Введите параметры поиска через запятую:\n"
                 "Формат: <название>, <автор>, <год>, <жанр>\n"
                 "Пример: Гарри Поттер, Роулинг, 2001, фэнтези"
        )
    else:
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text="Введите параметры поиска через запятую:\n"
                 "Формат: <название>, <режиссёр>, <год>, <жанр>, <продолжительность>, <рейтинг>\n"
                 "Пример: Гарри Поттер, Роулинг, 2001, фэнтези, 4.5"
        )

    return SEARCH_QUERY


async def third_step(update, context):
    search_terms = [term.strip() for term in update.message.text.split(',')]
    session = db_session.create_session()

    try:
        if context.user_data['type'] == 'book':
            try:
                title, author, year, genre = search_terms
            except Exception as e:
                await update.message.reply_text(f"❌ Неверный ввод данных для поиска: {str(e)}")

            query = session.query(Book).filter(Book.user_id == update.effective_user.id)
            if title:
                query = query.filter(Book.title == title)
            if author:
                # author_id = session.query(Author).filter(Author.name == author)
                # if not author_id:
                #     new_author = Author(name=author)
                #     session.add(new_author)
                #     session.commit()
                #     author_id = new_author.id
                query = query.filter(Book.author == author)
            if year:
                query = query.filter(Book.year == year)
            if genre:
                # genre_id = session.query(BooksGenre).filter(BooksGenre.name == genre)
                # if not genre_id:
                #     new_genre = BooksGenre(name=genre)
                #     session.add(new_genre)
                #     session.commit()
                #     genre_id = new_genre.id
                query = query.filter(Book.genre == genre)

            results = query.order_by(Book.title).all()

        else:
            try:
                title, director, year, genre, duration, rating = search_terms
            except Exception as e:
                await update.message.reply_text(f"❌ Неверный ввод данных для поиска: {str(e)}")
                session.close()

            query = session.query(Film).filter(Film.user_id == update.effective_user.id)
            if title:
                query = query.filter(Film.title == title)
            if director:
                # director_id = session.query(Director).filter(Director.name == director)
                # if not director_id:
                #     new_director = Director(name=director)
                #     session.add(new_director)
                #     session.commit()
                #     director_id = new_director.id
                query = query.filter(Film.director == director)
            if year:
                query = query.filter(Film.year == year)
            if genre:
                # genre_id = session.query(FilmsGenre).filter(FilmsGenre.name == genre)
                # if not genre_id:
                #     new_genre = FilmsGenre(name=genre)
                #     session.add(new_genre)
                #     session.commit()
                #     genre_id = new_genre.id
                query = query.filter(Film.genre == genre)
            if duration:
                query = query.filter(Film.duration == duration)
            if rating:
                query = query.filter(Film.rating == rating)

            results = query.order_by(Film.title).all()

        context.user_data['results'] = results

        await finish_step(update, context, update.message.chat_id)

    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка поиска: {str(e)}")

    finally:
        session.close()

    return ConversationHandler.END


async def finish_step(update, context, chat_id):
    results = context.user_data['results']

    if not results:
        await context.bot.send_message(
            chat_id=chat_id,
            text="😔 По Вашему запросу ничего не найдено"
        )
        return

    await context.bot.send_message(
        chat_id=chat_id,
        text=f"🔍 Найдено {len(results)} результатов ({(len(results) + PAGINATION_CNT - 1) // PAGINATION_CNT} страниц):"
    )

    await first_result_format(update, context, chat_id)


async def cancel(update, context):
    await update.message.reply_text(
        "❌ Вы отменили поиск элемента в каталоге",
    )
    return ConversationHandler.END