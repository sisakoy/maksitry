from bot import bot, user_data, db
from bot.helper.ML.message.message_utils import sendMessage
from bot.helper.other.commands import Commands
from pyrogram.handlers import MessageHandler
from pyrogram.filters import command
from bot.helper.ML.telegram.filters import CustomFilters


async def reset_db(_, message):
    if db:
        await db.reset_config()
        await sendMessage(message, 'Config Has Reset.')
    else:
        await sendMessage(message, 'No DB Found')
    return
    


bot.add_handler(MessageHandler(reset_db, filters=command(Commands.ResetConfig) & CustomFilters.owner))
