# fiadh.py
# https://github.com/raspilicious/fiadh
#
# A dice-rolling bot for use with The Forests of Faera roleplaying game.
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
        key, value = line.strip().split('=', 1)
        token = value
        env_vars.append({'name': key, 'value': value}) # Save to a list... probably not needed

bot = discord.Client()
bot = commands.Bot(command_prefix='.', description="A dice-rolling bot for use with The Forests of Faera roleplaying game.")
bot.remove_command('help')

@bot.event
@asyncio.coroutine
async def on_ready():
    await bot.change_presence(status=discord.Status.online, activity=discord.Game('The Forests of Faera'))
    print('{} has connected to Discord!'.format(bot.user))
    print('Logged in as {} with ID of [{}]'.format(bot.user.name, bot.user.id))
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
# Parameters: die_type
# Returns: string with results
def roll_single(die_type):
    results = ""
    x = randint(1, int(die_type))
    results += "{}".format(x)
    print("Rolled a d{} die and got {}.".format(die_type, results))
    return results

# Rolls a single die and returns the result.
# Parameters: die_type [ideally d4, d6, d8, d10, or d12]
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
    print("Rolled a d{} composure die and got {}.".format(die_type, results))
    return results

# Rolls a single die and returns the result.
# Parameters: die_type [ideally d4, d6, d8, d10, or d12]
# Returns: string with results
def roll_enchantment(die_type):
    results = ""
    x = randint(1, die_type)
    results += " ({})".format(x)
    if x >= die_type - 1:
        if die_type == 10:
            results += "\n*You become overwhelmed by the enchantment of the forests and become **distressed!***"
        else:
            results += "\n*You gain some enchantment. Upgrade your enchantment die and acquire a new rune.*"
    print("Rolled a d{} enchantment die and got {}.".format(die_type, results))
    return results

# Rolls two dice and returns the HIGHEST.
# Parameters: die_type [ideally d4, d6, d8, d10, or d12]
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
    print("Rolled a d{} die with strength and got {} and {}.".format(die_type, x, y))
    return results

# Rolls two dice and returns the LOWEST.
# Parameters: die_type [ideally d4, d6, d8, d10, or d12]
# Returns: string with results
def roll_weakness(die_type):
    results = ""
    x = randint(1, int(die_type))
    y = randint(1, int(die_type))
    lowest = 99
    if x < y:
        lowest = x
        results += " (**{}**, {}). Take the lower number, **{}**.".format(x, y, lowest)
    elif y < x:
        lowest = y
        results += " ({}, **{}**). Take the lower number, **{}**.".format(x, y, lowest)
    else:
        lowest = x
        results += " ({}, {}). Take **{}**.".format(x, y, x)
    if lowest <= 2:
        results += "{}".format(lose_composure(die_type))
    print("Rolled a d{} die with weakness and got {} and {}.".format(die_type, x, y))
    return results

# Append a message that the author has lost composure
# Parameters: die_type [ideally d4, d6, d8, d10, or d12]
# Returns: string with a message that the author has lost composure
def lose_composure(die_type):
    response = ""
    if die_type == 4:
        response += "\n*You lose the last of your composure and become **distressed!***"
    else:
        response += "\n*You lose some composure. Downgrade your composure die.*"
    print("Losing some composure.")
    return response

# Parse .r verbage
@bot.command(pass_context=True,description='Rolls dice.\nExamples:\n100  Rolls 1-100.\n50-100  Rolls 50-100.\n3d6  Rolls 3 d6 dice and returns total.\nModifiers:\n! Hit success. 3d6!5 Counts number of rolls that are greater than 5.\nmod: Modifier. 3d6mod3 or 3d6mod-3. Adds 3 to the result.\n> Threshold. 100>30 returns success if roll is greater than or equal to 30.\n\nFormatting:\nMust be done in order.\nSingle die roll: 1-100mod2>30\nMultiple: 5d6!4mod-2>2')
@asyncio.coroutine
def r(ctx, r : str):
    composure, enchantment, strength, weakness, die_type = 0, 0, 0, 0, 0
    # author: Writer of the Discord message
    author = ctx.message.author
    # Look for key letters
    if (r.find('c') != -1):
        r, composure = r.split('c')
    if (r.find('e') != -1):
        r, enchantment = r.split('e')
    if (r.find('s') != -1):
        r, strength = r.split('s')
    if (r.find('w') != -1):
        r, weakness = r.split('w')
    if (r.find('d') != -1):
        r, die_type = r.split('d')
    # Validate data
    try:
        # Roll a die of a certain size (ieally a d4, d6, d8, d10, or d12)
        if (die_type != 0):
            die_type_int = 0
            if (is_num(die_type) is False):
                raise ValueError("<@{}> :evergreen_tree:\nHey, wrong input! Please type your roll like this: `.r dXY` where X is the die size and Y is the type of roll (**c**omposure, **e**nchantment, **s**trength, or **w**eakness).\nEg: `.r d10c`, `.r d4e`, `.r d8s`, `.r d6w`, and so on.".format(author.id))
                return
            else:
                die_type_int = int(die_type)
            if (die_type_int <= 0):
                die_type_int *= -1
        #
        # Get Fiadh to respond in the channel
        if strength != 0:
            yield from ctx.send("<@{}> :game_die:\n:heartpulse: **Strength roll:** d{}{}".format(author.id, die_type_int, roll_strength(die_type_int)))
        elif weakness != 0:
            yield from ctx.send("<@{}> :game_die:\n:broken_heart: **Weakness roll:** d{}{}".format(author.id, die_type_int, roll_weakness(die_type_int)))
        elif composure != 0:
            yield from ctx.send("<@{}> :game_die:\n:punch: **Composure roll:** d{}{}".format(author.id, die_type_int, roll_composure(die_type_int)))
        elif enchantment != 0:
            yield from ctx.send("<@{}> :game_die:\n:sparkles:  **Enchantment roll:** d{}{}".format(author.id, die_type_int, roll_enchantment(die_type_int)))
        else:
            yield from ctx.send("<@{}> :game_die:\n**Single die roll:** d{} (**{}**)".format(author.id, die_type_int, roll_single(die_type_int)))
    except ValueError as err:
        # Display error message to channel
        yield from ctx.send(err)
    yield from purge_user_message(ctx)

@bot.command(pass_context=True,description='Help')
@asyncio.coroutine
def help(ctx):
    print("Asking for help.")
    yield from ctx.send("```Fiadh commands:\n.r dX    for a simple roll\n.r dXc   for a composure roll\n.r dXe   for an enchantment roll\n.r dXs   for a strength roll\n.r dXw   for a weakness roll\n\nRoll types:\n[c] Composure\n    - Roll one die\n    - Downgrade on 1-2\n[e] Enchantment\n    - Roll one die\n    - Upgrade on highest two numbers\n[s] Strength\n    - Roll two dice\n    - Take the higher number\n[w] Weakness\n    - Roll two dice\n    - Take the lower number```")

@bot.command()
@asyncio.coroutine
async def purge_user_message(ctx):
    await ctx.message.delete()

# Bot command to delete all messages the bot has made.
@bot.command(pass_context=True, description='Deletes all messages the bot has made.')
@asyncio.coroutine
def purge(ctx):
    channel = ctx.message.channel
    deleted = yield from bot.purge_from(channel, limit=100, check=is_me)
    yield from bot.send_message(channel, 'Deleted {} message(s)'.format(len(deleted)))

bot.run(token)
