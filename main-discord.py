import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import Button, View
import json
import requests
import random
import asyncio
import aiohttp
from dotenv import load_dotenv
import os

load_dotenv('.env')
intents = discord.Intents.default()
client = discord.Client(intents=intents)
client = commands.Bot(command_prefix=commands.when_mentioned, intents=intents)
client.remove_command("help")
WAIFUIMAPIURL = os.getenv("WAIFUIMBASEURL")
WAIFUIMTOKEN = os.getenv("WAIFUIMTOKEN")
STATUSAPIURL = "https://status.waifu.im/api/status-page/waifu"
HEARTBEATURL = f"{STATUSAPIURL.replace('/api/status-page/', '/api/status-page/heartbeat/')}"

@client.event
async def on_ready():
    try:
        synced = await client.tree.sync()
        print(f"{len(synced)} Slash Commands successfully Synced")
    except Exception as e:
        print(e)





@client.command()
async def help(ctx):
    embed = discord.Embed(title=f"{client.user.name}", description="help - This message\nnsfwtoggle - Toggle your current channels NSFW toggle\nwaifu - Send a waifu image based on a tag search\nwaifutags - Get all tag available for the waifu command\nwaifustatus - Checks the current status of the waifu image APIs\nfavsget\nfavtoggle", color=(65480))
    embed.add_field(name="waifu.pics images", value="waifupicssfw - Send a waifu image from waifu.pics\nwaifupicsnsfw - Send a NSFW waifu image from waifu.pics", inline=False)
    await ctx.send(embed=embed)

@client.command()
@commands.has_permissions(manage_channels=True)
@commands.bot_has_permissions(manage_channels=True)
async def nsfwtoggle(ctx, value=""):
    if value == "true":
        if ctx.channel.is_nsfw():
            embed = discord.Embed(title="AN ERROR HAS OCCURED", description="This channel is already marked as Age restricted", color=(16711680))
            await ctx.send(embed=embed)
            return
        else:
            await ctx.channel.edit(nsfw=True)
            await ctx.send("This channel is now marked as Age-restricted")
            return
    if value == "false":
        if ctx.channel.is_nsfw():
            await ctx.channel.edit(nsfw=False)
            await ctx.send("This channel is no longer marked as Age-restricted")
            return
        else:
            embed = discord.Embed(title="AN ERROR HAS OCCURED", description="This channel is already marked as NON Age-restricted", color=(16711680))
            await ctx.send(embed=embed)
            return

@nsfwtoggle.error
async def nsfwtoggle_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(title="AN ERROR HAS OCCURED", description="You need to have the **MANAGE_CHANNELS** permission to use this command.", color=(16711680))
        await ctx.send(embed=embed)
    if isinstance(error, commands.BotMissingPermissions):
        embed = discord.Embed(title="AN ERROR HAS OCCURED", description="I need to have the **MANAGE_CHANNELS** permission to use this command.", color=(16711680))
        await ctx.send(embed=embed)
    if isinstance(error, commands.MissingRequiredArgument):  
        embed = discord.Embed(title="ARGUMENTS REQUIRED", description="nsfwtoggle <true/false>", color=(16711680))
        await ctx.send(embed=embed)
    else:
        raise error

@client.command()
@commands.has_permissions(manage_messages=True)
async def say(ctx, *, question: commands.clean_content):
    await ctx.send(f'{question}')
    await ctx.message.delete()

@say.error
async def say_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(title="ARGUMENTS REQUIRED", description="What do you want me to say?", color=(16711680))
        await ctx.send(embed=embed)
    if isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(title="AN ERROR HAS OCCURED", description="You need to have the **MANAGE_MESSAGES** permission to use this command.", color=(16711680))
        await ctx.send(embed=embed)
    else:
        raise error

@client.command()
@commands.cooldown(1, 5, commands.BucketType.user)
async def waifu(ctx, tagsearch):
    if ctx.channel.is_nsfw():
        url = f"{WAIFUIMAPIURL}/search"
        waifu_params = {'included_tags': [f'{tagsearch}']}
        waifu_response = requests.get(url, params=waifu_params)
        if waifu_response.status_code == 200:
            waifu_image = waifu_response.json()['images'][0]['url']
        else:
            embed = discord.Embed(title="AN ERROR HAS OCCURED", description="No image was found with the provided tag search", color=(16711680))
            await ctx.send(embed=embed)

        embed = discord.Embed(title=f"Waifu image - Tag: {tagsearch}", color=(65480))
        embed.set_image(url=waifu_image)
        embed.set_footer(text=f"API source: https://www.waifu.im | Requested by {ctx.author.name}")
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(title="AN ERROR HAS OCCURED", description="This command can only be used in Age-restricted marked channes for safety reasons", color=(16711680))
        await ctx.send(embed=embed)

@client.command()
async def waifuimageinfo(ctx, imageid: int):
    if ctx.channel.is_nsfw():
        headers = {'Accept-Version': 'v7'}
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{WAIFUIMAPIURL}/images/{imageid}", headers=headers) as resp:
                if resp.status == 200:
                    data = await resp.json()
    
                    if not data:
                        embed = discord.Embed(title="AN ERROR HAS OCCURED", description="{imageid} could not be found", color=(16711680))
                        await ctx.send(embed=embed)

                    embed = discord.Embed(title=f"Image ID: {imageid}", color=discord.Color.random())
                    embed.set_image(url=data['url'])
                    embed.add_field(name="Source", value=data['source'])
                    embed.set_footer(text=f"API source: https://www.waifu.im | Requested by {ctx.author.name}")
                    await ctx.send(embed=embed)
    else:
        embed = discord.Embed(title="AN ERROR HAS OCCURED", description="This command can only be used in Age-restricted marked channes for safety reasons", color=(16711680))
        await ctx.send(embed=embed)

@client.command()
@commands.cooldown(1, 5, commands.BucketType.user)
async def waifutags(ctx):
    if ctx.channel.is_nsfw():
        request=requests.get(f"{WAIFUIMAPIURL}/tags").json()
        embed = discord.Embed(title="Waifu Command", description="Here are the tags available for: waifu <tagsearch>", color=(65480))
        embed.add_field(name="Versatile Tags", value=f"{request['versatile']}", inline=False)
        embed.add_field(name="NSFW Tags", value=f"{request['nsfw']}", inline=False)
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(title="AN ERROR HAS OCCURED", description="This command can only be used in Age-restricted marked channes for safety reasons", color=(16711680))
        await ctx.send(embed=embed)

@waifu.error
async def waifu_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        request=requests.get(f"{WAIFUIMAPIURL}/tags").json()
        embed = discord.Embed(title="Waifu Command", description=f"Here are the tags available for: waifu <tagsearch>", color=(65480))
        embed.add_field(name="Versatile Tags", value=f"{request['versatile']}", inline=False)
        embed.add_field(name="NSFW Tags", value=f"{request['nsfw']}", inline=False)
        embed.set_footer(text="API source: https://www.waifu.im")
        await ctx.send(embed=embed)
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send("This command has a 5 second cooldown. Please try again later.")
    else:
        raise error

@waifutags.error
async def waifutags_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send("This command has a 5 second cooldown. Please try again later.")
    else:
        raise error

@client.command()
@commands.cooldown(1, 5, commands.BucketType.user)
async def waifustatus(ctx):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(STATUSAPIURL) as status_page_response:
                status_page_response.raise_for_status()
                status_page_data = await status_page_response.json()
            async with session.get(HEARTBEATURL) as heartbeat_response:
                heartbeat_response.raise_for_status()
                heartbeat_data = (await heartbeat_response.json()).get('heartbeatList', {})

        status_message = "Current waifu.im API Status:\n"
        
        for group in status_page_data.get('publicGroupList', []):
            for monitor in group.get('monitorList', []):
                name = monitor['name']
                monitor_id = str(monitor['id'])
                heartbeats = heartbeat_data.get(monitor_id, [])
                latest_status_code = None

                if heartbeats:
                    sorted_heartbeats = sorted(
                        heartbeats,
                        key=lambda item: item['time'],
                        reverse=True
                    )
                    latest_status_code = sorted_heartbeats[0].get('status')

                status_code = latest_status_code if latest_status_code is not None else -1

                if status_code == 1:
                    status_emoji = "🟢"
                    status_text = "UP"
                elif status_code == 0:
                    status_emoji = "🔴"
                    status_text = "DOWN"
                elif status_code == 2:
                    status_emoji = "🟡"
                    status_text = "PENDING"
                elif status_code == 3:
                    status_emoji = "🟠"
                    status_text = "MAINTENANCE"
                else:
                    status_emoji = "❓"
                    status_text = "UNKNOWN"
                status_message += f"{status_emoji} **{name}**: {status_text}\n"

        if len(status_message.splitlines()) > 1:
            embed = discord.Embed(title="Waifu Image API Status", color=(65480))
            embed.add_field(name="Waifu.im", value=status_message, inline=False)
            await ctx.send(embed=embed)
        else:
            await ctx.send("No status data found.")

    except aiohttp.ClientResponseError as e:
        await ctx.send(f"⚠️ **HTTP Error** when fetching status: Status **{e.status}** - {e.message}")
    except aiohttp.ClientConnectorError:
        embed = discord.Embed(title="AN ERROR HAS OCCURED", description="Failed to connect to the waifu.im status API. Please try again later.", color=(16711680))
        await ctx.send(embed=embed)
    except (KeyError, TypeError, IndexError) as e:
        embed = discord.Embed(title="AN ERROR HAS OCCURED", description="Issues with data parsing has occured", color=(16711680))
        embed.add_field(value=f"{e}", inline=False)
        await ctx.send(embed=embed)
    except Exception as e:
        embed = discord.Embed(title="AN ERROR HAS OCCURED", description=f"{e}", color=(16711680))
        await ctx.send(embed=embed)

@client.command()
async def waifupicssfw(ctx):
    api_url = f"https://api.waifu.pics/sfw/waifu"
    waifupics_image = None
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(api_url) as response:
                if response.status == 200:
                    data = await response.json()
                    waifupics_image = data.get("url")
                else:
                    embed = discord.Embed(title="AN ERROR HAS OCCURED", description="Received status code {response.status} from the API for category `{category}`.", color=(16711680))
                    await ctx.send(embed=embed)
                    return
        except aiohttp.ClientConnectorError:
            embed = discord.Embed(title="AN ERROR HAS OCCURED", description="Failed to connect to the waifu.pics API. Please try again later.", color=(16711680))
            await ctx.send(embed=embed)
            return

    if waifupics_image:
        embed = discord.Embed(title=f"Waifu image", color=(65480))
        embed.set_image(url=waifupics_image)
        embed.set_footer(text=f"API source: https://waifu.pics | Requested by {ctx.author.name}", icon_url=ctx.author.avatar.url)
        await ctx.send(embed=embed)
    else:
        await ctx.send(f"Sorry, I couldn't find a valid image URL.")

@client.command()
async def waifupicsnsfw(ctx):
    if not ctx.channel.is_nsfw():
        embed = discord.Embed(title="AN ERROR HAS OCCURED", description="This command can only be used in Age-restricted marked channes for safety reasons", color=(16711680))
        await ctx.send(embed=embed)
        return
    api_url = f"https://api.waifu.pics/nsfw/waifu"
    waifupics_image = None
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(api_url) as response:
                if response.status == 200:
                    data = await response.json()
                    waifupics_image = data.get("url")
                else:
                    embed = discord.Embed(title="AN ERROR HAS OCCURED", description="Received status code {response.status} from the API for category `{category}`.", color=(16711680))
                    await ctx.send(embed=embed)
                    return
        except aiohttp.ClientConnectorError:
            embed = discord.Embed(title="AN ERROR HAS OCCURED", description="Failed to connect to the waifu.pics API. Please try again later.", color=(16711680))
            await ctx.send(embed=embed)
            return

    if waifupics_image:
        embed = discord.Embed(title=f"Waifu image", color=(65480))
        embed.set_image(url=waifupics_image)
        embed.set_footer(text=f"API source: https://waifu.pics | Requested by {ctx.author.name}", icon_url=ctx.author.avatar.url)
        await ctx.send(embed=embed)
    else:
        await ctx.send(f"Sorry, I couldn't find a valid image URL.")





@discord.app_commands.allowed_installs(guilds=True, users=False)
@discord.app_commands.allowed_contexts(guilds=True, dms=False, private_channels=False)
@client.tree.command(name="nsfwtoggle", description='Toggle your current channels NSFW toggle')
@app_commands.choices(value=[
    discord.app_commands.Choice(name="True", value=1),
    discord.app_commands.Choice(name="False", value=2),
])
@app_commands.checks.has_permissions(manage_channels=True)
@app_commands.checks.bot_has_permissions(manage_channels=True)
async def _nsfwtoggle(interaction: discord.Interaction, value: discord.app_commands.Choice[int]):
    if value.name == "True":
        if interaction.channel.is_nsfw():
            embed = discord.Embed(title="AN ERROR HAS OCCURED", description="This channel is already marked as Age restricted", color=(16711680))
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            await interaction.channel.edit(nsfw=True)
            await interaction.response.send_message("This channel is now marked as Age-restricted", ephemeral=True)
            return
    if value.name == "False":
        if interaction.channel.is_nsfw():
            await interaction.channel.edit(nsfw=False)
            await interaction.response.send_message("This channel is no longer marked as Age-restricted", ephemeral=True)
            return
        else:
            embed = discord.Embed(title="AN ERROR HAS OCCURED", description="This channel is already marked as NON Age-restricted", color=(16711680))
            await interaction.response.send_message(embed=embed, ephemeral=True)

@_nsfwtoggle.error
async def _nsfwtoggle_error(interaction, error):
    if isinstance(error, app_commands.MissingPermissions):
        embed = discord.Embed(title="AN ERROR HAS OCCURED", description="You need to have the **MANAGE_CHANNELS** permission to use this command.", color=(16711680))
        await interaction.response.send_message(embed=embed, ephemeral=True)
    if isinstance(error, app_commands.BotMissingPermissions):
        embed = discord.Embed(title="AN ERROR HAS OCCURED", description="I need to have the **MANAGE_CHANNELS** permission to use this command.", color=(16711680))
        await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
        raise error

@discord.app_commands.allowed_installs(guilds=True, users=True)
@discord.app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@client.tree.command(name="waifu", description='Send a waifu image based on a tag search')
@app_commands.checks.cooldown(1, 10)
async def _waifu(interaction: discord.Interaction, tagsearch:str):
    if interaction.channel.is_nsfw():
        url = f"{WAIFUIMAPIURL}/search"
        waifu_params = {'included_tags': [f'{tagsearch}']}
        waifu_response = requests.get(url, params=waifu_params)
        if waifu_response.status_code == 200:
            waifu_image = waifu_response.json()['images'][0]['url']
        else:
            embed = discord.Embed(title="AN ERROR HAS OCCURED", description="No image was found with the provided tag search", color=(16711680))
            await interaction.response.send_message(embed=embed, ephemeral=True)
        embed = discord.Embed(title=f"Waifu image - Tag: {tagsearch}", color=(65480))
        embed.set_image(url=waifu_image)
        embed.set_footer(text=f"API source: https://www.waifu.im | Requested by {interaction.user.name}")
        await interaction.response.send_message(embed=embed)
    else:
        embed = discord.Embed(title="AN ERROR HAS OCCURED", description="This command can only be used in Age-restricted marked channes for safety reasons", color=(16711680))
        await interaction.response.send_message(embed=embed, ephemeral=True)



@discord.app_commands.allowed_installs(guilds=True, users=True)
@discord.app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@client.tree.command(name="waifuimageinfo", description='Get information on a waifu image on waifu.im')
@app_commands.checks.cooldown(1, 10)
async def _waifuimageinfo(interaction: discord.Interaction, imageid:int):
    if interaction.channel.is_nsfw():
        headers = {'Accept-Version': 'v7'}
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{WAIFUIMAPIURL}/images/{imageid}", headers=headers) as resp:
                if resp.status == 200:
                    data = await resp.json()
    
                    if not data:
                        embed = discord.Embed(title="AN ERROR HAS OCCURED", description="{imageid} could not be found", color=(16711680))
                        await interaction.response.send_message(embed=embed, ephemeral=True)

                    embed = discord.Embed(title=f"Image ID: {imageid}", color=discord.Color.random())
                    embed.set_image(url=data['url'])
                    embed.add_field(name="Source", value=data['source'])
                    embed.set_footer(text=f"API source: https://www.waifu.im | Requested by {interaction.user.name}")
                    await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
        embed = discord.Embed(title="AN ERROR HAS OCCURED", description="This command can only be used in Age-restricted marked channes for safety reasons", color=(16711680))
        await interaction.response.send_message(embed=embed)

@discord.app_commands.allowed_installs(guilds=True, users=True)
@discord.app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@client.tree.command(name="waifutags", description='Get all tag available for the waifu command')
@app_commands.checks.cooldown(1, 10)
async def _waifutags(interaction: discord.Interaction):
    if interaction.channel.is_nsfw():
        request=requests.get(f"{WAIFUIMAPIURL}/tags").json()
        embed = discord.Embed(title="Waifu Command", description="Here are the tags available for: /waifu <tagsearch>", color=(65480))
        embed.add_field(name="Versatile Tags", value=f"{request['versatile']}", inline=False)
        embed.add_field(name="NSFW Tags", value=f"{request['nsfw']}", inline=False)
        await interaction.response.send_message(embed=embed)
    else:
        embed = discord.Embed(title="AN ERROR HAS OCCURED", description="This command can only be used in Age-restricted marked channes for safety reasons", color=(16711680))
        await interaction.response.send_message(embed=embed, ephemeral=True)

@_waifu.error
async def _waifu_error(interaction, error):
    if isinstance(error, app_commands.CommandOnCooldown):
        await interaction.response.send_message("This command has a 5 second cooldown. Please try again later.", ephemeral=True)
    else:
        raise error

@_waifutags.error
async def _waifutags_error(interaction, error):
    if isinstance(error, app_commands.CommandOnCooldown):
        await interaction.response.send_message("This command has a 5 second cooldown. Please try again later.", ephemeral=True)
    else:
        raise error

@discord.app_commands.allowed_installs(guilds=True, users=True)
@discord.app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@client.tree.command(name="waifustatus", description='Checks the current status of the waifu image APIs')
@app_commands.checks.cooldown(1, 10)
async def _waifustatus(interaction: discord.Interaction):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(STATUSAPIURL) as status_page_response:
                status_page_response.raise_for_status()
                status_page_data = await status_page_response.json()
            async with session.get(HEARTBEATURL) as heartbeat_response:
                heartbeat_response.raise_for_status()
                heartbeat_data = (await heartbeat_response.json()).get('heartbeatList', {})

        status_message = "Current waifu.im API Status:\n"
        
        for group in status_page_data.get('publicGroupList', []):
            for monitor in group.get('monitorList', []):
                name = monitor['name']
                monitor_id = str(monitor['id'])
                heartbeats = heartbeat_data.get(monitor_id, [])
                latest_status_code = None

                if heartbeats:
                    sorted_heartbeats = sorted(
                        heartbeats,
                        key=lambda item: item['time'],
                        reverse=True
                    )
                    latest_status_code = sorted_heartbeats[0].get('status')

                status_code = latest_status_code if latest_status_code is not None else -1

                if status_code == 1:
                    status_emoji = "🟢"
                    status_text = "UP"
                elif status_code == 0:
                    status_emoji = "🔴"
                    status_text = "DOWN"
                elif status_code == 2:
                    status_emoji = "🟡"
                    status_text = "PENDING"
                elif status_code == 3:
                    status_emoji = "🟠"
                    status_text = "MAINTENANCE"
                else:
                    status_emoji = "❓"
                    status_text = "UNKNOWN"
                status_message += f"{status_emoji} **{name}**: {status_text}\n"

        if len(status_message.splitlines()) > 1:
            embed = discord.Embed(title="Waifu Image API Status", color=(65480))
            embed.add_field(name="Waifu.im", value=status_message, inline=False)
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("No monitors found on this status page.", ephemeral=True)
    except requests.exceptions.RequestException as e:
        await interaction.response.send_message(f"Unable to fetch status: {e}", ephemeral=True)
    except KeyError:
        await interaction.response.send_message("Failed to parse status data.", ephemeral=True)
    except Exception as e:
        embed = discord.Embed(title="AN ERROR HAS OCCURED", description=f"{e}", color=(16711680))
        await interaction.response.send_message(embed=embed, ephemeral=True)

@discord.app_commands.allowed_installs(guilds=True, users=True)
@discord.app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@client.tree.command(name="waifupics", description="Send a waifu image from waifu.pics")
@app_commands.choices(option=[
    discord.app_commands.Choice(name="Waifu-SFW", value=1),
    discord.app_commands.Choice(name="Waifu-NSFW", value=2),
])
async def _waifupics(interaction: discord.Interaction, option: discord.app_commands.Choice[int]):
    if option.name == "Waifu-SFW":
        api_url = f"https://api.waifu.pics/sfw/waifu"
        waifupics_image = None
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(api_url) as response:
                    if response.status == 200:
                        data = await response.json()
                        waifupics_image = data.get("url")
                    else:
                        embed = discord.Embed(title="AN ERROR HAS OCCURED", description="Received status code {response.status} from the API for category `{category}`.", color=(16711680))
                        await interaction.response.send_message(embed=embed, ephemeral=True)
                        return
            except aiohttp.ClientConnectorError:
                embed = discord.Embed(title="AN ERROR HAS OCCURED", description="Failed to connect to the waifu.pics API. Please try again later.", color=(16711680))
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
        if waifupics_image:
            embed = discord.Embed(title=f"Waifu image", color=(65480))
            embed.set_image(url=waifupics_image)
            embed.set_footer(text=f"API source: https://waifu.pics | Requested by {interaction.user.name}", icon_url=interaction.user.avatar.url)
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message(f"Sorry, I couldn't find a valid image URL.", ephemeral=True)
    if option.name == "Waifu-NSFW":
        if not interaction.channel.is_nsfw():
            embed = discord.Embed(title="AN ERROR HAS OCCURED", description="This command can only be used in Age-restricted marked channes for safety reasons", color=(16711680))
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        api_url = f"https://api.waifu.pics/nsfw/waifu"
        waifupics_image = None
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(api_url) as response:
                    if response.status == 200:
                        data = await response.json()
                        waifupics_image = data.get("url")
                    else:
                        embed = discord.Embed(title="AN ERROR HAS OCCURED", description="Received status code {response.status} from the API for category `{category}`.", color=(16711680))
                        await interaction.response.send_message(embed=embed, ephemeral=True)
                        return
            except aiohttp.ClientConnectorError:
                embed = discord.Embed(title="AN ERROR HAS OCCURED", description="Failed to connect to the waifu.pics API. Please try again later.", color=(16711680))
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
        if waifupics_image:
            embed = discord.Embed(title=f"Waifu image", color=(65480))
            embed.set_image(url=waifupics_image)
            embed.set_footer(text=f"API source: https://waifu.pics | Requested by {interaction.user.name}", icon_url=interaction.user.avatar.url)
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message(f"Sorry, I couldn't find a valid image URL.", ephemeral=True)




if "__main__" == __name__:
    with open("blockedwords.txt", "r") as f:
        blockedwords = f.read().splitlines()

matthewdevstaff = [815684414045552680, 724723809218723970]
WAIFUIMTOKEN = os.getenv("WAIFUIMTOKEN")

@client.command()
async def favsget(ctx):
    if ctx.author.id not in matthewdevstaff:
        return await ctx.send("Only Matthews Development Staff members can use this command")
    if ctx.channel.is_nsfw():
        url = f"{WAIFUIMAPIURL}/users/me/albums/favorites/images?IsNsfw=All"
        headers = {
            'Accept': 'application/json',
            'Accept-Version': 'v7',
            'Authorization': f'Bearer {WAIFUIMTOKEN}',
            'X-Api-Key': f'{WAIFUIMTOKEN}'
        }
        params = {
            "included_tags": "true",
            "page_size": 10
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, params=params) as resp:
                if resp.status == 200:
                    data = await resp.json()

                    if not data or 'items' not in data:
                        return await ctx.send("Sorry, your favorites list is empty or album does not exist")

                    images = data['items'][:10] 
                    embed = discord.Embed(title=f"Album Favorites - Showing {len(images)})")
    
                    links = []
                    for img in images:
                        links.append(f"**ID:** {img['id']} | [Link]({img['url']})")
                    embed.description = "\n".join(links)
                    await ctx.send(embed=embed)
                else:
                    embed = discord.Embed(title="AN ERROR HAS OCCURED", description=f"{response.status}", color=(16711680))
                    await ctx.send(embed=embed)
    else:
        embed = discord.Embed(title="AN ERROR HAS OCCURED", description="This command can only be used in Age-restricted marked channes for safety reasons", color=(16711680))
        await ctx.send(embed=embed)

@client.command()
async def favtoggle(ctx, imageid: int):
    if ctx.author.id not in matthewdevstaff:
        return await ctx.send("Only Matthews Development Staff members can use this command")

    url = f"{WAIFUIMAPIURL}/fav/toggle"
    headers = {
        'Accept-Version': 'v5',
        'Authorization': f'Bearer {WAIFUIMTOKEN}',
        'Content-Type': 'application/json',
    }
    payload = {'image_id': imageid}

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=payload) as response:
            if response.status in [200, 201]:
                data = await response.json()
                msg = data.get('message', 'Action successful!')
                await ctx.send(f"**{msg}** (ID: {imageid})")
            else:
                embed = discord.Embed(title="AN ERROR HAS OCCURED", description=f"{response.status}", color=(16711680))
                await ctx.send(embed=embed)

@discord.app_commands.allowed_installs(guilds=True, users=False)
@discord.app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@client.tree.command(name="favsget", description="Get your favorite waifus (Bot staff only)")
async def _favsget(interaction: discord.Interaction):
    if interaction.user.id in matthewdevstaff:
        if interaction.channel.is_nsfw():
            url = f"{WAIFUIMAPIURL}/users/me/albums/favorites/images?IsNsfw=All"
            headers = {
                'Accept': 'application/json',
                'Accept-Version': 'v7',
                'Authorization': f'Bearer {WAIFUIMTOKEN}',
                'X-Api-Key': f'{WAIFUIMTOKEN}'
            }
            params = {
                "included_tags": "true",
                "page_size": 10
            }
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params) as resp:
                    if resp.status == 200:
                        data = await resp.json()

                        if not data or 'items' not in data:
                            return await interaction.response.send_message("Sorry, your favorites list is empty or album does not exist", ephemeral=True)

                        images = data['items'][:10] 
                        embed = discord.Embed(title=f"Album Favorites - Showing {len(images)})")
    
                        links = []
                        for img in images:
                            links.append(f"**ID:** {img['id']} | [Link]({img['url']})")
                        embed.description = "\n".join(links)
                        await interaction.response.send_message(embed=embed)
                    else:
                        embed = discord.Embed(title="AN ERROR HAS OCCURED", description=f"{resp.status}", color=(16711680))
                        await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            embed = discord.Embed(title="AN ERROR HAS OCCURED", description="This command can only be used in Age-restricted marked channes for safety reasons", color=(16711680))
            await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
        await interaction.response.send_message("Only Matthews Development Staff members can use this command", ephemeral=True)
        return

@discord.app_commands.allowed_installs(guilds=True, users=False)
@discord.app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@client.tree.command(name="favtoggle", description='Toggle a waifu image to be your fav (Bot staff only)')
@app_commands.checks.cooldown(1, 10)
async def _favtoggle(interaction: discord.Interaction, imageid:int):
    if interaction.user.id in matthewdevstaff:
        url = f"{WAIFUIMAPIURL}/fav/toggle"
        headers = {
            'Accept-Version': 'v5',
            'Authorization': f'Bearer {WAIFUIMTOKEN}',
            'Content-Type': 'application/json',
        }
        payload = {'image_id': imageid}

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as response:
                if response.status in [200, 201]:
                    data = await response.json()
                    msg = data.get('message', 'Action successful!')
                    await interaction.response.send_message(f"**{msg}** (ID: {imageid})")
                else:
                    embed = discord.Embed(title="AN ERROR HAS OCCURED", description=f"{response.status}", color=(16711680))
                    await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
        await interaction.response.send_message("Only Matthews Development Staff members can use this command", ephemeral=True)
        return

@client.command()
async def status(ctx, value="", *, statustext):
    if ctx.author.id in matthewdevstaff:
        if value == "watch":
            await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"{statustext}"))
            await ctx.send("My Status is Successfully Changed")
            return
        if value == "listen":
            await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=f"{statustext}"))
            await ctx.send("My Status is Successfully Changed")
            return
        if value == "play":
            await client.change_presence(activity=discord.Game(name=f"{statustext}"))
            await ctx.send("My Status is Successfully Changed")
            return
        if value == "custom":
            await client.change_presence(activity=discord.CustomActivity(name=f"{statustext}"))
            await ctx.send("My Status is Successfully Changed")
            return
    else:
        await ctx.send("Only Matthews Development Staff members can use this command")
        return

@discord.app_commands.allowed_installs(guilds=True, users=False)
@discord.app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@client.tree.command(name="status", description="Change the status of the bot (Bot staff only)")
@app_commands.choices(status=[
    discord.app_commands.Choice(name="Watching", value=1),
    discord.app_commands.Choice(name="Listening", value=2),
    discord.app_commands.Choice(name="Playing", value=3),
    discord.app_commands.Choice(name="Custom", value=4),
])
async def _status(interaction: discord.Interaction, status: discord.app_commands.Choice[int], statustext:str):
    if interaction.user.id in matthewdevstaff:
        if status.name == "Watching":
            await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"{statustext}"))
            await interaction.response.send_message("My Status is Successfully Changed", ephemeral=True)
            return
        if status.name == "Listening":
            await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=f"{statustext}"))
            await interaction.response.send_message("My Status is Successfully Changed", ephemeral=True)
            return
        if status.name == "Playing":
            await client.change_presence(activity=discord.Game(name=f"{statustext}"))
            await interaction.response.send_message("My Status is Successfully Changed", ephemeral=True)
            return
        if status.name == "Custom":
            await client.change_presence(activity=discord.CustomActivity(name=f"{statustext}"))
            await interaction.response.send_message("My Status is Successfully Changed", ephemeral=True)
            return
    else:
        await interaction.response.send_message("Only Matthews Development Staff members can use this command", ephemeral=True)
        return





TOKEN = os.getenv("DISCORDBOTTOKEN")
client.run(TOKEN)
