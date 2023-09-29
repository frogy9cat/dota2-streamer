from environs import Env


env = Env()
env.read_env()

BOT_TOKEN = env.str("BOT_TOKEN")

ADMINS = env.str("ADMINS").split()
CHANNELS = env.str("CHANNELS").split()
VID_CHANNEL_ID = env.int("VID_CHANNEL_ID")
VID_CHANNEL_TAG = env.str("VID_CHANNEL_TAG")

API_ID = env.int("API_ID")
API_HASH = env.str("API_HASH")

OBS_PASSWORD = env.str("OBS_PASSWORD")