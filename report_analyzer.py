import asyncio
import io
import os
from http import HTTPStatus

import markdown
import pdfkit
import requests
from dotenv import load_dotenv
from langchain.agents import (AgentExecutor, AgentType, Tool, create_sql_agent,
                              initialize_agent, load_tools)
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain.chains import (APIChain, ConversationalRetrievalChain,
                              ConversationChain)
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

from keys import OPENAI_API_KEY, SUPABASE_CLIENT
from prompt import fill_company_details, format_prompts_as_string
from response_model import ResponseModel


def extract(obj):
    obj.pop('question')
    obj.pop('type')
    return obj

def getInstitutionDetails(id:str):
    data =  SUPABASE_CLIENT.from_("institutions").select('*').eq('id',id).single().execute()
    return data.data

def getAnalysisReport(data):
    companyDetails = getInstitutionDetails(data["id"])
    responseList = data['qa']
    template = """
{question}

**Output Format:**
Generate the report in Markdown format.
    """ + '\n' + format_prompts_as_string(responseList) + '\n'+ fill_company_details(companyDetails["name"],companyDetails["website"],companyDetails["city"],companyDetails["industry"])
    prompt = PromptTemplate(template=template,input_variables=['question'])
    chatLLM = ChatOpenAI(temperature=0.1,openai_api_key=OPENAI_API_KEY)
    reportAnalyzerChain = create_structured_output_chain(ResponseModel,chatLLM,prompt=prompt,verbose = False)
    response =  reportAnalyzerChain.run("""
    - Provide a detailed analysis of the company's ESG approach.
- Identify areas of improvement based on the questionnaire responses.
- If there are numerical figures or data, present them in tabular form.
- Include recommendations on how the company can enhance its ESG practices.
""")
    SUPABASE_CLIENT.from_("institution_assesments").insert(  list(map(extract, data['qa']))).execute()
    mail = SUPABASE_CLIENT.from_("users").select('emailxz_id').eq("id",data.get("id")).execute().data[0].get("email_id")
    print(mail)
    html_content = markdown.markdown(response.markdownContent)
    requests.post('https://asia-south1-lakshya-202.cloudfunctions.net/send-mail-esg', json={
        "subject":"Report Generation",
        "sender":[mail],
        "body":html_content
    })   
    return response
 