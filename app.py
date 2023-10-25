import openai
import json
import streamlit as st
import requests
from bs4 import BeautifulSoup
from googlesearch import search
from dependencies import td, utilities

# you might wanna change theese my deer visitors
captions_path = "captions.json"
prompt_path = 'prompts/new chatAI prompt2.txt'
apikeys_path = 'apikeys.json'
logo_path = r"media\teles logo1-modified.png"

with open(apikeys_path) as config:
    openai.api_key = json.load(config)['openai']

setup_question = """
🔴Which level of setup are you comfortable in undertaking? (note that telescopes with more complex setup procedures
usually perform better.)
"""

with open(captions_path, 'r') as captions_file:
    captions = json.loads(captions_file.read())

col1, col2, col3 = st.columns(3)
with col2:
    st.image(logo_path, width=190)
    st.title("TeleSmart")

experience = st.radio(
    '🔴How would you describe your experience with telescopes?',
    ['beginner', 'intermediate', 'advanced'],
    captions=[captions['beginner_caption'], captions['intermediate_caption'], captions['advanced_caption']],
)

budget = st.number_input("🔴What is your budget(in dollars) for purchasing a telescope?", min_value=0, max_value=20000, value=0)

interest = st.selectbox("🔴What aspect of astronomy interests you the most?",
                        ("planetary", "deep sky", "terrestrial", "solar"))

portability = st.selectbox("🔴Do you require a portable telescope that is easy to transport?",
                           ("yes", "no"))

astrophotography = st.selectbox("🔴Are you interested in astro-photography, capturing images of celestial objects?",
                                ("yes", "no"))

setup = st.radio(setup_question, ["simple", "moderate", "complex"],
                 captions=[captions['simple_caption'], captions['moderate_caption'], captions['complex_caption']])
# ⭕ 🔴
# user_data_labels = ['experience', 'budget', 'interest', 'portable', 'astrophoto', 'setup']

if st.button("Submit"):
    st.write("your data has been submitted successfully")
    user_data_map = {
        'experience': experience,
        'budget': budget,
        'interest': interest,
        'portable': portability,
        'astrophoto': astrophotography,
        'setup': setup
    }

    db_connection = td.TelescopeDatabase()
    telescope_data_map = db_connection.get_telescope_data(user_data_map)

    try:
        telescope_data_map['name'] = utilities.unpack_quotes(telescope_data_map['name'])
        # get response from chat
        system_content = '''
        you are a helpful assistant who is very knowledgeable about all consumer telescopes. you
        also recommend telescopes to users based off of their needs in a informative and a friendly
        manner.
        '''

        with open(prompt_path, 'r') as user_content_file:
            user_content = user_content_file.read().format(**telescope_data_map)

        prompt = [
            {'role': 'system', 'content': system_content},
            {'role': 'user', 'content': user_content}
        ]

        response = openai.ChatCompletion.create(model='gpt-3.5-turbo', messages=prompt, temperature=1).choices[
            0].message.content

        # search image and shops

        telescope_name = telescope_data_map['name']
        image_response = requests.get('https://www.google.com/search', params={'q': telescope_name, 'tbm': 'isch'})

        image_soup = BeautifulSoup(image_response.text, 'html.parser')
        images = image_soup.find_all('img')
        image_urls = [image['src'] for image in images]
        image_url = image_urls[1]

        shop_links = [link for link in search(telescope_name + 'buy', stop=2, pause=3)]

        shop_section = '\n\nwhere to buy:'
        for link in shop_links:
            shop_section += f'\n\n{link}'

        # show response
        st.image(image_url, caption=telescope_name, width=300)
        st.write(response + shop_section)

    except TypeError:
        st.write(
            "Apologies, but we couldn't find a telescope matching your interests. We are deeply sorry for the inconvenience caused")
