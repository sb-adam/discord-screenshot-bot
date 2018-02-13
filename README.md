# discord-screenshot-bot
A discord bot which takes full or partial screenshots of pages then posts them.

Requires python3.5+

Uses https://github.com/Rapptz/discord.py

Requires installation and setup of [chromedriver](https://sites.google.com/a/chromium.org/chromedriver/) and `chromium-browser`

Clone repo, run `pip install -r requirements.txt`, set token variable in `bot.py` and then run `python ./bot.py`.

Public invite link: https://discordapp.com/api/oauth2/authorize?client_id=409259614341824513&permissions=105472&scope=bot
Support server: https://discord.gg/mmg7fsT

## Usage

Command: `!ss`

#### Arguments (all optional):

 `-f` - Takes a fullpage screenshot. Turned off by default.
 
 `-w=N` - Width of brower, `N` being an integer. Default is 1024
 
 `-h=N` - Height of browser `N` being an integer. Default is 768
 
#### Example

`!ss -f  -w=1920 -h=1024 yahoo.com`
