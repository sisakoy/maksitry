from logger import LOGGER, log_file
from os import environ, getcwd
from os.path import exists
from dotenv import load_dotenv


def get_config(variable, value):
        try:
                if variable=='ALLOWED_CHATS':
                        return environ.get("ALLOWED_CHATS","").split()
                elif variable=='SUDO_USERS':
                        return environ.get("SUDO_USERS","").split()
                elif variable=='DOWNLOAD_DIR':
                        DOWNLOAD_DIR = environ.get("DOWNLOAD_DIR","/content/BaseBot/downloads/")
                        return DOWNLOAD_DIR if DOWNLOAD_DIR.endswith("/") else f'{DOWNLOAD_DIR}/'
                elif variable=='AS_DOCUMENT':
                        AS_DOCUMENT = environ.get("AS_DOCUMENT","")
                        return True if AS_DOCUMENT.lower() == 'true' else False
                elif variable=='EQUAL_SPLITS':
                        EQUAL_SPLITS = environ.get("EQUAL_SPLITS","")
                        return True if EQUAL_SPLITS.lower() == 'true' else False
                elif variable=='MEDIA_GROUP':
                        MEDIA_GROUP = environ.get("MEDIA_GROUP","")
                        return True if MEDIA_GROUP.lower() == 'true' else False
                elif variable=='USE_SERVICE_ACCOUNTS':
                        USE_SERVICE_ACCOUNTS = environ.get("USE_SERVICE_ACCOUNTS","")
                        return True if USE_SERVICE_ACCOUNTS.lower() == 'true' else False
                elif variable=='DUMP_CHAT_ID':
                        DUMP_CHAT_ID = environ.get("DUMP_CHAT_ID","")
                        return int(DUMP_CHAT_ID) if len(DUMP_CHAT_ID) else 0
                elif variable=='FLASK_SERVER':
                        FLASK_SERVER = environ.get("FLASK_SERVER","")
                        return True if FLASK_SERVER.lower() == 'true' else False
                elif variable=='PORT':
                        return int(environ.get("PORT","8080"))
        
        except Exception as e:
                LOGGER.error(f'Error Getting Variable {variable}:  {str(e)}')
                return value



if exists('config.env'):
        LOGGER.info("config.env file found")
        load_dotenv('config.env', override=True)

user_data = {}
config_dict = {}

if len(environ.get("Telegram_BOT_TOKEN","")) == 0:
        LOGGER.error("BOT_TOKEN variable is missing! Exiting now")
        exit(1)
        
bot_id = environ.get("Telegram_BOT_TOKEN","").split(':', 1)[0]
PORT = get_config('PORT', 8080)




class Config:
        ####----Bot Variables----####
        Telegram_API_ID = int(environ.get("Telegram_API_ID",""))
        Telegram_API_HASH = environ.get("Telegram_API_HASH","")
        Telegram_BOT_TOKEN = environ.get("Telegram_BOT_TOKEN","")
        
        ####----Auth Variables----####
        OWNER_ID = int(environ.get("OWNER_ID","12345"))
        ALLOWED_CHATS = get_config('ALLOWED_CHATS', [])
        SUDO_USERS = get_config('SUDO_USERS', [])
        
        ####----Database Variables----####
        MONGODB_URI = environ.get("MONGODB_URI", "")
        DB_NAME = environ.get("DB_NAME","Nik66_Bots")
        
        ####----Updates Variables----####
        UPSTREAM_REPO = environ.get("UPSTREAM_REPO", "")
        UPSTREAM_BRANCH = environ.get("UPSTREAM_BRANCH", "")
        UPDATE_PACKAGES = environ.get("UPDATE_PACKAGES", "")
        
        ####----Rclone Variables----####
        RCLONE_CONFIG_URL = environ.get("RCLONE_CONFIG_URL","")
        RCLONE_PATH = environ.get("RCLONE_PATH", "")
        RCLONE_FLAGS = environ.get("RCLONE_FLAGS", "")
        USE_SERVICE_ACCOUNTS = get_config("USE_SERVICE_ACCOUNTS", False)
        
        ####----Queue Variables----####
        QUEUE_ALL = int(environ.get("QUEUE_ALL", "0"))
        QUEUE_DOWNLOAD = int(environ.get("QUEUE_DOWNLOAD", "0"))
        QUEUE_UPLOAD = int(environ.get("QUEUE_UPLOAD", "0"))
        
        ####----TG Upload Variables----####
        DUMP_CHAT_ID = get_config("DUMP_CHAT_ID", 0)
        LEECH_SPLIT_SIZE = int(environ.get("LEECH_SPLIT_SIZE", "2097152000"))
        LEECH_FILENAME_PREFIX = environ.get("LEECH_FILENAME_PREFIX", "")
        AS_DOCUMENT =get_config("AS_DOCUMENT", False)
        EQUAL_SPLITS = get_config("EQUAL_SPLITS", False)
        MEDIA_GROUP = get_config("MEDIA_GROUP", False)
        
        ####----Status Variables----####
        STATUS_LIMIT = int(environ.get("STATUS_LIMIT", "5"))
        STATUS_UPDATE_INTERVAL = int(environ.get("STATUS_UPDATE_INTERVAL", '10'))
        
        ####----Other Variables----####
        DOWNLOAD_DIR = f"{getcwd()}/downloads/"
        YT_DLP_OPTIONS = environ.get("YT_DLP_OPTIONS", "")
        TORRENT_TIMEOUT = int(environ.get("TORRENT_TIMEOUT", "0"))
        UPTOBOX_TOKEN = environ.get("UPTOBOX_TOKEN", "")
        FLASK_SERVER = get_config('FLASK_SERVER', False)
        GENERATE_CLOUD_LINK = True