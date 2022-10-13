# -*- coding: utf-8 -*-

import requests
import re
import os

requests.packages.urllib3.disable_warnings()


class SspanelQd(object):
    def __init__(self):
        # 机场地址
        self.base_url = os.environ['BASE_URL']
        # 登录信息
        self.email = os.environ['USER_ID']
        self.password = os.environ['PASS_WD']
        # Bark Push
        self.BarkKey = os.environ['BARK_KEY']
        # TG Push
        self.tg_bot_token = os.environ['TG_BOT_TOKEN']
        self.tg_user_id = os.environ['TG_USER_ID']


    def checkin(self):
        email = self.email.split('@')
        email = email[0] + '%40' + email[1]
        password = self.password
        try:
            session = requests.session()
            session.get(self.base_url, verify=False)

            login_url = self.base_url + '/auth/login'
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            }

            post_data = 'email=' + email + '&passwd=' + password + '&code='
            post_data = post_data.encode()
            session.post(login_url, post_data, headers=headers, verify=False)

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
                'Referer': self.base_url + '/user'
            }

            response = session.post(self.base_url + '/user/checkin', headers=headers, verify=False)
            # print(response.text)
            msg = (response.json()).get('msg')
            print(msg)
        except:
            return False

        info_url = self.base_url + '/user'
        response = session.get(info_url, verify=False)
        """
        以下只适配了editXY主题
        """
        try:
            level = re.findall(r'\["Class", "(.*?)"],', response.text)[0]
            day = re.findall(r'\["Class_Expire", "(.*)"],', response.text)[0]
            rest = re.findall(r'\["Unused_Traffic", "(.*?)"]', response.text)[0]
            msg = "- 今日签到信息：" + str(msg) + "\n- 用户等级：" + str(level) + "\n- 到期时间：" + str(day) + "\n- 剩余流量：" + str(rest)
            print(msg)
            return msg
        except:
            return msg

    # Bark Push
    def bark_send(self, msg):
        if self.BarkKey == '':
            return
        barkurl = 'https://api.day.app/' + str(self.BarkKey)
        title = '签到信息'
        body = msg
        response = requests.get(url=f'{barkurl}/{title}/{body}?isArchive=1')
        if response.status_code != 200:
            print('Bark 推送失败')
        else:
            print('Bark 推送成功')

    def tg_send(self, msg):
        if self.tg_bot_token == '' or self.tg_user_id == '':
            return
        server = 'https://api.telegram.org'
        tgurl = server + '/bot' + self.tg_bot_token + '/sendMessage'
        rq_tg = requests.post(tgurl, data={'chat_id': self.tg_user_id, 'text': msg}, headers={
            'Content-Type': 'application/x-www-form-urlencoded'})
        if rq_tg.status_code == 200:
            print('- tg push Done!\nfinish!')
        else:
            print(rq_tg.content.decode('utf-8'))

    def main(self):
        msg = self.checkin()
        if msg == False:
            print('请检查网址/账户信息')
        else:
            self.bark_send(msg)
            self.tg_send(msg)

if __name__ == '__main__':
    run = SspanelQd()
    run.main()
