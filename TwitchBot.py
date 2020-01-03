import queue
import threading
import time
from collections import deque

import irc.bot
import requests

import CharacterLimit


class OnlineChecker(threading.Thread):
    def __init__(self, twitchbot: 'TwitchBot'):
        self.twitchbot = twitchbot
        threading.Thread.__init__(self)

    def run(self):
        while True:
            payload = 'https://api.twitch.tv/helix/streams?user_login=' + self.twitchbot.config.channel[1:]
            r = requests.get(payload, headers={'Client-ID': self.twitchbot.config.client_id})
            res = r.json()['data']
            if res == []:
                self.twitchbot.online = False
            else:
                self.twitchbot.online = True
            print("channel online: ", self.twitchbot.online)
            time.sleep(60 * 15)


class BanPhraseChecker(threading.Thread):
    def __init__(self, twitchbot: 'TwitchBot', message, callback, checkban):
        self.twitchbot = twitchbot
        self.message = message
        self.callback = callback
        self.checkban = checkban

        threading.Thread.__init__(self)

    def run(self):
        payload = {'message': self.message}
        r = requests.post("https://forsen.tv/api/v1/banphrases/test", data=payload)
        if r.status_code == 200:
            if not r.json()['banned']:
                self.twitchbot.message_queue.put((self.message, self.callback, self.checkban))
            else:
                self.twitchbot.message_queue.put(
                    ('Some kind of banphrased message eShrug', lambda *args: None, self.checkban))
        else:
            self.twitchbot.message_queue.put(
                ('Banphrase checker: Some kind of bad http response eShrug', lambda *args: None, self.checkban))


class TwitchBot(irc.bot.SingleServerIRCBot):
    privBinds = []
    pubBinds = []

    invisible_character = ' ⁭'

    lastmessage = ''

    lastmessage_time = time.time()

    message_queue = queue.Queue()

    banbuffer = deque()

    def __init__(self, config):
        self.config = config
        self.online = False

        if self.config.checkOnline:
            OnlineChecker(self).start()

        self.timedout = time.time()

        # Get the channel id, we will need this for v5 API calls
        url = 'https://api.twitch.tv/kraken/users?login=' + self.config.channel
        headers = {'Client-ID': self.config.client_id, 'Accept': 'application/vnd.twitchtv.v5+json'}
        r = requests.get(url, headers=headers).json()
        ####self.config.channel_id = r['users'][0]['_id']
        # Create IRC bot connection
        server = 'irc.chat.twitch.tv'
        port = 6667
        print(3)
        print('Connecting to ' + server + ' on port ' + str(port) + '...')
        irc.bot.SingleServerIRCBot.__init__(self, [(server, port, 'oauth:' + self.config.token)], self.config.username,
                                            self.config.username)

    def on_welcome(self, c, e):

        print('Joining ' + self.config.channel)
        self.c = c

        # You must request specific capabilities before you can use them
        c.cap('REQ', ':twitch.tv/membership')
        c.cap('REQ', ':twitch.tv/tags')
        c.cap('REQ', ':twitch.tv/commands')
        print("requested caps")
        c.join(self.config.channel)

        self.queue_message('NaM 7', priority=True)

    def add_pub_bind(self, fun):
        self.pubBinds.append(fun)

    def add_priv_bind(self, fun):
        self.privBinds.append(fun)

    def on_privnotice(self, c, e):
        for f in self.privBinds:
            f(c, e)

    def on_pubmsg(self, c, e):
        if self.config.checkOnline and not self.online:
            for f in self.pubBinds:
                f(c, e)

    def queue_message(self, message, callback=lambda *args: None, priority=False, banphrasecheck=False,
                      ignorelength=False, checkban=False):
        if not ignorelength:
            message = CharacterLimit.trim(message, self.config.characterMessageLimit)
        if priority or self.message_queue.empty():
            if banphrasecheck and self.config.checkBanPhrase:
                BanPhraseChecker(self, message, callback, checkban).start()
            else:
                self.message_queue.put((message, callback, checkban))
                # words = message.split(" ")
                # m = ""
                # for word in words:
                #     if len(m) + len(word) > 400:
                #         self.message_queue.put((m, callback, checkban))
                #         m = ""
                #     m += " " + word
                # if m != "":
                #     self.message_queue.put((m, callback, checkban))

    def check_queue(self):
        if not self.too_fast() and not self.message_queue.empty():
            message, f, checkban = self.message_queue.get()
            if self.config.checkOnline and self.online:
                print('message scrapped, channel online')
            else:
                if message == self.lastmessage:
                    message += self.invisible_character
                self.lastmessage = message
                self.c.privmsg(self.config.channel, message)
                if checkban:
                    self.banbuffer.append((f, time.time() + 3))
                else:
                    f()
                self.lastmessage_time = time.time()

    def check_banbuffer(self):
        # print(self.banbuffer)
        while len(self.banbuffer) > 0 and self.banbuffer[0][1] < time.time():
            print('popping')
            e = self.banbuffer.popleft()
            if self.timedout > time.time():
                print('timed out scrapping message')
            else:
                e[0]()

    def too_fast(self):
        return time.time() - self.lastmessage_time < 1.55

    def parse_message_banned(self, c, e):
        if e.type == 'all_raw_messages' and e.arguments[0].startswith('@msg-id=msg_timedout'):
            if self.timedout < time.time():
                self.timedout = time.time() + 3
        if e.type == 'all_raw_messages' and e.arguments[0].startswith('@msg-id=msg_banned') and 'permanently' in \
                e.arguments[0]:
            if self.timedout < time.time():
                self.timedout = time.time() + 3
            print('perm')
        if e.type == 'clearchat':
            print('clearchat')
            cleartarget = e.arguments[0]
            if cleartarget == self.config.username.lower():
                duration = int(e.tags[0]['value'])
                if duration == None:
                    self.timedout = time.time() + 3
                    print('perm')
                else:
                    self.timedout = time.time() + duration
                    print(duration)
