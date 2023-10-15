from utils import *
import time
import emoji
import random
import openai
import re
import config

# Списочок адмінів
ADMINS = [921172948,
          740241575]

# Час коли було запущено юзербота, потрібен щоб слідкувати скільки часу вже виконується код
STARTUP_TIME = time.time()

# Список усіх емоджі
emoji_db = list(emoji.EMOJI_DATA.keys())

# API openai
openai.api_key = config.openai_api_hash


async def universal_message_handler(event):
    chat_id = event.chat_id
    message_text = event.text
    sender = event.sender_id
    timestamp = event.date

    # Якщо надіслано стікер/ґіф/відео/т.д. не додавати повідомлення
    if message_text != "":

        # Зберегти повідомлення у базі даних для групи з вказаним chat_id
        save_message_to_db(message_text, sender, timestamp, chat_id)


async def start_command_handler(event):
    create_whitelist_table(event.chat_id)
    create_group_table(event.chat_id)

    await event.respond('Started!')
    await event.respond('Для отримання довідки, надішліть /help.')


async def help_command_handler(event):
    # Просто записую тут яка команда що робить та їх синтаксис (щоб не забути)

    cmd_list = {
        "/sum": {
            "args": "<n>",
            "help": "про що йдеться у останніх n повідомленнях чату?",
            "emoji": "⁉️"
        },
        "/ping": {
            "args": "",
            "help": "чи працює юзербот?",
            "emoji": "🏓"
        },
        "/tag_all": {
            "args": "",
            "help": "тегнути всіх у чаті (не роби це по приколу, бо тебе вб'ють)",
            "emoji": "🔗"
        },
        "/add_wl": {
            "args": "<group>",
            "help": "надати людині дозвіл на використання певних команд у цьому чаті",
            "emoji": "🔒"
        },
        "/remove_wl": {
            "args": "<group>",
            "help": "забрати в людини дозвіл на використання певних команд у цьому чаті",
            "emoji": "🔒"
        }

    }
    edited_text = "/help:\n"
    m = await event.respond(edited_text, silent=True)
    for key in cmd_list.keys():
        args_ = cmd_list[key]["args"]
        help_ = cmd_list[key]["help"]
        emoji_ = cmd_list[key]["emoji"]

        # хелп виводиться за цим патерном, він єдиний для усіх команд,
        # це для того щоб не треба було змінювати кожну команду якщо захотілось змінити патерн
        edited_text += f'{emoji_} `{key} {args_}` - {help_}\n'

        await m.edit(edited_text)
    edited_text += f'\nдозволи для поточного чату:\n'

    # Отримання вайтлисту для чату
    whitelists = get_all_whitelists(event.chat_id)
    for whitelist in whitelists:
        command, user_id = whitelist
        edited_text += f"\n{command} - [{random.choice(emoji_db)}](tg://user?id={user_id})"

        await m.edit(edited_text)

    edited_text += f"\n\n[github](https://github.com/SoappGuy/the-dumbest-nerd)|[author](tg://user?id=921172948)"
    await m.edit(edited_text)


async def add_user_to_whitelist_command_handler(event):
    user_id = event.sender_id
    chat_id = event.chat_id
    args = get_args(event)

    # Перевірка, чи юзер має доступ до цієї команди
    if is_user_in_whitelist(chat_id, 'add_wl', user_id) or user_id in ADMINS:

        # Банальна перевірка того, що юзер ввів як аргументи
        if len(args) != 0:
            command = args[0]
        else:
            await event.respond('Повтори нормально, я не розчув')
            return

        # Треба відповісти на повідомлення юзера якого треба додати
        reply = event.reply_to
        if reply is None:
            await event.respond('Треба відповісти на повідомлення юзера якого треба додати')
            return

        # Отримати id юзера якого треба додати
        reply = await event.client.get_messages(event.chat_id, ids=event.reply_to.reply_to_msg_id)
        user_to_add = int(reply.sender_id)

        # Нарешті додати до вайтлисту
        if not is_user_in_whitelist(chat_id, command, user_id):
            add_user_to_whitelist_db(chat_id, command, user_to_add)
            await event.respond(f'✅[Юзера](tg://user?id={user_to_add}) успішно додано до {command}')
        else:
            await event.respond(f'[Юзер](tg://user?id={user_to_add}) вже має доступ до {command}')

    else:

        # Юзеру не дозволено використовувати цю команду
        await event.respond('Відмовлено у доступі')


async def remove_user_from_whitelist_command_handler(event):
    user_id = event.sender_id
    chat_id = event.chat_id
    args = get_args(event)

    # Перевірка, чи юзер має доступ до цієї команди
    if is_user_in_whitelist(chat_id, 'remove_wl', user_id) or user_id in ADMINS:

        # Банальна перевірка того, що юзер ввів як аргументи
        if len(args) != 0:
            command = args[0]
        else:
            await event.respond('Повтори нормально, я не розчув')
            return

        # Треба відповісти на повідомлення юзера якого треба видалити
        reply = event.reply_to
        if reply is None:
            await event.respond('Треба відповісти на повідомлення юзера якого треба видалити')
            return

        # Отримати id юзера якого треба видалити
        reply = await event.client.get_messages(event.chat_id, ids=event.reply_to.reply_to_msg_id)
        user_to_add = int(reply.sender_id)

        # Нарешті видалити з вайтлисту
        if is_user_in_whitelist(chat_id, command, user_id):
            remove_user_from_whitelist_db(chat_id, command, user_to_add)
            await event.respond(f'✅[Юзера](tg://user?id={user_to_add}) успішно видалено з {command}')
        else:
            await event.respond(f'[Юзер](tg://user?id={user_to_add}) і так не має доступ до {command}')

    else:

        # Юзеру не дозволено використовувати цю команду
        await event.respond('Відмовлено у доступі')


async def ping(event):
    global STARTUP_TIME
    answer = time.strftime("%H:%M:%S", time.gmtime(time.time() - STARTUP_TIME))
    await event.respond(f'🏓 Pong!\nЯ виконуюсь вже: {answer}!/')


async def tag_all(event):
    user_id = event.sender_id
    chat_id = event.chat_id

    # Перевірка довзволу
    if not (is_user_in_whitelist(chat_id, 'tag_all', user_id) or user_id == 921172948):
        await event.respond('Тобі не можна, за дозволом звернись до когось з адмінів')
        return

    # Спочатку треба взяти список усіх учасників чату
    user_list = await event.client.get_participants(entity=event.chat_id)
    usernames = []
    for user in user_list:

        # Ботів та видалені акаунти нам тегати не треба
        if (not user.bot) and (not user.deleted):

            # цей інлайн використовується щоб тегати за айді, бо не у всіх є юзернейми,
            # у [] записано як назвати того кого треба тегнути
            # я використовую рандомне емоджі, бо чому б ні
            usernames.append(f'[{random.choice(emoji_db)}](tg://user?id={user.id})')

    # Тг тегне лише перші 5 юзерів з повідомлення,
    # тому треба розбити повідомлення на шматки по 5 людей
    chunked_usernames = []
    for i in range(0, len(usernames), 5):
        chunked_usernames.append(usernames[i:i + 5])

    # І нарешті пінг
    for usernames in chunked_usernames:
        await event.respond("/".join(usernames))


async def get_log(event):
    user_id = event.sender_id

    if user_id in ADMINS:
        await event.client.send_file(-1001829214060, "./dumb_log.log")
    else:
        await event.respond('Думаєш найрозумніший? Тобі не можна.')
        return


async def summarise(event):
    # нове повідомлення у якому буде відображатись результат
    m = await event.respond('Processing ⏳..')

    arguments = get_args(event)
    # перевірка чи є аргументи взагалі, і якщо немає встановлює "100" як значення за змовчуванням
    if len(arguments) == 0:
        arguments = ["100"]

    # перевірка чи є перший аргумент числом
    arguments[0] = re.sub(r'[^0-9]', '', arguments[0])
    if arguments[0] == '':
        await m.edit('Треба число, довбань')
        return

    if int(arguments[0]) <= 50:
        await m.edit('Ти думаєш ти кумедний? Ні, це не смішно.')
        return

    # збирає останні arguments[0] повідомлень
    messages = get_last_n_messages(int(arguments[0]), event.chat_id)

    # залишає з повідомлень лише текст
    messages_text = []
    for message in messages:
        if "/" not in message[1]:  # якщо у повідомленні є "/" це повідомлення не буде враховуватись
            messages_text.append(message[1])

    # промпт для джипіті
    prompt = f"now you will be given messages, your task is to provide list of topics (maximum 10 topics) which was discussed in the conversation, start with the most discussed topics and end with those that were briefly mentioned (do not write about similar topics) (answer in Ukrainian):"
    prompt += "\n".join(messages_text[::-1])

    # формування запиту для API
    messages = []
    messages.append({"role": "user", "content": prompt})
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k",  # бажана модель GPT
            messages=messages,
            temperature=0.8,  # строгість відповіді - чим менше тим точніше відповідь
        )

        # надсилання результату
        await m.edit(f'sum of {arguments[0]} /\n{response["choices"][0]["message"]["content"]}\n\nTokens used - {response["usage"]["total_tokens"]}')
    except openai.error.ServiceUnavailableError:
        await m.edit(f"сервери openai перевантажені, перепрошую за незручності, спробуйте пізніше")

