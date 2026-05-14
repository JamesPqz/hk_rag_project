# from google import genai
#
# # The client gets the API key from the environment variable `GEMINI_API_KEY`.
# client = genai.Client()
#
# response = client.models.generate_content(
#     model="gemini-3-flash-preview", contents="Explain how AI works in a few words"
# )
# print(response.text)


import os
from google.genai import Client

client = Client(api_key=os.getenv("GEMINI_API_KEY"))

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="你好"
)
print(response.text)