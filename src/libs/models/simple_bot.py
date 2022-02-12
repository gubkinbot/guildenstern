import torch
import yaml
import warnings

from os import path as os_path
from transformers import T5ForConditionalGeneration, T5Tokenizer


warnings.filterwarnings('ignore', message='__floordiv__ is deprecated')


class MLChitChat:
    def __init__(self) -> None:
        self.tokenizer = T5Tokenizer.from_pretrained("cointegrated/rut5-small-chitchat")
        self.generator = T5ForConditionalGeneration.from_pretrained("cointegrated/rut5-small-chitchat")
        config_path = os_path.abspath(os_path.join(os_path.dirname(__file__), 'bot_config.yml'))
        self.config = yaml.safe_load(open(config_path))

    def __call__(self, texts) -> dict:
        inputs = self.tokenizer(texts, return_tensors='pt', padding=True)
        with torch.no_grad():
            hypotheses = self.generator.generate(
                **inputs, **self.config
            )

        ans_li = []
        hypotheses = zip(hypotheses.sequences, hypotheses.sequences_scores)
        for tens, score in hypotheses:
            ans_li.append((self.tokenizer.decode(tens, skip_special_tokens=True), score.item()))
        return ans_li
