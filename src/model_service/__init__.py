from Llama2ModelService import Llama2ModelService
from Llama2Model import Llama2Model

if __name__ == '__main__':
    assistant = Llama2ModelService(Llama2Model.LLAMA2_7B_CHAT)
    user_input = input("Enter your prompt: ")
    reply = assistant.get_reply(user_input)
    print(reply)