from bot import bot, user_data, db
from bot.helper.other.other_utils import update_user_data, is_sudo
from bot.helper.ML.message.message_utils import sendMessage
from bot.helper.other.commands import Commands
from pyrogram.handlers import MessageHandler
from pyrogram.filters import command
from bot.helper.ML.telegram.filters import CustomFilters


async def authorize(_, message):
    reply_message = message.reply_to_message
    if len(message.command) ==2:
        id_ = int(message.command[1])
    elif reply_message:
        id_ = reply_message.from_user.id
    else:
        id_ = message.chat.id
    if id_ in user_data and user_data[id_].get('is_auth'):
        msg = f'[{id_}] Already Authorized!'
    else:
        update_user_data(id_, 'is_auth', True)
        if db:
            await db.update_user_data(id_)
        msg = f'[{id_}] Authorized'
    await sendMessage(message, msg)


async def unauthorize(_, message):
    reply_message = message.reply_to_message
    if len(message.command) ==2:
        id_ = int(message.command[1])
    elif reply_message:
        id_ = reply_message.from_user.id
    else:
        id_ = message.chat.id
    if id_ in user_data and user_data[id_].get('is_auth'):
        update_user_data(id_, 'is_auth', False)
        if db:
            await db.update_user_data(id_)
        msg = f'[{id_}] Unauthorized'
    else:
        msg = f'[{id_}] Already Unauthorized!'
    await sendMessage(message, msg)


async def addSudo(_, message):
    id_ = ""
    reply_message = message.reply_to_message
    if len(message.command) ==2:
        id_ = int(message.command[1])
    elif reply_message:
        id_ = reply_message.from_user.id
    if id_:
        if is_sudo(id_):
            msg = f'[{id_}] Already Sudo! '
        else:
            update_user_data(id_, 'is_sudo', True)
            if db:
                await db.update_user_data(id_)
            msg = f'[{id_}] Promoted as Sudo '
    else:
        msg = "Give ID or Reply To message of whom you want to Promote."
    await sendMessage(message, msg)


async def removeSudo(_, message):
    id_ = ""
    reply_message = message.reply_to_message
    if len(message.command) ==2:
        id_ = int(message.command[1])
    elif reply_message:
        id_ = reply_message.from_user.id
    if id_:
        if is_sudo(id_):
            update_user_data(id_, 'is_sudo', False)
            if db:
                await db.update_user_data(id_)
            msg = f'[{id_}] Demoted'
        else:
            msg = f'[{id_}] Already Demoted'
    else:
        msg = "Give ID or Reply To message of whom you want to remove from Sudo"
    await sendMessage(message, msg)



bot.add_handler(MessageHandler(authorize, filters=command(Commands.Authorize) & CustomFilters.owner))
bot.add_handler(MessageHandler(unauthorize, filters=command(Commands.UnAuthorize) & CustomFilters.owner))
bot.add_handler(MessageHandler(addSudo, filters=command(Commands.AddSudo) & CustomFilters.owner))
bot.add_handler(MessageHandler(removeSudo, filters=command(Commands.RemoveSudo) & CustomFilters.owner))
