#!/usr/bin/env python3
from aiofiles.os import remove as aioremove, path as aiopath
from asyncio import sleep
from time import time

from bot import aria2, download_dict_lock, download_dict, LOGGER, config_dict, aria2_options, aria2c_global, non_queued_dl, queue_dict_lock
from bot.helper.ML.other.utils import sync_to_async, getDownloadByGid, new_thread, Name, get_readable_time
from bot.helper.ML.message.message_utils import sendStatusMessage, sendMessage
from bot.helper.ML.task.task_manager import is_queued
from bot.helper.ML.other.files_utils import clean_unwanted
from bot.helper.ML.message.message_utils import sendMessage, update_all_messages


###############-----Add_Download-----###############


async def add_aria2c_download(link, path, listener, filename, auth, ratio, seed_time):
    a2c_opt = {**aria2_options}
    [a2c_opt.pop(k) for k in aria2c_global if k in aria2_options]
    a2c_opt['dir'] = path
    if filename:
        a2c_opt['out'] = filename
    if auth:
        a2c_opt['header'] = f"authorization: {auth}"
    if ratio:
        a2c_opt['seed-ratio'] = ratio
    if seed_time:
        a2c_opt['seed-time'] = seed_time
    if TORRENT_TIMEOUT := config_dict['TORRENT_TIMEOUT']:
        a2c_opt['bt-stop-timeout'] = f'{TORRENT_TIMEOUT}'
    added_to_queue, event = await is_queued(listener.uid)
    if added_to_queue:
        if link.startswith('magnet:'):
            a2c_opt['pause-metadata'] = 'true'
        else:
            a2c_opt['pause'] = 'true'
    try:
        download = (await sync_to_async(aria2.add, link, a2c_opt))[0]
    except Exception as e:
        LOGGER.info(f"Aria2c Download Error: {e}")
        await sendMessage(listener.message, f'{e}')
        return
    if await aiopath.exists(link):
        await aioremove(link)
    if download.error_message:
        error = str(download.error_message).replace('<', ' ').replace('>', ' ')
        LOGGER.info(f"Aria2c Download Error: {error}")
        await sendMessage(listener.message, error)
        return

    gid = download.gid
    name = download.name
    async with download_dict_lock:
        download_dict[listener.uid] = Aria2Status(
            gid, listener, queued=added_to_queue)
    if added_to_queue:
        LOGGER.info(f"Added to Queue/Download: {name}. Gid: {gid}")
        if not download.is_torrent:
            await sendStatusMessage(listener.message)
    else:
        async with queue_dict_lock:
            non_queued_dl.add(listener.uid)
        LOGGER.info(f"Aria2Download started: {name}. Gid: {gid}")

    await listener.onDownloadStart()

    if not added_to_queue:
        await sendStatusMessage(listener.message)

    if added_to_queue:
        await event.wait()

        async with download_dict_lock:
            if listener.uid not in download_dict:
                return
            download = download_dict[listener.uid]
            download.queued = False
            new_gid = download.gid()

        await sync_to_async(aria2.client.unpause, new_gid)
        LOGGER.info(f'Start Queued Download from Aria2c: {name}. Gid: {gid}')

        async with queue_dict_lock:
            non_queued_dl.add(listener.uid)

###############-----Listener-----###############

@new_thread
async def __onDownloadStarted(api, gid):
    download = await sync_to_async(api.get_download, gid)
    if download.is_metadata:
        LOGGER.info(f'onDownloadStarted: {gid} METADATA')
    else:
        LOGGER.info(f'onDownloadStarted: {download.name} - Gid: {gid}')


@new_thread
async def __onDownloadComplete(api, gid):
    try:
        download = await sync_to_async(api.get_download, gid)
    except:
        return
    if download.followed_by_ids:
        new_gid = download.followed_by_ids[0]
        LOGGER.info(f'Gid changed from {gid} to {new_gid}')
    elif download.is_torrent:
        if dl := await getDownloadByGid(gid):
            if hasattr(dl, 'listener') and dl.seeding:
                LOGGER.info(
                    f"Cancelling Seed: {download.name} onDownloadComplete")
                listener = dl.listener()
                await listener.onUploadError(f"Seeding stopped with Ratio: {dl.ratio()} and Time: {dl.seeding_time()}")
                await sync_to_async(api.remove, [download], force=True, files=True)
    else:
        LOGGER.info(f"onDownloadComplete: {download.name} - Gid: {gid}")
        if dl := await getDownloadByGid(gid):
            listener = dl.listener()
            await listener.onDownloadComplete()
            await sync_to_async(api.remove, [download], force=True, files=True)


@new_thread
async def __onBtDownloadComplete(api, gid):
    seed_start_time = time()
    await sleep(1)
    download = await sync_to_async(api.get_download, gid)
    LOGGER.info(f"onBtDownloadComplete: {download.name} - Gid: {gid}")
    if dl := await getDownloadByGid(gid):
        listener = dl.listener()
        if listener.seed:
            try:
                await sync_to_async(api.set_options, {'max-upload-limit': '0'}, [download])
            except Exception as e:
                LOGGER.error(
                    f'{e} You are not able to seed because you added global option seed-time=0 without adding specific seed_time for this torrent GID: {gid}')
        else:
            try:
                await sync_to_async(api.client.force_pause, gid)
            except Exception as e:
                LOGGER.error(f"{e} GID: {gid}")
        await listener.onDownloadComplete()
        download = download.live
        if listener.seed:
            if download.is_complete:
                if dl := await getDownloadByGid(gid):
                    LOGGER.info(f"Cancelling Seed: {download.name}")
                    await listener.onUploadError(f"Seeding stopped with Ratio: {dl.ratio()} and Time: {dl.seeding_time()}")
                    await sync_to_async(api.remove, [download], force=True, files=True)
            else:
                async with download_dict_lock:
                    if listener.uid not in download_dict:
                        await sync_to_async(api.remove, [download], force=True, files=True)
                        return
                    download_dict[listener.uid] = Aria2Status(
                        gid, listener, True)
                    download_dict[listener.uid].start_time = seed_start_time
                LOGGER.info(f"Seeding started: {download.name} - Gid: {gid}")
                await update_all_messages()
        else:
            await sync_to_async(api.remove, [download], force=True, files=True)


@new_thread
async def __onDownloadStopped(api, gid):
    await sleep(6)
    if dl := await getDownloadByGid(gid):
        listener = dl.listener()
        await listener.onDownloadError('Dead torrent!')


@new_thread
async def __onDownloadError(api, gid):
    LOGGER.info(f"onDownloadError: {gid}")
    error = "None"
    try:
        download = await sync_to_async(api.get_download, gid)
        error = download.error_message
        LOGGER.info(f"Download Error: {error}")
    except:
        pass
    if dl := await getDownloadByGid(gid):
        listener = dl.listener()
        await listener.onDownloadError(error)


def start_aria2_listener():
    aria2.listen_to_notifications(threaded=True,
                                  on_download_start=__onDownloadStarted,
                                  on_download_error=__onDownloadError,
                                  on_download_stop=__onDownloadStopped,
                                  on_download_complete=__onDownloadComplete,
                                  on_bt_download_complete=__onBtDownloadComplete,
                                  timeout=60)


###############-----Status-----###############

def get_download(gid):
    try:
        return aria2.get_download(gid)
    except Exception as e:
        LOGGER.error(f'{e}: Aria2c, Error while getting torrent info')
        return None


class Aria2Status:

    def __init__(self, gid, listener, seeding=False, queued=False):
        self.__gid = gid
        self.__download = get_download(gid)
        self.__listener = listener
        self.queued = queued
        self.start_time = 0
        self.seeding = seeding
        self.message = listener.message

    def __update(self):
        if self.__download is None:
            self.__download = get_download(self.__gid)
        else:
            self.__download = self.__download.live
        if self.__download.followed_by_ids:
            self.__gid = self.__download.followed_by_ids[0]
            self.__download = get_download(self.__gid)

    def progress(self):
        return self.__download.progress_string()

    def processed_bytes(self):
        return self.__download.completed_length_string()

    def speed(self):
        return self.__download.download_speed_string()

    def name(self):
        return self.__download.name

    def size(self):
        return self.__download.total_length_string()

    def eta(self):
        return self.__download.eta_string()

    def status(self):
        self.__update()
        if self.__download.is_waiting or self.queued:
            if self.seeding:
                return Name.STATUS_QUEUEUP
            else:
                return Name.STATUS_QUEUEDL
        elif self.__download.is_paused:
            return Name.STATUS_PAUSED
        elif self.__download.seeder and self.seeding:
            return Name.STATUS_SEEDING
        else:
            return Name.STATUS_DOWNLOADING

    def seeders_num(self):
        return self.__download.num_seeders

    def leechers_num(self):
        return self.__download.connections

    def uploaded_bytes(self):
        return self.__download.upload_length_string()

    def upload_speed(self):
        self.__update()
        return self.__download.upload_speed_string()

    def ratio(self):
        return f"{round(self.__download.upload_length / self.__download.completed_length, 3)}"

    def seeding_time(self):
        return get_readable_time(time() - self.start_time)

    def download(self):
        return self

    def listener(self):
        return self.__listener

    def gid(self):
        self.__update()
        return self.__gid

    async def cancel_download(self):
        self.__update()
        await sync_to_async(self.__update)
        if self.__download.seeder and self.seeding:
            LOGGER.info(f"Cancelling Seed: {self.name()}")
            await self.__listener.onUploadError(f"Seeding stopped with Ratio: {self.ratio()} and Time: {self.seeding_time()}")
            await sync_to_async(aria2.remove, [self.__download], force=True, files=True)
        elif downloads := self.__download.followed_by:
            LOGGER.info(f"Cancelling Download: {self.name()}")
            await self.__listener.onDownloadError('Download cancelled by user!')
            downloads.append(self.__download)
            await sync_to_async(aria2.remove, downloads, force=True, files=True)
        else:
            if self.queued:
                LOGGER.info(f'Cancelling QueueDl: {self.name()}')
                msg = 'task have been removed from queue/download'
            else:
                LOGGER.info(f"Cancelling Download: {self.name()}")
                msg = 'Download stopped by user!'
            await self.__listener.onDownloadError(msg)
            await sync_to_async(aria2.remove, [self.__download], force=True, files=True)

