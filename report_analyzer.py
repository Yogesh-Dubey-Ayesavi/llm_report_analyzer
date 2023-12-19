import asyncio
import io
import os
from http import HTTPStatus

import requests
from dotenv import load_dotenv
from langchain.agents import (AgentExecutor, AgentType, Tool, create_sql_agent,
                              initialize_agent, load_tools)
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain.chains import APIChain, ConversationalRetrievalChain
from langchain.chains.llm import LLMChain
from langchain.chains.openai_functions import create_structured_output_chain
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import PDFPlumberLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.llms import OpenAI
from langchain.prompts.prompt import PromptTemplate
from langchain.schema.document import Document
from langchain.sql_database import SQLDatabase
from langchain.text_splitter import CharacterTextSplitter
from PyPDF2 import PdfFileReader, PdfFileWriter, PdfReader

from keys import OPENAI_API_KEY, SUPABASE_CLIENT
from response_model import ResponseModel


def getFileNameOnReportId(reportId:str)->str:
       data = SUPABASE_CLIENT.from_('reports').select('uri').eq("id",reportId).execute()
       print(data)
       return data.data[0]["uri"]

def downloadSupabaseFile(path:str):
                client = SUPABASE_CLIENT
                response =  client.storage.from_("reports").download(path)
                return io.BytesIO(response)                

def getReportContext(pdf_bytes)->str:
       context :str = ""
                # Initialize PyPDF2 PdfFileReader
       pdf_reader = PdfReader(pdf_bytes)
            
            # Iterate through the pages of the PDF
       for index in range(0,len(pdf_reader.pages)):
                page = pdf_reader.pages[index]
                context = context + '\n' +  page.extract_text()

       return context


def make_post_request(dir:str):
    # URL for the POST request
    url = 'https://asia-south1-esgedu-740d2.cloudfunctions.net/git-api?type=custom&dir={}&name=cop-agreement'.format(dir)

    try:
        # Making a POST request with the requests library
        response = requests.post(url)

        # Check if the request was successful (status code 2xx)
        if response.status_code // 100 == 2:
            # Parse the JSON response
            return response.json()

            # Process the received data
            print('Response data:', response_data)
        else:
            print(f'Request failed with status code {response.status_code}')

    except requests.exceptions.RequestException as e:
        print(f'Request failed with exception: {e}')

           

def getAlignmentContext(dir:str):
      data = make_post_request(dir)
      print(data.get("content",""))
      return data.get("content","")



def getAnalysisReport(fname:str,dir:str)->ResponseModel:
    pdf_bytes = downloadSupabaseFile(fname)
    context = getAlignmentContext(dir)
    reportContext = getReportContext(pdf_bytes)

    template = """ 
    Question: {question}
    Answer: 
    """
    print(template)
    prompt = PromptTemplate(template=template,input_variables=['question'])
    chatLLM = ChatOpenAI(temperature=0.1,openai_api_key=OPENAI_API_KEY)
    reportAnalyzerChain = create_structured_output_chain(ResponseModel,chatLLM,prompt=prompt,verbose = False)
    responseModel : ResponseModel =  reportAnalyzerChain.run(  
      '''
       Context : {},
       Provided Report : {}
       question : {}
       '''.format(context,reportContext,"Analyze the report, Think step by step and reward points on the scale of 1 to 100, tell me ")
       )
    return responseModel




