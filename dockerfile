FROM python:3.9

ENV OPENAI_API_KEY "YOUR_OPENAI_API_KEY"
ENV TELEGRAM_API_KEY "YOUR_TELEGRAM_API_KEY"

WORKDIR /app

COPY autoGPT_Telegram-bot.py /app/GPT_Telegram-bot.py

RUN pip install requests

CMD ["python", "GPT_Telegram-bot.py"]
