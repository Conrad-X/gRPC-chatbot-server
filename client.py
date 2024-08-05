import grpc
from protoc import chatApp_pb2
from protoc import chatApp_pb2_grpc
from api._google.speechToText import get_speech_prompt
from api._google.textToSpeech import textToSpeech


def getClientQueries():

    while True:
        input_type = input("1- Audio\n2-Text\nChoice: ")
        if input_type == "1":
            userPrompt = get_speech_prompt()
        else:
            userPrompt = input("Enter your prompt: ")
        request = chatApp_pb2.Query(prompt=userPrompt)
        yield request


def client():
    global start
    print("Welcome to the ChatApp powered by OpenAI")
    with grpc.insecure_channel("localhost:52002") as channel:
        stub = chatApp_pb2_grpc.ChatAppStub(channel)
        responses = stub.SendQuery(getClientQueries())
        for response in responses:
            print(response.text, end="", flush=True)
            textToSpeech(response.text)


if __name__ == "__main__":
    client()
