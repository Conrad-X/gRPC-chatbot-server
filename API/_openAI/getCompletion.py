from openai import OpenAI
import tiktoken
from dotenv import load_dotenv

_MODEL = "gpt-4o-mini"

load_dotenv()
client = OpenAI()
encoding = tiktoken.encoding_for_model(_MODEL)


def getChatCompletion(prompt):

    responseText = ""
    completion = client.chat.completions.create(
                model=_MODEL,
                messages=[
                    {"role": "system", "content": "You are a helpful chatbot that speaks like scripture."},
                    {"role": "user", "content": prompt}
                ],
                stream=True
                )
    for chunk in completion:
        if chunk.choices[0].delta.content != None:
            responseText += chunk.choices[0].delta.content
        if(len(encoding.encode(responseText)) > 5):
            yield responseText
            responseText = ""
    responseText += "\n"
    yield responseText