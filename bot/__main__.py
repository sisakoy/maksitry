from bot import bot, botloop, LOGGER, log_file, botloop, FLASK_SERVER
from signal import signal, SIGINT
from sys import argv, executable, exit as sysexit
from os import execl, remove
from os.path import isfile
from asyncio import create_subprocess_exec
from pyrogram.filters import command
from pyrogram.handlers import MessageHandler
from asyncio import gather

from .helper.other.commands import Commands
from .helper.ML.message.message_utils import sendMessage, sendFile
from .helper.ML.message.button_build import ButtonMaker
from .helper.other.other_utils import bot_uptime, get_logs_msg, get_host_stats
from .helper.ML.other.files_utils import start_cleanup, exit_clean_up, clean_all
from .helper.ML.other.utils import sync_to_async
from bot.helper.other import reset_config
from bot.helper.ML import cancel, ml_handler, task_status, user_settings, yt_handler, authorize



async def restart(_, message):
    restart_msg= await sendMessage(message, "Restarting...") 
    await sync_to_async(clean_all)
    await (await create_subprocess_exec("pkill", "-9", "-f", "aria2c|rclone|ffmpeg")).wait()
    await (await create_subprocess_exec("python3", "update.py")).wait()
    with open(".restartmsg", "w") as f:
        f.truncate(0)
        f.write(f"{restart_msg.chat.id}\n{restart_msg.id}\n")
    execl(executable, executable, "-m", "bot")


async def start(bot, message):
            text = f"Hi {message.from_user.mention(style='md')}, I Am Alive."
            buttons = ButtonMaker()
            buttons.ubutton("⭐ Bot By 𝚂𝚊𝚑𝚒𝚕 ⭐", "https://t.me/nik66")
            buttons.ubutton("❤ Join Channel ❤", "https://t.me/nik66x")
            await sendMessage(message, text, buttons=buttons.build_menu(1))
            return


async def uptime(_, message):
    await sendMessage(message, f'♻Bot UpTime {bot_uptime()}')
    return

async def send_log(_, message):
    await sendMessage(message, get_logs_msg(log_file))
    await sendFile(message, log_file)
    return

async def bot_stats(_, message):
    await sendMessage(message, (await get_host_stats()))
    return

async def main(bot_name):
    await gather(start_cleanup())
    if isfile(".restartmsg"):
        try:
            with open(".restartmsg") as f:
                    chat_id, msg_id = map(int, f)
            await bot.edit_message_text(chat_id, msg_id, "Restarted successfully!")  
        except Exception as e:
            LOGGER.error(str(e))
        remove(".restartmsg")
    bot.add_handler(MessageHandler(start, filters= command(Commands.StartCommand)))
    bot.add_handler(MessageHandler(restart, filters= command(Commands.ReStartCommand)))
    bot.add_handler(MessageHandler(uptime, filters= command(Commands.UpTime)))
    bot.add_handler(MessageHandler(send_log, filters= command(Commands.Log)))
    bot.add_handler(MessageHandler(bot_stats, filters= command(Commands.Stats)))
    LOGGER.info(f'✅@{bot_name} Started Successfully!✅')
    LOGGER.info(f"⚡Bot By Sahil Nolia⚡")
    signal(SIGINT, exit_clean_up)

LOGGER.info(f'Starting Bot')
bot.start()

botloop.run_until_complete(main(bot.get_me().username))

if FLASK_SERVER:
    LOGGER.info('Starting Flask Server')
    from .helper.other.flask_server import run_flask
    run_flask()

botloop.run_forever()

