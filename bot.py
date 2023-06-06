import telebot
import time
from prometheus_client import start_http_server, Histogram, Counter
import fluent.sender

bot_token = 'your-token'

fluentd_host = '127.0.0.1'
fluentd_port = 24224

requests_counter = Counter('bot_requests_total', 'Total number of bot requests')
response_time_histogram = Histogram('bot_response_time_seconds' , 'Bot response time in seconds')

bot = telebot.TeleBot(bot_token)

logger = fluent.sender.FluentSender('telegram_bot', host=fluentd_host, port=fluentd_port)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_input = message.text
    start_time = time.time()
    response ="Відповідь від бота: " + user_input + " "

    log_message(user_input, response)

    bot.send_message(message.chat.id, response)

    requests_counter.inc()

    response_time = time.time() - start_time
    response_time_histogram.observe(response_time)

def log_message(user_input, generated_text):
    time_test = time.time()
    log_data = {
        'time' : time_test,
        'user_input': user_input,
        'generated_text': generated_text
    }
    logger.emit('telegram_message', log_data)

if __name__ == '__main__':
    start_http_server(9091)
    bot.polling()