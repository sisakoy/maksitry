from config import Config, LOGGER, user_data, bot_id, config_dict
from motor.motor_asyncio import AsyncIOMotorClient
from aiofiles import open as aiopen
from aiofiles.os import path as aiopath, makedirs
from dotenv import dotenv_values


class Database:
    def __init__(self, close=True):
        self._client = None
        self.db = None
        self.error = False
        self.close = close
        self.__checkConnection()
        
    def __checkConnection(self):
        if not len(Config.MONGODB_URI):
            LOGGER.info("MongoDB URI not found")
            self.error = True
            return
        try:
            LOGGER.info("Connecting with MongoDB database")
            self._client = AsyncIOMotorClient(Config.MONGODB_URI)
            self.db = self._client[Config.DB_NAME]
        except Exception as e:
            LOGGER.error(f"Error In Database connection: {e}")
            self.error = True
    
    async def update_user_data(self, user_id):
        if self.error:
            return
        if not user_id in user_data:
            LOGGER.error(f"{user_id} not found in user_data")
            if self.close:
                    self._client.close()
            return
        data = user_data[user_id]
        if data.get('thumb'):
            del data['thumb']
        if data.get('rclone'):
            del data['rclone']
        await self.db.user_data.update_one({'_id': user_id}, {'$set': data}, upsert=True)
        if self.close:
            self._client.close()
    
    async def update_user_doc(self, user_id, key, path=''):
        if self.error:
            return
        if await aiopath.exists(path):
            async with aiopen(path, 'rb+') as doc:
                doc_bin = await doc.read()
        else:
            doc_bin = ''
        await self.db.user_data.update_one({'_id': user_id}, {'$set': {key: doc_bin}}, upsert=True)
        if self.close:
            self._client.close()
    
    async def update_private_file(self, path):
        if self.error:
            return
        if await aiopath.exists(path):
            async with aiopen(path, 'rb+') as pf:
                pf_bin = await pf.read()
        else:
            pf_bin = ''
        path = path.replace('.', '__')
        await self.db.files.update_one({'_id': bot_id}, {'$set': {path: pf_bin}}, upsert=True)
        if path == 'config.env':
            await self.update_deploy_config()
        if self.close:
            self._client.close()
    
    async def load_user_data(self):
        if self.error:
            return
        rows = self.db.user_data.find({})
        async for row in rows:
            thumb_path = f'Thumbnails/{row["_id"]}.jpg'
            rclone_path = f'rclone/{row["_id"]}.conf'
            if row.get('thumb'):
                if not await aiopath.exists('Thumbnails'):
                    await makedirs('Thumbnails')
                async with aiopen(thumb_path, 'wb+') as f:
                    await f.write(row['thumb'])
            if row.get('rclone'):
                if not await aiopath.exists('rclone'):
                    await makedirs('rclone')
                async with aiopen(rclone_path, 'wb+') as f:
                    await f.write(row['rclone'])
            uid = row['_id']
            del row['_id']
            user_data[uid] = row
            del row
        await rows.close()
        if self.close:
            self._client.close()
    
    async def delete_user_data(self):
        if self.error:
            return
        result = await self.db.drop_collection('user_data')
        if self.close:
            self._client.close()
        return result
    
    async def update_config(self, dict_):
        if self.error:
            return
        await self.db.config.update_one({'_id': bot_id}, {'$set': dict_}, upsert=True)
        if self.close:
            self._client.close()
    
    async def update_deploy_config(self):
        if self.error:
            return
        await self.db.deployConfig.replace_one({'_id': bot_id}, dict(dotenv_values('config.env')), upsert=True)
        if self.close:
            self._client.close()
    
    async def save_config(self):
        if self.error:
            return
        await self.db.config.update_one({'_id': bot_id}, {'$set': config_dict}, upsert=True)
        if self.close:
            self._client.close()
    
    async def reset_config(self):
        if self.error:
            return
        for var in vars(Config):
            if not var.startswith('__'):
                config_dict[var] = vars(Config)[var]
        await self.db.config.update_one({'_id': bot_id}, {'$set': config_dict}, upsert=True)
        if self.close:
            self._client.close()
        
    async def load_config(self):
        if self.error:
            return
        config = await self.db.config.find_one({'_id': bot_id})
        if config:
            config_dict.update(config)
        del config
        if self.close:
            self._client.close()
    
    async def delete_config(self):
        if self.error:
            return
        result = await self.db.drop_collection('config')
        if self.close:
            self._client.close()
        return result
    
    async def insert_one(self, dict_, _id, col_name):
        if self.error:
            return
        await self.db[col_name].update_one({'_id': _id}, {'$set': dict_}, upsert=True)
        if self.close:
            self._client.close()
    
    async def get_doc(self, _id, col_name):
        if self.error:
            return
        result = await self.db[col_name].find_one({'_id': _id})
        if self.close:
            self._client.close()
        return result
    
    async def get_all_docs(self, col_name):
        if self.error:
            return
        all_docs = []
        rows = self.db[col_name].find({})
        async for row in rows:
            all_docs.append(row)
            del row
        await rows.close()
        if self.close:
            self._client.close()
        return all_docs
    
    async def delete_docs(self, _id, col_name):
        if self.error:
            return
        await self.db[col_name].delete_many({'_id': _id})
        if self.close:
            self._client.close()
    
    async def is_doc_exist(self, _id, col_name):
        if self.error:
            return
        result = await self.db[col_name].find_one({'_id': _id})
        if self.close:
            self._client.close()
        return result
    
    async def count_docs(self, col_name):
        if self.error:
            return
        result = await self.db[col_name].count_documents({})
        if self.close:
            self._client.close()
        return result
    
    async def col_stats(self, col_name):
        if self.error:
            return
        result = await self.db.command("collstats", col_name)
        if self.close:
            self._client.close()
        return result
    
    async def col_size(self, col_name):
        if self.error:
            return 0
        result = (await self.db.command("collstats", col_name)).get('storageSize', 0)
        if self.close:
            self._client.close()
        return result
    
    async def db_stats(self):
        if self.error:
            return
        result = await self.db.command("dbstats")
        if self.close:
            self._client.close()
        return result
    
    async def db_size(self): 
        if self.error:
            return 0
        result = (await self.db.command("dbstats")).get('storageSize', 0)
        if self.close:
            self._client.close()
        return result
    
    async def col_list(self):
        if self.error:
            return
        result = await self.db.list_collection_names()
        if self.close:
            self._client.close()
        return result
    
    async def delete_col(self, col_name):
        if self.error:
            return
        result = await self.db.drop_collection(col_name)
        if self.close:
            self._client.close()
        return result
    
    async def db_list(self):
        if self.error:
            return
        result = await self._client.list_database_names()
        if self.close:
            self._client.close()
        return result
    
    async def delete_current_db(self):
        if self.error:
            return
        await self._client.drop_database(Config.DB_NAME)
        if self.close:
            self._client.close()
    
    async def delete_db(self, db_name):
        if self.error:
            return
        await self._client.drop_database(db_name)
        if self.close:
            self._client.close()