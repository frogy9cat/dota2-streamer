import time
import requests
from PIL import ImageGrab
import pydirectinput
import win32gui
import cv2
import json
import pyautogui
from aiogram import types
from aiogram.bot import Bot
import asyncio

from script_utils import open_write_console, cusotom_click, make_img_grey, get_hero
from obs_websocket import start_rec, stop_rec
from user_bot import send_replay
from config import ADMINS, CHANNELS, VID_CHANNEL_TAG, VID_CHANNEL_ID, BOT_TOKEN



bot = Bot(BOT_TOKEN)

sess = requests.session()


async def send_through_bot(chat_id, text):
    await bot.send_message(chat_id=chat_id, text=text)



def get_custom_screen(x1=0, y1=0, x2=0, y2=0):
    return ImageGrab.grab(bbox=(x1, y1, x2, y2))



def set_active_dota():
    if win32gui.GetWindowText(win32gui.GetForegroundWindow()) == "Dota 2":
        return
    else:
        hwnd = win32gui.FindWindow(None, "Dota 2")
        win32gui.SetForegroundWindow(hwnd)



async def check_is_start():
    is_start_screen = get_custom_screen(1700, 1025, 1900, 1075)
    is_start_screen.save("media/is_start_current.png")

    is_start_grey = make_img_grey("media/is_start_current.png")
    tmp_grey = make_img_grey("media/is_start_tmp.png")

    res = cv2.matchTemplate(is_start_grey, tmp_grey, cv2.TM_CCOEFF_NORMED)

    if res[0][0] > 0.8:
        return True
    else:
        await check_in_menu()



async def enter_latest_live_match(server_steam_id=None):

    try:
        await stop_rec()
    except:
            pass

    # Trying to find a match
    result = sess.get("https://api.opendota.com/api/live")
    lives = json.loads(result.content)
    latest_match = lives[-1]
    if server_steam_id:
        for live in lives:
            if live['server_steam_id'] == server_steam_id:
                latest_match =live
                return latest_match
            else:
                for admin in ADMINS:
                    await bot.send_message(chat_id=int(admin))
    else:
        pass

  
    match_id = int(latest_match["match_id"])
    print("Match id: "+str(match_id))

    server_steam_id = latest_match['server_steam_id']
    print("Server steam id: "+str(server_steam_id))

    # Get, order, and send match statistics
    for channel in CHANNELS:
        chat = await bot.get_chat(chat_id=channel)
        pinned_msg = chat["pinned_message"]["text"]
        pinned_id = chat["pinned_message"]["message_id"]
        new_msg = "⚫️ Ended/Closed" + pinned_msg[6:]
        new_msg = new_msg[:-18]
        await bot.edit_message_text(text=new_msg, chat_id=channel, message_id=pinned_id)

    try:
        statistics = await get_statistics(latest_match)
        await send_statistics(message=statistics)
    except:
        await enter_latest_live_match(1)

    # Opening new match
    connect_command = f"watch_server {server_steam_id}"
    set_active_dota()
    time.sleep(0.3)
    open_write_console(connect_command)
    time.sleep(10)
    await start_rec()

    # Waiting for the start / main page
    while True: 
        time.sleep(2)
        pydirectinput.press("1")
        is_start = await check_is_start()
        if is_start:

            time.sleep(0.1)
            cusotom_click(1894, 71)
            time.sleep(0.1)
            pyautogui.moveTo(800, 100)

            # Setting default settings in dota 2 console
            default_commands = [
                'dota_spectator_mode 2',
                'dota_minimap_always_draw_hero_icons false',
                'dota_camera_hold_select_to_follow true',
                'dota_spectator_fog_of_war -1'
            ]
            open_write_console(command=default_commands)
            time.sleep(0.1)
    
            pydirectinput.press('y')
            break
        else:
            time.sleep(1)
    
    try:
        await update_statistics(match_id=match_id)
        print("Statistics are updated successfully!")
    except:
        print("Statistics are not updated!")
        pass

    
    try:
        # Sendig a replay that was recorded one match ago
        await send_replay()

        # Addind video url to message in the main channel
        video_channel = await bot.get_chat(chat_id=VID_CHANNEL_ID)
        pinned_vid_id = video_channel["pinned_message"]["message_id"]

        await bot.send_message(chat_id=486178287, text=video_channel)
        await bot.pin_chat_message(chat_id=VID_CHANNEL_ID, message_id=pinned_vid_id+2)
        
        try:
            await bot.delete_message(chat_id=VID_CHANNEL_ID, message_id=pinned_vid_id+1)
        except:
            pass

        try:
            for channel in CHANNELS:
                chat = await bot.get_chat(chat_id=channel)
                video_channel = await bot.get_chat(chat_id=VID_CHANNEL_ID)
                pinned_vid_id = video_channel["pinned_message"]["message_id"]

                try:
                    pinned_msg = chat["pinned_message"]["text"]
                    pinned_id = chat["pinned_message"]["message_id"]
                    msg_for_link = int(pinned_id) - 4
                    await bot.edit_message_text(
                        text=pinned_msg+f'\n<a href="https://t.me/{VID_CHANNEL_TAG}/{pinned_vid_id}">Watch replay</a>',
                        chat_id=channel, 
                        message_id=msg_for_link,
                        parse_mode="HTML")
                except:
                    print("Message with stats is probably deleted")
    
        except:
            pass

    except:
        pass

    # Just the end of the function
    return True



async def check_in_menu():
    base_screen = get_custom_screen(600, 0, 1200, 50)
    base_screen.save("media/screen.png")            

    ok_button = get_custom_screen(800, 425, 1100, 650)
    ok_button.save("media/is_ok_button.png")             

    # Check if there are menu buttons
    base_screen_grey = make_img_grey("media/screen.png")
    base_tmp_grey = make_img_grey("media/template.png")

    # Check if there is "ok" button
    is_ok_btn_grey = make_img_grey("media/is_ok_button.png")
    ok_btn_tmp_grey = make_img_grey("media/ok_button.png")

    menu_result = cv2.matchTemplate(base_screen_grey, base_tmp_grey, cv2.TM_CCOEFF_NORMED)
    ok_btn_result = cv2.matchTemplate(is_ok_btn_grey, ok_btn_tmp_grey, cv2.TM_CCOEFF_NORMED)

    if menu_result[0][0] > 0.5:
        await enter_latest_live_match()
        return True
    elif ok_btn_result[0][0] > 0.7:
        pydirectinput.press("esc")
        pass
    else:
        print("In game")
        return False
    


async def get_statistics(latest_match, start=True, update=False):
    if start:
        server_steam_id = int(latest_match['server_steam_id'])
        match_info_json = sess.get(f"https://api.steampowered.com/IDOTA2MatchStats_570/GetRealtimeStats/v1?key=266DD08608085CE8EC90240302249C49&server_steam_id={server_steam_id}")
        match_info = json.loads(match_info_json.content)
        try:    
            teams = match_info["teams"]
            team_radiant = ""
            team_dire = ""
            message = ""
            message += f"🔴 Live Match | Average MMR:{latest_match['average_mmr']}\n"

            players_radiant = teams[0]["players"]
            players_dire = teams[1]["players"]

            team_radiant += f"\n1🏳️Team Radiant:\n"
            team_dire += f"\n🏴Team Dire:\n"

            team_radiant = await divide_into_teams(players=players_radiant, message=team_radiant, is_rad=True, update=update)
            team_dire = await divide_into_teams(players=players_dire, message=team_dire, is_rad=False, update=update) 

            message += team_radiant
            message += team_dire

        except KeyError:
            print("!!! Key Error in get_statistics !!!")

        print(message)   
        return message



async def divide_into_teams(players, message, is_rad=True, update=False):
    for num, player in enumerate(players):
        
        # Enumerating by order
        if is_rad:
            num += 1
        elif not is_rad:
            num += 6

        try:
            account_json = sess.get(f"https://api.opendota.com/api/players/{player['accountid']}/")
            account = json.loads(account_json.content)
            account_profile = account["profile"]
            pro = await is_pro(player)
            if pro:
                if player['heroid'] == 0:
                    message += f"{num}. {pro['personaname']} ({pro['name']}) | Draft | {account['leaderboard_rank']}\n"
                else:
                    message += f"{num}. {pro['personaname']} ({pro['name']}) | {await get_hero(player['heroid'])} | {account['leaderboard_rank']}\n"
            else:
                if player['heroid'] == 0:
                    message += f"{num}. {account_profile['personaname']} | Draft | {account['leaderboard_rank']}\n"
                else:
                    message += f"{num}. {account_profile['personaname']} | {await get_hero(player['heroid'])} | {account['leaderboard_rank']}\n"
        except KeyError:
            message += f"{num}. [Hidden profile]\n"

    return message



async def is_pro(player):
    json_all_pro = sess.get("https://api.opendota.com/api/proPlayers")
    all_pro = json.loads(json_all_pro.content)

    for pro in all_pro:
        if pro["account_id"] == player["accountid"]:
            return pro
        else:
            pass
    return False



async def send_statistics(message):

    for channel in CHANNELS:
        chat = await bot.get_chat(channel)
        pinned = int(chat["pinned_message"]["message_id"])
        new_message_id = pinned + 2
        service_message_id = pinned + 1
        await bot.delete_message(channel, message_id=service_message_id)
        time.sleep(0.3)
        await bot.send_message(chat_id=channel, text=message, parse_mode=types.ParseMode.HTML)
        time.sleep(0.3)
        await bot.pin_chat_message(chat_id=channel, message_id=new_message_id, disable_notification=True)
        print("sent!")



async def update_statistics(match_id):
    new_info_json = sess.get("https://api.opendota.com/api/live")
    new_info = json.loads(new_info_json.content)
    for channel in CHANNELS:
        chat = await bot.get_chat(channel)
        pinned = int(chat["pinned_message"]["message_id"])
        time.sleep(3)
        for match in new_info:
            if match['match_id'] == match_id:
                return match
        new_message = await get_statistics(match, update=True)
        await bot.edit_message_text(text=new_message+f"\nMatch is started!", chat_id=channel, message_id=pinned)
        print("updated! Live status.")





async def main():
    set_active_dota()
    time.sleep(2)
    while True:
        await check_in_menu()
        time.sleep(3)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(main())
    loop.run_forever()
    pending = asyncio.all_tasks(loop=loop)
    group = asyncio.gather(*pending, return_exceptions=True)
    loop.run_until_complete(group)
    loop.close()