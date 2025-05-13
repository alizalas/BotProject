import datetime
import os
from telegram.ext import ConversationHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from MyProject.data.authors import Author
from MyProject.data.books_genres import BooksGenre
from MyProject.data.directors import Director
from MyProject.data.films_genres import FilmsGenre
from config import COVERS_DIR
from data import db_session
from data.books import Book
from data.films import Film

TYPE, SEARCH_QUERY = range(10)


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
                session.close()

            query = session.query(Book).filter(Book.user_id == update.effective_user.id)
            if title:
                query = query.filter(Book.title == title)
            if author:
                author_id = session.query(Author).filter(Author.name == author)
                if not author_id:
                    new_author = Author(name=author)
                    session.add(new_author)
                    session.commit()
                    author_id = new_author.id
                query = query.filter(Book.author_id == author_id)
            if year:
                query = query.filter(Book.year == year)
            if genre:
                genre_id = session.query(BooksGenre).filter(BooksGenre.name == genre)
                if not genre_id:
                    new_genre = BooksGenre(name=genre)
                    session.add(new_genre)
                    session.commit()
                    genre_id = new_genre.id
                query = query.filter(Book.genre_id == genre_id)

            results = query.order_by(Book.title)

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
                director_id = session.query(Director).filter(Director.name == director)
                if not director_id:
                    new_director = Director(name=director)
                    session.add(new_director)
                    session.commit()
                    director_id = new_director.id
                query = query.filter(Film.director_id == director_id)
            if year:
                query = query.filter(Film.year == year)
            if genre:
                genre_id = session.query(FilmsGenre).filter(FilmsGenre.name == genre)
                if not genre_id:
                    new_genre = FilmsGenre(name=genre)
                    session.add(new_genre)
                    session.commit()
                    genre_id = new_genre.id
                query = query.filter(Film.genre_id == genre_id)
            if duration:
                query = query.filter(Film.duration == duration)
            if rating:
                query = query.filter(Film.rating == rating)

            results = query.order_by(Film.title)

        context.user_data['search_results'] = results
        await finish_step(update, context, update.message.chat_id)

    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка поиска: {str(e)}")
    finally:
        session.close()

    return ConversationHandler.END


async def finish_step(update, context, chat_id):
    """Отправка результатов с клавиатурой пагинации"""
    results = context.user_data.get('search_results', [])
    if not results:
        await context.bot.send_message(
            chat_id=chat_id,
            text="😔 Ничего не найдено"
        )
        return

    context.user_data['current_page'] = 0
    total_pages = (len(results) + 4) // 5  # По 5 результатов на страницу

    # Формируем сообщение
    message = f"🔍 Найдено {len(results)} результатов (стр. 1/{total_pages}):\n\n"
    for item in results[:5]:
        message += f"📌 {item.title} ({item.year})\n"

    # Создаем клавиатуру пагинации
    keyboard = []
    if len(results) > 5:
        keyboard.append([
            InlineKeyboardButton("▶️ Далее", callback_data="search:next")
        ])

    await update.message.reply_text(
        message,
        reply_markup=InlineKeyboardMarkup(keyboard) if keyboard else None
    )