import torch
import yaml
from transformers import T5ForConditionalGeneration, T5Tokenizer

class MLChitChat:
    def __init__(self) -> None:
        self.tokenizer = T5Tokenizer.from_pretrained("cointegrated/rut5-small-chitchat")
        self.generator = T5ForConditionalGeneration.from_pretrained("cointegrated/rut5-small-chitchat")
        self.config = yaml.safe_load(open('bot_config.yml'))

    def __call__(self, texts) -> dict:
        ret_seq = self.config['num_return_sequences']
        inputs = self.tokenizer(texts, return_tensors='pt', padding=True)
        with torch.no_grad():
            hypotheses = self.generator.generate(
                **inputs, **self.config
            )

        ans_di = {}
        tmp_li = []
        hypotheses = zip(hypotheses.sequences, hypotheses.sequences_scores)
        for i, (tens, score) in enumerate(hypotheses):
            tmp_li.append((self.tokenizer.decode(tens, skip_special_tokens=True), score.item()))
            if (i+1) % ret_seq == 0:
                ans_di.update({(i+1)//ret_seq:tmp_li})
                tmp_li = []
        return ans_di