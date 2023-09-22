import time
import requests
from PIL import ImageGrab
import pydirectinput
import win32gui
import cv2
import json
import asyncio
from aiogram import types
from aiogram.bot import Bot

from .a_utils import open_write_console, select_hero, cusotom_click
from .config import CHANNELS, BOT_TOKEN




bot = Bot(BOT_TOKEN)

sess = requests.session()

with open("heroes.json", "r") as j:
    heroes = json.loads(j.read())['heroes']



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

    is_start_rgb = cv2.imread("media/is_start_current.png")
    is_start_grey = cv2.cvtColor(is_start_rgb, cv2.COLOR_BGR2RGB)

    tmp_rgb = cv2.imread("media/is_start_tmp.png")
    tmp_grey = cv2.cvtColor(tmp_rgb, cv2.COLOR_BGR2RGB)

    res = cv2.matchTemplate(is_start_grey, tmp_grey, cv2.TM_CCOEFF_NORMED)

    if res[0][0] > 0.8:
        return True
    else:
        await check_in_menu(1)



async def enter_latest_live_match(player=1):

    result = sess.get("https://api.opendota.com/api/live")
    latest_match = json.loads(result.content)[-1]
    match_id = int(latest_match["match_id"])
    print(match_id)

    server_steam_id = latest_match['server_steam_id']
    print(server_steam_id)
#
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
#
    connect_command = f"watch_server {server_steam_id}"
    set_active_dota()
    time.sleep(0.3)
    open_write_console(connect_command)
    time.sleep(10)
    while True: 
        time.sleep(2)
        pydirectinput.press("1")
        is_start = await check_is_start()
        await check_in_menu(1)
        if is_start:
            time.sleep(0.1)
            cusotom_click(1894, 71)
            select_hero(num=player)
            time.sleep(0.1)
            open_write_console(command='dota_spectator_mode 2')
            open_write_console(command='dota_minimap_always_draw_hero_icons false')
            open_write_console(command='dota_camera_hold_select_to_follow true')
            open_write_console(command='dota_spectator_fog_of_war -1')
            pydirectinput.press('y')
            break
        else:
            time.sleep(1)
    await update_statistics(match_id=match_id)
    return True



async def check_in_menu(player: int):
    base_screen = get_custom_screen(600, 0, 1200, 50)
    base_screen.save("media/screen.png")            #check if there are menu buttons

    scrn = get_custom_screen(800, 425, 1100, 650)
    scrn.save("media/is_ok_button.png")             #check if there is "ok" button

    base_img_rgb = cv2.imread("media/screen.png")
    base_img_grey = cv2.cvtColor(base_img_rgb, cv2.COLOR_BGR2RGB)

    base_tmp_rgb = cv2.imread("media/template.png")
    base_tmp_grey = cv2.cvtColor(base_tmp_rgb, cv2.COLOR_BGR2RGB)

    scrn_img_rgb = cv2.imread("media/is_ok_button.png")
    scrn_img_grey = cv2.cvtColor(scrn_img_rgb, cv2.COLOR_BGR2RGB)
    
    scrn_tmp_rgb = cv2.imread("media/ok_button.png")
    scrn_tmp_grey = cv2.cvtColor(scrn_tmp_rgb, cv2.COLOR_BGR2RGB)

    res1 = cv2.matchTemplate(base_img_grey, base_tmp_grey, cv2.TM_CCOEFF_NORMED)
    res2 = cv2.matchTemplate(scrn_img_grey, scrn_tmp_grey, cv2.TM_CCOEFF_NORMED)

    if res1[0][0] > 0.5:
        await enter_latest_live_match(player)
        return True
    elif res2[0][0] > 0.7:
        pydirectinput.press("esc")
        pass
    else:
        print("in game")
        return False



async def get_hero(hero_id):
    result = ""
    for hero in heroes:
        if hero_id == hero["id"]:
            result = hero['localized_name']
    if hero:
        return result
    else:
        return None
    


async def get_statistics(latest_match, start=True):
    if start:
        # players = latest_match["players"]
        server_steam_id = int(latest_match['server_steam_id'])
        match_info_json = sess.get(f"https://api.steampowered.com/IDOTA2MatchStats_570/GetRealtimeStats/v1?key=266DD08608085CE8EC90240302249C49&server_steam_id={server_steam_id}")
        match_info = json.loads(match_info_json.content)
        teams = match_info["teams"]
        team_radiant = ""
        team_dire = ""
        message = ""
        message += f"🔴 Live Match | Average MMR:{latest_match['average_mmr']}\n"
        # message += f"Match id: {latest_match['match_id']}\n\n"

        players_radiant = teams[0]["players"]
        # print(players_radiant)
        players_dire = teams[1]["players"]

        team_radiant += f"\n1🏳️Team Radiant:\n"
        team_dire += f"\n🏴Team Dire:\n"

        team_radiant = await divide_into_teams(players=players_radiant, message=team_radiant, is_rad=True)
        team_dire = await divide_into_teams(players=players_dire, message=team_dire, is_rad=False) 

        message += team_radiant
        message += team_dire
        print(message)   
        return message



async def divide_into_teams(players, message, is_rad=True):
    for num, player in enumerate(players):
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
                    message += f"{num}. <b>{pro['personaname']} ({pro['name']}) | Draft | {account['leaderboard_rank']}</b>\n"
                else:
                    message += f"{num}. <b>{pro['personaname']} ({pro['name']}) | {await get_hero(player['heroid'])} | {account['leaderboard_rank']}</b>\n"
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
        await bot.unpin_chat_message(channel, message_id=pinned)
        time.sleep(0.3)
        await bot.send_message(chat_id=channel, text=message, parse_mode=types.ParseMode.HTML)
        time.sleep(0.3)
        await bot.pin_chat_message(chat_id=channel, message_id=new_message_id, disable_notification=True)
        print("sent!")



async def get_match_info(match_id):
    time.sleep(2)
    await check_in_menu(1)
    match_info_json = sess.get(f"https://api.opendota.com/api/matches/{match_id}")
    match_info = json.loads(match_info_json.content)
    try:
        print(match_info['match_id'])
        return True
    except KeyError:
        pass



async def update_statistics(match_id):
    for channel in CHANNELS:
        chat = await bot.get_chat(channel)
        pinned = int(chat["pinned_message"]["message_id"])
        time.sleep(3)
        new_info_json = sess.get("https://api.opendota.com/api/live")
        new_info = json.loads(new_info_json.content)
        for match in new_info:
            if match['match_id'] == match_id:
                return match
        new_message = await get_statistics(match)
        await bot.edit_message_text(text=new_message+f"\nMatch is started!", chat_id=channel, message_id=pinned)
        print("updated! Live status.")



async def main():
    set_active_dota()
    time.sleep(2)
    while True:
        await check_in_menu(1)
        time.sleep(3)



loop = asyncio.get_event_loop()
loop.create_task(main())
loop.run_forever()
pending = asyncio.all_tasks(loop=loop)
group = asyncio.gather(*pending, return_exceptions=True)
loop.run_until_complete(group)
loop.close()