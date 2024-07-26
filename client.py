import grpc
import time
from protoc import chatApp_pb2
from protoc import chatApp_pb2_grpc
from API._google.speechToText import main
 
start = 0.0

def getClientQueries():
    global start

    while True:
        input_type = input("1- Audio\n2-Text\nChoice: ")
        if(input_type == "1"):
            userPrompt = main()
        else:
            userPrompt = input("Enter your prompt: ")

        start = time.time()
        request = chatApp_pb2.Query(prompt = userPrompt)
        yield request

def client():
    global start
    print("Welcome to the ChatApp powered by OpenAI")
    with grpc.insecure_channel("localhost:52002") as channel:
        stub = chatApp_pb2_grpc.ChatAppStub(channel)
        responses = stub.SendQuery(getClientQueries())
        for response in responses:
            print(response.text, end="", flush=True)
            
        endTime = time.time() - start
        print("Response took: {0} s.".format(endTime))

if __name__ == "__main__":
    client()