"""
Use !mc to access commands here.

Boot up server:            [!mc start]
Shutdown server:           [!mc stop/shutdown]
Check server status with:  [!mc status]
Check server info with:    [!mc info]

"""
from enum import Enum
import urllib.request
from subprocess import Popen, PIPE, CREATE_NEW_CONSOLE
import os
import time
import aiomcrcon
from jproperties import Properties
import discord


class ServerState(Enum):
    ON = 1
    OFF = 2
    STARTING = 3
    STOPPING = 4

class MC_Server_Controller:

    def __init__(self, server_dir):
        print("MC server controller created")
        self.server_state = ServerState.OFF
        self.external_ipv4 = urllib.request.urlopen('https://v4.ident.me').read().decode('utf8')
        self.server_dir = str(server_dir)
        self.update_server_config()
        self.prev_boot_time = 0

    def update_server_config(self):
        
        server_configs = Properties()
        with open(f'{self.server_dir}\\server.properties', 'rb') as config_file:
            server_configs.load(config_file)
        
        self.rcon_port = server_configs.get("rcon.port").data
        self.rcon_password = server_configs.get("rcon.password").data

    async def start(self, channel):
        try:
            p = Popen(['start', 'cmd', '/C', 'start.bat'], cwd=self.server_dir, shell=True)
            self.server_state = ServerState.STARTING
            loadingMsg = await channel.send("```\nMinecraft server is booting up :)\n```")
            time.sleep(1)
            p.terminate()
            current_boot_time = 0
            print(self.rcon_port, self.rcon_password)
            self.client = aiomcrcon.Client(self.external_ipv4, self.rcon_port, self.rcon_password)
        except:
            self.server_state = ServerState.OFF
            return False

        while (not (self.server_state == ServerState.ON)):
            try:
                await self.client.connect(timeout=1)
                print("Server on")
                self.server_state = ServerState.ON
                self.prev_boot_time = current_boot_time + 1
                onlineMsg = "```\n {0}\nServer is now online\n```".format(progressBar(current_boot_time, self.prev_boot_time, complete=True))
                await loadingMsg.edit(content=onlineMsg)
            except:
                print("Server not on yet")
                current_boot_time += 1
                print(f"{current_boot_time}/{self.prev_boot_time}")
                progressMsg = "```\n {0} \n```".format(progressBar(current_boot_time, self.prev_boot_time))
                await loadingMsg.edit(content=progressMsg)
                continue

        print("Server online")
        return True

    async def stop(self, channel):
        self.server_state = ServerState.STOPPING
        print("Stopping server")
        shutdownMsg = await channel.send("```\nServer shutting down\n```")

        try:
            await self.client.connect()
            await self.client.send_cmd("stop")
            await self.client.close()
            self.server_state = ServerState.OFF
            await shutdownMsg.edit(content="```\nServer offline\n```")
        except:
            await shutdownMsg.edit(content="```\nSomething went wrong while attempting to shutdown, ask the server host to check their hosting machine.\n```")
        return True


def progressBar(timeElapsed, averagePrevtime, complete=False):
    if not complete:
        if timeElapsed >= averagePrevtime:
            averagePrevtime = timeElapsed + 1
        percent = 100 * (timeElapsed / float(averagePrevtime))
    else:
        percent = 100
    bar = '█' * int(percent) + '-' * (100 - int(percent))
    return f"\n---Based on previous load times---\n| {bar} | {percent:.2f}%\n"
