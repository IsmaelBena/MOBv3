import os
from dotenv import load_dotenv
import json
import discord
from discord.ext import commands
from mc_server_controller import MC_Server_Controller, ServerState

# get env vars
load_dotenv()
BOT_TOKEN = os.environ.get("BOT_TOKEN")
MC_SERVER_DIR = os.environ.get("MC_SERVER_DIR")

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

# 
MCSC = MC_Server_Controller(MC_SERVER_DIR)

# get list of commands for the help command
with open('./help.json', 'r') as file:
    help_data = json.load(file)

@bot.event
async def on_ready():
    print('Logged on as {0}!'.format(bot.user))

@bot.command()
async def ping(ctx):
    print('ping recieved from {0}'.format(ctx.author))
    await ctx.channel.send("```\npong\n```")
    print('responded with pong in {0}'.format(ctx.channel))

bot.remove_command("help")
@bot.command()
async def help(ctx, *args):
    print('{0} asked for help'.format(ctx.author))
    await ctx.channel.send(f"```\n{help_data}\n```")

@bot.command()
async def mc(ctx, *args):
    if len(args) < 1:
        await ctx.channel.send("```\nNo args given\n```")
    else:
        if (args[0].lower() == "start"):
            await mcStart(ctx.channel)
        elif (args[0].lower() in ["stop", "shutdown", "kill"]):
            await mcStop(ctx.channel)


async def mcStart(channel):
    if MCSC.server_state != ServerState.OFF:
        await channel.send("```\nServer is currently not off\n```")
    else:
        await MCSC.start(channel)


async def mcStop(channel):
    if MCSC.server_state != ServerState.ON:
        await channel.send("```\nServer is not currently on so it cannot shutdown\n```")
    else:
        await MCSC.stop(channel)

async def mcStatus(ctx):
    print("server status")

async def mcInfo(ctx):
    print("server info")


bot.run(BOT_TOKEN)