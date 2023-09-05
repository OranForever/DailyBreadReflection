import streamlit as st
import pandas as pd
import os
import openai
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from langchain.chains import SequentialChain
from dotenv import load_dotenv, find_dotenv
from datetime import datetime
from newsdataapi import NewsDataApiClient
from elevenlabs import clone, generate, play, set_api_key
from elevenlabs.api import History
_ = load_dotenv(find_dotenv()) # read local .env file
# elevenlabs api key = 64d7cfe7ed3cae3cc80bef44b593a558
set_api_key("64d7cfe7ed3cae3cc80bef44b593a558")

api = NewsDataApiClient(apikey="pub_27051eca379954fd03e84e06490e34bf9c5fc")
# key = pub_27051eca379954fd03e84e06490e34bf9c5fc
# bible api key = 3e407cc38336eb8ff24e6305a2fa8b3b
# bible book = 685d1470fe4d5c3b-01
st.header("Daily Bread Reflection")

#Retrieve bible passage
today = datetime.today()
apidate = today.strftime("%Y-%m-%d")
url = "https://github.com/OranForever/DailyBreadReflection/blob/5110dd29f0a5f7b57c287fb60a1c27410026ae58/bas_short_2022-2023.csv?raw=true"
df = pd.read_csv(url,index_col=0)
new_date = df[apidate][0]

#extract data from news data api
response = api.news_api(country="ca", category="top", language="en")
PROMPT = response["results"][0]["title"]
content = response["results"][0]["description"]

#establish llm
llm = ChatOpenAI(temperature=0.9, openai_api_key="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")


openai.api_key = "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"

#st.image(image["data"][0]["url"])

def get_completion(prompt, model="gpt-3.5-turbo", temperature=0):
    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=temperature,
    )
    return response.choices[0].message["content"]

today_date = datetime.today().strftime('%m-%d')
#chains
first_prompt = ChatPromptTemplate.from_template(
   "Create a new short story less than 2000 characters, based on the daily gospel reading {new_date} with the news description: {content}"
)
chain_one = LLMChain(llm=llm, prompt=first_prompt,
                     output_key="new_story"
                    )
second_prompt = ChatPromptTemplate.from_template(
   "Write a reflection on {new_story} within 6 sentences and make sure to create a newline after every sentence"
)
# chain 2
chain_two = LLMChain(llm=llm, prompt=second_prompt,
                     output_key="reflection"
                    )
third_prompt = ChatPromptTemplate.from_template(
    "Write a short prompt within 200 characters that will accurately portray the following story into an image generated by openai: {reflection}"
)
chain_three = LLMChain(llm=llm, prompt=third_prompt,
                       output_key="image")

overall_chain = SequentialChain(
    chains=[chain_one, chain_two, chain_three],
    input_variables=["new_date", "content"],
    output_variables=["new_story", "reflection", "image"],
    verbose=True
)
stories = overall_chain({"new_date":new_date, "content":content})
image = openai.Image.create(
    prompt=stories["image"],
    n=1,
    size="256x256",
)
audio = generate(
    text=stories["reflection"],
    voice="Clyde",
    model='eleven_multilingual_v1'
)
st.text("gospel reading: " + new_date)
st.text("news content: " + content)
st.markdown("Generated story: " + stories["new_story"])
st.image(image["data"][0]["url"])
st.markdown(stories["reflection"])
st.audio(audio)
