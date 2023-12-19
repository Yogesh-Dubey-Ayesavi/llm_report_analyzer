import asyncio
import io
import os
from http import HTTPStatus

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

def getAlignmentContext():
       return 'This will be context'


def getAnalysisReport(fname)->ResponseModel:
    pdf_bytes = downloadSupabaseFile(fname)
    context = getAlignmentContext()
    reportContext = getReportContext(pdf_bytes)

    template = """ 
    Question: {question}
    Answer: 
    """
    print(template)
    prompt = PromptTemplate(template=template,input_variables=['question'])
    chatLLM = ChatOpenAI(temperature=0.1,openai_api_key=OPENAI_API_KEY)
    reportAnalyzerChain = create_structured_output_chain(ResponseModel,chatLLM,prompt=prompt,verbose = True)
    responseModel : ResponseModel =  reportAnalyzerChain.run(  
            '''
Context : {},
Provided Report : {}
question : {}
'''.format(context,reportContext,"Analyze the report, Think step by step")

    )
    print(responseModel)


getAnalysisReport('public/doc.pdf')








     
       