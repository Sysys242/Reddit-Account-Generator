import httpx, tls_client, random
import string, threading, json
from account_generator_helper import GmailNator
from colorama import Fore

config = json.loads(open('config.json', 'r').read())
usernamePrefix = config['username-prefix']
api_key = config['capsolver-api-key']

with open('proxies.txt', 'r', encoding="utf-8") as f:
    proxies = f.read().splitlines()

def getRandomString(length:int) -> str:
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

class Reddit:
    def __init__(self) -> None:
        self.session = tls_client.Session(
            client_identifier="chrome_110"
        )
        self.session.headers = {
            'authority': 'www.reddit.com',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'accept-language': 'fr-FR,fr;q=0.9',
            'referer': 'https://www.reddit.com/r/place/?screenmode=fullscreen&cx=0&cy=-247&px=252',
            'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Brave";v="114"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'iframe',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'sec-gpc': '1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
        }
        self.session.proxies = {
            "http": f"http://{random.choice(proxies)}",
            "https": f"http://{random.choice(proxies)}"
        }

        response = self.session.get(
            'https://www.reddit.com/register/?experiment_d2x_2020ify_buttons=enabled&use_accountmanager=true&experiment_d2x_google_sso_gis_parity=enabled&experiment_d2x_onboarding=enabled&experiment_d2x_am_modal_design_update=enabled&lang=fr',
        )

        self.csrf = response.text.split('  <input type="hidden" name="csrf_token" value="')[1].split('"')[0]
        self.log(f"CSRF: {self.csrf}")
    
        self.gmailNator = GmailNator()
        self.email = self.gmailNator.get_email_online(False,False,True)
        self.gmailNator.set_email(self.email)
        self.log(f'{Fore.CYAN}EMAIL: {self.email}')

        self.username = f'{usernamePrefix}{getRandomString(10)}'
        self.password = f'$y$y_{getRandomString(10)}'
        self.log(f'USERNAME: {self.username}')
        self.log(f'PASSWORD: {self.password}')

    def log(self, text):
        if 1 == 2: print(text)
    
    def solveCaptcha(self):
        ez = False
        while not ez:
            try:
                taskId = httpx.post(
                    'https://api.capsolver.com/createTask',
                    json={
                        "clientKey": api_key,
                        "appId": "6725ABD5-6E08-4BE2-8E62-6751EC27FDC8",
                        "task": {
                            "type": "ReCaptchaV2TaskProxyLess",
                            "websiteURL": "https://reddit.com/register",
                            "websiteKey": "6LeTnxkTAAAAAN9QEuDZRpn90WwKk_R1TRW_g-JC"
                        }
                    }
                ).json()['taskId']
                while True:
                    response = httpx.post(f"https://api.capsolver.com/getTaskResult",json={"clientKey":api_key,"taskId":taskId})
                    if response.json()["status"] == "ready":
                        key = response.json()["solution"]["gRecaptchaResponse"]
                        return key
                    elif response.json()['status'] == "failed":
                        return None
            except Exception as e:
                self.log(f"[ERROR] {e}")
    
    def register(self):
        captchaKey = self.solveCaptcha()
        self.log(f'{Fore.YELLOW}SOLVED: {captchaKey[:20]}')

        response = self.session.post(
            'https://www.reddit.com/register',
            data={
                'csrf_token': self.csrf,
                'g-recaptcha-response': captchaKey,
                'password': self.password,
                'dest': 'https://www.reddit.com',
                'email_permission': 'false',
                'lang': 'fr-FR',
                'username': self.username,
                'email': self.email,
            }
        )
        if response.status_code == 200:
            self.session.cookies.update(response.cookies)
            print(f'{Fore.GREEN}CREATED: {self.email}:{self.password[:-5]}*****')
        else:
            print(f'{Fore.RED}FAILED: {self.email}:{self.password[:-5]}***** | {response.status_code}')

    def verifyByMail(self):
        ez = True
        while ez:
            for letter in self.gmailNator.get_inbox():
                if "reddit" in letter.from_email:
                    verifyLink = letter.letter.split('<td class="btn-14" bgcolor="#0079d3" style="border-radius: 4px; font-size:14px; line-height:18px; mso-padding-alt:8px; color:#ffffff; font-family:Helvetica, Arial, sans-serif; text-align:center; min-width:auto !important;"><a href="')[1].split('"')[0]
                    ez = False
                    break
        self.session.get(verifyLink, allow_redirects=True)
        print(f'{Fore.YELLOW}MAIL VERIFIED: {self.email}:{self.password[:-5]}*****')
        with open('accounts.txt', 'a') as f:
            f.write(f'{self.username}:{self.password}\n')
        
    def generate(self):
        self.register()
        self.verifyByMail()

def gen():
    while True:
        try:
            reddit = Reddit()  
            reddit.generate()
        except:
            pass

if __name__ == "__main__":
    print(Fore.MAGENTA + """
██████╗░███████╗██████╗░██████╗░██╗████████╗░██████╗░███████╗███╗░░██╗
██╔══██╗██╔════╝██╔══██╗██╔══██╗██║╚══██╔══╝██╔════╝░██╔════╝████╗░██║
██████╔╝█████╗░░██║░░██║██║░░██║██║░░░██║░░░██║░░██╗░█████╗░░██╔██╗██║
██╔══██╗██╔══╝░░██║░░██║██║░░██║██║░░░██║░░░██║░░╚██╗██╔══╝░░██║╚████║
██║░░██║███████╗██████╔╝██████╔╝██║░░░██║░░░╚██████╔╝███████╗██║░╚███║
╚═╝░░╚═╝╚══════╝╚═════╝░╚═════╝░╚═╝░░░╚═╝░░░░╚═════╝░╚══════╝╚═╝░░╚══╝""")
    thread = int(input('Thread Number> '))
    for i in range(thread):
        threading.Thread(target=gen).start()