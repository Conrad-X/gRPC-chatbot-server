import grpc
from concurrent import futures
import protoc.chatApp_pb2_grpc as chatApp_pb2_grpc
import protoc.chatApp_pb2 as chatApp_pb2
from api._openAI.getCompletion import getChatCompletion
from api._openAI.assistant import ConradAssitant

ca = ConradAssitant()


class ChatAppServicer(chatApp_pb2_grpc.ChatAppServicer):
    def SendQuery(self, request_iterator, context):
        for request in request_iterator:
            # print("--- Recieved From Client: " + request.prompt + " ----")
            # tokens = getChatCompletion(request.prompt)
            # for token in tokens:
            #     response = chatApp_pb2.Response(text=token)
            #     yield response

            ca.add_message_to_thread(role="user", content=request.prompt)
            response_tokens = ca.run_assistant(instructions=None)
            for tokens in response_tokens:
                response = chatApp_pb2.Response(text=tokens)
                yield response


def server():
    port = "52002"
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=2))
    chatApp_pb2_grpc.add_ChatAppServicer_to_server(ChatAppServicer(), server)
    server.add_insecure_port("localhost:" + port)
    server.start()
    print("Server Up, listening on port " + port)
    server.wait_for_termination()


if __name__ == "__main__":
    server()
