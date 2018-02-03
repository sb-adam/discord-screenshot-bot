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

eti_username = 'u'
eti_password = 'p'

MAX_SIZE = 1024 * 8000  # 8MB

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


def login_eti(driver, site):
    print('logging into eti')
    driver.get('http://endoftheinter.net')
    username = driver.find_element_by_name("b")
    password = driver.find_element_by_name("p")

    username.send_keys(eti_username)
    password.send_keys(eti_password)

    driver.find_element_by_class_name("submit").click()
    driver.get(site)


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

        if len(slices) > 150:
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


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


@client.event
async def on_message(message):
    if message.content.startswith(command):
        print ('starting screenshot process')
        arguments = message.content.split(' ')
        options = deepcopy(default_options)
        custom_options = arguments[1:-1]
        site = arguments[-1]
        for option in custom_options:
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

        driver = configure_browser(options)

        rand_str = lambda n: ''.join(
            random.choice(
                string.ascii_uppercase + string.digits) for _ in range(n))

        filename = rand_str(5)
        png = '{}.{}'.format(filename, 'png')
        jpg = '{}.{}'.format(filename, 'jpg')

        try:
            driver.get(site)

            if 'endoftheinter.net' in site:
                print ('site is eti')
                login_eti(driver, site)

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

                os.remove(jpg)

                driver.quit()
        except:
            try:
                os.remove(png)
            except OSError:
                pass
            try:
                os.remove(jpg)
            except OSError:
                pass
            await client.edit_message(
                tmp,
                'Failed! Could be a timeout, file too large or site is down')


client.run(token)
