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
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="over you"))

@bot.command()
async def ping(ctx):
    print('ping recieved from {0}'.format(ctx.author))
    await ctx.channel.send("```\npong\n```")
    print('responded with pong in {0}'.format(ctx.channel))

bot.remove_command("help")
@bot.command()
async def help(ctx, *args):
    print('{0} asked for help'.format(ctx.author))
    helpMsg = ''
    for command in help_data:
        if "args" in command:
            args = ''
            for arg in command["args"]:
                args += f"\t-- {arg['arg']}: {arg['desc']}\n"
            helpMsg += f"\n + {command['command']}:\n\t{command['desc']}\n - For the command to work you need to use one of the following arguments:\n{args}\n"
        else:
            helpMsg += f"\n + {command['command']}:\n\t{command['desc']}\n"
    await ctx.channel.send(f"```\n----- All Commands -----\n{helpMsg}\n```")

@bot.command()
async def mc(ctx, *args):
    if len(args) < 1:
        await ctx.channel.send("```\nNo args given\n```")
    else:
        if (args[0].lower() == "start"):
            await mcStart(ctx.channel)
        elif (args[0].lower() == "stop"):
            await mcStop(ctx.channel)
        elif (args[0].lower() == "status"):
            await mcStatus(ctx.channel)
        elif (args[0].lower() == "info"):
            await mcInfo(ctx.channel)
        elif (args[0].lower() == "op"):
            await mcOP(ctx.channel, args[1])

async def mcStart(channel):
    if MCSC.server_state != ServerState.OFF:
        await channel.send("```\nServer is currently not off\n```")
    else:
        await MCSC.start(channel)
        await bot.change_presence(activity=discord.Game(name="Minecraft Server Management"))

async def mcStop(channel):
    if MCSC.server_state != ServerState.ON:
        await channel.send("```\nServer is not currently on so it cannot shutdown\n```")
    else:
        await MCSC.stop(channel)
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="over you"))

async def mcStatus(channel):
    print("server status")
    await MCSC.status(channel)

async def mcInfo(channel):
    print("server info")
    await MCSC.getInfo(channel)

async def mcOP(channel, target):
    print(f"Attempting to OP {target}")
    await MCSC.op(channel, target)


bot.run(BOT_TOKEN)