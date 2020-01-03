import random
import threading
import time

import requests

import CharacterLimit
import Command
import DataBase
import NaMBounty
import TwitchBot
import markov


class ActiveUsers(threading.Thread):
    def __init__(self, bot):
        self.bot = bot
        threading.Thread.__init__(self)

    def run(self):
        payload = "https://tmi.twitch.tv/group/user/" + self.bot.channel + "/chatters"
        r = requests.get(payload, headers={'Client-ID': self.bot.config.client_id})
        viewers = r.json()['chatters']['viewers']
        message = " ".join(viewers)
        print(message)
        self.bot.queue_message(message)


def starts_with_list(str: str, list: list, cap_important=True):
    if not cap_important:
        for b in list:
            if str.lower().split(' ')[0] == b.lower():
                return True
    else:
        for b in list:
            if str.split(' ')[0] == b:
                return True
    return False


class Main:
    intrets_id = 86679158

    nammersemojis = ['NaM 👎', 'NaM 👍', 'NaM 🎐💦', 'NaM ❗', 'NaM ❓', 'NaM 🎺', 'NaM 🖕',
                     'NaM 👌', 'NaM Clap', 'NaM 💨', 'NaM 🚬', 'NaM <3',
                     '👏 NaM', 'NaM TTours', '💪 NaM',
                     'NaM ✌ THE TWO NAM NaM ✌', '🤘 NaM 🤘',
                     'NaM 👉 👌 ❓', '🅱 a 🅱 😂', '✓ NaM NAM test passed 👌',
                     '🎵 🎷 NaM 🎵', '🎵 🎻 NaM 🎵',
                     '👁 C NAMMERS 🔭 NaM', 'NaM 👉 🕐 IT\'S NaM O\'CLOCK ❗', '!roulette all 👈 NaM',
                     'PowerUpL NaM PowerUpR']

    # nammers = [('NaM 👉 CIN _ _ _ ON', 'cinnamon'),
    #            ('NaM 👉 AERODY _ _ _ IC', 'aerodynamic'),
    #            ('NaM 👉 DY _ _ _ ITE', 'dynamite'),
    #            ('NaM 👉 DY _ _ _ O', 'dynamo'),
    #            ('NaM 👉 _ _ _ ASTE', 'namaste'),
    #            ('NaM 👉 E _ _ _ EL', 'enamel'),
    #            ('NaM 👉 _ _ _ IBIA', 'namibia'),
    #            ('NaM 👉 OR _ _ _ ENT', 'ornament'),
    #            ('NaM 👉 PA _ _ _ A', 'panama'),
    #            ('NaM 👉 SURI _ _ _ E', 'suriname'),
    #            ('NaM 👉 TSU _ _ _ I', 'tsunami'),
    #            ('NaM 👉 U _ _ _ BIGUOUS', 'unambiguous'),
    #            ('NaM 👉 A _ _ _ ORPH', 'anamorph'),
    #            ('NaM 👉 BIRTH _ _ _ E', 'birthname'),
    #            ('NaM 👉 E _ _ _ OUR', 'enamour'),
    #            ('NaM 👉 METHE _ _ _ INE', 'methenamine'),
    #            ('NaM 👉 SULFO _ _ _ IDE', 'sulfonamide'),
    #            ('NaM 👉 TOUR _ _ _ ENT', 'tournament'),
    #            ('NaM 👉 AFOR _ _ _ ED', 'afornamed'),
    #            ('NaM 👉 A _ _ _ NESIS', 'anamnesis'),
    #            ('NaM 👉 LU _ _ _ ANCY', 'lunamancy'),
    #            ('NaM 👉 OPHTHALMODY _ _ _ OMETER', 'ophthalmodynamometer'),
    #            ('NaM 👉 PSYCHODY _ _ _ ICS', 'psychodynamics'),
    #            ('NaM 👉 U _ _ _ USED', 'unamused'),
    #            ('NaM 👉 KO _ _ _ I', 'konami'),
    #            ('NaM 👉 BANDAI _ _ _ CO', 'bandainamco'),
    #            ('NaM 👉 U _ _ _ PLIFIED', 'unamplified'),
    #            ('NaM 👉 CIN _ _ _ ALDEHYDE', 'cinnamaldehyde'),
    #            ]

    # ,
    # ('NaM 👉 ', ''),

    usercooldown = dict()

    # for nam in nammersemojis:
    #     nammers.append((nam, ''))

    laststring = ''

    counting_nams = False
    start_nam_count = time.time()
    nam_count = 0
    namperiod = 5

    def nam_callback(self, message, word):
        self.bountyHandler.set_bounty_word(word)

    def ok(self):
        self.bountyHandler.add_bounty(self.nam_count)
        self.nam_count = 0

        next_bounty = self.bountyHandler.next_bounty_value

        if random.random() > 0.2:
            ch = random.choice(self.nammers)
            message = ch[0]

            if next_bounty == 1:
                message += ' (' + str(next_bounty) + ' point ❗)'
            else:
                message += ' (' + str(next_bounty) + ' points ❗)'
            self.counting_nams = False
            self.bot.queue_message(message, lambda *args: self.nam_callback(message, ch[1]), priority=True)
        else:
            message = random.choice(self.nammersemojis)
            self.counting_nams = False
            self.bot.queue_message(message)

    def handle_nam(self, message, user_id, display_name, delay=True):
        print('nam')
        print(str(delay))
        if not self.counting_nams:
            self.counting_nams = True
            self.nam_count = 1
            if delay:
                self.add_timer(self.namperiod, self.ok)
            else:
                print('no')
                self.ok()
        elif self.counting_nams:
            self.nam_count += 1

    def add_timer(self, duration, f):
        self.timer_list.append((time.time() + duration, f))

    def __init__(self, config):
        self.config = config

        self.nammers = []
        for word in open(self.config.namwordsFileLocation, 'r'):
            word = word.rstrip()
            stylizednam = word.replace('nam', ' _ _ _ ')
            stylizednam = stylizednam.upper()
            self.nammers.append(('NaM 👉 ' + stylizednam.rstrip(), word))

        self.catfactsGen = markov.Markov(self.config.factsFileLocation)
        self.questionsGen = markov.Markov(self.config.questionsFileLocation)
        self.answersGen = markov.Markov(self.config.answersFileLocation)
        self.jokes = []

        with open(self.config.jokesFileLocation, encoding='utf-8-sig') as file:
            for line in file:
                self.jokes.append(line.rstrip())

        self.bountyHandler = NaMBounty.BountyHandler()
        self.bot = TwitchBot.TwitchBot(config)
        self.commandHandler = Command.CommandHandler()
        self.create_commands()

        # self.bot.add_clear_bind(self.on_clearchat)
        self.bot.add_pub_bind(self.on_pubmsg)
        self.bot.add_pub_bind(self.bountyHandler.incomingMessage)

        self.bot.reactor.add_global_handler("all_events", self.bot.parse_message_banned, -10)

        self.timer_list = list()

        print("starting")

        self.bot._connect()
        print('connected to ' + self.config.channel)

        while True:
            currenttime = time.time()
            called = False
            for (t, f) in self.timer_list:
                if t < currenttime:
                    called = True
                    print('calling')
                    f()
            if called:
                self.timer_list = [a for a in self.timer_list if not a[0] < currenttime]

            self.bot.check_queue()
            self.bot.check_banbuffer()
            self.bot.reactor.process_once()
            time.sleep(0.1)

    def on_privnotice(self, c, e):
        pass

    def cmd_nampoints(self, message, user_id, display_name):
        points = self.bountyHandler.get_nammer_points(user_id)
        if points == 0:
            out = 'complete the "VIET _ _ _" like this "VIET NaM " for NaM points, 20 seconds time limit'
            self.bountyHandler.set_tutorial_word('vietnam', None)
        else:
            out = display_name + ' you have ' + str(points) + ' NaM ' + ('point' if points == 1 else 'points')
        self.bot.queue_message(out, banphrasecheck=True)

    def cmd_commands(self, message, user_id, display_name):
        self.bountyHandler.set_tutorial_word('vietnam', None)
        self.bot.queue_message('complete the "VIET _ _ _" like this "VIET NaM " for NaM points, 20 seconds time limit')

    def cmd_parrot(self, message, user_id, display_name):
        out = ''.join(message.split(' ', maxsplit=1)[1:])
        self.bot.queue_message(out, priority=True, banphrasecheck=True)

    def cmd_topnammers(self, message, user_id, display_name):
        res = DataBase.DataBase('nammers').get_top_points(limit=9)
        out = 'Top x nammers NaM 👉 '
        count = 0
        for (_, display_name, points, _) in res:
            new = out + display_name + ': ' + str(points) + ', '
            if CharacterLimit.check_size(new, self.bot.config.characterMessageLimit):
                count += 1
                out = new
            else:
                break
        out = 'Top ' + str(count) + out[5:]
        out = out[:-2]
        self.bot.queue_message(out, banphrasecheck=True)

    def create_commands(self):
        commandList = [
            Command.Command(self.handle_dicegolf, ['!dicegolf', '!dg']),
            Command.Command(self.handle_text, ["!fact", "!f", 'forsenScoots', 'OMGScoots']),
            Command.Command(self.handle_joke, ["!joke", "!j", 'EleGiggle', '4Head']),
            # Command.Command(self.handle_pun, ["!pun", "!p", '4Head'],
            #                 user_cooldown=1, command_cooldown=1),
            Command.Command(self.wat,
                            ['!active', '!activehours', '!tophours', '!topactivehours', '!tophoursinchat',
                             '!activehoursinchat', '!acivehoursinchat', '!topactivehoursinchat']),
            Command.Command(lambda a, b, c: self.bot.queue_message("bUrself"), ["bUrself"]),
            Command.Command(self.handle_dicethrow, ['!d']),
            Command.Command(self.handle_nam, ['NaM', 'NAMMERS'], 0, 0, False, False, requires_start_message=False),
            Command.Command(self.cmd_nampoints, ['!nampoints', '!nampoint']),
            Command.Command(self.cmd_parrot, ['!parrot'], 0, 0, requires_user_cooldown=False,
                            requires_global_cooldown=False,
                            id_verification=lambda x: x == str(self.intrets_id)),
            Command.Command(lambda *args: self.bot.queue_message('NaM ' * 70, ignorelength=True, priority=True),
                            ['!70nams']),
            Command.Command(self.cmd_topnammers, ['!topnammers'], command_cooldown=30),
            Command.Command(
                lambda *args: self.bot.queue_message('You flpping nammers really NaM here after the stream?')
                , ['!losers'], command_cooldown=30),
            Command.Command(lambda *args: self.bot.queue_message('NaM - made by Intrets', priority=True)
                            , ['!bot'], command_cooldown=30),
        ]

        # commandList = [
        #     Command.Command(self.handle_nam, ['NaM', 'NAMMERS'], 0, 0, False, False),
        #     Command.Command(self.cmd_nampoints, ['!nampoints', '!nampoint']),
        #     Command.Command(lambda *args: self.bot.queue_message('MrDestructoid 👌 !namcommands - made by Intrets__')
        #                     , ['!bot'], command_cooldown=30),
        #     Command.Command(self.cmd_commands, ['!namcommands', '!namhelp'], command_cooldown=20),
        #     Command.Command(lambda *args: self.bot.queue_message('NaM ' * 70, ignorelength=True, priority=True),
        #                     ['!70nams']),
        #     Command.Command(self.cmd_parrot, ['!parrot'], 0, 0, requires_user_cooldown=False,
        #                     requires_global_cooldown=False,
        #                     id_verification=lambda x: x == str(self.intrets_id)),
        #     Command.Command(
        #         lambda *args: self.bot.queue_message('You fucking nammers.prepi really NaM here after the stream?')
        #         , ['!losers'], command_cooldown=30),
        # ]

        for c in commandList:
            self.commandHandler.add_command(c)

    def handle_pun(self, message, user_id, display_name):
        res = random.choice(self.jokes)
        self.bot.queue_message(res, priority=True, banphrasecheck=True)

    def handle_joke(self, message, user_id, display_name):
        m = message.split()

        question = self.questionsGen.gen()
        answer = self.answersGen.gen()
        res = question + ' ' + answer
        # if (len(m) > 1):
        #     res = self.catfactsGen.gen(m[1:])
        # else:
        #     res = self.catfactsGen.gen()
        self.bot.queue_message(res, priority=True, banphrasecheck=True)

    def handle_text(self, message, user_id, display_name):
        m = message.split()
        if (len(m) > 1):
            res = self.catfactsGen.gen(m[1:])
        else:
            res = self.catfactsGen.gen()
        self.bot.queue_message(res, priority=True, banphrasecheck=True)

    def wat(self, m, u, d):
        ok = ActiveUsers(self.bot)
        ok.start()

    def handle_dicethrow(self, message, user_id, display_name):
        m = message[1:].split()
        d = 20
        try:
            d = int(m[0])
        except:
            pass
        d = max(1, d)
        self.bot.queue_message("Rolling a d" + str(d) + ": " + str(random.randint(1, d)))

    def handle_dicegolf(self, message, user_id, display_name):
        m = message.split()
        d = 100
        try:
            d = int(m[1])
        except:
            pass
        l = 0
        res = str(d)
        while d > 1:
            l += 1
            d = random.randint(1, d)
            res += ', ' + str(d)
        self.bot.queue_message("Dicegolf ⛳ " + res + "⛳ " + str(l), banphrasecheck=False, ignorelength=False)

    def on_pubmsg(self, c, e):
        received = e.arguments[0]
        tags = dict()
        for tag in e.tags:
            tags[tag['key']] = tag['value']

        self.commandHandler.run_commands(received, tags['user-id'], tags['display-name'])
