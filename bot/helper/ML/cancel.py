#!/usr/bin/env python3
from asyncio import sleep
from pyrogram.handlers import MessageHandler, CallbackQueryHandler
from pyrogram.filters import command, regex

from bot import download_dict, bot, download_dict_lock, config_dict, user_data
from bot.helper.other.commands import Commands
from bot.helper.ML.telegram.filters import CustomFilters
from bot.helper.ML.message.message_utils import sendMessage
from bot.helper.ML.other.utils import getDownloadByGid, getAllDownload, Name, new_task
from bot.helper.ML.message import button_build

OWNER_ID = config_dict['OWNER_ID']


async def cancel_mirror(_, message):
    user_id = message.from_user.id
    msg = message.text.split()
    if len(msg) > 1:
        gid = msg[1]
        dl = await getDownloadByGid(gid)
        if dl is None:
            await sendMessage(message, f"GID: <code>{gid}</code> Not Found.")
            return
    elif reply_to_id := message.reply_to_message_id:
        async with download_dict_lock:
            dl = download_dict.get(reply_to_id, None)
        if dl is None:
            await sendMessage(message, "This is not an active task!")
            return
    elif len(msg) == 1:
        msg = "Reply to an active Command message which was used to start the download" \
              f" or send <code>/{Commands.CancelMirror} GID</code> to cancel it!"
        await sendMessage(message, msg)
        return
    if OWNER_ID != user_id and dl.message.from_user.id != user_id and \
       (user_id not in user_data or not user_data[user_id].get('is_sudo')):
        await sendMessage(message, "This task is not for you!")
        return
    obj = dl.download()
    await obj.cancel_download()


async def cancel_all(status):
    matches = await getAllDownload(status)
    if not matches:
        return False
    for dl in matches:
        obj = dl.download()
        await obj.cancel_download()
        await sleep(1)
    return True


async def cancell_all_buttons(_, message):
    async with download_dict_lock:
        count = len(download_dict)
    if count == 0:
        await sendMessage(message, "No active tasks!")
        return
    buttons = button_build.ButtonMaker()
    buttons.ibutton("Downloading", f"canall {Name.STATUS_DOWNLOADING}")
    buttons.ibutton("Uploading", f"canall {Name.STATUS_UPLOADING}")
    buttons.ibutton("Seeding", f"canall {Name.STATUS_SEEDING}")
    buttons.ibutton("Cloning", f"canall {Name.STATUS_CLONING}")
    buttons.ibutton("Extracting", f"canall {Name.STATUS_EXTRACTING}")
    buttons.ibutton("Archiving", f"canall {Name.STATUS_ARCHIVING}")
    buttons.ibutton("QueuedDl", f"canall {Name.STATUS_QUEUEDL}")
    buttons.ibutton("QueuedUp", f"canall {Name.STATUS_QUEUEUP}")
    buttons.ibutton("Paused", f"canall {Name.STATUS_PAUSED}")
    buttons.ibutton("All", "canall all")
    buttons.ibutton("Close", "canall close")
    button = buttons.build_menu(2)
    await sendMessage(message, 'Choose tasks to cancel.', button)


@new_task
async def cancel_all_update(_, query):
    data = query.data.split()
    message = query.message
    reply_to = message.reply_to_message
    await query.answer()
    if data[1] == 'close':
        await reply_to.delete()
        await message.delete()
    else:
        res = await cancel_all(data[1])
        if not res:
            await sendMessage(reply_to, f"No matching tasks for {data[1]}!")


bot.add_handler(MessageHandler(cancel_mirror, filters=command(
    Commands.CancelCommand) & CustomFilters.authorized))
bot.add_handler(MessageHandler(cancell_all_buttons, filters=command(
    Commands.CancelAllCommand) & CustomFilters.sudo))
bot.add_handler(CallbackQueryHandler(cancel_all_update,
                filters=regex("^canall") & CustomFilters.sudo))
