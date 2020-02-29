# fiadh.py
# A dice-rolling bot for Discord servers to be used with The Forests of Faera PBP.
# @category  Tools
# @version   1.0
# @author    Aaron Goss

# Dice imports
from random import randint

# Core imports
import os
import discord # Imported from https://github.com/Rapptz/discord.py
import asyncio
from discord.ext import tasks, commands

# Read token from .env file
env_vars = []
with open('/home/pi/fiadh/.env') as f:
    for line in f:
        if line.startswith('#'):
            continue
        # if 'export' not in line:
        #   continue
        # Remove leading 'export', if you have those
        # then, split name / value pair
        # key, value = line.replace('export ', '', 1).strip().split('=', 1)
        key, value = line.strip().split('=', 1)
        token = value
        # os.environ[key] = value  # Load to local environ
        env_vars.append({'name': key, 'value': value}) # Save to a list

bot = discord.Client()
bot = commands.Bot(command_prefix='.', description="A dice-rolling bot for use with The Forests of Faera roleplaying game.")

@bot.event
@asyncio.coroutine
async def on_ready():
    await bot.change_presence(status=discord.Status.online, activity=discord.Game('The Forests of Faera'))
    print('{bot.user} has connected to Discord!')
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('--------')

# Determines if a message is owned by the bot
def is_me(m):
    return m.author == bot.user

# Determines if the value can be converted into an integer
# Parameters: s - input string
# Returns: boolean. True if it can be converted, False if it throws an error.
def is_num(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

# Rolls a single die and returns the result.
# Parameters: die_type [d4, d6, d8, d10, d12]
# Returns: string with results
def roll_single(die_type):
    results = ""
    #print("rolling a single die. results: {}".format(results))
    x = randint(1, int(die_type))
    #print("x: {}".format(x))
    results += "{}".format(x)
    return results

# Rolls a single die and returns the result.
# Parameters: die_type [d4, d6, d8, d10, d12]
# Returns: string with results
def roll_composure(die_type):
    results = ""
    x = randint(1, int(die_type))
    results += " ({})".format(x)
    if x <= 2:
        if die_type == 4:
            results += "\n*You lose the last of your composure and become **distressed!***"
        else:
            results += "\n*You lose some composure. Downgrade your composure die.*"
    return results

# Rolls a single die and returns the result.
# Parameters: die_type [d4, d6, d8, d10, d12]
# Returns: string with results
def roll_enchantment(die_type):
    results = ""
    x = randint(1, int(die_type))
    results += " ({})".format(x)
    if x >= die_type - 1:
        if die_type == 10:
            results += "\n*You become overwhelmed by the enchantment of the forests and become **distressed!***"
        else:
            results += "\n*You gain some enchantment. Upgrade your enchantment die and acquire a new rune.*"
    return results

# Rolls two dice and returns the HIGHEST.
# Parameters: die_type [d4, d6, d8, d10, d12]
# Returns: string with results
def roll_strength(die_type):
    results = ""
    x = randint(1, int(die_type))
    y = randint(1, int(die_type))
    highest = 0
    if x > y:
        highest = x
        results += " (**{}**, {}). Take the higher number, **{}**.".format(x, y, highest)
    elif y > x:
        highest = y
        results += " ({}, **{}**). Take the higher number, **{}**.".format(x, y, highest)
    else:
        highest = x
        results += " ({}, {}). Take **{}**.".format(x, y, x)
    if highest <= 2:
        results += "{}".format(lose_composure(die_type))
    return results

# Rolls two dice and returns the LOWEST.
# Parameters: die_type [d4, d6, d8, d10, d12]
# Returns: string with results
def roll_weakness(die_type):
    results = ""
    x = randint(1, int(die_type))
    y = randint(1, int(die_type))
    lowest = 99
    if x < y:
        lowest = x
        results += "( **{}**, {}). Take the lower number, **{}**.".format(x, y, lowest)
    elif y < x:
        lowest = y
        results += " ({}, **{}**). Take the lower number, **{}**.".format(x, y, lowest)
    else:
        lowest = x
        results += " ({}, {}). Take **{}**.".format(x, y, x)
    if lowest <= 2:
        results += "{}".format(lose_composure(die_type))
    return results

# Rolls two dice and returns the LOWEST.
# Parameters: die_type [d4, d6, d8, d10, d12]
# Returns: string with results
def lose_composure(die_type):
    response = ""
    if die_type == 4:
        response += "\n*You lose the last of your composure and become **distressed!***"
    else:
        response += "\n*You lose some composure. Downgrade your composure die.*"
    return response

# Parse .r verbage
@bot.command(pass_context=True,description='Rolls dice.\nExamples:\n100  Rolls 1-100.\n50-100  Rolls 50-100.\n3d6  Rolls 3 d6 dice and returns total.\nModifiers:\n! Hit success. 3d6!5 Counts number of rolls that are greater than 5.\nmod: Modifier. 3d6mod3 or 3d6mod-3. Adds 3 to the result.\n> Threshold. 100>30 returns success if roll is greater than or equal to 30.\n\nFormatting:\nMust be done in order.\nSingle die roll: 1-100mod2>30\nMultiple: 5d6!4mod-2>2')
@asyncio.coroutine
def r(ctx, r : str):
    a, b, hit, num_of_dice, threshold, composure, enchantment, strength, weakness, die_type = 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
    # author: Writer of Discord message
    author = ctx.message.author
    if (r.find('>') != -1):
        r, threshold = r.split('>')
    if (r.find('!') != -1):
        r, hit = r.split('!')
    if (r.find('c') != -1):
        r, composure = r.split('c')
    if (r.find('e') != -1):
        r, enchantment = r.split('e')
    if (r.find('s') != -1):
        r, strength = r.split('s')
    if (r.find('w') != -1):
        r, weakness = r.split('w')
    if (r.find('d') != -1):
        num_of_dice, die_type = r.split('d')
    elif (r.find('-') != -1):
        a, b = r.split('-')
    else:
        a = 1
        b = r
    #Validate data
    try:
        if (hit != 0):
            if (is_num(hit) is False):
                raise ValueError("Hit value format error. Proper usage XdY!Z (eg: 3d6!5).")
                return
            else:
                print("[hit: {}]".format(hit))
                hit = int(hit)
        if (num_of_dice != 0):
            if (is_num(num_of_dice) is False):
                raise ValueError("Number of dice format error [num_of_dice: {}]. Proper usage XdY (eg: 3d6).".format(num_of_dice))
                return
            elif (int(num_of_dice) <= 0):
                raise ValueError("Number of dice format error [num_of_dice: {}]. Please use a number greater than zero.".format(num_of_dice))
                return
            else:
                print("[num_of_dice: {}]".format(num_of_dice))
                num_of_dice = int(num_of_dice)
        if (num_of_dice > 2):
            raise ValueError("Too many dice [num_of_dice: {}]. Please limit to two or less.".format(num_of_dice))
            return
        if (die_type != 0):
            if (is_num(die_type) is False):
                raise ValueError("Dice type format error [die_type: {}]. Proper usage XdY (eg: 3d6).".format(die_type))
                return
            else:
                print("[die_type: {}]".format(die_type))
                die_type = int(die_type)
        if (a != 0):
            if (is_num(a) is False):
                raise ValueError("Error: Minimum must be a number. Proper usage 1-50.")
                print("[a: {}]".format(a))
                return
            else:
                print("[a: {}]".format(a))
                a = int(a)
        if (b != 0):
            if (is_num(b) is False):
                raise ValueError("Error: Maximum must be a number. Proper usage 1-50 or 50.")
                print("[b: {}]".format(b))
                return
            else:
                print("[b: {}]".format(b))
                b = int(b)
        if (threshold != 0):
            if (is_num(threshold) is False):
                raise ValueError("Error: Threshold must be a number. Proper usage 1-100>30.")
                return
            else:
                print("[threshold: {}]".format(threshold))
                threshold = int(threshold)
        if (die_type != 0 and hit != 0):
            if (hit > die_type):
                raise ValueError("Error: Hit value cannot be greater than dice type.")
                return
            elif (die_type <= 0):
                raise ValueError("Dice type must be a positive number.")
                return
            elif (num_of_dice <= 0):
                raise ValueError("Number of dice must be a positive number.")
                return
        #if a == 0:
            #yield from ctx.send("{} rolls d{}. Result: {}".format(author, die_type, roll_single(die_type)))
        #elif b == 0:
            #yield from ctx.send("{} rolls d{}. Result: {}".format(author, die_type, roll_single(die_type)))
        #if (a == 0 and b == 0):
            #yield from ctx.send("{} rolls 1d{}. Result: {}".format(author, a, roll_single))
        #else:
            #ctx.send("Error. [author: {}], [a: {}], [b: {}], [roll_single: {}]".format(author,a,b,roll_single))
        print("[a={}], [b={}], [hit={}], [num_of_dice={}], [threshold={}], [die_type={}]".format(a,b,hit,num_of_dice,threshold,die_type))
        if a != 0 and b != 0:
            yield from ctx.send("{} rolls {}-{}. Result: {}".format(author, a, b, roll_single(a, b)))
        elif strength != 0:
            yield from ctx.send("<@{}> :game_die:\n**Strength roll:** d{}{}".format(author.id, die_type, roll_strength(die_type)))
        elif weakness != 0:
            yield from ctx.send("<@{}> :game_die:\n**Weakness roll:** d{}{}".format(author.id, die_type, roll_weakness(die_type)))
        elif composure != 0:
            yield from ctx.send("<@{}> :game_die:\n**Composure roll:** d{}{}".format(author.id, die_type, roll_composure(die_type)))
        elif enchantment != 0:
            yield from ctx.send("<@{}> :game_die:\n**Enchantment roll:** d{}{}".format(author.id, die_type, roll_enchantment(die_type)))
        else:
            yield from ctx.send("<@{}> :game_die:\n**Result:** {}d{} ({})".format(author.id, num_of_dice, die_type, roll_single(die_type)))
    except ValueError as err:
        # Display error message to channel
        yield from ctx.send(err)

# Bot command to delete all messages the bot has made.
@bot.command(pass_context=True, description='Deletes all messages the bot has made.')
@asyncio.coroutine
def purge(ctx):
    channel = ctx.message.channel
    deleted = yield from bot.purge_from(channel, limit=100, check=is_me)
    yield from bot.send_message(channel, 'Deleted {} message(s)'.format(len(deleted)))

# Follow this helpful guide on creating a bot and adding it to your server.
# https://github.com/reactiflux/discord-irc/wiki/Creating-a-discord-bot-&-getting-a-token
bot.run(token)
