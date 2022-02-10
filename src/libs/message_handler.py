from Levenshtein import distance
from nltk import sent_tokenize
import re
if __name__ == '__main__':
    from models.simple_bot import MLChitChat
else:
    from .models.simple_bot import MLChitChat


class MessageHandler:
    def __init__(self) -> None:
        self.dialog_model = MLChitChat()

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

            for row in model_msg:
                msg_start += row[0] + "\n\n"
                msg_end += str(row[1]) + "\n"
            
            ###

            good = str(msg_start+msg_end) + str(model_msg)

        return self.postprocess(good + bad)

    @staticmethod
    def preprocess(question: str) -> str:
        question = re.sub(r'\s+', ' ', question) # удаление дублей в пробелах
        question = re.sub(r'(?<=[.,!?:;])(?=[^\s])', r' ', question) # вставка пробелов после знаков препинания
        question = re.sub('\s+(?=[,.!?])', '', question) # удаление пробелов перед знаками препинания
        # пока так, когда появится история сообщений, надо будет переделать
        question += "\n\n"
        
        return question

    @staticmethod
    def postprocess(answer: str) -> str:
        # заглушка под постобработку
        return answer
