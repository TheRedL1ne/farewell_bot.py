import logging
import html
import os

from telegram import Update, ChatMember, ChatMemberUpdated
from telegram.constants import ParseMode
from telegram.ext import Application, ChatMemberHandler, ContextTypes

# Налаштування логування
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

def track_chats(update: ChatMemberUpdated) -> tuple[bool, bool]:
    """
    Відстежує зміну статусу "учасник" -> "покинув/вигнаний" у чатах, де знаходиться бот.
    """
    status_change = update.difference().get("status")
    if status_change is None:
        return False, False

    old_is_member, new_is_member = (
        status in (ChatMember.MEMBER, ChatMember.ADMINISTRATOR, ChatMember.OWNER)
        for status in status_change
    )
    return old_is_member, not new_is_member

async def greet_chat_members(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Реагує на вихід учасника з чату, згадуючи список користувачів.
    """
    was_member, is_member = track_chats(update.chat_member)

    # Якщо користувач був учасником і покинув чат
    if was_member and is_member:
        user = update.chat_member.new_chat_member.user
        
        # Екрануємо ім'я користувача, який покинув чат
        safe_user_name = html.escape(user.first_name)
        
        # Список ID користувачів, яких потрібно згадати
        users_to_mention_ids = [5455509037, 1842622156, 5106459300]
        
        # Смайлик для згадки
        emoji = "❗️"

        # Створюємо список HTML-посилань для кожного користувача
        mention_links = [f'<a href="tg://user?id={user_id}">{emoji}</a>' for user_id in users_to_mention_ids]
        
        # Об'єднуємо всі посилання в один рядок, розділяючи їх пробілом
        mentions_string = " ".join(mention_links)
        
        # Формуємо фінальне повідомлення
        message = f"{safe_user_name} покинул(а) наш приют. {mentions_string}"

        try:
            # Надсилаємо повідомлення, вказавши parse_mode=ParseMode.HTML
            await update.effective_chat.send_message(
                text=message,
                parse_mode=ParseMode.HTML
            )
        except Exception as e:
            logger.error(f"Не вдалося надіслати повідомлення: {e}")

def main() -> None:
    """Запускає бота."""

    application = Application.builder().token("7998039239:AAGAvSd3Vb1GmXRuRUFQA9R-RIUVl3A5KCY").build()

    # Додаємо обробник, який реагує на зміну статусу учасників
    application.add_handler(ChatMemberHandler(greet_chat_members, ChatMemberHandler.ANY_CHAT_MEMBER))

    logger.info("Бот запущений...")
    application.run_polling()

if __name__ == "__main__":
    main()

