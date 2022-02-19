import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification


class ToxicityChecker:
    def __init__(self) -> None:
        model_checkpoint = 'cointegrated/rubert-tiny-toxicity'
        self.tokenizer = AutoTokenizer.from_pretrained(model_checkpoint)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_checkpoint)

        device = "cuda" if torch.cuda.is_available() else "cpu"

        self.model.to(device)

    def __call__(self, text):
        return self.text2toxicity(text, aggregate=True)

    def text2toxicity(self, text, aggregate=True):
        """ Calculate toxicity of a text (if aggregate=True) or a vector of toxicity aspects (if aggregate=False)"""
        with torch.no_grad():
            inputs = self.tokenizer(text, return_tensors='pt', truncation=True, padding=True).to(self.model.device)
            proba = torch.sigmoid(self.model(**inputs).logits).cpu().numpy()
        if isinstance(text, str):
            proba = proba[0]
        if aggregate:
            return 1 - proba.T[0] * (1 - proba.T[-1])
        return proba
