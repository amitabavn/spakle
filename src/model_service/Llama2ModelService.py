import torch
from llama import Llama2Model


class Llama2ModelService:
    def __init__(self, model_name):
        model_path = model_name.value
        self.tokenizer = torch.hub.load('facebookresearch/llama', 'llama2_tokenizer')
        self.model = Llama2Model.from_pretrained(model_path)

    def get_reply(self, prompt):
        input_ids = self.tokenizer.encode(prompt, return_tensors='pt')
        output = self.model.generate(input_ids)
        reply = self.tokenizer.decode(output[0], skip_special_tokens=True)
        return reply
