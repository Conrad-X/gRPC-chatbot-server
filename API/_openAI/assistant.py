from openai import OpenAI
import tiktoken
from dotenv import load_dotenv
from typing_extensions import override
from openai import AssistantEventHandler

_MODEL = "gpt-4o-mini"

load_dotenv()
client = OpenAI()
encoding = tiktoken.encoding_for_model(_MODEL)


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


class EventHandler(AssistantEventHandler):
    @override
    def on_text_created(self, text) -> None:
        print(f"\nassistant > ", end="", flush=True)

    @override
    def on_text_delta(self, delta, snapshot):
        print(delta.value, end="", flush=True)

    def on_tool_call_created(self, tool_call):
        print(f"\nassistant > {tool_call.type}\n", flush=True)

    def on_tool_call_delta(self, delta, snapshot):
        if delta.type == "code_interpreter":
            if delta.code_interpreter.input:
                print(delta.code_interpreter.input, end="", flush=True)
            if delta.code_interpreter.outputs:
                print(f"\n\noutput >", flush=True)
                for output in delta.code_interpreter.outputs:
                    if output.type == "logs":
                        print(f"\n{output.logs}", flush=True)


class ConradAssitant:
    assistant_id = "asst_i1ni4xVblTLM0ITk6jHNEF4G"
    thread_id = "thread_0jZGzNJTT6eNK4RMXjx6QZWB"

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
    ca.create_assistant(
        name="Conrad Assistant - Saim",
        instructions='You are Conrad Labs assistant to help employees with the queries regarding Conrad Labs.\
                    --- Response Instructions ---\
                    1- You should always answer in two sentences max. \
                    2- Use a paragraph format to answer.\
                    3- Be precise in your answer.\
                    4- Do not contain any asterisk or inverted commas (single or double) or quotations in your response.\
                    5- If you do not understand the user\'s query, respond "Sorry, I am unable to answer your query, please clarify your query with regard to Conrad Labs"\
                    6- If a user asks a query that does not relate to Conrad Labs, respond "Sorry, I am unable to answer your query, please clarify your query with regard to Conrad Labs"',
        tools=None,
    )

    #     tools=[
    #         {
    #             "type": "function",
    #             "function": {
    #                 "name": "get_song_title",
    #                 "description": "Returns a superhero name based on the integer parameter 'songnum'",
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

    # while True:
    #     text = input("\nEnter your prompt: ")

    #     ca.add_message_to_thread(role="user", content=text)

    text = input("\nEnter your prompt: ")
    ca.add_message_to_thread(role="user", content=text)
    ca.run_assistant(instructions=None)


main()
