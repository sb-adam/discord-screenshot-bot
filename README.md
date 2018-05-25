# discord-screenshot-bot
A discord bot which takes full or partial screenshots of pages then posts them.

## Installation instructions

Installation is if you do not wish to use the public bot and wish to create and maintain your own bot.

Requires python3.5+

Uses https://github.com/Rapptz/discord.py

Requires installation and setup of [chromedriver](https://sites.google.com/a/chromium.org/chromedriver/) and `chromium-browser`

Clone repo, run `pip install -r requirements.txt`, set token variable in `bot.py` and then run `python ./bot.py`.

Support server: https://discord.gg/mmg7fsT

## Public bot

The public bot is if you wish to use my publically available bot instead of maintaining your own.

Public invite link: https://discordapp.com/api/oauth2/authorize?client_id=409259614341824513&permissions=105472&scope=bot

## Usage

Command: `!ss`

#### Arguments (all optional):

 `-f` - Takes a fullpage screenshot. Turned off by default.
 
 `-w=N` - Width of brower, `N` being an integer. Default is 1024
 
 `-h=N` - Height of browser `N` being an integer. Default is 768
 
#### Example

`!ss -f  -w=1920 -h=1024 yahoo.com`
