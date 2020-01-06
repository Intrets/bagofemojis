import time

import DataBase


def check_nam(message):
    return 'NaM' in message.split(' ')


def clean_nam_sentence(str):
    return ''.join(str.split()).lower()


class BountyHandler:
    def __init__(self, config):
        self.database = DataBase.DataBase(config.databaseLocation)

        self.openBounty = dict()
        self.claimedBounty = dict()

    def clean_old_bounties(self):
        to_delete = []
        for word, (value, time_limit) in self.openBounty.items():
            if time_limit < time.time():
                to_delete.append(word)
        for do in to_delete:
            del self.openBounty[do]
            del self.claimedBounty[do]

    def check_bounty(self, message, user_id):
        cleaned_message = clean_nam_sentence(message)
        if cleaned_message in self.openBounty and check_nam(message):
            bounty = self.openBounty[cleaned_message]
            if not (bounty[1] > time.time()):
                return ('', 0)
            if user_id in self.claimedBounty[cleaned_message]:
                return ('', 0)

            return (cleaned_message, bounty[0])
        return ('', 0)

    def set_bounty_word(self, str, points, duration=20):
        if str != '':
            self.clean_old_bounties()

            str = clean_nam_sentence(str)
            if str in self.openBounty:
                old_bounty_value = self.openBounty[str][0]
                self.openBounty[str] = (points + old_bounty_value, time.time() + duration)
            else:
                self.openBounty[str] = (points, time.time() + duration)
            self.claimedBounty[str] = set()

    def add_points(self, user_id, display_name, value):
        print('awarding ', display_name.encode('utf-8'), ' ', value, ' points')
        if not self.database.add_user(user_id, display_name, value, 0):
            print('failed adding')
            print('trying updating: ', self.database.add_points_id(user_id, value))

    def incomingMessage(self, connection, type, source, target, message, tags):
        user_id = int(tags['user-id'])
        display_name = tags['display-name']

        (word, award) = self.check_bounty(message, user_id)
        if word != '':
            self.add_points(user_id, display_name, award)
            self.claimedBounty[word].add(user_id)

    def get_nammer_points(self, user_id):
        res = self.database.get_by_ID(user_id)
        if res == None:
            return 0
        else:
            return res[2]

    def reset_nammer_points(self, user_id):
        return self.database.reset_user_points(user_id)
