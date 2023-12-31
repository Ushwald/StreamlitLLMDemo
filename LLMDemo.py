# Import os to set API key


import os

# Import OpenAI as main LLM service

from langchain.llms import OpenAI
import openai

from langchain.embeddings import OpenAIEmbeddings
from langchain.embeddings.sentence_transformer import SentenceTransformerEmbeddings

# Bring in streamlit for UI/app interface

import streamlit as st



# Import PDF document loaders...there's other ones as well!

from langchain.document_loaders import PyPDFLoader

# Import chroma as the vector store 

from langchain.vectorstores import Chroma



# Import vector store stuff

from langchain.agents.agent_toolkits import (

    create_vectorstore_agent,

    VectorStoreToolkit,

    VectorStoreInfo

)



# Set APIkey for OpenAI Service

# Can sub this out for other LLM providers

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())



# Create instance of OpenAI LLM

llm = OpenAI(temperature=0.1, verbose=True)

embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")




# Create and load PDF Loader

loader = PyPDFLoader('NIWA2022.pdf')

# Split pages from pdf 

pages = loader.load_and_split()

# Load documents into vector database aka ChromaDB

store = Chroma.from_documents(pages, embeddings, collection_name='annualreport')



# Create vectorstore info object - metadata repo?

vectorstore_info = VectorStoreInfo(

    name="annual_report",

    description="a NIWA annual report as a pdf",

    vectorstore=store

)

# Convert the document store into a langchain toolkit

toolkit = VectorStoreToolkit(vectorstore_info=vectorstore_info)



# Add the toolkit to an end-to-end LC

agent_executor = create_vectorstore_agent(

    llm=llm,

    toolkit=toolkit,

    verbose=True

)

st.title('🦜🔗  NIWA-expert bot')

# Create a text input box for the user

prompt = st.text_input('Input your prompt here')



# If the user hits enter

if prompt:

    # Then pass the prompt to the LLM

    #response = agent_executor.run(prompt)

    docs = store.similarity_search(prompt)

    # print results
    #print(docs[0].page_content)
    completion = openai.ChatCompletion.create(
      model="gpt-3.5-turbo",
    messages = [{"role": "system", "content" : "You are ChatGPT, a large language model trained by OpenAI. Answer as concisely as possible.\nKnowledge cutoff: 2021-09-01\nCurrent date: 2023-03-02"},
    {"role": "user", "content" : "How are you?"},
    {"role": "assistant", "content" : "I am doing well"},
    {"role": "user", "content" : "Read the following: {}.\nnow reply to the following prompt: {}".format(docs[0].page_content,prompt)}]
    )


    # ...and write it out to the screen

    #st.write(response)
    st.write(completion['choices'][0]['message']['content'])



    # With a streamlit expander  

    with st.expander('Document Similarity Search'):

        # Find the relevant pages

        search = store.similarity_search_with_score(prompt) 

        # Write out the first 

        st.write(search[0][0].page_content) 


