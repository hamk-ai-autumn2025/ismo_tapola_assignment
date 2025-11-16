import os
from google import genai

client = genai.Client()

while True:
    word = input("Word?")
    if not word:
        break
    prompt = f"""Provide a dictionary entry for the word '{word}' in JSON format.

If the word is in English, provide the Finnish translation as the 'word', definition in English, synonyms and antonyms in Finnish, examples in Finnish.

If the word is in Finnish, provide the word as is, definition in English, synonyms and antonyms in Finnish, examples in Finnish.

Output only valid JSON with keys: word (string), definition (string), synonyms (array of strings), antonyms (array of strings), examples (array of strings).

No other text."""
    response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
    json_output = response.text.strip()
    print(json_output)