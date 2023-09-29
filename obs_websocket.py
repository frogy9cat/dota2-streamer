import sys
from config import OBS_PASSWORD

# import logging
# logging.basicConfig(level=logging.DEBUG)

sys.path.append('../')
from obswebsocket import obsws, requests

host = "localhost"
port = 4455

ws = obsws(host, port, OBS_PASSWORD)


async def start_rec():
    scenes = ws.call(requests.GetSceneList())
    for s in scenes.getScenes():
        ws.call(requests.StartRecord())


async def stop_rec():
    ws.connect()
    scenes = ws.call(requests.GetSceneList())
    for s in scenes.getScenes():
        ws.call(requests.StartRecord())

    ws.call(requests.StopRecord())