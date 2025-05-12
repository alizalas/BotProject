def format_item_message(item, type):
    """Форматирует информацию об элементе для сообщения"""
    if type == "book":
        type_str = "🎬 Фильм"
        duration_str = ""
        master_str = f"Автор: {item.author}\n"
        rating_str = ""
    else:
        type_str = "🎬 Фильм"
        duration_str = f"\n⏱ Продолжительность: {item.duration} мин"
        master_str = f"Режиссёр: {item.director}\n"
        rating_str = f"⭐ Рейтинг: {item.rating}\n"

    return (
        f"{type_str}: {item.title}\n"
        f"👤 {master_str}"
        f"📅 Год: {item.year}\n"
        f"🏷️ Жанр: {item.genre}\n"
        f"{duration_str}"
        f"{rating_str}"
        f"\n🔗 Ссылка: {item.link}\n"
    )