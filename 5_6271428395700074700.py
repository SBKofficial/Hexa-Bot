import asyncio
import sqlite3
import json
import logging
import os
from datetime import datetime
from telethon import TelegramClient, events, Button
from telethon.sessions import StringSession
from telethon.errors import SessionPasswordNeededError
from random import randint

# --- CONFIGURATION ---
API_ID = 26759620
API_HASH = 'e5c2cfff7011b7fee949ed8293bafde8'
BOT_TOKEN = '8524436090:AAEkcu9kriRybZGxL9a6M-LWMnS8qgKh0N0'
HEXA_ID = "HeXamonbot"  # Username string to prevent initial ID errors

DEFAULT_LIST = ["Tauros","Toucannon","Trumbeak","Pikipek","Lillipup","Arrokuda", "Barraskewda","Dragapult","Drakloak","Duraludon","Rookidee","impidimp","Drizzile","Cufant","Koffing","Weezing","Thwackey","Sirfetch'd","Raboot","Scorbunny","Grookey","Sobble","Passimian","Impidimp","Rillaboom","Morgrem","Primeape","Drampa","Wimpod","Durant","Torracat","Mankey","Rotom", "Basculin", "Greninja", "Froakie", "Kakuna", "Frogadier","Floette", "Flabebe","Florges", "Fennekin", "Braixen", "Delphox", "Fletchling", "Weedle", "Wyrdeer", "Gible", "Ursaluna", "Cyndaquil", "Sneasel", "Sneasler", "Happiny", "Stantler", "Voltorb", "Starly", "Porygon", "Staraptor", "Basculegion", "Diglett", "Dugtrio", "Rufflet", "Lycanroc", "Goomy", "Sliggoo", "Goodra", "Golisopod", "Turtonator", "Vulpix", "Ninetales", "Dhelmise", "Jangmo-o", "Hakamo-o", "Kommo-o", "Lapras","Popplio", "Brionne","Bewear","Primarina", "Chansey", "Blissey", "Munchlax", "Snorlax","Cyndaquill", "Quilava", "Typhlosiom","Totodile", "Croconaw", "Feraligatr","Togepi", "Togetic","Teddiursa","Ursaring","Oranguru","Blissey", "Stufful", "Litwick"," Unfezant", "Golett", "Lampent", "Frillish", "Timburr", "Axew", "Herdier", "Gurdurr", "Archen", "Tranquill", "Dwebble", "Darumaka", "Crustle", "Sandile", "Krookodile", "Haxorus", "Vibrava", "Drapion", "Darmanitan", "Snivy", "Chandelure", "Conkeldurr", "Escavalier", "Karrablast", "Drilbur", "Skorupi", "Zorua", "Litwick", "Stoutland", "Krokorok", "Pidove", "Braviary", "Archeops", "Staryu", "Fraxure", "Golurk", "Mareep", "Charizard","Slakoth","Tyrogue","Magikarp","Dragonair","Dragonite","Dratini","Squirtle","Wartortle","Ivysaur","Bulbasaur","Charmander","Charmeleon","Gastly","Haunter","Grimer","Sceptile","Muk","Beldum","Metang","Swablu","Ralts","Kirlia","Bagon","Shelgon","Vigoroth","Slaking", "Abra","Kadabra","Meditite","Torchic","Combusken","Mudkip","Marshtomp","Grovyle","Treecko", "Venusaur", "Blastoise", "Beedrill", "Pidgeot", "Alakazam", "Slowbro", "Gengar","Larvitar", "Litten","Pinsir", "Gyarados", "Aerodactyl", "Mewtwo", "Kyogre", " Gr
oundon", "Ampharos", " Steelix", "Scizor", "Heracross", "Houndoom", "Tyranitar", "Blaziken", "Swampert", "Gardevoir", "Sableye", "Mawile", "Medicham", "Manectric", "Sharpedo", "Camerupt", "Altaria", "Banette", "Absol", "Salamence", "Metagross", "Latias", "Latios", "Rayquaza", "Lopunny", "Garchomp", "Lucario", "Abomasnow", "Gallade", "Audino", "Diancie", "Zacian", "Zamazenta", "Glastrier", "Spectrier", "Deoxys","Cresselia", "Zapdos", "Regigigas", "Raikou", "Entei", "Mewtwo", "Jirachi", "Kyurem", "Ho-Oh", "Cobalion", "Articuno", "Latios", "Suicune", "Lugia", "Latias", "Groudon", "Kyogre", "Deoxys", "Regice", "Registeel", "Regirock", "Rayquaza", "Mew", "Celebi", "Uxie", "Mesprit", "Azelf", "Dialga", "Palkia", "Heatran", "Giratina", "Cresselia", "Phione", "Manaphy", "Darkrai", "Shaymin", "Arceus", "Victini", "Terrakion", "Virizion", "Tornadus", "Thundurus", "Reshiram", "Zekrom", "Landorus", "Kyurem", "Keldeo", "Meloetta", "Genesect", "Cosmog", "Cosmoem", "Solgaleo", "Lunala", "Buzzwole", "Pheromosa", "Necrozma", "Kartana", "Guzzlord", "Magearna", "Marshadow", "Naganadel", "Zeraora", "Meltan", "Melmetal", "Urshifu", "Eternatus", "Spectrier"]

# --- LOGGING ---
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- GLOBAL VARS ---
user_clients = {}   
user_configs = {}   

# --- DATABASE SETUP ---
def init_db():
    conn = sqlite3.connect('hexabot.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                      (user_id INTEGER PRIMARY KEY, 
                       session TEXT, 
                       poke_list TEXT, 
                       ball TEXT,
                       total_matched INTEGER DEFAULT 0,
                       total_caught INTEGER DEFAULT 0,
                       total_fled INTEGER DEFAULT 0,
                       total_tms INTEGER DEFAULT 0,
                       total_megastones INTEGER DEFAULT 0,
                       total_shinies INTEGER DEFAULT 0,
                       start_time TEXT)''')
    conn.commit()
    return conn

db = init_db()

# --- DATABASE HELPERS ---
def update_stat(user_id, column):
    """Increments a specific stat column for a user."""
    cursor = db.cursor()
    cursor.execute(f"UPDATE users SET {column} = {column} + 1 WHERE user_id = ?", (user_id,))
    db.commit()
    if user_id in user_configs:
        user_configs[user_id]['stats'][column] += 1

def reset_stats(user_id):
    """Resets all stats."""
    cursor = db.cursor()
    now = datetime.now().isoformat()
    cursor.execute("""UPDATE users SET 
                      total_matched=0, total_caught=0, total_fled=0, 
                      total_tms=0, total_megastones=0, total_shinies=0, start_time=? 
                      WHERE user_id = ?""", (now, user_id))
    db.commit()
    if user_id in user_configs:
        user_configs[user_id]['stats'] = {
            'total_matched': 0, 'total_caught': 0, 'total_fled': 0,
            'total_tms': 0, 'total_megastones': 0, 'total_shinies': 0, 'start_time': now
        }

# --- CLICK RETRY HELPER ---
async def smart_click_with_retry(client, chat_id, message_object, button_text_to_click):
    attempt = 1
    original_id = message_object.id
    original_text_len = len(message_object.raw_text)
    
    while attempt <= 10:
        try:
            msg_current = await client.get_messages(chat_id, ids=original_id)
            if not msg_current or not msg_current.reply_markup: return

            all_buttons = []
            for row in msg_current.reply_markup.rows:
                all_buttons.extend(row.buttons)
            
            target_index = -1
            for i, btn in enumerate(all_buttons):
                if button_text_to_click.lower() in btn.text.lower():
                    target_index = i
                    break
            
            if target_index == -1: return

            await msg_current.click(target_index)
            await asyncio.sleep(5) 

            # Check for Updates
            latest_msgs = await client.get_messages(chat_id, limit=1)
            if latest_msgs and latest_msgs[0].id > original_id: return 

            msg_after = await client.get_messages(chat_id, ids=original_id)
            if not msg_after: return 
            
            if len(msg_after.raw_text) != original_text_len: return 
            
            current_buttons = [b.text for row in msg_after.reply_markup.rows for b in row.buttons] if msg_after.reply_markup else []
            if not any(button_text_to_click.lower() in b.lower() for b in current_buttons): return 
            
            logger.info(f"[RETRY CLICK] No update for '{button_text_to_click}'. Clicking again...")
            attempt += 1

        except Exception as e:
            logger.error(f"[ERROR] Click Retry: {e}")
            await asyncio.sleep(5)

# --- HUNT RETRY HELPER ---
async def send_hunt_with_retry(client, chat_id, user_id):
    # RESOLVE ID: Fix for ValueError with username
    try:
        if isinstance(chat_id, str):
            entity = await client.get_entity(chat_id)
            target_id = entity.id
        else:
            target_id = chat_id
    except Exception as e:
        logger.error(f"[ERROR] Could not resolve bot ID: {e}")
        return

    await client.send_message(chat_id, "/hunt")
    await asyncio.sleep(1)
    
    try:
        latest = await client.get_messages(chat_id, limit=1)
        last_msg_id = latest[0].id if latest else 0
    except: last_msg_id = 0

    while True: 
        await asyncio.sleep(5)
        try:
            if user_configs[user_id].get('mode') != 'SEARCHING':
                logger.info("[HUNT ABORT] User entered battle.")
                return

            latest = await client.get_messages(chat_id, limit=1)
            if not latest: continue
            
            latest_msg = latest[0]

            if latest_msg.id > last_msg_id:
                if latest_msg.sender_id == target_id:
                    logger.info("[HUNT SUCCESS] Game responded.")
                    return
                else:
                    logger.info("[HUNT RESET] User action detected.")
                    last_msg_id = latest_msg.id
                    continue
            
            logger.info("[HUNT RETRY] No response. Retrying...")
            await client.send_message(chat_id, "/hunt")
            
            latest_retry = await client.get_messages(chat_id, limit=1)
            if latest_retry: last_msg_id = latest_retry[0].id
            
        except Exception as e:
             logger.error(f"[ERROR] Hunt Retry: {e}")
             await asyncio.sleep(10)

# --- MASTER BOT INSTANCE ---
master_bot = TelegramClient('master_bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# --- USERBOT LOGIC ---
async def run_userbot(user_id, session_str):
    try:
        client = TelegramClient(StringSession(session_str), API_ID, API_HASH)
        await client.connect()
        user_clients[user_id] = client
        try: await client.get_entity(HEXA_ID) 
        except: await client.send_message(HEXA_ID, "/start")

        logger.info(f"--- Userbot Started for ID: {user_id} ---")
    except Exception as e:
        logger.error(f"FATAL: {e}")
        return

    @client.on(events.NewMessage(chats=HEXA_ID))
    async def msg_handler(event):
        config = user_configs.get(user_id)
        if not config or not config.get('hunting'): return
        
        mode = config.get('mode', 'SEARCHING')
        text = event.raw_text
        text_lower = text.lower()
        
        # --- GLOBAL CHECKS ---
        if "✨" in text_lower or "shiny" in text_lower:
            config['hunting'] = False
            update_stat(user_id, 'total_shinies') 
            await master_bot.send_message(user_id, "🛑 **SHINY DETECTED!** Bot stopped.")
            return

        if "💿 found!" in text:
            update_stat(user_id, 'total_tms')
            logger.info(f"[LOOT] TM Found! Total: {config['stats']['total_tms']}")
            await asyncio.sleep(1)
            await send_hunt_with_retry(client, HEXA_ID, user_id)
            return

        if "mega stone found!" in text_lower:
            update_stat(user_id, 'total_megastones')
            logger.info(f"[LOOT] Mega Stone Found! Total: {config['stats']['total_megastones']}")
            await asyncio.sleep(1)
            await send_hunt_with_retry(client, HEXA_ID, user_id)
            return

        # --- MODE 1: SEARCHING ---
        if mode == 'SEARCHING':
            if "battle begins" in text_lower: return

            if "wild" in text_lower:
                target_found = False
                for p in config['list']:
                    if p.lower() in text_lower:
                        target_found = True
                        break
                
                if target_found:
                    update_stat(user_id, 'total_matched')
                    logger.info(f"[MATCH] Target Found! Total Matched: {config['stats']['total_matched']}")
                    
                    if event.message.reply_markup:
                        config['mode'] = 'BATTLING'
                        await smart_click_with_retry(client, HEXA_ID, event.message, "Battle")
                        return
                else:
                    logger.info(f"[SKIP] Skipping...")
                    await asyncio.sleep(1)
                    await send_hunt_with_retry(client, HEXA_ID, user_id)
                    return

        # --- MODE 2: BATTLING ---
        elif mode == 'BATTLING':
            if "caught" in text_lower:
                update_stat(user_id, 'total_caught')
                logger.info(f"[CAUGHT] Total Caught: {config['stats']['total_caught']}")
                config['mode'] = 'SEARCHING'
                await asyncio.sleep(1)
                await send_hunt_with_retry(client, HEXA_ID, user_id)
                return
            
            if "fled" in text_lower:
                update_stat(user_id, 'total_fled')
                logger.info(f"[FLED] Total Fled: {config['stats']['total_fled']}")
                config['mode'] = 'SEARCHING'
                await asyncio.sleep(1)
                await send_hunt_with_retry(client, HEXA_ID, user_id)
                return

            if event.message.reply_markup:
                all_buttons = [b.text for row in event.message.reply_markup.rows for b in row.buttons]
                ball = config.get('ball')
                
                found_btn = next((b for b in all_buttons if ball.lower() in b.lower()), None)
                if found_btn:
                    await smart_click_with_retry(client, HEXA_ID, event.message, found_btn)
                    return
                
                found_menu = next((b for b in all_buttons if "poke balls" in b.lower()), None)
                if found_menu:
                    await smart_click_with_retry(client, HEXA_ID, event.message, "Poke Balls")
                    return

    @client.on(events.MessageEdited(chats=HEXA_ID))
    async def edit_handler(event):
        config = user_configs.get(user_id)
        if not config or not config.get('hunting'): return
        
        if config.get('mode') == 'BATTLING':
            text_lower = event.raw_text.lower()
            
            if "caught" in text_lower:
                update_stat(user_id, 'total_caught')
                config['mode'] = 'SEARCHING'
                await asyncio.sleep(1)
                await send_hunt_with_retry(client, HEXA_ID, user_id)
                return

            if "fled" in text_lower:
                update_stat(user_id, 'total_fled')
                config['mode'] = 'SEARCHING'
                await asyncio.sleep(1)
                await send_hunt_with_retry(client, HEXA_ID, user_id)
                return

            if event.message.reply_markup:
                all_buttons = [b.text for row in event.message.reply_markup.rows for b in row.buttons]
                ball = config.get('ball')
                
                found_btn = next((b for b in all_buttons if ball.lower() in b.lower()), None)
                if found_btn:
                    await smart_click_with_retry(client, HEXA_ID, event.message, found_btn)
                    return
                
                found_menu = next((b for b in all_buttons if "poke balls" in b.lower()), None)
                if found_menu:
                    await smart_click_with_retry(client, HEXA_ID, event.message, "Poke Balls")
                    return

    await client.run_until_disconnected()

# --- MASTER COMMANDS ---

# 1. EXPORT
@master_bot.on(events.NewMessage(pattern='/sessionexport'))
async def session_export(event):
    uid = event.sender_id
    if uid not in user_configs: return await event.reply("Login first.")
    
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (uid,))
    row = cursor.fetchone()
    
    data = {
        'user_id': row[0],
        'session': row[1],
        'poke_list': json.loads(row[2]),
        'ball': row[3],
        'stats': {
            'total_matched': row[4],
            'total_caught': row[5],
            'total_fled': row[6],
            'total_tms': row[7],
            'total_megastones': row[8],
            'total_shinies': row[9],
            'start_time': row[10]
        }
    }
    fname = f"backup_{uid}.json"
    with open(fname, "w") as f: json.dump(data, f, indent=4)
    await event.reply("📂 **Your Database Backup:**", file=fname)
    os.remove(fname)

# 2. IMPORT (Fixed Auto-Start)
@master_bot.on(events.NewMessage(pattern='/sessionimport'))
async def session_import(event):
    uid = event.sender_id
    reply = await event.get_reply_message()
    if not reply or not reply.file:
        return await event.reply("⚠️ Reply to a .json backup file.")
    
    try:
        fpath = await reply.download_media()
        with open(fpath, 'r') as f: data = json.load(f)
        
        stats = data['stats']
        cursor = db.cursor()
        cursor.execute("""INSERT OR REPLACE INTO users 
                          (user_id, session, poke_list, ball, 
                           total_matched, total_caught, total_fled, total_tms, total_megastones, total_shinies, start_time) 
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", 
                       (uid, data['session'], json.dumps(data['poke_list']), data['ball'],
                        stats['total_matched'], stats['total_caught'], stats['total_fled'], 
                        stats['total_tms'], stats['total_megastones'], stats.get('total_shinies', 0), stats['start_time']))
        db.commit()
        
        user_configs[uid] = {
            'list': data['poke_list'],
            'ball': data['ball'],
            'hunting': False, 
            'mode': 'SEARCHING',
            'stats': stats
        }
        
        # FIX: START USERBOT
        if uid in user_clients:
            await user_clients[uid].disconnect()
        asyncio.create_task(run_userbot(uid, data['session']))
        
        await event.reply("✅ **Backup Imported!**\nUserbot started automatically.")
        os.remove(fpath)
    except Exception as e:
        await event.reply(f"❌ Error: {e}")

# 3. STATUS
@master_bot.on(events.NewMessage(pattern='/status'))
async def status_command(event):
    uid = event.sender_id
    if uid not in user_configs: return await event.reply("Login first.")
    
    stats = user_configs[uid]['stats']
    start_dt = datetime.fromisoformat(stats['start_time'])
    uptime = datetime.now() - start_dt
    hours, remainder = divmod(uptime.seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    
    msg = (
        f"📊 **HUNTING STATUS**\n\n"
        f"🎯 **Matched:** `{stats['total_matched']}`\n"
        f"✅ **Caught:** `{stats['total_caught']}`\n"
        f"💨 **Fled:** `{stats['total_fled']}`\n"
        f"✨ **Shinies:** `{stats.get('total_shinies', 0)}`\n"
        f"💿 **TMs:** `{stats['total_tms']}`\n"
        f"🔮 **Mega Stones:** `{stats['total_megastones']}`\n\n"
        f"⏱️ **Uptime:** `{uptime.days}d {hours}h {minutes}m`"
    )
    btns = [[Button.inline("🔄 Refresh", b"refresh_status"), Button.inline("🗑️ Reset", b"reset_status")]]
    await event.reply(msg, buttons=btns)

@master_bot.on(events.CallbackQuery(pattern=b'refresh_status'))
async def refresh_status(event):
    uid = event.sender_id
    if uid not in user_configs: return
    
    stats = user_configs[uid]['stats']
    start_dt = datetime.fromisoformat(stats['start_time'])
    uptime = datetime.now() - start_dt
    hours, remainder = divmod(uptime.seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    
    msg = (
        f"📊 **HUNTING STATUS**\n\n"
        f"🎯 **Matched:** `{stats['total_matched']}`\n"
        f"✅ **Caught:** `{stats['total_caught']}`\n"
        f"💨 **Fled:** `{stats['total_fled']}`\n"
        f"✨ **Shinies:** `{stats.get('total_shinies', 0)}`\n"
        f"💿 **TMs:** `{stats['total_tms']}`\n"
        f"🔮 **Mega Stones:** `{stats['total_megastones']}`\n\n"
        f"⏱️ **Uptime:** `{uptime.days}d {hours}h {minutes}m`"
    )
    await event.edit(msg, buttons=[[Button.inline("🔄 Refresh", b"refresh_status"), Button.inline("🗑️ Reset", b"reset_status")]])

@master_bot.on(events.CallbackQuery(pattern=b'reset_status'))
async def reset_status_cb(event):
    reset_stats(event.sender_id)
    await event.answer("✅ Stats Reset!", alert=True)
    await refresh_status(event)

# 4. LIST MGMT
@master_bot.on(events.NewMessage(pattern='/list'))
async def view_list(event):
    uid = event.sender_id
    if uid not in user_configs: return
    current_list = user_configs[uid]['list']
    list_str = ", ".join(current_list)
    if len(list_str) > 4000:
        with open("mylist.txt", "w") as f: f.write(list_str)
        await event.reply("📜 **Target List:**", file="mylist.txt")
        os.remove("mylist.txt")
    else:
        await event.reply(f"📜 **Target List:**\n\n{list_str}")

@master_bot.on(events.NewMessage(pattern='/add'))
async def add_pokemon(event):
    uid = event.sender_id
    if uid not in user_configs: return
    try:
        args = event.text.split('/add', 1)[1].strip()
        new_mons = [name.strip() for name in args.split(',') if name.strip()]
        for mon in new_mons:
            if mon not in user_configs[uid]['list']:
                user_configs[uid]['list'].append(mon)
        cursor = db.cursor()
        cursor.execute("UPDATE users SET poke_list = ? WHERE user_id = ?", (json.dumps(user_configs[uid]['list']), uid))
        db.commit()
        await event.reply(f"✅ Added **{len(new_mons)}** Pokemon(s).")
    except: await event.reply("Usage: /add Pkmn1, Pkmn2")

@master_bot.on(events.NewMessage(pattern='/remove'))
async def remove_pokemon(event):
    uid = event.sender_id
    if uid not in user_configs: return
    try:
        args = event.text.split('/remove', 1)[1].strip()
        to_remove = [name.strip() for name in args.split(',')]
        current_list = user_configs[uid]['list']
        new_list = [p for p in current_list if p not in to_remove]
        user_configs[uid]['list'] = new_list
        cursor = db.cursor()
        cursor.execute("UPDATE users SET poke_list = ? WHERE user_id = ?", (json.dumps(user_configs[uid]['list']), uid))
        db.commit()
        await event.reply(f"🗑️ Removed **{len(current_list) - len(new_list)}** Pokemon(s).")
    except: await event.reply("Usage: /remove Pkmn1, Pkmn2")

# 5. CORE COMMANDS
@master_bot.on(events.NewMessage(pattern='/login'))
async def login(event):
    sender = event.sender_id
    async with master_bot.conversation(sender) as conv:
        await conv.send_message("📞 Phone:")
        phone = (await conv.get_response()).text
        client = TelegramClient(StringSession(), API_ID, API_HASH)
        await client.connect()
        try:
            await client.send_code_request(phone)
            await conv.send_message("🔢 OTP:")
            otp = (await conv.get_response()).text.replace(" ", "")
            await client.sign_in(phone, otp)
        except SessionPasswordNeededError:
            await conv.send_message("🔐 2FA:")
            pwd = (await conv.get_response()).text
            await client.sign_in(password=pwd)
        except Exception as e: return await conv.send_message(f"❌ {e}")
        
        sess = client.session.save()
        cursor = db.cursor()
        now = datetime.now().isoformat()
        cursor.execute("""INSERT OR REPLACE INTO users 
                          (user_id, session, poke_list, ball, total_matched, total_caught, total_fled, total_tms, total_megastones, total_shinies, start_time) 
                          VALUES (?, ?, ?, ?, 0, 0, 0, 0, 0, 0, ?)""", 
                       (sender, sess, json.dumps(DEFAULT_LIST), None, now))
        db.commit()
        
        user_configs[sender] = {
            'list': DEFAULT_LIST, 'ball': None, 'hunting': False, 'mode': 'SEARCHING',
            'stats': {'total_matched': 0, 'total_caught': 0, 'total_fled': 0, 'total_tms': 0, 'total_megastones': 0, 'total_shinies': 0, 'start_time': now}
        }
        asyncio.create_task(run_userbot(sender, sess))
        await conv.send_message("✅ Logged in!")

@master_bot.on(events.NewMessage(pattern='/ball'))
async def ball_picker(event):
    btns = [[Button.inline("Ultra Ball", b"Ultra"), Button.inline("Great Ball", b"Great")],
            [Button.inline("Regular Ball", b"Regular"), Button.inline("Repeat Ball", b"Repeat")]]
    await event.reply("Ball:", buttons=btns)

@master_bot.on(events.CallbackQuery)
async def set_ball(event):
    if event.data in [b'refresh_status', b'reset_status']: return 
    ball = event.data.decode()
    user_configs[event.sender_id]['ball'] = ball
    cursor = db.cursor()
    cursor.execute("UPDATE users SET ball = ? WHERE user_id = ?", (ball, event.sender_id))
    db.commit()
    await event.edit(f"✅ Ball: **{ball}**")

@master_bot.on(events.NewMessage(pattern='/hunt'))
async def start_hunt(event):
    uid = event.sender_id
    if uid not in user_configs: return await event.reply("Login first.")
    if user_configs[uid].get('ball') is None: return await event.reply("Set ball first.")

    user_configs[uid]['hunting'] = True
    user_configs[uid]['mode'] = 'SEARCHING' 
    await event.reply("🚀 Hunting Started...")
    await send_hunt_with_retry(user_clients[uid], HEXA_ID, uid)

@master_bot.on(events.NewMessage(pattern='/stop'))
async def stop_hunt(event):
    if event.sender_id in user_configs:
        user_configs[event.sender_id]['hunting'] = False
        await event.reply("🛑 Stopped.")

async def main():
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users")
    for row in cursor.fetchall():
        try:
            uid, sess, plist, ball, t_match, t_caught, t_fled, t_tms, t_mega, t_shiny, s_time = row
            user_configs[uid] = {
                'list': json.loads(plist), 'ball': ball, 'hunting': False, 'mode': 'SEARCHING',
                'stats': {
                    'total_matched': t_match, 'total_caught': t_caught, 'total_fled': t_fled,
                    'total_tms': t_tms, 'total_megastones': t_mega, 'total_shinies': t_shiny, 'start_time': s_time
                }
            }
            asyncio.create_task(run_userbot(uid, sess))
        except ValueError:
            logger.error("DB mismatch. Delete hexabot.db and restart.")
            return

    await master_bot.run_until_disconnected()

if __name__ == '__main__':
    master_bot.loop.run_until_complete(main())