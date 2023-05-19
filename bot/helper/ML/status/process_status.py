#!/usr/bin/env python3
from time import time

from bot import LOGGER
from bot.helper.ML.other.utils import get_readable_file_size, Name, get_readable_time, async_to_sync
from bot.helper.ML.other.files_utils import get_path_size


###############-----Telegram_Status-----###############
class TelegramStatus:
    def __init__(self, obj, size, message, gid, status):
        self.__obj = obj
        self.__size = size
        self.__gid = gid
        self.__status = status
        self.message = message

    def processed_bytes(self):
        return get_readable_file_size(self.__obj.processed_bytes)

    def size(self):
        return get_readable_file_size(self.__size)

    def status(self):
        if self.__status == 'up':
            return Name.STATUS_UPLOADING
        return Name.STATUS_DOWNLOADING

    def name(self):
        return self.__obj.name

    def progress(self):
        try:
            progress_raw = self.__obj.processed_bytes / self.__size * 100
        except:
            progress_raw = 0
        return f'{round(progress_raw, 2)}%'

    def speed(self):
        return f'{get_readable_file_size(self.__obj.speed)}/s'

    def eta(self):
        try:
            seconds = (self.__size - self.__obj.processed_bytes) / \
                self.__obj.speed
            return get_readable_time(seconds)
        except:
            return '-'

    def gid(self) -> str:
        return self.__gid

    def download(self):
        return self.__obj




###############-----Rclone_Status-----###############
class RcloneStatus:
    def __init__(self, obj, message, gid, status):
        self.__obj = obj
        self.__gid = gid
        self.__status = status
        self.message = message

    def gid(self):
        return self.__gid

    def progress(self):
        return self.__obj.percentage

    def speed(self):
        return self.__obj.speed

    def name(self):
        return self.__obj.name

    def size(self):
        return self.__obj.size

    def eta(self):
        return self.__obj.eta

    def status(self):
        if self.__status == 'dl':
            return Name.STATUS_DOWNLOADING
        elif self.__status == 'up':
            return Name.STATUS_UPLOADING
        else:
            return Name.STATUS_CLONING

    def processed_bytes(self):
        return self.__obj.transferred_size

    def download(self):
        return self.__obj


###############-----YTDL_Status-----###############
class YtDlpDownloadStatus:
    def __init__(self, obj, listener, gid):
        self.__obj = obj
        self.__listener = listener
        self.__gid = gid
        self.message = listener.message

    def gid(self):
        return self.__gid

    def processed_bytes(self):
        return get_readable_file_size(self.processed_raw())

    def processed_raw(self):
        if self.__obj.downloaded_bytes != 0:
            return self.__obj.downloaded_bytes
        else:
            return async_to_sync(get_path_size, self.__listener.dir)

    def size(self):
        return get_readable_file_size(self.__obj.size)

    def status(self):
        return Name.STATUS_DOWNLOADING

    def name(self):
        return self.__obj.name

    def progress(self):
        return f'{round(self.__obj.progress, 2)}%'

    def speed(self):
        return f'{get_readable_file_size(self.__obj.download_speed)}/s'

    def eta(self):
        if self.__obj.eta != '-':
            return get_readable_time(self.__obj.eta)
        try:
            seconds = (self.__obj.size - self.processed_raw()) / \
                self.__obj.download_speed
            return get_readable_time(seconds)
        except:
            return '-'

    def download(self):
        return self.__obj



###############-----ZIP_Status-----###############
class ZipStatus:
    def __init__(self, name, size, gid, listener):
        self.__name = name
        self.__size = size
        self.__gid = gid
        self.__listener = listener
        self.__uid = listener.uid
        self.__start_time = time()
        self.message = listener.message

    def gid(self):
        return self.__gid

    def speed_raw(self):
        return self.processed_raw() / (time() - self.__start_time)

    def progress_raw(self):
        try:
            return self.processed_raw() / self.__size * 100
        except:
            return 0

    def progress(self):
        return f'{round(self.progress_raw(), 2)}%'

    def speed(self):
        return f'{get_readable_file_size(self.speed_raw())}/s'

    def name(self):
        return self.__name

    def size(self):
        return get_readable_file_size(self.__size)

    def eta(self):
        try:
            seconds = (self.__size - self.processed_raw()) / self.speed_raw()
            return get_readable_time(seconds)
        except:
            return '-'

    def status(self):
        return Name.STATUS_ARCHIVING

    def processed_raw(self):
        if self.__listener.newDir:
            return async_to_sync(get_path_size, self.__listener.newDir)
        else:
            return async_to_sync(get_path_size, self.__listener.dir) - self.__size

    def processed_bytes(self):
        return get_readable_file_size(self.processed_raw())

    def download(self):
        return self

    async def cancel_download(self):
        LOGGER.info(f'Cancelling Archive: {self.__name}')
        if self.__listener.suproc is not None:
            self.__listener.suproc.kill()
        else:
            self.__listener.suproc = 'cancelled'
        await self.__listener.onUploadError('archiving stopped by user!')


###############-----Extract_Status-----###############
class ExtractStatus:
    def __init__(self, name, size, gid, listener):
        self.__name = name
        self.__size = size
        self.__gid = gid
        self.__listener = listener
        self.__uid = listener.uid
        self.__start_time = time()
        self.message = listener.message

    def gid(self):
        return self.__gid

    def speed_raw(self):
        return self.processed_raw() / (time() - self.__start_time)

    def progress_raw(self):
        try:
            return self.processed_raw() / self.__size * 100
        except:
            return 0

    def progress(self):
        return f'{round(self.progress_raw(), 2)}%'

    def speed(self):
        return f'{get_readable_file_size(self.speed_raw())}/s'

    def name(self):
        return self.__name

    def size(self):
        return get_readable_file_size(self.__size)

    def eta(self):
        try:
            seconds = (self.__size - self.processed_raw()) / self.speed_raw()
            return get_readable_time(seconds)
        except:
            return '-'

    def status(self):
        return Name.STATUS_EXTRACTING

    def processed_bytes(self):
        return get_readable_file_size(self.processed_raw())

    def processed_raw(self):
        if self.__listener.newDir:
            return async_to_sync(get_path_size, self.__listener.newDir)
        else:
            return async_to_sync(get_path_size, self.__listener.dir) - self.__size

    def download(self):
        return self

    async def cancel_download(self):
        LOGGER.info(f'Cancelling Extract: {self.__name}')
        if self.__listener.suproc is not None:
            self.__listener.suproc.kill()
        else:
            self.__listener.suproc = 'cancelled'
        await self.__listener.onUploadError('extracting stopped by user!')


###############-----Split_Status-----###############
class SplitStatus:
    def __init__(self, name, size, gid, listener):
        self.__name = name
        self.__gid = gid
        self.__size = size
        self.__listener = listener
        self.message = listener.message

    def gid(self):
        return self.__gid

    def progress(self):
        return '0'

    def speed(self):
        return '0'

    def name(self):
        return self.__name

    def size(self):
        return get_readable_file_size(self.__size)

    def eta(self):
        return '0s'

    def status(self):
        return Name.STATUS_SPLITTING

    def processed_bytes(self):
        return 0

    def download(self):
        return self

    async def cancel_download(self):
        LOGGER.info(f'Cancelling Split: {self.__name}')
        if self.__listener.suproc is not None:
            self.__listener.suproc.kill()
        else:
            self.__listener.suproc = 'cancelled'
        await self.__listener.onUploadError('splitting stopped by user!')

