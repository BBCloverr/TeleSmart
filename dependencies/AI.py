import openai
import json

apikeys_file_path = 'apikeys.json'

with open(apikeys_file_path, 'r') as config:
    openai.api_key = json.load(config)["openai"]


def clean_text(unclean_text, impure_literals_list):
    cleaned_text = unclean_text
    for literal in impure_literals_list:
        cleaned_text = cleaned_text.replace(literal, '')
    return cleaned_text


def get_user_details(telescope_details, show_response=False):
    prompts_path = 'prompts/get user data/'
    with open(prompts_path + 'system.txt', 'r') as system:
        system_text = system.read()
    with open(prompts_path + 'user.txt', 'r') as user:
        user_text = user.read()

    prompt = [
        {"role": "system", "content": system_text},
        {"role": "user", "content": user_text.format(**telescope_details)}
    ]

    raw_response = openai.ChatCompletion.create(model='gpt-3.5-turbo', messages=prompt, temperature=0).choices[0].message.content

    if show_response:
        print(raw_response)

    response_dictionary_string = raw_response[raw_response.find('{'):raw_response.find('}')+1]
    return json.loads(response_dictionary_string)
