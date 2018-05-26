# https://discordapp.com/api/oauth2/authorize?client_id=409259614341824513&permissions=105472&scope=bot

import os
import discord
import asyncio
import string
import random
from selenium import webdriver
from PIL import Image
from io import BytesIO
from time import sleep
from copy import deepcopy


token = '1234'
command = '!ss'

MAX_SIZE = 1024 * 8000  # 8MB
MAX_PROCESSES = 4

processes = 0

client = discord.Client()


default_options = {
    '-f': False,
    '-w': 1024,
    '-h': 768,
}


def configure_browser(options):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('headless')
    chrome_options.add_argument('no-sandbox')
    driver = webdriver.Chrome(chrome_options=chrome_options)
    driver.set_window_position(0, 0)
    driver.set_window_size(options['-w'], options['-h'])
    return driver


def fullpage(driver):

    """
    from here
    http://stackoverflow.com/questions/1145850/
    how-to-get-height-of-entire-document-with-javascript
    """

    js = 'return Math.max( document.body.scrollHeight, document.body.offsetHeight,  document.documentElement.clientHeight,  document.documentElement.scrollHeight,  document.documentElement.offsetHeight);'

    scrollheight = driver.execute_script(js)

    slices = []
    offset = 0
    while offset < scrollheight:

        driver.execute_script("window.scrollTo(0, %s);" % offset)
        img = Image.open(BytesIO(driver.get_screenshot_as_png()))
        offset += img.size[1]
        slices.append(img)

        if len(slices) > 50:
            raise Exception('too fucking large!')

    screenshot = Image.new('RGB', (slices[0].size[0], scrollheight))
    offset = 0
    for img in slices:
        screenshot.paste(img, (0, offset))
        offset += img.size[1]

    return screenshot


def convert_to_jpeg(png, jpg):
    im = Image.open(png)
    rgb_im = im.convert('RGB')
    os.remove(png)
    rgb_im.save(jpg)


def set_processes(content, value):
    global processes
    if content.startswith('!ss'):
        processes = value


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


@client.event
async def on_message(message):
    global processes
    set_processes(message.content, processes + 1)
    if message.content == '!ss':
        await client.send_message(
            message.channel, """
            ```
# discord-screenshot-bot
A discord bot which takes full or partial screenshots of pages then posts them.

## Usage

Command: !ss

#### Arguments (all optional):

-f - Takes a fullpage screenshot. Turned off by default.

-w=N - Width of brower, `N` being an integer. Default is 1024

-h=N - Height of browser `N` being an integer. Default is 768

### Example

!ss -f -w=1920 -h=1024 reddit.com
            ```
            """)
    elif message.content.startswith(command) and processes <= MAX_PROCESSES:
        print ('starting screenshot process')
        arguments = message.content.split(' ')
        options = deepcopy(default_options)
        custom_options = arguments[1:-1]
        site = arguments[-1]
        for option in custom_options:
            if option in options:
                if '=' in option:
                    key, value = option.split('=')
                    options[key] = value
                else:
                    options[option] = not options[option]

        print(options)

        if 'http' not in site:
            site = 'http://{}'.format(site)

        tmp = await client.send_message(
            message.channel, 'Screenshotting <{}>...'.format(site))


        rand_str = lambda n: ''.join(
            random.choice(
                string.ascii_uppercase + string.digits) for _ in range(n))

        filename = rand_str(5)
        png = '{}.{}'.format(filename, 'png')
        jpg = '{}.{}'.format(filename, 'jpg')
        
        driver = configure_browser(options)
        try:
            driver.get(site)
            sleep(1)

            if options['-f']:
                print ('fullpage')
                tmp = await client.edit_message(
                    tmp,
                    'Screenshotting <{}>... fullpage screenshots can take a '
                    'while'.format(site))

                screenshot = fullpage(driver)

                # really need to find a better way to do all this.
                screenshot.save(png)
            else:
                screenshot = driver.save_screenshot(png)

            convert_to_jpeg(png, jpg)

            filesize = os.stat(jpg).st_size
            if filesize > MAX_SIZE:
                await client.edit_message(
                    tmp, 'File too large for {}'.format(site))
            else:
                await client.edit_message(
                    tmp, 'Screenshot for <{}> grabbed!'.format(site))
                await client.send_file(message.channel, jpg)

        except:
            await client.edit_message(
                tmp,
                'Failed! Could be a timeout, file too large or site is down')
        try:
            os.remove(png)
        except OSError:
            pass
        try:
            os.remove(jpg)
        except OSError:
            pass
        driver.quit()

    elif processes > MAX_PROCESSES:
        await client.send_message(message.channel, 'Too many processes running, try again later.')

    set_processes(message.content, processes - 1)


client.run(token)
