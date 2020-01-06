import random
import time
from collections import deque

import CharacterLimit
import Command
import DataBase
import NaMBounty
import TwitchBot
import markov


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


def stylize_nam(str, prefix='NaM 👉 '):
    return prefix + str.rstrip().replace('nam', ' _ _ _ ').upper()


class Main:
    intrets_id = 86679158

    def verify_intrets(self, id):
        if type(id) == int:
            return id == self.intrets_id
        elif type(id) == str:
            return id == str(self.intrets_id)
        else:
            return False

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

    usercooldown = dict()

    laststring = ''

    counting_nams = False
    nam_count = 0

    def post_nam_bounty(self, word=None, points=0, duration=20.0):
        points = int(points)
        points = max(1, points)

        if word is None and random.random() < 0.1:
            message = random.choice(self.nammersemojis)
            self.counting_nams = False
            self.bot.queue_message(message)
            return False
        if word is None:
            ch = random.choice(self.nammers)
            word = ch[1]
            message = ch[0]
        else:
            if 'nam' not in word.lower():
                return False
            message = stylize_nam(word)

        duration_part = ''
        if duration != 20:
            duration_part = f', {duration:.2f} seconds time limit'

        points_str = 'point' if points == 1 else 'points'

        message = f'{message} ({points} {points_str} ❗ {duration_part})'

        self.bot.queue_message(message, lambda *args: self.bountyHandler.set_bounty_word(word, points), priority=True)
        return True

    def handle_nam(self, message, user_id, display_name):
        self.nam_count += 1
        if not self.counting_nams:
            self.counting_nams = True

            def handle():
                if self.post_nam_bounty(points=self.nam_count):
                    self.counting_nams = False
                    self.nam_count = 0

            self.delay(self.nam_period, handle)

    def delay(self, duration, f):
        self.timer_list.append((time.time() + duration, f))

    def __init__(self, config):
        self.config = config
        self.nam_period = self.config.defaultNamRate
        self.nam_time_stamps = deque()

        self.nammers = []
        for word in open(self.config.namwordsFileLocation, 'r'):
            word = word.rstrip()
            language, word = word.split(maxsplit=1)
            if language == 'italian:':
                prefix = '🍝 👌 NaM 👉 '
            else:
                prefix = 'NaM 👉 '
            self.nammers.append((stylize_nam(word, prefix=prefix), word))

        self.realFacts = []
        with open(self.config.factsFileLocation, encoding='utf-8-sig') as file:
            for line in file:
                if len(line) > 3:
                    self.realFacts.append(line.rstrip())

        self.factsGen = markov.Markov(self.config.factsFileLocation)
        self.questionsGen = markov.Markov(self.config.questionsFileLocation)
        self.answersGen = markov.Markov(self.config.answersFileLocation)
        self.jokes = []

        with open(self.config.jokesFileLocation, encoding='utf-8-sig') as file:
            for line in file:
                self.jokes.append(line.rstrip())

        self.bountyHandler = NaMBounty.BountyHandler(self.config)
        self.bot = TwitchBot.TwitchBot(config)
        self.commandHandler = Command.CommandHandler()
        self.create_commands()

        self.bot.add_pub_bind(self.on_pubmsg)
        self.bot.add_pub_bind(self.bountyHandler.incomingMessage)

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
                    f()
            if called:
                self.timer_list = [a for a in self.timer_list if not a[0] < currenttime]

            self.bot.check_queue()
            self.bot.reactor.process_once()
            self.sample_duration = 60
            while self.nam_time_stamps and self.nam_time_stamps[0] < currenttime - self.sample_duration:
                self.nam_time_stamps.popleft()
            time.sleep(0.1)

    def get_nam_per_minute(self):
        return len(self.nam_time_stamps) / self.sample_duration * 60

    def on_privnotice(self, c, e):
        pass

    def cmd_nampoints(self, message, user_id, display_name):
        points = self.bountyHandler.get_nammer_points(user_id)
        if points == 0:
            out = 'complete the "VIET _ _ _" like this "VIET NaM " for NaM points, 20 seconds time limit'
            self.bountyHandler.set_bounty_word('vietnam', points=1)
        else:
            out = display_name + ' you have ' + str(points) + ' NaM ' + ('point' if points == 1 else 'points')
        self.bot.queue_message(out, banphrasecheck=True)

    def cmd_parrot(self, message, user_id, display_name):
        out = ''.join(message.split(' ', maxsplit=1)[1:])
        self.bot.queue_message(out, priority=True, banphrasecheck=True)

    def cmd_topnammers(self, message, user_id, display_name):
        res = DataBase.DataBase(self.config.databaseLocation).get_top_points(limit=9)
        out = 'Top xx nammers NaM 👉 '
        count = 0
        for (_, display_name, points, _) in res:
            new = out + display_name + ': ' + str(points) + ', '
            if CharacterLimit.check_size(new, self.bot.config.characterMessageLimit):
                count += 1
                out = new
            else:
                break
        out = 'Top ' + str(count) + out[6:]
        out = out[:-2]
        self.bot.queue_message(out, banphrasecheck=True)

    def create_commands(self):
        commandList = [
            Command.Command(self.handle_dicegolf, ['!dicegolf', '!dg']),
            Command.Command(self.handle_realfact, ["!fact", "!f", 'forsenScoots', 'OMGScoots']),
            Command.Command(self.handle_fakefact, ['!realfact', '!rf']),
            Command.Command(self.handle_joke, ["!joke", "!j", 'EleGiggle', '4Head']),
            Command.Command(self.handle_dicethrow, ['!d']),

            Command.Command(lambda *_: self.bot.queue_message("bUrself"), ["bUrself"]),

            Command.Command(self.handle_nam, ['NaM', 'NAMMERS'], 0, 0, requires_user_cooldown=False,
                            requires_global_cooldown=False, requires_start_message=False),
            Command.Command(lambda *_: self.nam_time_stamps.append(time.time()), ['NaM'], 0, 0,
                            requires_global_cooldown=False, requires_user_cooldown=False, requires_start_message=False),
            Command.Command(self.cmd_nampoints, ['!nampoints', '!nampoint']),
            Command.Command(self.cmd_parrot, ['!parrot'], 0, 0, requires_user_cooldown=False,
                            requires_global_cooldown=False,
                            id_verification=self.verify_intrets),
            Command.Command(lambda *_: self.bot.queue_message('NaM ' * 70, ignorelength=True, priority=True),
                            ['!70nams'], id_verification=self.verify_intrets),
            Command.Command(self.cmd_topnammers, ['!topnammers'], command_cooldown=30),
            Command.Command(
                lambda *args: self.bot.queue_message('You flpping nammers really NaM here after the stream?')
                , ['!losers'], command_cooldown=30),
            Command.Command(lambda *_: self.bot.queue_message('NaM - made by Intrets', priority=True)
                            , ['!bot'], command_cooldown=30),
            Command.Command(self.set_nam_rate, ['!setbotspeed'], 0, 0, requires_user_cooldown=False,
                            id_verification=self.verify_intrets),
            Command.Command(lambda *_: self.bot.queue_message(f'One NaM every: {self.nam_period} seconds'),
                            ['!nambotspeed'],
                            command_cooldown=30),
            Command.Command(self.add_custom_nam, ['*bounty'], 0, 0, requires_user_cooldown=False,
                            requires_global_cooldown=False, id_verification=self.verify_intrets),
            Command.Command(lambda *_: self.bot.queue_message(f'{self.get_nam_per_minute()}'), ['!npm'],
                            command_cooldown=30),
        ]

        for c in commandList:
            self.commandHandler.add_command(c)

    def add_custom_nam(self, message, user_id, display_name):
        m = message.split(maxsplit=3)
        try:
            points = int(m[1])
            length = float(m[2])
            word = m[3].lower()
        except:
            return
        self.post_nam_bounty(word, points=points, duration=length)

    def set_nam_rate(self, message, user_id, display_name):
        m = message.split()
        if len(m) == 1:
            self.nam_period = self.config.defaultNamRate
        elif len(m) > 1:
            try:
                self.nam_period = float(m[1])
            except:
                pass

    def handle_pun(self, message, user_id, display_name):
        res = random.choice(self.jokes)
        self.bot.queue_message(res, priority=True, banphrasecheck=True)

    def handle_joke(self, message, user_id, display_name):
        m = message.split()

        question = self.questionsGen.gen()
        answer = self.answersGen.gen()
        res = question + ' ' + answer
        self.bot.queue_message(res, priority=True, banphrasecheck=True)

    def handle_realfact(self, message, user_id, display_name):
        res = random.choice(self.realFacts)
        self.bot.queue_message(res, priority=True, banphrasecheck=True)

    def handle_fakefact(self, message, user_id, display_name):
        m = message.split()
        if (len(m) > 1):
            res = self.factsGen.gen(m[1:])
        else:
            res = self.factsGen.gen()
        self.bot.queue_message(res, priority=True, banphrasecheck=True)

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

    def on_pubmsg(self, connection, type, source, target, message, tags):
        self.commandHandler.run_commands(message, tags['user-id'], tags['display-name'])
