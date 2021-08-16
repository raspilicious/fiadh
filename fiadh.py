# Fiadh v1.0 by Raspilicious
# A dice-rolling Discord bot to be used with the lighthearted, cooperative tabletop roleplaying game The Forests of Faera.
#
# Change Log
# v1.0 20210817
# - Initial python version
# - Re-wrote commands to be SLASH COMMANDS! No more trying to remember the command syntax. Now, you can simply type / and choose a command. :)
# - Re-wrote message responses to use EMBEDS. Now, they look so clean and fancy. <3

# Dice Imports
from random import randint

# Coroutine Imports
import asyncio

# Discord Imports
import discord # Imported from https://github.com/Rapptz/discord.py
from discord.ext import commands
from discord_slash import SlashCommand

# Authentication Token
f = open('token.txt', 'r')
token = f.read()

# Bot
client = commands.Bot(command_prefix='/')
slash = SlashCommand(client, sync_commands=True) # Declares slash commands through the bot.

# Slash Commands

# Help
@slash.slash(name='help', description='Get help about using Fiadh.')
async def help(ctx):
    embed=discord.Embed(
        title=':evergreen_tree: Fiadh Help & Info :evergreen_tree:',
        description='Fiadh is a dice-rolling Discord bot to be used with the lighthearted, cooperative tabletop roleplaying game [The Forests of Faera](https://aarongoss.itch.io/the-forests-of-faera).\n\nThese die-rolling slash commands work with any whole number larger than 0, but when playing The Forests of Faera, you will commonly use d4, d6, and d8 dice.',
        color=0x00BA87)
    embed.add_field(name='/roll', value=':game_die: This command will roll a single die.', inline=False)
    embed.add_field(name='/use_an_ability', value=':heart: This command will roll a composure die against an obstacle die.', inline=False)
    embed.add_field(name='/use_your_strength', value=':heartpulse: This command will roll a composure die twice (taking the higher number) against an obstacle die.', inline=False)
    embed.add_field(name='/use_your_weakness', value=':mending_heart: This command will roll a composure die twice (taking the lower number) against an obstacle die.', inline=False)
    embed.add_field(name='/weave_a_spell', value=':sparkling_heart: This command will roll an enchantment die against an obstacle die.', inline=False)
    embed.add_field(name='How do you pronounce "Fiadh" in English?', value='"Fiadh" is a name of Irish origin that means "untamed" or "wild". It is pronounced in English as "Fee-ya"!')
    embed.set_footer(text='Fiadh v1.0 by Raspilicious. Look after each other when travelling through the forests!')
    await ctx.author.send(embed=embed)
    await ctx.send(content='{} asked for help, and I sent a help message to them.'.format(ctx.author.mention))

# Roll a single die
@slash.slash(name='roll', description='Roll a single die.')
async def roll(ctx, die_size:int):
    x = await roll_single(die_size)
    embed=discord.Embed(
        title='',
        description='',
        color=0x00BA87)
    embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
    embed.add_field(name=':game_die: Die Roll', value='Die size: d{}\nRoll result: **{}**'.format(die_size, x), inline=False)
    print('{} rolls a die! Die (d{}) roll result: {}.'.format(ctx.author.display_name, die_size, x))
    await ctx.send(content='{} rolls a die!'.format(ctx.author.mention), embed=embed)

# Weave a spell (roll enchantment die vs obstacle die)
@slash.slash(name='weave_a_spell', description='Roll your enchantment die against an obstacle die.')
async def weave_a_spell(ctx, die_size:int, boon:bool, bane:bool):
    obstacle_die_size = 8
    boon_bane_text = ''
    if boon==True and bane==False:
        obstacle_die_size = 6
        boon_bane_text += '(Rolling with a boon.)'
    elif boon==False and bane==True:
        obstacle_die_size = 10
        boon_bane_text += '(Rolling with a bane.)'
    else:
        obstacle_die_size = 8
    x = await roll_single(die_size)
    y = await roll_single(obstacle_die_size)
    embed = discord.Embed(
        title='',
        description='{}'.format(boon_bane_text),
        color=0x00BA87)
    embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
    embed.add_field(name=':sparkling_heart: Enchantment Die Roll', value='Die size: d{}\nRoll result: **{}**'.format(die_size, x), inline=True)
    embed.add_field(name=':evergreen_tree: Obstacle Die Roll', value='Die size: d{}\nRoll result: **{}**'.format(obstacle_die_size, y), inline=True)
    if x > y: # You succeed
        embed.add_field(name=':blush: Success!', value='Your spell works as you intended! Your Guide will tell you what happens next.', inline=False)
    elif y > x: # The situation becomes more complicated
        embed.add_field(name=':cold_sweat: Complication.', value='Something goes wrong! Your Guide will tell you how the situation becomes more complicated.', inline=False)
    else: # You tie and have to choose: succeed at a cost or allow the situation to become more complicated
        embed.add_field(name=':grimacing: Choose...', value='Your spell almost works as you intended, but not quite! Tell your Guide if you would like to succeed at a cost, or allow the situation to become more complicated. They will then describe what happens next.', inline=False)
    if x>=die_size-1: # Gain enchantment
        if die_size==4 or die_size==6:
            embed.add_field(name=':sparkles: You gain enchantment!', value='The grip of the forests\' magics on you grow stronger and you are marked with a new rune. Choose one from the Runes section, then describe how and where it appears on you. Your enchantment die cascades to the next larger size.')
        if die_size==8 or die_size==10 or die_size==12:
            embed.add_field(name=':broken_heart: You become distressed.', value='You lose yourself in the magics of the forests and become distressed.')
            embed.set_footer(text='Fauns only become distressed when weaving a spell and rolling high on a d10.')
    print('{} weaves a spell! Enchantment die (d{}) roll result: {}. Obstacle die (d{}) roll result: {}.'.format(ctx.author.display_name, die_size, x, obstacle_die_size, y))
    await ctx.send(content='{} weaves a spell!'.format(ctx.author.mention), embed=embed)

# Use an ability (roll composure die vs obstacle die)
@slash.slash(name='use_an_ability', description='Roll your composure die against an obstacle die.')
async def use_an_ability(ctx, die_size:int, boon:bool, bane:bool):
    obstacle_die_size = 8
    boon_bane_text = ''
    if boon==True and bane==False:
        obstacle_die_size = 6
        boon_bane_text += '(Rolling with a boon.)'
    elif boon==False and bane==True:
        obstacle_die_size = 10
        boon_bane_text += '(Rolling with a bane.)'
    else:
        obstacle_die_size = 8
    x = await roll_single(die_size)
    y = await roll_single(obstacle_die_size)
    embed = discord.Embed(
        title='',
        description='{}'.format(boon_bane_text),
        color=0x00BA87)
    embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
    embed.add_field(name=':heart: Composure Die Roll', value='Die size: d{}\nRoll result: **{}**'.format(die_size, x), inline=True)
    embed.add_field(name=':evergreen_tree: Obstacle Die Roll', value='Die size: d{}\nRoll result: **{}**'.format(obstacle_die_size, y), inline=True)
    if x > y: # You succeed
        embed.add_field(name=':blush: Success!', value='Your action works as you intended! Your Guide will tell you what happens next.', inline=False)
    elif y > x: # Situation becomes more complicated
        embed.add_field(name=':cold_sweat: Complication.', value='Something goes wrong! Your Guide will tell you how the situation becomes more complicated.', inline=False)
    else: # You tie and have to choose: succeed at a cost or allow the situation to become more complicated
        embed.add_field(name=':grimacing: Choose...', value='Your action almost works as you intended, but not quite! Tell your Guide if you would like to succeed at a cost, or allow the situation to become more complicated. They will then describe what happens next.', inline=False)
    if x<=2: # Lose composure
        if die_size==6 or die_size==8 or die_size==10 or die_size==12:
            embed.add_field(name=':dizzy: You lose composure!', value='Your physical ability and mental willpower weaken. Your composure die cascades to the next smaller die size.')
        if die_size==4:
            embed.add_field(name=':broken_heart: You become distressed.', value='You lose the last of your composure and become distressed.')
    print('{} uses an ability! Composure die (d{}) roll result: {}. Obstacle die (d{}) roll result: {}.'.format(ctx.author.display_name, die_size, x, obstacle_die_size, y))
    await ctx.send(content='{} uses an ability!'.format(ctx.author.mention), embed=embed)

# Use your strength (roll composure die twice vs an obstacle die and take the higher number)
@slash.slash(name='use_your_strength', description='Roll your composure die twice (taking the higher number) against an obstacle die.')
async def use_your_strength(ctx, die_size:int, boon:bool, bane:bool):
    obstacle_die_size = 8
    boon_bane_text = ''
    if boon==True and bane==False:
        obstacle_die_size = 6
        boon_bane_text += '(Rolling with a boon.)'
    elif boon==False and bane==True:
        obstacle_die_size = 10
        boon_bane_text += '(Rolling with a bane.)'
    else:
        obstacle_die_size = 8
    x_one = await roll_single(die_size)
    x_two = await roll_single(die_size)
    higher = max(x_one, x_two)
    y = await roll_single(obstacle_die_size)
    embed = discord.Embed(
        title='',
        description='{}'.format(boon_bane_text),
        color=0x00BA87)
    embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
    embed.add_field(name=':heartpulse: Composure Die Rolls', value='Die size: d{}\nRoll results: {} and {}. Taking **{}**'.format(die_size, x_one, x_two, higher), inline=True)
    embed.add_field(name=':evergreen_tree: Obstacle Die Roll', value='Die size: d{}\nRoll result: **{}**'.format(obstacle_die_size, y), inline=True)
    if higher > y: # You succeed
        embed.add_field(name=':blush: Success!', value='Your action works as you intended! Your Guide will tell you what happens next.', inline=False)
    elif y > higher: # The situation becomes more complicated
        embed.add_field(name=':cold_sweat: Complication.', value='Something goes wrong! Your Guide will tell you how the situation becomes more complicated.', inline=False)
    else: # You tie and have to choose: succeed at a cost or allow the situation to become more complicated
        embed.add_field(name=':grimacing: Choose...', value='Your action almost works as you intended, but not quite! Tell your Guide if you would like to succeed at a cost, or allow the situation to become more complicated. They will then describe what happens next.', inline=False)
    if higher<=2: # Lose composure
        if die_size==6 or die_size==8 or die_size==10 or die_size==12:
            embed.add_field(name=':dizzy: You lose composure!', value='The energies of your body, mind, and spirit deminish. Your composure die cascades to the next smaller die size.')
        if die_size==4:
            embed.add_field(name=':broken_heart: You become distressed.', value='You lose the last of your composure and become distressed.')
    print('{} uses their strength! Composure die (d{}) roll results: {} and {}. Obstacle die (d{}) roll result: {}.'.format(ctx.author.display_name, die_size, x_one, x_two, obstacle_die_size, y))
    await ctx.send(content='{} uses their strength!'.format(ctx.author.mention), embed=embed)

# Use your weakness (roll composure die twice vs an obstacle die and take the lower number)
@slash.slash(name='use_your_weakness', description='Roll your composure die twice (taking the lower number) against an obstacle die.')
async def use_your_weakness(ctx, die_size:int, boon:bool, bane:bool):
    obstacle_die_size = 8
    boon_bane_text = ''
    if boon==True and bane==False:
        obstacle_die_size = 6
        boon_bane_text += '(Rolling with a boon.)'
    elif boon==False and bane==True:
        obstacle_die_size = 10
        boon_bane_text += '(Rolling with a bane.)'
    else:
        obstacle_die_size = 8
    x_one = await roll_single(die_size)
    x_two = await roll_single(die_size)
    lower = min(x_one, x_two)
    y = await roll_single(obstacle_die_size)
    embed = discord.Embed(
        title='',
        description='{}'.format(boon_bane_text),
        color=0x00BA87)
    embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
    embed.add_field(name=':mending_heart: Composure Die Rolls', value='Die size: d{}\nRoll results: {} and {}. Taking **{}**'.format(die_size, x_one, x_two, lower), inline=True)
    embed.add_field(name=':evergreen_tree: Obstacle Die Roll', value='Die size: d{}\nRoll result: **{}**'.format(obstacle_die_size, y), inline=True)
    if lower > y: # You succeed
        embed.add_field(name=':blush: Success!', value='Your action works as you intended! Your Guide will tell you what happens next.', inline=False)
    elif y > lower: # The situation becomes more complicated
        embed.add_field(name=':cold_sweat: Complication.', value='Something goes wrong! Your Guide will tell you how the situation becomes more complicated.', inline=False)
    else: # You tie and have to choose: succeed at a cost or allow the situation to become more complicated
        embed.add_field(name=':grimacing: Choose...', value='Your action almost works as you intended, but not quite! Tell your Guide if you would like to succeed at a cost, or allow the situation to become more complicated. They will then describe what happens next.', inline=False)
    if lower<=2: # Lose composure
        if die_size==6 or die_size==8 or die_size==10 or die_size==12:
            embed.add_field(name=':dizzy: You lose composure!', value='The energies of your body, mind, and spirit deminish. Your composure die cascades to the next smaller die size.')
        if die_size==4:
            embed.add_field(name=':broken_heart: You become distressed.', value='You lose the last of your composure and become distressed.')
    print('{} uses their weakness! Composure die (d{}) roll results: {} and {}. Obstacle die (d{}) roll result: {}.'.format(ctx.author.display_name, die_size, x_one, x_two, obstacle_die_size, y))
    await ctx.send(content='{} uses their weakness!'.format(ctx.author.mention), embed=embed)

# Single die roll function to be called throughout the script
async def roll_single(die_size:int):
    roll_result = randint(1, die_size)
    return roll_result

# Client initialisation event
@client.event
async def on_ready():
    await client.change_presence(status=discord.Status.online, activity=discord.Game('in the forests. /roll'))
    print('{} has connected to Discord!'.format(client.user))
    print('Logged in as {} with ID of [{}]'.format(client.user.name, client.user.id))
    print('--------')

# Start the bot
client.run(token)