
#!/usr/bin/env python3
from asyncio import Event

from bot import config_dict, queued_dl, queued_up, non_queued_up, non_queued_dl, queue_dict_lock, LOGGER
from bot.helper.ML.other.utils import get_readable_file_size, Name


class QueueStatus:
    def __init__(self, name, size, gid, listener, status):
        self.__name = name
        self.__size = size
        self.__gid = gid
        self.__listener = listener
        self.__status = status
        self.message = listener.message

    def gid(self):
        return self.__gid

    def name(self):
        return self.__name

    def size(self):
        return get_readable_file_size(self.__size)

    def status(self):
        if self.__status == 'dl':
            return Name.STATUS_QUEUEDL
        return Name.STATUS_QUEUEUP

    def processed_bytes(self):
        return 0

    def progress(self):
        return '0%'

    def speed(self):
        return '0B/s'

    def eta(self):
        return '-'

    def download(self):
        return self

    async def cancel_download(self):
        LOGGER.info(f'Cancelling Queue{self.__status}: {self.__name}')
        if self.__status == 'dl':
            await self.__listener.onDownloadError('task have been removed from queue/download')
        else:
            await self.__listener.onUploadError('task have been removed from queue/upload')


async def is_queued(uid):
    all_limit = config_dict['QUEUE_ALL']
    dl_limit = config_dict['QUEUE_DOWNLOAD']
    event = None
    added_to_queue = False
    if all_limit or dl_limit:
        async with queue_dict_lock:
            dl = len(non_queued_dl)
            up = len(non_queued_up)
            if (all_limit and dl + up >= all_limit and (not dl_limit or dl >= dl_limit)) or (dl_limit and dl >= dl_limit):
                added_to_queue = True
                event = Event()
                queued_dl[uid] = event
    return added_to_queue, event


def start_dl_from_queued(uid):
    queued_dl[uid].set()
    del queued_dl[uid]


def start_up_from_queued(uid):
    queued_up[uid].set()
    del queued_up[uid]


async def start_from_queued():
    if all_limit := config_dict['QUEUE_ALL']:
        dl_limit = config_dict['QUEUE_DOWNLOAD']
        up_limit = config_dict['QUEUE_UPLOAD']
        async with queue_dict_lock:
            dl = len(non_queued_dl)
            up = len(non_queued_up)
            all_ = dl + up
            if all_ < all_limit:
                f_tasks = all_limit - all_
                if queued_up and (not up_limit or up < up_limit):
                    for index, uid in enumerate(list(queued_up.keys()), start=1):
                        f_tasks = all_limit - all_
                        start_up_from_queued(uid)
                        f_tasks -= 1
                        if f_tasks == 0 or (up_limit and index >= up_limit - up):
                            break
                if queued_dl and (not dl_limit or dl < dl_limit) and f_tasks != 0:
                    for index, uid in enumerate(list(queued_dl.keys()), start=1):
                        start_dl_from_queued(uid)
                        if (dl_limit and index >= dl_limit - dl) or index == f_tasks:
                            break
        return

    if up_limit := config_dict['QUEUE_UPLOAD']:
        async with queue_dict_lock:
            up = len(non_queued_up)
            if queued_up and up < up_limit:
                f_tasks = up_limit - up
                for index, uid in enumerate(list(queued_up.keys()), start=1):
                    start_up_from_queued(uid)
                    if index == f_tasks:
                        break
    else:
        async with queue_dict_lock:
            if queued_up:
                for uid in list(queued_up.keys()):
                    start_up_from_queued(uid)

    if dl_limit := config_dict['QUEUE_DOWNLOAD']:
        async with queue_dict_lock:
            dl = len(non_queued_dl)
            if queued_dl and dl < dl_limit:
                f_tasks = dl_limit - dl
                for index, uid in enumerate(list(queued_dl.keys()), start=1):
                    start_dl_from_queued(uid)
                    if index == f_tasks:
                        break
    else:
        async with queue_dict_lock:
            if queued_dl:
                for uid in list(queued_dl.keys()):
                    start_dl_from_queued(uid)
