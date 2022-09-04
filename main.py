# -*- coding: utf-8 -*-
# https://github.com/mybdye 🌟

import base64
import os
import ssl
import sys
import time
import urllib
import re

import requests
from requestium import Session, Keys
import undetected_chromedriver as uc
from helium import *
from selenium.webdriver.common.by import By

# 关闭证书验证
ssl._create_default_https_context = ssl._create_unverified_context

try:
    BASE_URL = os.environ['BASE_URL']
except:
    # 本地调试用
    BASE_URL = ''

try:
    USER_ID = os.environ['USER_ID']
except:
    # 本地调试用
    USER_ID = ''

try:
    PASS_WD = os.environ['PASS_WD']
except:
    # 本地调试用
    PASS_WD = ''

try:
    BARK_KEY = os.environ['BARK_KEY']
except:
    # 本地调试用
    BARK_KEY = ''

try:
    TG_BOT_TOKEN = os.environ['TG_BOT_TOKEN']
except:
    # 本地调试用
    TG_BOT_TOKEN = ''

try:
    TG_USER_ID = os.environ['TG_USER_ID']
except:
    # 本地调试用
    TG_USER_ID = ''


def urlDecode(s):
    return str(base64.b64decode(s + '=' * (4 - len(s) % 4))).split('\'')[1]


def scrollDown(key):
    i = 0
    while not S(key).exists():
        scroll_down(num_pixels=100)
        i = i + 1
        print('- scroll down 100px * %d for searching S(\'%s\')' % (i, key))


def speechToText():
    driver.tab_new(urlSpeech)
    delay(2)
    driver.switch_to.window(driver.window_handles[1])
    set_driver(driver)
    text = ''
    i = 0
    #while text == '':
    while ' ' not in text:
        i = i + 1
        if i > 3:
            print('*** speechToText issue! ***')
            break
        attach_file(os.getcwd() + audioFile, 'Upload Audio File')
        print('- waiting for transcribe')
        delay(6)
        driver.switch_to.window(driver.window_handles[1])
        set_driver(driver)
        textlist = find_all(S('.tab-panels--tab-content'))
        text = [key.web_element.text for key in textlist][0]
        print('- get text:', text)
    driver.close()
    return text


def getAudioLink():
    global block
    print('- audio file link searching...')
    if Text('Alternatively, download audio as MP3').exists() or Text('或者以 MP3 格式下载音频').exists():
        block = False
        try:
            src = Link('Alternatively, download audio as MP3').href
        except:
            src = Link('或者以 MP3 格式下载音频').href
        print('- get src:', src)

        # 下载音频文件
        delay(3)
        urllib.request.urlretrieve(src, os.getcwd() + audioFile)
        delay(4)
        text = speechToText()
        print('- waiting for switch to first window')

        # 切回第一个 tab
        # driver = get_driver()
        driver.switch_to.window(driver.window_handles[0])
        # delay(3)
        set_driver(driver)
        wait_until(S('#audio-response').exists)
        print('- fill audio response')
        write(text, into=S('#audio-response'))
        # delay(3)
        wait_until(S('#recaptcha-verify-button').exists)
        print('- click recaptcha verify button')
        click(S('#recaptcha-verify-button'))
        delay(3)
        if Text('Multiple correct solutions required - please solve more.').exists() or Text(
                '需要提供多个正确答案 - 请回答更多问题。').exists():
            print('*** Multiple correct solutions required - please solve more. ***')
            click(S('#rc-button goog-inline-block rc-button-reload'))
            getAudioLink()
        delay(1)

    elif Text('Try again later').exists() or Text('稍后重试').exists():
        textblock = S('.rc-doscaptcha-body-text').web_element.text
        print(textblock)
        body = ' *** 💣 Possibly blocked by google! ***\n' + textblock
        push(body)
        block = True

    elif not CheckBox('I\'m not a robot').is_checked() or CheckBox('我不是机器人').is_checked():
        print('*** checkbox issue ***')
        reCAPTCHA()

    else:
        print('*** audio download element not found, stop running ***')
        # print('- title:', Window().title)
        # screenshot() # debug


def reCAPTCHA():
    global block
    print('- click checkbox')
    click(S('.recaptcha-checkbox-borderAnimation'))
    # screenshot() # debug
    delay(4)
    if S('#recaptcha-audio-button').exists():
        print('- audio button found')
        click(S('#recaptcha-audio-button'))
        # screenshot() # debug
        delay(4)
        getAudioLink()
        return block


def cloudflareDT():
    try:
        i = 0
        while Text('Checking your browser before accessing').exists():
            i = i + 1
            print('*** cloudflare 5s detection *** ', i)
            time.sleep(1)
        if i > 0:
            print('*** cloudflare 5s detection finish! ***')
    except Exception as e:
        print('Error:', e)


def login():
    print('- login')
    delay(1)
    # CF
    cloudflareDT()

    #scrollDown('@login')
    #scrollDown('.btn btn-primary')

    print('- fill user id')
    if USER_ID == '':
        print('*** USER_ID is empty ***')
        kill_browser()
    else:
        write(USER_ID, into=S('@email'))
    print('- fill password')
    if PASS_WD == '':
        print('*** PASS_WD is empty ***')
        kill_browser()
    else:
        write(PASS_WD, into=S('@password'))

    # if Text('reCAPTCHA').exists():
    if Text('I\'m not a robot').exists() or Text('进行人机身份验证').exists():
        # if S('#recaptcha-token').exists():
        print('- reCAPTCHA found!')
        block = reCAPTCHA()
        if block:
            print('*** Possibly blocked by google! ***')
        else:
            submit()
    else:
        print('- reCAPTCHA not found!')
        submit()


def submit():
    print('- submit')
    try:
        click(Button('登录'))
        print('- submit clicked')
        delay(2)
    except Exception as e:
        print('*** 💣 some error in func submit!, stop running ***\nError:', e)

    cloudflareDT()

    try:
        wait_until(Text('Please correct your captcha!.').exists or Text('验证').exists())
        print('*** Network issue maybe, reCAPTCHA load fail! ***')
    except:
        pass
    try:
        wait_until(Text('Invalid').exists or Text('密码或邮箱不正确').exists())
        print('*** Invalid Username / Password ! ***')
    except:
        pass
    try:
        wait_until(Text('通知').exists)
        notice()
        try: click(Button('Read'))
        except: click(Button('已读'))
        print('- Read clicked')
        #renewVPS()
    except:
        pass
    try:
        wait_until(Text('Dashboard').exists() or Text('首页').exists())
        #userinfo()
        msg = checkin()
        print('----', msg)
    except Exception as e:
        body = '*** 💣 some error in func submit!, stop running ***'
        print('Error:', e)
        write('abc@d.com', into=S('@email'))
        screenshot()  # debug
        sys.exit(body)

def delay(i):
    time.sleep(i)

def screenshot():  # debug
    driver = get_driver()
    driver.get_screenshot_as_file(os.getcwd() + imgFile)
    print('- screenshot done')
    driver.tab_new(urlMJJ)
    # driver.execute_script('''window.open('http://mjjzp.cf/',"_blank")''')
    driver.switch_to.window(driver.window_handles[1])
    # switch_to('白嫖图床')
    delay(2)
    driver.find_element(By.ID, 'image').send_keys(os.getcwd() + imgFile)
    delay(4)
    click('上传')
    wait_until(Text('完成').exists)
    print('- upload done')
    # textList = find_all(S('#code-url'))
    # result = [key.web_element.text for key in textList][0]
    result = S('#code-url').web_element.text
    print('*** 📷 capture src:', result)
    driver.close()
    # driver.switch_to.window(driver.window_handles[0])

def notice():
    textList = find_all(S('.modal-content'))
    result = [key.web_element.text for key in textList][0]
    #if '' in result:
    print('*** %s ***' % result)

def checkin():
    s = Session(driver=driver)

    #try:
        # headers = {
        #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
        #     'Referer': base_url + '/user'
        # }
        # response = s.post(base_url + '/user/checkin', headers=headers, verify=False)
        # # print(response.text)
        # msg = (response.json()).get('msg')
        # print(msg)
    info_url = BASE_URL + '/user'
    response = s.get(info_url, verify=False)
    """
    以下只适配了editXY主题
    """
    try:
        level = re.findall(r'\["Class", "(.*?)"],', response.text)[0]
        day = re.findall(r'\["Class_Expire", "(.*)"],', response.text)[0]
        rest = re.findall(r'\["Unused_Traffic", "(.*?)"]', response.text)[0]
        msg = "- 今日签到信息：" + "\n- 用户等级：" + str(level) + "\n- 到期时间：" + str(
            day) + "\n- 剩余流量：" + str(rest)
        print(msg)
        return msg
    except:
        return msg

def push(body):
    print('- waiting for push result')
    # bark push
    if BARK_KEY == '':
        print('*** No BARK_KEY ***')
    else:
        barkurl = 'https://api.day.app/' + BARK_KEY
        title = BASE_URL
        rq_bark = requests.get(url=f'{barkurl}/{title}/{body}?isArchive=1')
        if rq_bark.status_code == 200:
            print('- bark push Done!')
        else:
            print('*** bark push fail! ***', rq_bark.content.decode('utf-8'))
    # tg push
    if TG_BOT_TOKEN == '' or TG_USER_ID == '':
        print('*** No TG_BOT_TOKEN or TG_USER_ID ***')
    else:
        body = BASE_URL + body
        server = 'https://api.telegram.org'
        tgurl = server + '/bot' + TG_BOT_TOKEN + '/sendMessage'
        rq_tg = requests.post(tgurl, data={'chat_id': TG_USER_ID, 'text': body}, headers={
            'Content-Type': 'application/x-www-form-urlencoded'})
        if rq_tg.status_code == 200:
            print('- tg push Done!')
        else:
            print('*** tg push fail! ***', rq_tg.content.decode('utf-8'))

    print('- finish!')
    # kill_browser()

audioFile = '/audio.mp3'
imgFile = '/capture.png'
##
urlSpeech = urlDecode('aHR0cHM6Ly9zcGVlY2gtdG8tdGV4dC1kZW1vLm5nLmJsdWVtaXgubmV0')
urlMJJ = urlDecode('aHR0cDovL21qanpwLmNm')
# robot = 0

print('- loading...')
driver = uc.Chrome(use_subprocess=True)
driver.set_window_size(800, 927)
delay(2)
set_driver(driver)
go_to(BASE_URL+'/auth/login')
login()
