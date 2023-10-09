from telethon.sync import TelegramClient, events
from config import api_id, api_hash, bot_token
from handlers import *
import logging

logging.basicConfig(level=logging.WARNING, filename="dumb_log.log", filemode="w",
                    format="%(levelname)s %(message)s")

# Telegram session
client = TelegramClient('the_dumbest_nerd_session', api_id, api_hash).start(bot_token=bot_token)


if __name__ == '__main__':
    client.parse_mode = 'markdown'

    # command handlers
    client.add_event_handler(start_command_handler, events.NewMessage(pattern='/start'))
    client.add_event_handler(help_command_handler, events.NewMessage(pattern='/help'))

    client.add_event_handler(add_user_to_whitelist_command_handler, events.NewMessage(pattern='/add_wl'))
    client.add_event_handler(remove_user_from_whitelist_command_handler, events.NewMessage(pattern='/remove_wl'))
    client.add_event_handler(get_log, events.NewMessage(pattern='/get_log'))

    client.add_event_handler(ping, events.NewMessage(pattern='/ping'))
    client.add_event_handler(tag_all, events.NewMessage(pattern='/tag_all'))
    client.add_event_handler(summarise, events.NewMessage(pattern='/sum'))
    client.add_event_handler(universal_message_handler, events.NewMessage(incoming=True))

    # start
    client.run_until_disconnected()
