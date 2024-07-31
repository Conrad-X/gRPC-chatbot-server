import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from typing_extensions import override
from openai import AssistantEventHandler


_MODEL = "gpt-4o-mini"

load_dotenv()
client = OpenAI()


class EventHandler(AssistantEventHandler):
    @override
    def on_text_created(self, text) -> None:
        print(f"assistant > ", end="", flush=True)

    @override
    def on_text_delta(self, delta, snapshot):
        print(delta.value, end="", flush=True)

    @override
    def on_event(self, event):
        # Retrieve events that are denoted with 'requires_action'
        # since these will have our tool_calls
        if event.event == "thread.run.requires_action":
            # Retrieve the run ID from the event data
            run_id = event.data.id
            self.handle_requires_action(event.data, run_id)

    def handle_requires_action(self, data, run_id):
        tool_outputs = []

        for tool in data.required_action.submit_tool_outputs.tool_calls:
            if tool.function.name == "log_leave_request":
                # extract arguments from the tool_call
                args = json.loads(tool.function.arguments)
                leave_status = log_leave_request(args)
                tool_outputs.append({"tool_call_id": tool.id, "output": leave_status})

        # Submit all tool_outputs at the same time
        self.submit_tool_outputs(tool_outputs, run_id)

    def submit_tool_outputs(self, tool_outputs, run_id):
        # Use the submit_tool_outputs_stream helper
        with client.beta.threads.runs.submit_tool_outputs_stream(
            thread_id=self.current_run.thread_id,
            run_id=self.current_run.id,
            tool_outputs=tool_outputs,
            event_handler=EventHandler(),
        ) as stream:
            stream.until_done()


class ConradAssitant:
    assistant_id = os.environ["ASSISTANT_V1"]
    thread_id = os.environ["THREAD_ID"]

    def __init__(self):
        self.client = client
        self.model = _MODEL
        self.assistant = None
        self.thread = None
        self.run = None
        self.summary = None

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
            with self.client.beta.threads.runs.stream(
                thread_id=self.thread.id,
                assistant_id=self.assistant.id,
                instructions=instructions,
                event_handler=EventHandler(),
            ) as stream:
                stream.until_done()


def main():
    ca = ConradAssitant()

    while True:
        text = input("\nme > ")
        ca.add_message_to_thread(role="user", content=text)
        ca.run_assistant(instructions=None)


main()
