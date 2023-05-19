#!/usr/bin/env python3
from pyrogram.handlers import MessageHandler, CallbackQueryHandler
from pyrogram.filters import command, regex
from psutil import cpu_percent, virtual_memory, disk_usage
from time import time

from bot import status_reply_dict_lock, download_dict, download_dict_lock, botStartTime, Interval, config_dict, bot
from bot.helper.ML.telegram.filters import CustomFilters
from bot.helper.other.commands import Commands
from bot.helper.ML.message.message_utils import sendMessage, deleteMessage, sendStatusMessage, update_all_messages
from bot.helper.ML.other.utils import get_readable_file_size, get_readable_time, turn_page, setInterval, new_task


DOWNLOAD_DIR = config_dict['DOWNLOAD_DIR']


@new_task
async def mirror_status(_, message):
    async with download_dict_lock:
        count = len(download_dict)
    if count == 0:
        currentTime = get_readable_time(time() - botStartTime)
        free = get_readable_file_size(disk_usage(DOWNLOAD_DIR).free)
        msg = 'No Active Downloads !\n___________________________'
        msg += f"\n<b>CPU:</b> {cpu_percent()}% | <b>FREE:</b> {free}" \
            f"\n<b>RAM:</b> {virtual_memory().percent}% | <b>UPTIME:</b> {currentTime}"
        await sendMessage(message, msg)
    else:
        await sendStatusMessage(message)
        await deleteMessage(message)
        async with status_reply_dict_lock:
            if Interval:
                Interval[0].cancel()
                Interval.clear()
                Interval.append(setInterval(
                    config_dict['STATUS_UPDATE_INTERVAL'], update_all_messages))


@new_task
async def status_pages(_, query):
    await query.answer()
    data = query.data.split()
    if data[1] == "ref":
        await update_all_messages(True)
    else:
        await turn_page(data)


bot.add_handler(MessageHandler(mirror_status, filters=command(
    Commands.StatusCommand) & CustomFilters.authorized))
bot.add_handler(CallbackQueryHandler(status_pages, filters=regex("^status")))
