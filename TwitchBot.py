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
            headers = {'Client-ID': self.twitchbot.config.client_id}
            r = requests.get(payload, headers=headers)
            if r.status_code != 200:
                self.twitchbot.online = True
                print('bad http response code: ', r.status_code)
            else:
                res = r.json()['data']
                if res == []:
                    self.twitchbot.online = False
                else:
                    self.twitchbot.online = True
                print("channel online: ", self.twitchbot.online)
            time.sleep(60 * 1)


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

    invisible_character = ' 󠀀'

    lastmessage = ''

    lastmessage_time = time.time()

    message_queue = queue.Queue()

    banbuffer = deque()

    def __init__(self, config):
        self.config = config
        self.online = False

        if self.config.checkOnline:
            OnlineChecker(self).start()

        # Get the channel id, we will need this for v5 API calls
        url = 'https://api.twitch.tv/kraken/users?login=' + self.config.channel
        headers = {'Client-ID': self.config.client_id, 'Accept': 'application/vnd.twitchtv.v5+json'}
        r = requests.get(url, headers=headers).json()

        # Create IRC bot connection
        server = 'irc.chat.twitch.tv'
        port = 6667
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

        if self.config.doWelcomeMessage:
            self.queue_message(self.config.welcomeMessage, priority=True)

    def add_pub_bind(self, fun):
        self.pubBinds.append(fun)

    def add_priv_bind(self, fun):
        self.privBinds.append(fun)

    def on_privnotice(self, c, e):
        for f in self.privBinds:
            f(c, e)

    def on_pubmsg(self, c, e):
        if not self.config.checkOnline or not self.online:
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
                f()
                self.lastmessage_time = time.time()

    def too_fast(self):
        return time.time() - self.lastmessage_time < self.config.messageRate

    # bind to "all_raw_messages"
    # self.reactor.add_global_handler('all_raw_messages', self.parse_message_banned, -10)
    def parse_message_banned(self, c, e):
        # timed out
        if e.arguments[0].startswith('@msg-id=msg_timedout'):
            pass
        # perm ban
        if e.arguments[0].startswith('@msg-id=msg_banned') and 'permanently' in \
                e.arguments[0]:
            pass

    # bind to "clearchat"
    # self.reactor.add_global_handler('clearchat', self.handle_clear, -10)
    def handle_clear(self, c, e):
        try:
            ban_target = e.arguments[0]
            duration = int(e.tags[0]['value'])
        except:
            pass
