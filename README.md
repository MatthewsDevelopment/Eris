# eris

> [!NOTE]
> To use the waifu.im API commands, you will need your own waifu.im v6 instance until I get v7 of the API to work. You can still use the waifu.pics API commands.

> [!NOTE]
> The Fluxer bot is currently very unfinished and still needs a lot of work. Currently a placeholder for now.

eris is a Discord, Stoat, and Fluxer bot that allows you to get waifu images in your server for free. It uses a couple waifu image APIs to get the waifu images to provide a variety of waifu images. This source code also includes commands to manage your waifu.im account waifu favorites.

With the Discord bot, it supports both mention prefix and slash commands. You can also allow the option for users to install the app to their account so they can use the commands anywhere where they have the "Use External Apps" permission.

For Stoat.chat users: Our Stoat bot is not available on any 3rd party stoat instances. To use eris on a 3rd party instance, you will need to self host the bot yourself. Make sure the Stoat instance you are using is using Stoat v0.7 or newer for this to work.

## Original Bots:

[Discord Bot](https://discord.com/oauth2/authorize?client_id=1442970275569471560&permissions=0&integration_type=0&scope=bot+applications.commands) - [Stoat Bot](https://old.stoat.chat/bot/01H0GNQ7KER508FKX7CX5476M2)

[Discord Server](https://discord.gg/QuZcKdDafa) - [Stoat Server](https://stt.gg/fSfKknAw)

## Setup Guide:

1. Fork/Download this source code
2. Create a Discord and/or Stoat bot
- For Discord: Create a Discord bot in https://discord.com/developers/applications
- For Stoat: Head to https://old.stoat.chat/settings/bots and create a bot by clicking "Create a bot" (if using a 3rd party instance, app.stoat.chat would be the domain of your instance)
3. Fill in everything in the .env.example file and rename .env.example to .env
- DISCORDBOTTOKEN= -> Your Discord bot token
- STOATBOTTOKEN= -> Your Stoat bot token
- STOATBOTPREFIX= -> Prefix for the Stoat bot
- STOATBASEURL= -> The base API url if the Stoat instance (Defaults to normal Stoat instance if left blank)
- STOATWEBSOCKETBASE= -> The websocket base. Can be found in the ws part in the base api url (Defaults to normal Stoat instance if left blank)
- FLUXERBOTTOKEN= -> Your Fluxer.app bot token
- FLUXERBOTPREFIX= -> Prefix for the Fluxer.app bot
- LAUNCHMODE=0 -> Refer to the modes section below
- WAIFUIMBASEURL= -> The base API url for the waifu.im API.
- WAIFUIMTOKEN= -> Your waifu.im token for using the favget and favtoggle commands.
4. Install everything from requirements.txt (Command is: pip install -r requirements.txt)
5. Run the Bot (Command is: python main.py)

> [!CAUTION]
> NEVER SHARE YOUR TOKENS WITH ANYONE!

MODES:

- 0 = Discord+Stoat Bot
- 1 = Discord Bot Only
- 2 = Stoat Bot Only
- 3 = Fluxer.app Bot Only
- 4 = Discord+Fluxer Bot Only
- 5 = Stoat+Fluxer Bot Only
- 6 = Discord+Stoat+Fluxer Bot Only

## WARNING:

THIS SOFTWARE IS PROVIDED AS-IS WITHOUT WARRENTY OF ANY KIND and it is to be used at your own risk. The Creator of this source code will NOT be liable for any damages caused from using the software. We will also not cover any hosting fees.