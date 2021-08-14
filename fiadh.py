# Fiadh v1.0 by Raspilicious
# A dice-rolling bot for Discord servers to be used with The Forests of Faera.
#
# Change Log
# v1.0 20210811
# - Initial python version

# Dice imports
from random import randint

# Core imports
import discord # Imported from https://github.com/Rapptz/discord.py
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext, ComponentContext # Importing the newly installed library.
#from discord_slash.utils.manage_commands import create_choice, create_option
#from discord_slash.utils.manage_components import create_select, create_select_option, create_actionrow
#from discord_slash.model import ButtonStyle
import asyncio

f = open('token.txt', 'r')
token = f.read()

client = commands.Bot(command_prefix='.')
slash = SlashCommand(client, sync_commands=True) # Declares slash commands through the bot.

guild_ids = [808133706195664906] # Put your server ID in this array.

@slash.slash(name='roll', description='Roll a die.', guild_ids=guild_ids)
async def roll(ctx, die_size:int):
    # NOTE 15/08/2021 Format the contents of the respondant message in an embed. It might look better!
    player_roll = randint(1, die_size)
    obstacle_roll = randint(1, 8)
    print('{} roll: d{} ({}). Obstacle roll: d8 ({}).'.format(ctx.author, die_size, player_roll, obstacle_roll))
    await ctx.send(content='{} attempts to overcome an obstacle. :game_die:\n:sparkles: **Player roll result:** d{} (**{}**).\n:evergreen_tree: **Obstacle roll result:** d8 (**{}**).'.format(ctx.author.mention, die_size, player_roll, obstacle_roll))

#async def perform_roll(die_size):
#    results = ''
#    x = randint(1, int(die_size))
#    results += '{}'.format(x)
#    return results

@client.event
async def on_ready():
    await client.change_presence(status=discord.Status.online, activity=discord.Game('The Forests of Faera /roll'))
    print('{} has connected to Discord!'.format(client.user))
    print('Logged in as {} with ID of [{}]'.format(client.user.name, client.user.id))
    print('--------')

client.run(token)

