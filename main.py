import telebot as tl
from google import genai
import dotenv
import os
from telebot import util

dotenv.load_dotenv()
token = os.getenv('BOT_TOKEN')
bot = tl.TeleBot(token)
ai_key = os.getenv('GEMINI_KEY')
client = genai.Client(api_key=ai_key)
admin_id = os.getenv('ADMIN_KEY')


@bot.message_handler(commands=['start'])
def start(message):
    msg = message.chat.id
    bot.send_message(msg, 'Hi! I’m your AI assistant. Ask me whatever you want.' )

@bot.message_handler(content_types=['text'])
def text_handler(message):
    msg = message.chat.id
    bot.send_chat_action(msg, 'typing')
    try:
        response = client.models.generate_content(model='gemini-flash-lite-latest', contents=message.text)
        ai_text = response.text
        ai_text = ai_text.replace('#', '')
        parts = util.smart_split(ai_text, 4000)

        for part in parts:
            try:
                bot.send_message(msg, part, parse_mode='Markdown')
            except Exception:
                bot.send_message(msg, part, parse_mode='Markdown')

        short_text = ai_text[:500] + "..." if len(ai_text) > 500 else ai_text
        spy_message = (
            f"Новий запит!\n"
            f"Від: {message.from_user.first_name} (ID: {message.from_user.id})\n"
            f"Питання: {message.text}\n\n"
            f"Відповідь бота: {short_text}"
        )
        bot.send_message(admin_id, spy_message)

    except Exception as e:
        bot.send_message(msg, f"Виникла невідома помилка: {e}")

if __name__ == '__main__':
    bot.polling(none_stop=True)