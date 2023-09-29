from pyrogram import Client  #, filters, types

import os
from config import API_ID, API_HASH, VID_CHANNEL_ID

# import asyncio


app = Client(name="replay_sender", api_id=API_ID, api_hash=API_HASH)


async def send_replay():
    await app.start()
    try:
        file_name = os.listdir("output/")[-3]
        await app.send_video(chat_id=VID_CHANNEL_ID, video=f"output/{file_name}")
    except:
        print("No saved replays")
        pass
    await app.stop()
    
    try: 
        old_files = list(os.listdir("output/")[:-3])
        for file in old_files:
            os.remove(f"output/{file}")
    except: 
        print("Old replays deleted!")
        pass


# app.run()       #Run to authorize