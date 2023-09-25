#from pymongo import MongoClient
import motor.motor_asyncio
import os
from dotenv import load_dotenv

load_dotenv()

#DB_URL = os.environ.get('MONGODB_URL')

DB_URL = "mongodb+srv://chathub:chathub@atlascluster.wzngxmf.mongodb.net/?retryWrites=true&w=majority"

#client = MongoClient(DB_URL)
client = motor.motor_asyncio.AsyncIOMotorClient(DB_URL)
db = client['chathub']
