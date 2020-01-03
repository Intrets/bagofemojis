import time


def valid_command(str: str, list: list, requires_start_message, cap_important=True):
    if requires_start_message:
        return starts_with_list(str, list, cap_important)
    else:
        for b in list:
            if b in str:
                return True
        return False


def starts_with_list(str: str, list: list, cap_important=True):
    if not cap_important:
        for b in list:
            if str.lower().split(' ')[0] == b.lower():
                return True
    else:
        for b in list:
            if str.split(' ', maxsplit=1)[0] == b:
                return True
    return False


class Command:
    def __init__(self, callback, command
                 , user_cooldown=5, command_cooldown=2
                 , requires_global_cooldown=True, requires_user_cooldown=True
                 , id_verification=lambda x: True, requires_start_message=True, additional_args=()):
        self.callback = callback
        self.command = command
        self.user_cooldown = user_cooldown
        self.command_cooldown = command_cooldown
        self.requires_global_cooldown = requires_global_cooldown
        self.requires_user_cooldown = requires_user_cooldown
        self.additional_args = additional_args
        self.id_verification = id_verification
        self.requires_start_message = requires_start_message


class CommandHandler:

    def __init__(self):
        self.command_list = []
        self.command_cooldowns = []
        self.user_cooldowns = dict()

    def add_command(self, command):
        self.command_list.append(command)
        self.command_cooldowns.append(0)

    def run_commands(self, message: str, user_id: int, display_name: str):
        # TODO: use dict
        for i, c in enumerate(self.command_list):
            if valid_command(message, c.command, c.requires_start_message) and \
                    c.id_verification(user_id) and \
                    ((not c.requires_user_cooldown) or (user_id not in self.user_cooldowns) or self.user_cooldowns[
                        user_id] < time.time()) and \
                    ((not c.requires_global_cooldown) or self.command_cooldowns[i] < time.time()):
                c.callback(message, user_id, display_name, *c.additional_args)
                self.user_cooldowns[user_id] = c.user_cooldown + time.time()
                self.command_cooldowns[i] = c.command_cooldown + time.time()
