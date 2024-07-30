import os
import json
from openai import OpenAI
import tiktoken
from dotenv import load_dotenv
from typing_extensions import override
from openai import AssistantEventHandler


_MODEL = "gpt-4o-mini"

load_dotenv()
client = OpenAI()
# encoding = tiktoken.encoding_for_model(_MODEL)


def get_song_title(n):
    """
    Returns a song title from 2010 to 2024 based on the integer parameter n.
    The function uses the integer to index into a list of popular song titles from these years.

    Args:
    n (int): The index for selecting a song title.

    Returns:
    str: The title of the song.
    """
    # List of popular song titles from 2010 to 2024
    songs = [
        "Rolling in the Deep - Adele (2011)",
        "Uptown Funk - Mark Ronson ft. Bruno Mars (2014)",
        "Shape of You - Ed Sheeran (2017)",
        "Blinding Lights - The Weeknd (2019)",
        "Old Town Road - Lil Nas X ft. Billy Ray Cyrus (2019)",
        "Levitating - Dua Lipa (2020)",
        "drivers license - Olivia Rodrigo (2021)",
        "Good 4 U - Olivia Rodrigo (2021)",
        "Stay - The Kid LAROI & Justin Bieber (2021)",
        "As It Was - Harry Styles (2022)",
        "Anti-Hero - Taylor Swift (2022)",
        "Flowers - Miley Cyrus (2023)",
        "Kill Bill - SZA (2023)",
        "Bad Habit - Steve Lacy (2023)",
        "Calm Down - Rema & Selena Gomez (2024)",
    ]

    # Use modulo to handle out-of-bounds indices
    return songs[n % len(songs)]


# class EventHandler(AssistantEventHandler):
#     @override
#     def on_text_created(self, text) -> None:
#         print(f"\nassistant > ", end="", flush=True)

#     @override
#     def on_text_delta(self, delta, snapshot):
#         print(delta.value, end="", flush=True)

#     def on_tool_call_created(self, tool_call):
#         print(f"\nassistant > {tool_call.type}\n", flush=True)

#     def on_tool_call_delta(self, delta, snapshot):
#         if delta.type == "code_interpreter":
#             if delta.code_interpreter.input:
#                 print(delta.code_interpreter.input, end="", flush=True)
#             if delta.code_interpreter.outputs:
#                 print(f"\n\noutput >", flush=True)
#                 for output in delta.code_interpreter.outputs:
#                     if output.type == "logs":
#                         print(f"\n{output.logs}", flush=True)


class EventHandler(AssistantEventHandler):
    @override
    def on_event(self, event):
        # Retrieve events that are denoted with 'requires_action'
        # since these will have our tool_calls
        if event.event == "thread.run.requires_action":
            run_id = event.data.id  # Retrieve the run ID from the event data
            self.handle_requires_action(event.data, run_id)

    def handle_requires_action(self, data, run_id):
        tool_outputs = []

        for tool in data.required_action.submit_tool_outputs.tool_calls:
            if tool.function.name == "get_song_title":
                args = json.loads(tool.function.arguments)
                song_title = get_song_title(args["songnum"])
                tool_outputs.append({"tool_call_id": tool.id, "output": song_title})

        # Submit all tool_outputs at the same time
        # print(tool_outputs)
        self.submit_tool_outputs(tool_outputs, run_id)

    def submit_tool_outputs(self, tool_outputs, run_id):
        # Use the submit_tool_outputs_stream helper
        with client.beta.threads.runs.submit_tool_outputs_stream(
            thread_id=self.current_run.thread_id,
            run_id=self.current_run.id,
            tool_outputs=tool_outputs,
            event_handler=EventHandler(),
        ) as stream:
            for text in stream.text_deltas:
                print(text, end="", flush=True)
            print()


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
            print("-------------------")
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

    # ca.create_assistant(
    #     name="Conrad Assistant - Saim",
    #     instructions='You are Conrad Labs assistant to help employees with the queries regarding Conrad Labs.\n\
    #       --- Response Instructions ---\n\
    #         1- You should always answer in two sentences max.\n\
    #           2- Use a paragraph format to answer.\n\
    #             3- Be precise in your answer.\n\
    #               5- If you do not understand the user\'s query, respond "Sorry, I am unable to answer your query, please clarify your query with regard to Conrad Labs"\n\
    #                 6- If a user asks a query that does not relate to Conrad Labs, respond "Sorry, I am unable to answer your query, please clarify your query with regard to Conrad Labs"',
    #     tools=[
    #         {
    #             "type": "function",
    #             "function": {
    #                 "name": "get_song_title",
    #                 "description": "Returns a song name based on the integer parameter 'songnum'",
    #                 "parameters": {
    #                     "type": "object",
    #                     "properties": {
    #                         "songnum": {
    #                             "type": "integer",
    #                             "description": "An integer for indexing",
    #                         },
    #                     },
    #                     "required": ["songnum"],
    #                 },
    #             },
    #         }
    #     ],
    # )
    # ca.create_thread()

    # client.beta.threads.runs.cancel(
    #     "run_0Df0IDlNBpjnp0P6fUsU23R8", thread_id=ca.thread_id
    # )

    text = input("\nEnter your prompt: ")
    ca.add_message_to_thread(role="user", content=text)
    ca.run_assistant(instructions=None)


main()
