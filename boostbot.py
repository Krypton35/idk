import discord, json, requests, os, httpx, base64, time, subprocess
from discord.ext import commands, tasks
from keyauth import api
from colorama import Fore, init
import ctypes
import random
import string
import hashlib
from pystyle import Colors, Colorate

cmd = 'mode 50,30'
os.system(cmd)

ctypes.windll.kernel32.SetConsoleTitleW("UP")

activity = discord.Activity(type=discord.ActivityType.watching, name="hello")

bot = discord.Bot(command_prefix='$', activity=activity, status=discord.Status.dnd, intents=discord.Intents.all())


settings = json.load(open("settings.json", encoding="utf-8"))

if not os.path.isfile("used.json"):
    used = {}
    json.dump(used, open("used.json", "w", encoding="utf-8"), indent=4)

used = json.load(open("used.json"))

def is_licensed(target):
    try:
        open(f"{target}.txt", "r")
        return True
    except FileNotFoundError:
        return False

def isAdmin(ctx):
    return str(ctx.author.id) in settings["botAdminId"]


@bot.event
async def on_ready():
    activity = discord.Game(name="Buy 14 boosts", type=2)
    await  bot.change_presence(status=discord.Status.do_not_disturb, activity=discord.Activity(type=discord.ActivityType.watching, name="Up"))
    print(Fore.LIGHTMAGENTA_EX+"""
              ...                            
             ;::::;                           
           ;::::; :;                          
         ;:::::'   :;                         
        ;:::::;     ;.                        
       ,:::::'       ;           OOO\         
       ::::::;       ;          OOOOO\        
       ;:::::;       ;         OOOOOOOO       
      ,;::::::;     ;'         / OOOOOOO      
    ;:::::::::`. ,,,;.        /  / DOOOOOO    
  .';:::::::::::::::::;,     /  /     DOOOO   
 ,::::::;::::::;;;;::::;,   /  /        DOOO                -------------------
;`::::::`'::::::;;;::::: ,#/  /          DOOO             Made By xsp v2#7931
:`:::::::`;::::::;;::: ;::#  /            DOOO              -------------------
::`:::::::`;:::::::: ;::::# /              DOO
`:`:::::::`;:::::: ;::::::#/               DOO
 :::`:::::::`;; ;:::::::::##                OO
 ::::`:::::::`;::::::::;:::#                OO
 `:::::`::::::::::::;'`:;::#                O 
  `:::::`::::::::;' /  / `:#                  
   ::::::`:::::;'  /  /   `# 
    """)
    print(f"({Fore.YELLOW}INFO{Fore.RESET}) Authentification . . .")
    time.sleep(2)
    print(f"({Fore.GREEN}SUCCESS{Fore.RESET}) Authentified")
    time.sleep(1)
    #print(f"\n({Fore.RED}STATUS{Fore.RESET}) Sellix")
    #print(f"({Fore.RED}STATUS{Fore.RESET}) Sell.App")
    print(f"({Fore.GREEN}STATUS{Fore.RESET}) Discord Bot\n\n")



def isWhitelisted(ctx):
    return str(ctx.author.id) in settings["botWhitelistedId"]


def makeUsed(token: str):
    data = json.load(open('used.json', 'r'))
    with open('used.json', "w") as f:
        if data.get(token): return
        data[token] = {
            "boostedAt": str(time.time()),
            "boostFinishAt": str(time.time() + 30 * 86400)
        }
        json.dump(data, f, indent=4)


def removeToken(token: str):
    with open('tokens.txt', "r") as f:
        Tokens = f.read().split("\n")
        for t in Tokens:
            if len(t) < 5 or t == token:
                Tokens.remove(t)
        open("tokens.txt", "w").write("\n".join(Tokens))

@bot.slash_command(guild_id=[settings["guildID"]], name="restart", description="Restarts your boost bot!")
async def restart(ctx):
    if not str(ctx.author.id) in settings["botadminid"]:
        return await ctx.respond(embed=discord.Embed(description="*Only Reaper can you this command!*", color=0xFF0000))
    embed=discord.Embed(title="__**Restarting Bot**__", description=f"Bot is Restarting...", color=0x0000ff)
    embed.set_image(url="https://media.discordapp.net/attachments/1056661732782776441/1059302783498592276/Roblox_12_31_2022_12_05_08_PM.png?width=1190&height=625")
    embed.set_footer(text=".gg/verycheapserverboosts")
    await ctx.respond(embed=embed)
    print(f"[{Fore.LIGHTBLUE_EX}{time.strftime('%H:%M:%S', time.gmtime())}{Fore.RESET}] Exiting For Restart in 5 Seconds!")
    time.sleep(4)
    embed=discord.Embed(title="__**Bot Has Restarted!**__", description=f"Bot Restarted Continuing", color=0x0000ff)
    embed.set_image(url="https://media.discordapp.net/attachments/1056661732782776441/1059302783498592276/Roblox_12_31_2022_12_05_08_PM.png?width=1190&height=625")
    embed.set_footer(text="gg/verycheapserverboosts")
    await ctx.send(embed=embed)
    os.system("python main.py")
    os.system("cls")
    time.sleep(5)
    exit()

def runBoostshit(invite: str, amount: int, expires: bool):
    if amount % 2 != 0:
        amount += 1

    tokens = get_all_tokens("tokens.txt")
    all_data = []
    tokens_checked = 0
    actually_valid = 0
    boosts_done = 0
    for token in tokens:
        s, headers = get_headers(token)
        profile = validate_token(s, headers)
        tokens_checked += 1

        if profile != False:
            actually_valid += 1
            data_piece = [s, token, headers, profile]
            all_data.append(data_piece)
            print(f"{Fore.GREEN} > {Fore.WHITE}{profile}")
        else:
            pass
    for data in all_data:
        if boosts_done >= amount:
            return
        s, token, headers, profile = get_items(data)
        boost_data = s.get(f"https://discord.com/api/v9/users/@me/guilds/premium/subscription-slots", headers=headers)
        if boost_data.status_code == 200:
            if len(boost_data.json()) != 0:
                join_outcome, server_id = do_join_server(s, token, headers, profile, invite)
                if join_outcome:
                    for boost in boost_data.json():

                        if boosts_done >= amount:
                            removeToken(token)
                            if expires:
                                makeUsed(token)
                            return
                        boost_id = boost["id"]
                        bosted = do_boost(s, token, headers, profile, server_id, boost_id)
                        if bosted:
                            print(f"{Fore.GREEN} > {Fore.WHITE}{profile} {Fore.MAGENTA}BOOSTED {Fore.WHITE}{invite}")
                            boosts_done += 1
                        else:
                            print(f"{Fore.GREEN} > {Fore.WHITE}{profile} {Fore.RED}ERROR BOOSTING {Fore.WHITE}{invite}")
                    removeToken(token)
                    if expires:
                        makeUsed(token)
                else:
                    print(f"{Fore.RED} > {Fore.WHITE}{profile} {Fore.RED}Error joining {invite}")

            else:
                removeToken(token)
                print(f"{Fore.GREEN} > {Fore.WHITE}{profile} {Fore.RED}BROKE ASS DONT GOT NITRO")

@tasks.loop(seconds=5.0)
async def check_used():
    used = json.load(open("used.json"))
    toremove = []
    for token in used:
        print(token)
        if str(time.time()) >= used[token]["boostFinishAt"]:
            toremove.append(token)

    for token in toremove:
        used.pop(token)
        with open("tokens.txt", "a", encoding="utf-8") as file:
            file.write(f"{token}\n")
            file.close()

    json.dump(used, open("used.json", "w"), indent=4)

@bot.slash_command(guild_id=[settings["guildID"]], name="whitelist", description="Whitelist a person to use the bot.")
async def whitelist(ctx: discord.ApplicationContext,
                    user: discord.Option(discord.Member, "Member to whitelist.", required=True)):
    if not isAdmin(ctx):
        return await ctx.respond("*Only Bot Admins can use this command.*")

    settings["botWhitelistedId"].append(str(user.id))
    json.dump(settings, open("settings.json", "w", encoding="utf-8"), indent=4)

    return await ctx.respond(f"*{user.mention} has been whitelisted.*")

@bot.slash_command(guild_id=[settings["guildID"]], name="addadmin", description="adds admin to the bot")
async def whitelist(ctx: discord.ApplicationContext,
                    user: discord.Option(discord.Member, "Member to admin", required=True)):
    if not isAdmin(ctx):
        return await ctx.respond("*Only Bot Admins can use this command.*")

    settings["botAdminId"].append(str(user.id))
    json.dump(settings, open("settings.json", "w", encoding="utf-8"), indent=4)

    return await ctx.respond(f"*{user.mention} has been added to admin.*")

@bot.slash_command(guild_id=[settings["guildID"]], name="givetokens",
                   description="Gives X amount of tokens to a specified user")
async def give_tokens(ctx: discord.ApplicationContext, amount: discord.Option(int, "Amount of tokens.", required=True),
                      targetid: discord.Option(str, "Target ID.", required=True)):
    if is_licensed(ctx.author.id):

        temp_tokens = open(f"{ctx.author.id}.txt", encoding="UTF-8").read().splitlines()
        if len(temp_tokens) < amount:
            return await ctx.send("You do not have enough tokens in stock.")

        tokens_to_give = temp_tokens[0:amount]
        temp_tokens = temp_tokens[amount:]

        f = open(f"temp.txt", "w", encoding="UTF-8")
        for tk in tokens_to_give:
            f.write(tk + "\n")
        f.close()

        f = open(f"{ctx.author.id}.txt", "w", encoding="UTF-8")
        for tk in temp_tokens:
            f.write(tk + "\n")
        f.close()

        embed = discord.Embed(title=f"Nitro Tokens",
                              description=f"Sent {amount} tokens to user <@!{targetid}>.",
                              color=0x3498db)
        await ctx.send(embed=embed, file=discord.File("temp.txt"))
        os.remove("temp.txt")
    else:
        await ctx.send(f"You do not have an active subscription for the bot.")

@bot.slash_command(guild_id=[settings["guildID"]], name="addlicense",
                   description="Adds a license to a specified user ID.")
async def add_license(ctx: discord.ApplicationContext, targetid: discord.Option(str, "Target ID.", required=True)):
    if isAdmin(ctx):
        if not is_licensed(targetid):
            open(f"{targetid}.txt", "w")
            embed = discord.Embed(title=f"Licensed", description=f"User <@!{targetid}> licensed.",
                                  color=0x3498db)
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title=f"Already licensed", description=f"User <@!{targetid}> is already licensed.",
                                  color=0x3498db)
            await ctx.send(embed=embed)


@bot.slash_command(guild_id=[settings["guildID"]], name="removelicense",
                   description="Removes a license from a specified user ID.")
async def remove_license(ctx: discord.ApplicationContext, targetid: discord.Option(str, "Target ID.", required=True)):
    if isAdmin(ctx):
        if is_licensed(ctx.author.id):
            os.remove(f"{targetid}.txt")
            embed = discord.Embed(title=f"License removed", description=f"User <@!{targetid}> license has been removed.",
                                  color=0x3498db)
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title=f"No license",
                                  description=f"User <@!{targetid}> does not have a license.",
                                  color=0x3498db)
            await ctx.send(embed=embed)



@bot.slash_command(guild_id=[settings["guildID"]], name="cashapp", description="Sends u link to our cashapp")
async def on_message(message):
   embedVar = discord.Embed(title="CASHAPP", description=(settings["cashapp"]))
   embedVar.set_image(url="https://media.discordapp.net/attachments/1056661732782776441/1059302783498592276/Roblox_12_31_2022_12_05_08_PM.png?width=1190&height=625")
   await message.respond(embed=embedVar)
 
def getRandomString(length): #Letters and numbers
    pool=string.ascii_lowercase+string.digits
    return "".join(random.choice(pool) for i in range(length))

def getRandomNumber(length): #Chars only
    return "".join(random.choice(string.digits) for i in range(length)) 

cardstart = "515462"

@bot.slash_command(guild_id=[settings["guildID"]], name="paypal", description="Sends u link to our paypal")
async def on_message(message):
   embedVar = discord.Embed(title="Paypal", description=(settings["paypal"]))
   embedVar.set_image(url="https://media.discordapp.net/attachments/1056661732782776441/1059302783498592276/Roblox_12_31_2022_12_05_08_PM.png?width=1190&height=625")
   await message.respond(embed=embedVar)
 
def getRandomString(length): #Letters and numbers
    pool=string.ascii_lowercase+string.digits
    return "".join(random.choice(pool) for i in range(length))

def getRandomNumber(length): #Chars only
    return "".join(random.choice(string.digits) for i in range(length)) 

cardstart = "515462"



@bot.slash_command(guild_id=[settings["guildID"]], name="stock", description="Allows you to see the current token stock and boost stock!")
async def stock(ctx):
    emoji = discord.utils.get(bot.emojis, name='pbj1')
    embed = discord.Embed(title=f"**{emoji} l Stock**",
                          color=0xFF00D0)
    embed=discord.Embed(title="__**Boost Stock**__", description=f"*Nitro Tokens:* `{len(open('tokens.txt', encoding='utf-8').read().splitlines())}` \n*Server Boost:* `{len(open('tokens.txt', encoding='utf-8').read().splitlines()) * 2}`", color=0x0000ff)
    embed.set_image(url="https://media.discordapp.net/attachments/1056661732782776441/1059302783498592276/Roblox_12_31_2022_12_05_08_PM.png?width=1190&height=625")
    embed.set_footer(text="gg/verycheapserverboosts")
    await ctx.respond(embed=embed)



@bot.slash_command(guild_id=[settings["guildID"]], name="restock", description="Allows you to restock Nitro Tokens.")
async def restock(ctx: discord.ApplicationContext,
                  code: discord.Option(str, "paste.ee paste link or code", required=True)):
    if not is_licensed(ctx.author.id):
        return await ctx.respond("*Only Bot Admins can use this command.*")

    code = code.replace("https://paste.ee/p/", "")

    temp_stock = requests.get(f"https://paste.ee/d/{code}", headers={
        "User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.61 Safari/537.36"}).text

    f = open(f"{ctx.author.id}.txt", "a", encoding="utf-8")
    f.write(f"{temp_stock}\n")
    f.close()

    embed = discord.Embed(title=f"Stock updated",
                          description=f"You Now Have {len(open(f'{ctx.author.id}.txt', encoding='utf-8').read().splitlines())} Tokens*.",
                          color=0xFF00D0)
    print(f"[ + ] {ctx.author.id} has Just Restocked {len(open(f'{ctx.author.id}.txt', encoding='utf-8').read().splitlines())} Tokens")
    await ctx.send(embed=embed)

@bot.slash_command(guild_id=[settings["guildID"]], name="boost",
                   description="Allows you to boost a server with Nitro Tokens.")
async def boost(ctx: discord.ApplicationContext,
                invitecode: discord.Option(str, "Discord Invite Code to join the server (ONLY CODE).", required=True),
                amount: discord.Option(int, "Number of times to boost.", required=True),
                days: discord.Option(int, "Number of days the boosts will stay.", required=True)):
    if not isAdmin(ctx):
        return await ctx.respond(
            embed=discord.Embed(title="Error | Admin", description="Only Bot Admins Can Use This Command", color=0xFF5733)
        )

    if days != 30 and days != 90:
        return await ctx.respond(
            embed=discord.Embed(title="Error | Days Entered", description="Number Of Days Can Only Be 30 Or 90", color=0xFF5733)
        )

    await ctx.respond(
        embed=discord.Embed(title="Success | Started", description="The Operation Has Started", color=0xFF5733)
    )

    INVITE = invitecode.replace("//", "")
    if "/invite/" in INVITE:
        INVITE = INVITE.split("/invite/")[1]

    elif "/" in INVITE:
        INVITE = INVITE.split("/")[1]

    dataabotinvite = httpx.get(f"https://discord.com/api/v9/invites/{INVITE}").text

    if '{"message": "Unknown Invite", "code": 10006}' in dataabotinvite:
        print(f"{Fore.RED}discord.gg/{INVITE} is invalid")
        return await ctx.edit(
            embed=discord.Embed(title="Error | Invite", description="The Invite Stated Is Invalid", color=0xFF5733)
        )
    else:
        print(f"{Fore.GREEN}discord.gg/{INVITE} appears to be a valid server")

    EXP = True
    if days == 90:
        EXP = False

    runBoostshit(INVITE, amount, EXP)


    return await ctx.edit(
        embed=discord.Embed(title="Success | FINISHED BOOSTING, thanks for using cheap boosts service", description="The Operation Has Finished", color=0xFF5733)
    )


def get_super_properties():
    properties = '''{"os":"Windows","browser":"Chrome","device":"","system_locale":"en-GB","browser_user_agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36","browser_version":"95.0.4638.54","os_version":"10","referrer":"","referring_domain":"","referrer_current":"","referring_domain_current":"","release_channel":"stable","client_build_number":102113,"client_event_source":null}'''
    properties = base64.b64encode(properties.encode()).decode()
    return properties


def get_fingerprint(s):
    try:
        fingerprint = s.get(f"https://discord.com/api/v9/experiments", timeout=5).json()["fingerprint"]
        return fingerprint
    except Exception as e:
        # print(e)
        return "Error"


def get_cookies(s, url):
    try:
        cookieinfo = s.get(url, timeout=5).cookies
        dcf = str(cookieinfo).split('__dcfduid=')[1].split(' ')[0]
        sdc = str(cookieinfo).split('__sdcfduid=')[1].split(' ')[0]
        return dcf, sdc
    except:
        return "", ""


def get_proxy():
    return None  # can change if problems occur


def get_headers(token):
    while True:
        s = httpx.Client(proxies=get_proxy())
        dcf, sdc = get_cookies(s, "https://discord.com/")
        fingerprint = get_fingerprint(s)
        if fingerprint != "Error":  # Making sure i get both headers
            break

    super_properties = get_super_properties()
    headers = {
        'authority': 'discord.com',
        'method': 'POST',
        'path': '/api/v9/users/@me/channels',
        'scheme': 'https',
        'accept': '*/*',
        'accept-encoding': 'gzip, deflate',
        'accept-language': 'en-US',
        'authorization': token,
        'cookie': f'__dcfduid={dcf}; __sdcfduid={sdc}',
        'origin': 'https://discord.com',
        'sec-ch-ua': '"Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36',

        'x-debug-options': 'bugReporterEnabled',
        'x-fingerprint': fingerprint,
        'x-super-properties': super_properties,
    }

    return s, headers


def find_token(token):
    if ':' in token:
        token_chosen = None
        tokensplit = token.split(":")
        for thing in tokensplit:
            if '@' not in thing and '.' in thing and len(
                    thing) > 30:  # trying to detect where the token is if a user pastes email:pass:token (and we dont know the order)
                token_chosen = thing
                break
        if token_chosen == None:
            print(f"Error finding token", Fore.RED)
            return None
        else:
            return token_chosen


    else:
        return token


def get_all_tokens(filename):
    all_tokens = []
    with open(filename, 'r') as f:
        for line in f.readlines():
            token = line.strip()
            token = find_token(token)
            if token != None:
                all_tokens.append(token)

    return all_tokens


def validate_token(s, headers):
    check = s.get(f"https://discord.com/api/v9/users/@me", headers=headers)

    if check.status_code == 200:
        profile_name = check.json()["username"]
        profile_discrim = check.json()["discriminator"]
        profile_of_user = f"{profile_name}#{profile_discrim}"
        return profile_of_user
    else:
        return False


def do_member_gate(s, token, headers, profile, invite, server_id):
    outcome = False
    try:
        member_gate = s.get(
            f"https://discord.com/api/v9/guilds/{server_id}/member-verification?with_guild=false&invite_code={invite}",
            headers=headers)
        if member_gate.status_code != 200:
            return outcome
        accept_rules_data = member_gate.json()
        accept_rules_data["response"] = "true"

        # del headers["content-length"] #= str(len(str(accept_rules_data))) #Had too many problems
        # del headers["content-type"] # = 'application/json'  ^^^^

        accept_member_gate = s.put(f"https://discord.com/api/v9/guilds/{server_id}/requests/@me", headers=headers,
                                   json=accept_rules_data)
        if accept_member_gate.status_code == 201:
            outcome = True

    except:
        pass

    return outcome


def do_join_server(s, token, headers, profile, invite):
    join_outcome = False;
    server_id = None
    try:
        # headers["content-length"] = str(len(str(server_join_data)))
        headers["content-type"] = 'application/json'

        for i in range(15):
            try:
                createTask = httpx.post("https://api.capmonster.cloud/createTask", json={
                    "clientKey": settings["capmonsterKey"],
                    "task": {
                        "type": "HCaptchaTaskProxyless",
                        "websiteURL": "https://discord.com/channels/@me",
                        "websiteKey": "76edd89a-a91d-4140-9591-ff311e104059"
                    }
                }).json()["taskId"]

                print(f"Captcha Task: {createTask}")

                getResults = {}
                getResults["status"] = "processing"
                while getResults["status"] == "processing":
                    getResults = httpx.post("https://api.capmonster.cloud/getTaskResult", json={
                        "clientKey": settings["capmonsterKey"],
                        "taskId": createTask
                    }).json()

                    time.sleep(1)

                solution = getResults["solution"]["gRecaptchaResponse"]

                print(f"Captcha Solved")

                join_server = s.post(f"https://discord.com/api/v9/invites/{invite}", headers=headers, json={
                    "captcha_key": solution
                })

                break
            except:
                pass

        server_invite = invite
        if join_server.status_code == 200:
            join_outcome = True
            server_name = join_server.json()["guild"]["name"]
            server_id = join_server.json()["guild"]["id"]
            print(f"{Fore.GREEN} > {Fore.WHITE}{profile} {Fore.GREEN}> {Fore.WHITE}{server_invite}")
    except:
        pass

    return join_outcome, server_id


def do_boost(s, token, headers, profile, server_id, boost_id):
    boost_data = {"user_premium_guild_subscription_slot_ids": [f"{boost_id}"]}
    headers["content-length"] = str(len(str(boost_data)))
    headers["content-type"] = 'application/json'

    boosted = s.put(f"https://discord.com/api/v9/guilds/{server_id}/premium/subscriptions", json=boost_data,
                    headers=headers)
    if boosted.status_code == 201:
        return True
    else:
        return False


def get_invite():
    while True:
        print(f"{Fore.CYAN}Server invite?", end="")
        invite = input(" > ").replace("//", "")

        if "/invite/" in invite:
            invite = invite.split("/invite/")[1]

        elif "/" in invite:
            invite = invite.split("/")[1]

        dataabotinvite = httpx.get(f"https://discord.com/api/v9/invites/{invite}").text

        if '{"message": "Unknown Invite", "code": 10006}' in dataabotinvite:
            print(f"{Fore.RED}discord.gg/{invite} is invalid")
        else:
            print(f"{Fore.GREEN}discord.gg/{invite} appears to be a valid server")
            break

    return invite


def get_items(item):
    s = item[0]
    token = item[1]
    headers = item[2]
    profile = item[3]
    return s, token, headers, profile

#hwid = subprocess.check_output("wmic csproduct get uuid").decode().split("\n")[1].strip()
#if hwid in httpx.get("https://pastebin.com/nCCA3XyG").text:
bot.run(settings["botToken"])
#else:
#    print(f"{Fore.LIGHTRED_EX}Not Whitelisted!\n\nHWID: {hwid}")

    #input()
    