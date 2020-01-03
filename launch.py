import sys

import Config
import replybot

if len(sys.argv) == 1:
    print('missing config file argument')
    exit()

config = Config.Config()
if not config.init(sys.argv[1]):
    print('error parsing config file')
    exit()

main = replybot.Main(config)
