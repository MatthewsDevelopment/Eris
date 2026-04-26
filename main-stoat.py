import stoat
from stoat.ext import commands
import json
import requests
import random
import asyncio
import aiohttp
from dotenv import load_dotenv
import os

load_dotenv('.env')
BOTPREFIX = os.getenv("STOATBOTPREFIX")
BASEURL=os.getenv("STOATBASEURL")
WEBSOCKETURL=os.getenv("STOATWEBSOCKETURL")
WAIFUIMTOKEN = os.getenv("WAIFUIMTOKEN")
client = commands.Bot(command_prefix=BOTPREFIX, http_base=BASEURL, websocket_base=WEBSOCKETURL)
client.remove_command("help")
WAIFUIMAPIURL = os.getenv("WAIFUIMBASEURL")
STATUSAPIURL = "https://status.waifu.im/api/status-page/waifu"
HEARTBEATURL = f"{STATUSAPIURL.replace('/api/status-page/', '/api/status-page/heartbeat/')}"

@client.on(commands.CommandErrorEvent)
async def on_command_error(event):
    ctx = event.context
    error = event.error
    await ctx.send(f"Something went wrong. {error}")





@client.command()
async def help(ctx):
    embed = stoat.SendableEmbed(title=f"{client.user.name}", description=f"{BOTPREFIX}help - This message\n{BOTPREFIX}waifu - Send a waifu image based on a tag search\n{BOTPREFIX}waifutags - Get all tag available for the waifu command\nwaifuimageinfo\n{BOTPREFIX}waifustatus - Checks the current status of the waifu image APIs\n{BOTPREFIX}waifupicssfw - Send a waifu image from waifu.pics\n{BOTPREFIX}waifupicsnsfw - Send a NSFW waifu image from waifu.pics\n{BOTPREFIX}favsget\n{BOTPREFIX}favtoggle")
    await ctx.channel.send(embeds=[embed])

@client.command()
@commands.server_only()
async def say(ctx, *, message:str):
    if not ctx.server.permissions_for(ctx.author).manage_server:
        embed = stoat.SendableEmbed(title="AN ERROR HAS OCCURED", description="You need to have the **MANAGE SERVER** permission to use this command.")
        await ctx.channel.send(embeds=[embed])
        return
    if "@everyone" in message.lower():
        await ctx.channel.send("You can not have the bot mention everyone")
        return
    await ctx.channel.send(message)

@client.command()
@commands.cooldown(1, 5, commands.BucketType.user)
async def waifu(ctx, tagsearch):
    if ctx.channel.nsfw:
        url = f"{WAIFUIMAPIURL}/search"
        waifu_params = {'included_tags': [f'{tagsearch}']}
        waifu_response = requests.get(url, params=waifu_params)
        if waifu_response.status_code == 200:
            waifu_image = waifu_response.json()['images'][0]['url']
        else:
            embed = stoat.SendableEmbed(title="AN ERROR HAS OCCURED", description="No image was found with the provided tag search")
            await ctx.channel.send(embeds=[embed])

        embed = stoat.SendableEmbed(title=f"Waifu image - Tag: {tagsearch}", description=f"API source: https://www.waifu.im | Requested by {ctx.author.name}")
        await ctx.channel.send(content=f"{waifu_image}", embeds=[embed])
    else:
        embed = stoat.SendableEmbed(title="AN ERROR HAS OCCURED", description="This command can only be used in Age-restricted marked channes for safety reason")
        await ctx.channel.send(embeds=[embed])

@client.command()
@commands.cooldown(1, 5, commands.BucketType.user)
async def waifutags(ctx):
    if ctx.channel.nsfw:
        request=requests.get(f"{WAIFUIMAPIURL}/tags").json()
        embed = stoat.SendableEmbed(title="Waifu Command", description=f"Here are the tags available for: waifu <tagsearch>\nVersatile Tags: {request['versatile']}\nNSFW Tags: {request['nsfw']}")
        await ctx.channel.send(embeds=[embed])
    else:
        embed = stoat.SendableEmbed(title="AN ERROR HAS OCCURED", description="This command can only be used in Age-restricted marked channes for safety reason")
        await ctx.channel.send(embeds=[embed])

@client.command()
@commands.cooldown(1, 5, commands.BucketType.user)
async def waifuimageinfo(ctx, imageid: int):
    if ctx.channel.nsfw:
        headers = {'Accept-Version': 'v7'}
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{WAIFUIMAPIURL}/images/{imageid}", headers=headers) as resp:
                if resp.status == 200:
                    data = await resp.json()
    
                    if not data:
                        embed = stoat.SendableEmbed(title="AN ERROR HAS OCCURED", description=f"API source: https://www.waifu.im | Requested by {ctx.author.name}")
                        await ctx.channel.send(embeds=[embed])

                    embed = stoat.SendableEmbed(title=f"Image ID: {imageid}", description=f"Source: {data['source']}\nAPI source: https://www.waifu.im | Requested by {ctx.author.name}")
                    await ctx.channel.send(content=f"{data['url']}", embeds=[embed])
    else:
        embed = stoat.SendableEmbed(title="AN ERROR HAS OCCURED", description="This command can only be used in Age-restricted marked channes for safety reasons")
        await ctx.channel.send(embeds=[embed])

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
            embed = stoat.SendableEmbed(title="Waifu Image API Status", description=status_message)
            await ctx.channel.send(embeds=[embed])
        else:
            await ctx.channel.send("No status data found.")

    except aiohttp.ClientResponseError as e:
        await ctx.channel.send(f"⚠️ **HTTP Error** when fetching status: Status **{e.status}** - {e.message}")
    except aiohttp.ClientConnectorError:
        embed = stoat.SendableEmbed(title="AN ERROR HAS OCCURED", description="Failed to connect to the waifu.im status API. Please try again later.")
        await ctx.channel.send(embeds=[embed])
    except (KeyError, TypeError, IndexError) as e:
        embed = stoat.SendableEmbed(title="AN ERROR HAS OCCURED", description="Issues with data parsing has occured. {e}")
        await ctx.channel.send(embeds=[embed])
    except Exception as e:
        embed = stoat.SendableEmbed(title="AN ERROR HAS OCCURED", description=f"{e}")
        await ctx.channel.send(embeds=[embed])

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
                    embed = stoat.SendableEmbed(title="AN ERROR HAS OCCURED", description="Received status code {response.status} from the API for category `{category}`.")
                    await ctx.channel.send(embed=embed)
                    return
        except aiohttp.ClientConnectorError:
            embed = stoat.SendableEmbed(title="AN ERROR HAS OCCURED", description="Failed to connect to the waifu.pics API. Please try again later.")
            await ctx.channel.send(embeds=[embed])
            return

    if waifupics_image:
        embed = stoat.SendableEmbed(title=f"Waifu image", description=f"API source: https://waifu.pics | Requested by {ctx.author.name}")
        await ctx.channel.send(content=f"{waifupics_image}", embeds=[embed])
    else:
        await ctx.channel.send(f"Sorry, I couldn't find a valid image URL.")

@client.command()
async def waifupicsnsfw(ctx):
    if not ctx.channel.nsfw:
        embed = stoat.SendableEmbed(title="AN ERROR HAS OCCURED", description="This command can only be used in Age-restricted marked channes for safety reason")
        await ctx.channel.send(embeds=[embed])
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
                    print(f"Waifu API error for {search_type}/{category}: Status {response.status}")
                    embed = stoat.SendableEmbed(title="AN ERROR HAS OCCURED", description="Received status code {response.status} from the API for category `{category}`.")
                    await ctx.channel.send(embeds=[embed])
                    return
        except aiohttp.ClientConnectorError:
            embed = stoat.SendableEmbed(title="AN ERROR HAS OCCURED", description="Failed to connect to the waifu.pics API. Please try again later.")
            await ctx.channel.send(embeds=[embed])
            return

    if waifupics_image:
        embed = stoat.SendableEmbed(title=f"Waifu image", description=f"API source: https://waifu.pics | Requested by {ctx.author.name}")
        await ctx.channel.send(content=f"{waifupics_image}", embeds=[embed])
    else:
        await ctx.channel.send(f"Sorry, I couldn't find a valid image URL.")





@client.command()
@commands.is_owner()
async def favsget(ctx):
    if ctx.channel.nsfw:
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
                        return await ctx.channel.send("Sorry, your favorites list is empty or album does not exist")

                    images = data['items'][:10] 
                    embed = stoat.SendableEmbed(title=f"Album Favorites - Showing {len(images)})")
    
                    links = []
                    for img in images:
                        links.append(f"**ID:** {img['id']} | [Link]({img['url']})")
                    embed.description = "\n".join(links)
                    await ctx.channel.send(embeds=[embed])
                else:
                    embed = stoat.SendableEmbed(title="AN ERROR HAS OCCURED", description=f"{response.status}")
                    await ctx.channel.send(embeds=[embed])
    else:
        embed = stoat.SendableEmbed(title="AN ERROR HAS OCCURED", description="This command can only be used in Age-restricted marked channes for safety reasons")
        await ctx.channel.send(embeds=[embed])

@client.command()
@commands.is_owner()
async def favtoggle(ctx, imageid: int):
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
                await ctx.channel.send(f"**{msg}** (ID: {imageid})")
            else:
                embed = stoat.SendableEmbed(title="AN ERROR HAS OCCURED", description=f"{response.status}")
                await ctx.channel.send(embeds=[embed])





TOKEN = os.getenv("STOATBOTTOKEN")
client.run(TOKEN)
