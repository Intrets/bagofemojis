import os
import pickle
import random


def cleanWords(str):
    return ''.join(c for c in str.lower() if c.isalpha() or c == ' ')


class Markov:

    def __init__(self, path, ruleN=2):
        self.ruleN = ruleN
        self.rules = [dict() for _ in range(ruleN + 1)]
        self.startWords = []

        startPath = path + '.starts.pickle'
        if os.path.isfile(startPath):
            with open(startPath, 'rb') as file:
                self.startWords = pickle.load(file)
        else:
            for line in open(path, encoding="utf-8-sig"):
                if len(line) < 3:
                    continue
                # cleanedLine = ''[c for c in line.lower() if c.isalpha() or c == ' ']
                line = line.split(maxsplit=1)
                if len(line) == 0:
                    continue
                self.startWords.append(line[0])
            with open(startPath, 'wb') as file:
                pickle.dump(self.startWords, file)

        for context in range(1, self.ruleN + 1):
            pickledPath = path + '.' + str(context) + '.pickle'
            if os.path.isfile(pickledPath):
                with open(pickledPath, 'rb') as pickleFile:
                    self.rules[context] = pickle.load(pickleFile)
            else:
                for line in open(path, encoding="utf-8-sig"):
                    if len(line) < 3:
                        continue

                    # cleanedLine = ''[c for c in line.lower() if c.isalpha() or c == ' ']
                    line = line.split()
                    if len(line) == 0:
                        continue
                    # print(cleanedLine)

                    self.startWords.append(line[0])

                    rule = self.rules[context]
                    index = context
                    for word in line[context:]:
                        # key = line[index - context:index].
                        key = cleanWords(' '.join(line[index - context:index]))
                        if key in rule:
                            rule[key].append(word)
                        else:
                            rule[key] = [word]
                        index += 1
                        pass
                with open(pickledPath, 'wb') as pickleFile:
                    pickle.dump(self.rules[context], pickleFile)

    def makeStart(self, words, N):
        if len(words) == 0:
            words.append(random.choice(self.startWords))
            return self.makeStart(words, N)

        if len(words) >= N:
            return words

        context = len(words)

        try:
            key = ' '.join(words)
            newword = random.choice(self.rules[context][cleanWords(key)])
            words.append(newword)
        except KeyError:
            return words

        return self.makeStart(words, N)

    def gen(self, start="", startingN=5):
        if type(start) == list:
            start = ' '.join(start)
        startingN = min(startingN, self.ruleN)

        oldwords = start.split()
        oldwords = self.makeStart(oldwords, startingN)

        string = ' '.join(oldwords)

        oldwords = oldwords[-self.ruleN:]

        if ' '.join(oldwords) not in self.rules[startingN]:
            oldwords = self.makeStart([], startingN)
            string = ' '.join(oldwords)

        string = string[0].upper() + string[1:]

        # if oldwords is None:
        #     oldwords = random.choice(list(self.rules[startingN].keys())).split(' ')  # random starting words
        #     string = ' '.join(oldwords)
        # else:
        #     string = oldwords
        #     oldwords = oldwords.split()
        #     if (len(oldwords) < startingN):
        #         for context in range(len(oldwords), startingN + 1):
        #             try:
        #                 key = ' '.join(oldwords)
        #                 newword = random.choice(self.rules[context][key])
        #                 string += ' ' + newword
        #
        #                 for word in range(len(oldwords)):
        #                     oldwords[word] = oldwords[(word + 1) % len(oldwords)]
        #                 oldwords[-1] = newword
        #
        #             except KeyError:
        #                 break

        while string[-1] != '.' and string[-1] != '!' and string[-1] != '?':
            # for i in range(length):
            try:
                key = ' '.join(oldwords)
                newword = random.choice(self.rules[startingN][cleanWords(key)])
                string += ' ' + newword

                for word in range(len(oldwords)):
                    oldwords[word] = oldwords[(word + 1) % len(oldwords)]
                oldwords[-1] = newword

            except KeyError:
                return string
        return string
