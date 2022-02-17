from Levenshtein import distance
from nltk import sent_tokenize
import re
import random
import pandas as pd

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
    
    

    def impudence(self, message, count_message_in_session) -> list:
        if ((count_message_in_session > 10 and 
            self.triger_for_show_Anton(message)) or 
            self.flag):
            self.flag = False # for /test command

            res = []
            
            model_msg = self.dialog_model(message)

            for row in model_msg:
                res.append(self.preprocess(str(row[0])))

            return res
        else:
            return None

    def triger_for_show_Anton(self, message):
        return random.randint(1, 10) == 1 # <>
    
    def fuckoff(self):
        hi = ['слышь', 'так', 'а ну-ка', 'слушай сюда', 'внимание']
        mr = ['ушлепыш', 'натоптыш', 'мазоль', 'отрыжка', 'макака', 'бот', 'собака', 'тупица']
        go = ['канай отсюда', 'лучше бы ты на салфетке остался', 'убейся', 'заройся', 'отдайся бегемоту', 'завернись в лаваш']
        return random.choice(hi) + ', ' + random.choice(mr) + ', ' + random.choice(go)

    def addeddot(self, message):
        if message[-1] not in [')', '(', '!', '?', '.', ',']:
            return message + '.'
        else:
            return message

    def dialogue_analysis(self, data, user_id, session_id_in, count_msg):
        print(count_msg)
        if (not count_msg) or count_msg < 3:
            return "<>"

        '''
        минимально: скорость ответа и средняя и максимальная длина сообщений
        dataset - данные из лога в формате: id, user_id, session_id, message, time_send, type, grade
        user_id_1 - user_id пользователя, которому отправили сообщение
        user_id_2 - user_id пользователя, отправившего сообщение
        '''
        
        # <> db должна быть при инициализации
        dataset = pd.DataFrame(data, columns=['id', 'user_id', 'session_id', 'message', 'time_send', 'type',	'grade'])
        
        # исключение ненужных сессий и сообщений бота
        dataset = dataset[(dataset.session_id == session_id_in) & (dataset.type == 'original')]
        # порядковые номера с учетом последовательных сообщений
        dataset.loc[:,'UID'] = dataset.user_id.diff().apply(lambda x: 0 if x == 0 else 1).cumsum()
        # добавление точки. это больше для того, чтобы потом передавать модели нормальную историю
        dataset['message'] = dataset.message.apply(self.addeddot)
        # кручу-верчу
        aggdata = dataset.pivot_table(index='UID', values=['message', 'user_id', 'time_send', 'session_id'],
                    aggfunc={'message': ' '.join, 'user_id': 'mean', 'time_send': 'max', 'session_id': 'count'})
        history = '<eom>'.join(list(aggdata.tail(5).message))
        # максимальная длина сообщений с учетом 20 процентов сверху. для генерации ответа
        max_length_for_a_bot = dataset[dataset.user_id == user_id].message.apply(len).max() * 1.2
        # средняя длина сообщений для оценки содержательности
        mean_length = dataset[dataset.user_id == user_id].message.apply(len).mean()
        # подсчет задержки
        aggdata['delay'] = pd.to_datetime(aggdata['time_send']).diff().dt.total_seconds()
        # подсчет длины сообщений
        aggdata['len'] = aggdata.message.apply(len)
        # подсчет скорости ответа
        aggdata['intensity'] = aggdata['len'] / aggdata['delay']
        # исключение сообщений собеседника
        aggdata = aggdata[aggdata.user_id == user_id]
        # и все
        intensity = aggdata['intensity'].median()

        len_score = mean_length / 2.5

        if mean_length < 5:
            len_score = 2
        elif mean_length > 25:
            len_score = 10
        
        int_score = intensity * 2

        if intensity < 0.5:
            int_score = 1
        elif intensity > 2.5:
            int_score = 5

        score = len_score + int_score

        return f'MAX L = {max_length_for_a_bot}\nMEAN L = {mean_length}\nV = {intensity}\nSCORE = {score}.\n\n{history}'

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
        # question += "\n\n"
        
        return question

    @staticmethod
    def postprocess(answer: str) -> str:
        # заглушка под постобработку
        return answer
