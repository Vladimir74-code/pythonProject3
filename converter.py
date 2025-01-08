import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# Вопросы викторины и варианты ответов
questions = [
    {
        "question": "Какой у вас стиль жизни?",
        "options": [
            "Активный и жизнерадостный",
            "Спокойный и размеренный",
            "Приключенческий и любопытный"
        ],
        "weights": [2, 1, 3]
    },
    {
        "question": "Где вы хотели бы жить?",
        "options": [
            "В городе",
            "На природе",
            "У моря"
        ],
        "weights": [1, 3, 2]
    },
    {
        "question": "Какая у вас любимая еда?",
        "options": [
            "Мясо",
            "Овощи и фрукты",
            "Десерты"
        ],
        "weights": [3, 2, 1]
    },
    {
        "question": "Какой ваш подход к решению проблем?",
        "options": [
            "Незамедлительно действую",
            "Пробую разные варианты",
            "Обдумываю ситуацию долго"
        ],
        "weights": [3, 2, 1]
    },
    {
        "question": "Как вы относитесь к общению с людьми?",
        "options": [
            "Обожаю общаться",
            "Нравится, но бывает утомительно",
            "Предпочитаю общаться с близкими"
        ],
        "weights": [3, 2, 1]
    }
]

# Хранение ответов пользователей
user_answers = []
user_scores = []

# Информация о животных
animals = [
    ("Лев", "Ты смелый и энергичный, как настоящий король саванны!", "https://moscowzoo.ru/animals/kinds/indiyskiy_lev"),
    ("Черепаха", "Ты спокойный и мудрый, как черепаха!", "https://moscowzoo.ru/animals/kinds/luchistaya_cherepaha"),
    ("Обезьяна", "Ты любопытный и игривый, как настоящая обезьяна!", "https://moscowzoo.ru/animals/kinds/boliviyskaya_mirikina")
]

# адрес зоопарка
zoo_address = "Москва, ул. Большая Грузинская, 1"


def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    welcome_message = (
        "👋 Привет! Добро пожаловать в бот зоопарка!\n\n"
        "Узнай, какое животное тебе подходит, пройдя нашу викторину! Просто follow the instructions on the screen.\n\n"
        "Нажми на кнопку ниже, чтобы начать."
    )
    keyboard = [[InlineKeyboardButton("Начать викторину", callback_data='start_quiz')]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text(welcome_message, reply_markup=reply_markup)


def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_answers.clear()
    user_scores.clear()
    context.user_data['question_index'] = 0
    ask_question(update)


def ask_question(update: Update) -> None:
    question_index = update.effective_user.user_data['question_index']
    question = questions[question_index]['question']
    options = '\n'.join(f"{i + 1}. {option}" for i, option in enumerate(questions[question_index]['options']))
    update.message.reply_text(f"{question}\n{options}")


def answer_question(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        question_index = context.user_data['question_index']

        if question_index < len(questions):
            answer_index = int(update.message.text.split('.')[0]) - 1
            user_scores.append(questions[question_index]['weights'][answer_index])

            context.user_data['question_index'] += 1
            if context.user_data['question_index'] < len(questions):
                ask_question(update)
            else:
                total_score = sum(user_scores)
                result(update, total_score)
    except Exception as e:
        logger.error(f"Error in answering question: {e}")
        update.message.reply_text("Произошла ошибка. Пожалуйста, попробуйте ещё раз.")


def result(update: Update, total_score: int) -> None:
    animal_index = total_score % len(animals)
    animal = animals[animal_index]

    message = f"🎉 Твоё тотемное животное – **{animal[0]}**! 🐾\n{animal[1]}"
    update.message.reply_text(message)

    update.message.reply_photo(animal[2])  # URL изображения животного


    update.message.reply_text("📲 Поделитесь результатом в социальных сетях!")

    # Кнопка для ссылки на адрес зоопарка
    keyboard = [
        [InlineKeyboardButton("Связаться с сотрудником зоопарка", callback_data='contact_info')],
        [InlineKeyboardButton("Узнать больше о программе опеки", callback_data='program_info')],
        [InlineKeyboardButton("Попробовать ещё раз?", callback_data='restart_quiz')],
        [InlineKeyboardButton("Адрес зоопарка",
                              url="https://www.google.com/maps/search/?api=1&query=Москва,+ул.+Большая+Грузинская,+1")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text("Выберите, что хотите сделать дальше:", reply_markup=reply_markup)


def contact_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = "Вы можете связаться с нами по следующему номеру или почте:\n\n- 📞 Телефон: +7 (962) 971-38-75\n- ✉️ Email: zoofriends@moscowzoo.ru\n\nЕсли вы хотите, можете поделиться результатом викторины с нашими сотрудниками:"
    total_score_str = ', '.join(map(str, user_scores))

    update.message.reply_text(message + f"\nРезультаты викторины: {total_score_str}")


def program_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    update.message.reply_text(
        "🦁 **Программа опеки над животными**\n"
        "Стань опекуном и помоги сохранить удивительный мир животных! Участвуй в программе опеки и получи возможность:\n"
        "- Ближе познакомиться с любимыми животными\n"
        "- Участвовать в мероприятиях и акциях зоопарка\n"
        "- Получать эксклюзивные новости и фотографии\n\n"
        "Поддержи наших обитателей и сделай мир лучше!"
    )


def feedback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_feedback = update.message.text
    logger.info(f"Received feedback: {user_feedback}")
    # Здесь добавьте логику для сохранения обратной связи, например, в файл или базу данных
    update.message.reply_text("Спасибо за вашу обратную связь! Мы ценим ваше мнение.")


def restart_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    update.message.reply_text("Давайте начнём викторину снова!")
    quiz(update, context)


def main() -> None:
    application = ApplicationBuilder().token("7783435527:AAEUd1FC_ZWRrq72EiPePl_43mzw7iQIirE").build()

    # Команды и обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, answer_question))

    application.run_polling()


if __name__ == '__main__':
    main()
