from Levenshtein import distance
from nltk import sent_tokenize
import re
import random

if __name__ == '__main__':
    from models.simple_bot import MLChitChat
else:
    from .models.simple_bot import MLChitChat


class MessageHandler:
    def __init__(self) -> None:
        self.dialog_model = MLChitChat()
    
    # обработка сообщений. решение, что, кому и как отправлять
    def analysis(message):
        return None
    
    # чистка сообщений, приведение к одному виду
    def normalization(text):
        return None

    def process(self, question):
        question = self.preprocess(question)

        # обрабатываем правилами
        primitive_phrases = [x.lower() for x in ['Как дела', 'Что делаешь', 'Чем занят', 'Как тебя звать', 'Как звать',
                                                'Как зовут', 'Что нового', 'Давай знакомиться']]
        array_sentences = sent_tokenize(question, language='russian')
        good = []
        bad = []
        for sentence in array_sentences:
            sentence = sentence[0].upper() + sentence[1:] # начинаем новое предложение с заглавной буквы
            if any(distance(sentence.lower(), x) < 4 for x in primitive_phrases): # пересечение со списком примитивных фраз
                bad.append(sentence)
            else:
                good.append(sentence)
        if len(good) > 0:
            good = ' '.join(good) + ' '
        if len(good) == 0:
            good = ''
        if len(bad) == 0:
            bad = ''
        if len(bad) > 0:
            bad = '\n\nСообщение легко перехватит Антон. Ты уверен, что хочешь отправить его?: ' + ' '.join(bad) + ' '
        # если правила не проходят, запускаем модель
        else:
            model_msg = self.dialog_model(question)

            ### kekw

            msg_start = ""
            msg_end = ""
            
            i = 1
            for row in model_msg:
                msg = row[0]
                if msg[-1] == '.':
                    msg = msg[:-1]
                msg_start += f'{str(i)}. ' + msg + "\n\n"
                i += 1
                
            
            ###

            good = '*Выберите, какое из сообщений отправить собеседнику:*\n\n' + str(msg_start+msg_end)

        return self.postprocess(good + bad)

    flag = False # for /test command
    
    

    def impudence(self, message, count_message_in_session = 0) -> list:
        if self.triger_for_show_Anton(message):
            self.flag = False # for /test command

            res = []
            
            model_msg = self.dialog_model(message)

            for row in model_msg:
                msg = row[0]
                if msg[-1] == '.':
                    msg = msg[:-1]
                res.append(str(row[0]))

            return res
        else:
            return None

    def triger_for_show_Anton(self, message):
        return random.randint(1, 5) == 1 or self.flag # <>
    
    def fuckoff(self):
        hi = ['слышь', 'так', 'а ну-ка', 'слушай сюда', 'внимание']
        mr = ['ушлепыш', 'натоптыш', 'мазоль', 'отрыжка', 'макака', 'бот', 'собака', 'тупица']
        go = ['канай отсюда', 'лучше бы ты на салфетке остался', 'убейся', 'заройся', 'отдайся бегемоту', 'завернись в лаваш']
        return random.choice(hi) + ', ' + random.choice(mr) + ', ' + random.choice(go)

    # @staticmethod
    def preprocess(self, question: str) -> str:
        question = question[0].upper() + question[1:] # начинаем новое предложение с заглавной буквы
        question = re.sub(r'!+', '!', question) # удаление дублей в пробелах
        question = re.sub(r'\)+', ')', question) # удаление дублей в пробелах
        question = re.sub(r'\s+', ' ', question) # удаление дублей в пробелах
        question = re.sub(r'(?<=[.,!?:;])(?=[^\s])', r' ', question) # вставка пробелов после знаков препинания
        question = re.sub('\s+(?=[,.!?])', '', question) # удаление пробелов перед знаками препинания
        # пока так, когда появится история сообщений, надо будет переделать
        if question[-1] == '.':
            question = question[:-1]
        question += "\n\n"
        
        return question

    @staticmethod
    def postprocess(answer: str) -> str:
        # заглушка под постобработку
        return answer
