def bool(str):
    return str.lower() == 'true'


class Config:

    def __init__(self):
        pass

    def init(self, file):
        try:
            options = dict()
            for line in open(file):
                if len(line) > 1:
                    p = line.split()
                    options[p[0]] = p[2]

            self.username = options['username']

            self.client_id = options['client_id']
            self.token = options['token']

            self.channel = options['channel']
            self.characterMessageLimit = int(options['characterLimit'])
            self.checkOnline = bool(options['checkOnline'])
            self.checkBanPhrase = bool(options['checkBanPhrase'])
            self.replyToBannedMessage = bool(options['replyToBannedMessage'])
            self.factsFileLocation = options['factsFileLocation']
            self.answersFileLocation = options['answersFileLocation']
            self.questionsFileLocation = options['questionsFileLocation']
            self.jokesFileLocation = options['jokesFileLocation']
            self.namwordsFileLocation = options['namwordsFileLocation']
            self.databaseLocation = options['databaseLocation']
            self.welcomeMessage = options['welcomeMessage']
            self.doWelcomeMessage = bool(options['doWelcomeMessage'])
            self.messageRate = float(options['messageRate'])
            self.defaultNamRate = int(options['defaultNamRate'])

        except:
            return False
        return True
