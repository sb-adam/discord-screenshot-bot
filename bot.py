import os
import discord
import asyncio
import string
import random
from selenium import webdriver
from PIL import Image
from io import BytesIO
from time import sleep

token = '1234'
command = '!ss'

MAX_SIZE = 1024 * 8000  # 8MB

client = discord.Client()


def configure_browser():
    print('starting chrome')
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('headless')
    chrome_options.add_argument('no-sandbox')
    driver = webdriver.Chrome(chrome_options=chrome_options)
    driver.set_window_position(0, 0)
    driver.set_window_size(1024, 768)
    return driver


def fullpage(driver):

    verbose = 1

    """
    from here
    http://stackoverflow.com/questions/1145850/
    how-to-get-height-of-entire-document-with-javascript
    """

    js = 'return Math.max( document.body.scrollHeight, document.body.offsetHeight,  document.documentElement.clientHeight,  document.documentElement.scrollHeight,  document.documentElement.offsetHeight);'

    scrollheight = driver.execute_script(js)

    if verbose > 0:
        print(scrollheight)

    slices = []
    offset = 0
    while offset < scrollheight:
        if verbose > 0:
            print(offset)

        driver.execute_script("window.scrollTo(0, %s);" % offset)
        img = Image.open(BytesIO(driver.get_screenshot_as_png()))
        offset += img.size[1]
        slices.append(img)

        if len(slices) > 50:
            print('too fucking large!')
            raise Exception('too fucking large!')

        if verbose > 0:
            driver.get_screenshot_as_file(
                '%s/screen_%s.png' % ('/tmp', offset))
            print(scrollheight)

    screenshot = Image.new('RGB', (slices[0].size[0], scrollheight))
    offset = 0
    print(len(slices))
    for img in slices:
        screenshot.paste(img, (0, offset))
        offset += img.size[1]

    return screenshot


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


@client.event
async def on_message(message):
    if message.content.startswith(command):
        site = message.content[len(command) + 1:]
        if '--full' in message.content:
            site = message.content[len(command) + 8:]

        if 'http' not in site:
            site = 'http://{}'.format(site)

        print('site is {}'.format(site))

        tmp = await client.send_message(
            message.channel, 'Screenshotting <{}>...'.format(site))

        driver = configure_browser()
        try:
            driver.get(site)
            print('site loaded')

            print('sleeping')
            sleep(1)

            ext = 'png'
            filename = ''.join(
                random.choice(
                    string.ascii_uppercase + string.digits) for _ in range(10))
            full_filename = '{}.{}'.format(filename, ext)

            print('getting screenshot')
            if '--full' in message.content:
                tmp = await client.edit_message(
                    tmp,
                    'Screenshotting <{}>... fullpage screenshots can take a '
                    'while'.format(site))

                print('fullpage')
                screenshot = fullpage(driver)

                # really need to find a better way to do all this.
                screenshot.save(full_filename)
                im = Image.open(full_filename)
                rgb_im = im.convert('RGB')
                os.remove(full_filename)
                ext = 'jpg'
                full_filename = '{}.{}'.format(filename, ext)
                rgb_im.save(full_filename)
            else:
                screenshot = driver.save_screenshot(
                    full_filename)

            # filesize = os.stat(full_filename).st_size
            # if filesize > MAX_SIZE:
            #     print('file size too large: {}'.format(filesize))
            #     raise Exception('file size too large')

            await client.edit_message(
                tmp, 'Screenshot for <{}> grabbed!'.format(site))
            await client.send_file(message.channel, full_filename)

            print ('removing file')
            os.remove(full_filename)

            print('closing browser')
            driver.quit()
        except:
            print ('removing file')
            os.remove(full_filename)
            await client.edit_message(
                tmp,
                'Failed! Could be a timeout, file too large or site is down')


client.run(token)
