from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from huggingface_hub import InferenceClient

import os

TOKEN = os.getenv("TOKEN")
HF_KEY = os.getenv("HF_KEY")

client = InferenceClient(api_key=HF_KEY)

# память диалогов
history = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    history[user_id] = [
        {
            "role": "system",
            "content": (
                "Ты Dronin GPT. "
                "Отвечай на русском языке грамотно и понятно. "
                "Будь дружелюбным. "
                "Запоминай информацию из текущего разговора."
            )
        }
    ]

    await update.message.reply_text(
        "Привет! 👋\n"
        "Я Dronin GPT 🤖\n"
        "Я буду помнить наш разговор, пока бот работает."
    )


async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text

    # показываем печать
    await update.message.chat.send_action(
        action=ChatAction.TYPING
    )

    if user_id not in history:
        history[user_id] = [
            {
                "role": "system",
                "content": (
                    "Ты Dronin GPT. "
                    "Отвечай грамотно на русском языке."
                )
            }
        ]

    # добавляем сообщение пользователя
    history[user_id].append(
        {
            "role": "user",
            "content": text
        }
    )

    try:
        response = client.chat.completions.create(
            model="meta-llama/Llama-3.1-8B-Instruct",
            messages=history[user_id],
            max_tokens=500
        )

        answer = response.choices[0].message.content

    except Exception as e:
        answer = "Произошла ошибка. Попробуй ещё раз."

        print(e)

    # сохраняем ответ в память
    history[user_id].append(
        {
            "role": "assistant",
            "content": answer
        }
    )

    await update.message.reply_text(answer)


app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

print("Dronin GPT запущен!")

app.run_polling()