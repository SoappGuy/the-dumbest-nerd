from telethon.sync import TelegramClient, events
from config import api_id, api_hash, bot_token
from handlers import *

# Telegram session
client = TelegramClient('the_dumbest_nerd_session', api_id, api_hash).start(bot_token=bot_token)

if __name__ == '__main__':
    client.parse_mode = 'markdown'

    # command handlers
    client.add_event_handler(start_command_handler, events.NewMessage(pattern='/start'))
    client.add_event_handler(help_command_handler, events.NewMessage(pattern='/help'))
    client.add_event_handler(add_user_to_whitelist_command_handler, events.NewMessage(pattern='/add_wl'))
    client.add_event_handler(remove_user_from_whitelist_command_handler, events.NewMessage(pattern='/remove_wl'))
    client.add_event_handler(universal_message_handler, events.NewMessage(incoming=True))

    # start
    client.run_until_disconnected()
