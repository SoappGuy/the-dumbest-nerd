from telethon import events
from utils import *
import asyncio


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
    await event.respond('/start - Початок роботи з ботом')
    await event.respond('/help - Вивести цю довідку')


async def add_user_to_whitelist_command_handler(event):
    user_id = event.sender_id
    chat_id = event.chat_id
    args = get_args(event)

    # Перевірка, чи юзер має доступ до цієї команди
    if is_user_in_whitelist(chat_id, 'add_wl', user_id) or user_id == 921172948:

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
    if is_user_in_whitelist(chat_id, 'remove_wl', user_id) or user_id == 921172948:

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