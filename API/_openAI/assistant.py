import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from typing_extensions import override
from openai import AssistantEventHandler
from api.simplistc.functions import post_leave
import tiktoken

_MODEL = "gpt-4o-mini"

load_dotenv()
client = OpenAI()
encoding = tiktoken.encoding_for_model(_MODEL)


def log_leave_request(args):
    if post_leave(args) == 200:
        return "Success"
    return "Error Occured"


class ConradAssitant:
    assistant_id = os.environ["ASSISTANT_V1"]
    thread_id = os.environ["THREAD_ID"]

    def __init__(self):
        self.client = client
        self.model = _MODEL
        self.assistant = None
        self.thread = None
        self.run = None

        if ConradAssitant.assistant_id:
            self.assistant = self.client.beta.assistants.retrieve(
                assistant_id=ConradAssitant.assistant_id
            )

        if ConradAssitant.thread_id:
            self.thread = self.client.beta.threads.retrieve(
                thread_id=ConradAssitant.thread_id
            )

    def create_assistant(self, name, instructions, tools):
        if not self.assistant:
            assistant = self.client.beta.assistants.create(
                name=name, instructions=instructions, tools=tools, model=self.model
            )
            ConradAssitant.assistant_id = assistant.id
            self.assistant = assistant
            print(f"Assistant ID: {self.assistant.id}")

    def create_thread(self):
        if not self.thread:
            thread = self.client.beta.threads.create()
            ConradAssitant.thread_id = thread.id
            self.thread = thread
            print(f"Thread ID: {self.thread.id}")

    def add_message_to_thread(self, role, content):
        if self.thread:
            self.client.beta.threads.messages.create(
                thread_id=self.thread.id, role=role, content=content
            )

    def run_assistant(self, instructions):
        if self.assistant and self.thread:
            responseText = ""
            run_stream = self.client.beta.threads.runs.stream(
                thread_id=self.thread.id,
                assistant_id=self.assistant.id,
                instructions=instructions,
            )
            response_stream = self.eventHandler(run_stream)
            for text_deltas in response_stream:
                responseText += text_deltas
                if len(encoding.encode(responseText)) > 6:
                    yield responseText
                    responseText = ""
            if responseText != "":
                yield responseText

    def eventHandler(self, run_stream):
        with run_stream as stream:
            for event in stream:
                if event.event == "thread.run.created":
                    self.run = event.data.id
                elif event.event == "thread.message.delta":
                    print(event.data.delta.content[0].text.value, end="", flush=True)
                    yield event.data.delta.content[0].text.value
                elif event.event == "thread.run.requires_action":
                    tool_outputs = []
                    for (
                        tool
                    ) in event.data.required_action.submit_tool_outputs.tool_calls:
                        if tool.function.name == "log_leave_request":
                            arguments = json.loads(tool.function.arguments)
                            leave_status = log_leave_request(arguments)
                            tool_outputs.append(
                                {"tool_call_id": tool.id, "output": leave_status}
                            )
                        submit_tool_stream = (
                            client.beta.threads.runs.submit_tool_outputs_stream(
                                thread_id=self.thread.id,
                                run_id=self.run,
                                tool_outputs=tool_outputs,
                            )
                        )
                        for text in self.eventHandler(submit_tool_stream):
                            yield text


# def main():
#     ca = ConradAssitant()

#     # client.beta.threads.runs.cancel(
#     #     thread_id=ca.thread_id, run_id="run_AcdCG35EwLKaixxNqyRTbdN1"
#     # )

#     while True:
#         text = input("\nme > ")
#         ca.add_message_to_thread(role="user", content=text)
#         gen = ca.run_assistant(instructions=None)
#         for text in gen:
#             for chars in text:
#                 print(chars, end="", flush=True)


# main()
