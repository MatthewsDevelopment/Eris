import fluxer
import asyncio
import aiohttp
from dotenv import load_dotenv
import os

load_dotenv('.env')
BOTPREFIX=os.getenv("FLUXERBOTPREFIX")
client = fluxer.Bot(command_prefix=BOTPREFIX, intents=fluxer.Intents.default())

@client.event
async def on_ready():
    print(f"{client.user.username} [Fluxer.app] Bot is Ready")

@client.command()
async def help(ctx):
    embed = fluxer.Embed(title=f"{client.user.username}", description=f"{BOTPREFIX}help\n{BOTPREFIX}ping\n{BOTPREFIX}say")
    await ctx.reply(content="Help menu", embeds=[embed.to_dict()])

@client.command()
async def ping(ctx):
    await ctx.reply("Pong!")





if __name__ == "__main__":
    TOKEN = os.getenv("FLUXERBOTTOKEN")
    client.run(TOKEN)
