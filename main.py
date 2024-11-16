import flask
import telebot
from moscow_boardgames_bot import bot
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
    
WEBHOOK_HOST = os.getenv('WEBHOOK_HOST')
WEBHOOK_PORT = int(os.getenv('WEBHOOK_PORT'))
WEBHOOK_URL_BASE = f"https://{WEBHOOK_HOST}"
WEBHOOK_URL_PATH = "/MoscowBoardgamesBot/"
    
app = flask.Flask(__name__)

# Обработка входящих сообщений
@app.route(WEBHOOK_URL_PATH, methods=['POST'])
def webhook():
    if flask.request.headers.get('content-type') == 'application/json':
        json_string = flask.request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return 'ok', 200
    else:
        flask.abort(403)

# Установка webhook
bot.remove_webhook()
bot.set_webhook(url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH)

# Запуск Flask приложения
if __name__ == "__main__":
    app.run(port=WEBHOOK_PORT)
