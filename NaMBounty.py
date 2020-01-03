import time

import DataBase


def check_word(message, word):
    words = message.split(' ')
    return word in ''.join(words).lower() and 'NaM' in words


class BountyHandler:

    def __init__(self, config):
        self.database = DataBase.DataBase(config.databaseLocation)

        self.openBounty = dict()
        self.claimedBounty = dict()

        self.next_bounty_value = 0

    def check_bounty(self, message, user_id):
        # print('checking bounty')
        for word, obj in self.openBounty.items():
            # print(word)
            # print(obj)
            if check_word(message, word) \
                    and (obj[0] == user_id or obj[0] == None) \
                    and time.time() < obj[2] \
                    and user_id not in self.claimedBounty[word]:
                print('True')
                return (word, obj[1])
        return ('', 0)

    def add_bounty(self, value):
        self.next_bounty_value += value

    def set_bounty_word(self, str, duration=20):
        if str != '':
            self.openBounty[str] = (None, self.next_bounty_value, time.time() + duration)
            self.claimedBounty[str] = []
            self.next_bounty_value = 0

    def set_tutorial_word(self, str, user_id, duration=20):
        self.openBounty[str] = (user_id, 1, time.time() + duration)
        self.claimedBounty[str] = []

    def add_points(self, user_id, display_name, value):
        print('awarding ', display_name.encode('utf-8'), ' ', value, ' points')
        if not self.database.add_user(user_id, display_name, value, 0):
            print('failed adding')
            print('trying updating: ', self.database.add_points_id(user_id, value))

    def incomingMessage(self, c, e):
        def parseTags(l):
            res = {}
            for d in l:
                res[d['key']] = d['value']
            return res

        tags = parseTags(e.tags)
        user_id = int(tags['user-id'])
        display_name = tags['display-name']

        message = e.arguments[0]
        (word, award) = self.check_bounty(message, user_id)
        if word != '':
            self.add_points(user_id, display_name, award)
            self.claimedBounty[word].append(user_id)

    def get_nammer_points(self, user_id):
        res = self.database.get_by_ID(user_id)
        if res == None:
            return 0
        else:
            return res[2]

    def reset_nammer_points(self, user_id):
        return self.database.reset_user_points(user_id)
