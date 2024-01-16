from telegram.constants import ParseMode
import os
from telegram import ReplyKeyboardMarkup,Update,WebAppInfo,KeyboardButton,InlineKeyboardMarkup,InlineKeyboardButton,ReplyKeyboardRemove
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler,PicklePersistence

)
from variables import text
from dotenv import load_dotenv
import requests
import crud
import database
languagees = {'1':'uz','2':'ru'}
load_dotenv()
manu_button = [['Задать вопрос❔','Отправить возражение📝'],['Часто задаваемые вопосы❓','Отправить предложение🧠'],['Настройки⚙️','О ботеℹ️']]

#Base.metadata.create_all(bind=engine)
BOTTOKEN = os.environ.get('BOT_TOKEN')
url = f"https://api.telegram.org/bot{BOTTOKEN}/sendMessage"
LANGUAGE,MANU,SPHERE,COMMENTS,QUESTIONS,LANGUPDATE,SETTINGS,SPHEREUPDATE= range(8)
persistence = PicklePersistence(filepath='hello.pickle')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the conversation and asks the user about their gender."""
    user = crud.get_user(database.session,update.message.from_user.id)
    if user:
        await update.message.reply_text(text['ru']['manu'],reply_markup=ReplyKeyboardMarkup(manu_button,resize_keyboard=True))
        context.user_data['lang'] = str(user.lang)
        context.user_data['sphere'] = str(user.sphere)
        return MANU
    await update.message.reply_text(text['ru']['start'])
    await update.message.reply_text(text['ru']['lang'],reply_markup=ReplyKeyboardMarkup([['🇺🇿O`zbekcha','🇷🇺Русский']],resize_keyboard=True))

    return LANGUAGE





async def language(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.text == '🇺🇿O`zbekcha':
        context.user_data['lang'] = '1'
    else:
        context.user_data['lang'] = '2'
    await update.message.reply_text(text[languagees[context.user_data['lang']]]['sphere'],reply_markup=ReplyKeyboardMarkup([['Производство','Розница']],resize_keyboard=True))
    return SPHERE

async def sphere(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if sphere=='Производство':
        context.user_data['sphere'] = '2'
    else:
        context.user_data['sphere'] = '1'
    crud.create_user(database.session,update.message.from_user.id,context.user_data['lang'],context.user_data['sphere'])
    await update.message.reply_text(text[languagees[context.user_data['lang']]]['success'],
                                    reply_markup=ReplyKeyboardMarkup(manu_button,resize_keyboard=True))
    
    return MANU



async def manu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.text == 'Задать вопрос❔':
        context.user_data['commentsphere'] = 1
        await update.message.reply_text('Задайте вопрос',reply_markup=ReplyKeyboardMarkup([[text[languagees[context.user_data['lang']]]['back']]],resize_keyboard=True))

        return COMMENTS
    elif update.message.text == 'Отправить возражение📝':
        context.user_data['commentsphere'] = 2
        await update.message.reply_text('Отправьте возражение',reply_markup=ReplyKeyboardMarkup([[text[languagees[context.user_data['lang']]]['back']]],resize_keyboard=True))
        return COMMENTS
    elif update.message.text == 'Часто задаваемые вопосы❓':
        qeuestions = crud.get_questions(database.session,None) 
        if questions:
            question_list = []
            for i in qeuestions:
                question_list.append([i.question])
            question_list.append([text[languagees[context.user_data['lang']]]['back']])
            await update.message.reply_text('Часто задаваемые вопосы',reply_markup=ReplyKeyboardMarkup(question_list,resize_keyboard=True))
            return QUESTIONS
        else:
            await update.message.reply_text("Главная страница",
                                    reply_markup=ReplyKeyboardMarkup(manu_button,resize_keyboard=True))
    
            return MANU
    elif update.message.text == 'Отправить предложение🧠':
        context.user_data['commentsphere'] = 3
        await update.message.reply_text('Отправить предложение',reply_markup=ReplyKeyboardMarkup([[text[languagees[context.user_data['lang']]]['back']]],resize_keyboard=True))
        return COMMENTS
    elif update.message.text == 'Настройки⚙️':
        #await update.message.reply_text('Настройки',reply_markup=ReplyKeyboardMarkup([['🇺🇿O`zbekcha','🇷🇺Русский']],resize_keyboard=True))
        await update.message.reply_text('Настройки',reply_markup=ReplyKeyboardMarkup([["Поменять сферу",'Изменить язык'],[text[languagees[context.user_data['lang']]]['back']]],resize_keyboard=True))
        return SETTINGS
    elif update.message.text == 'О ботеℹ️':
        await update.message.reply_text(text[languagees[context.user_data['lang']]]['about'],
                                    reply_markup=ReplyKeyboardMarkup(manu_button,resize_keyboard=True))
        return MANU



async def settings(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.text == text[languagees[context.user_data['lang']]]['back']:
        await update.message.reply_text("Главная страница",
                                    reply_markup=ReplyKeyboardMarkup(manu_button,resize_keyboard=True))
        return MANU
    if update.message.text == 'Поменять сферу':
        await update.message.reply_text('Сфера',reply_markup=ReplyKeyboardMarkup([['Производство','Розница'],[text[languagees[context.user_data['lang']]]['back']]],resize_keyboard=True))
        return SPHEREUPDATE
    else:
        await update.message.reply_text('Язык',reply_markup=ReplyKeyboardMarkup([['🇺🇿O`zbekcha','🇷🇺Русский'],[text[languagees[context.user_data['lang']]]['back']]],resize_keyboard=True))
        return LANGUPDATE
    
async def sphereupdate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.text == text[languagees[context.user_data['lang']]]['back']:
        await update.message.reply_text('Настройки',reply_markup=ReplyKeyboardMarkup([["Поменять сферу",'Изменить язык'],[text[languagees[context.user_data['lang']]]['back']]],resize_keyboard=True))
        return SETTINGS
    if update.message.text == 'Производство':
        context.user_data['sphere'] = '2'
    else:
        context.user_data['sphere'] = '1'
    crud.update_user(database.session,update.message.from_user.id,context.user_data['lang'],context.user_data['sphere'])
    await update.message.reply_text("Главная страница",
                                    reply_markup=ReplyKeyboardMarkup(manu_button,resize_keyboard=True))
    return MANU


async def comments(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.text == text[languagees[context.user_data['lang']]]['back']:
        await update.message.reply_text("Главная страница",
                                    reply_markup=ReplyKeyboardMarkup(manu_button,resize_keyboard=True))
        return MANU
    user = crud.get_user(database.session,update.message.from_user.id)
    crud.create_request(database.session,int(context.user_data['commentsphere']),user.id,update.message.text)
    if context.user_data['commentsphere'] == 1:
        await update.message.reply_text(text[languagees[context.user_data['lang']]]['question_created'],
                                        reply_markup=ReplyKeyboardMarkup(manu_button,resize_keyboard=True))
    elif context.user_data['commentsphere'] == 2:
        await update.message.reply_text(text[languagees[context.user_data['lang']]]['feedback_created'],
                                        reply_markup=ReplyKeyboardMarkup(manu_button,resize_keyboard=True))
        
    elif context.user_data['commentsphere'] == 3:
        await update.message.reply_text(text[languagees[context.user_data['lang']]]['suggest_created'],
                                        reply_markup=ReplyKeyboardMarkup(manu_button,resize_keyboard=True))
    return MANU

async def langupdate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.text == text[languagees[context.user_data['lang']]]['back']:
        await update.message.reply_text('Настройки',reply_markup=ReplyKeyboardMarkup([["Поменять сферу",'Изменить язык'],[text[languagees[context.user_data['lang']]]['back']]],resize_keyboard=True))
        return SETTINGS
    if update.message.text == '🇺🇿O`zbekcha':
        context.user_data['lang'] = str(1)
    else:
        context.user_data['lang'] = str(2)
    await update.message.reply_text("Главная страница",
                            reply_markup=ReplyKeyboardMarkup(manu_button,resize_keyboard=True))
    return MANU
    

async def questions(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.text == text[languagees[context.user_data['lang']]]['back']:
        await update.message.reply_text("Главная страница",
                                    reply_markup=ReplyKeyboardMarkup(manu_button,resize_keyboard=True))
        return MANU
    question = crud.get_questions(database.session,update.message.text)
    if question:
        await update.message.reply_text(question[0].answer,
                                    reply_markup=ReplyKeyboardMarkup(manu_button,resize_keyboard=True))
    else:
        await update.message.reply_text('Вопрос не найден',
                                    reply_markup=ReplyKeyboardMarkup(manu_button,resize_keyboard=True))
    
    return MANU


def main() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    persistence = PicklePersistence(filepath="conversationbot")
    application = Application.builder().token(BOTTOKEN).persistence(persistence).build()
    #add states phone fullname category desction and others 
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            LANGUAGE:[MessageHandler(filters.TEXT,language)],
            SPHERE:[MessageHandler(filters.TEXT,sphere)],
            MANU:[MessageHandler(filters.TEXT,manu)],
            COMMENTS:[MessageHandler(filters.TEXT,comments)],
            QUESTIONS:[MessageHandler(filters.TEXT,questions)],
            LANGUPDATE:[MessageHandler(filters.TEXT,langupdate)],
            SPHEREUPDATE:[MessageHandler(filters.TEXT,sphereupdate)],
            SETTINGS:[MessageHandler(filters.TEXT,settings)]
        },
        fallbacks=[CommandHandler('start',start)],
        allow_reentry=True,
        name="my_conversation",
        persistent=True,

    )

    application.add_handler(conv_handler)

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()