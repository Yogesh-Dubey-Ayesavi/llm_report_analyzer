import json
import os

from dotenv import load_dotenv
from flask import Flask, request

from keys import SUPABASE_CLIENT
from report_analyzer import getAnalysisReport
from response_model import ResponseModel

app = Flask(__name__)
load_dotenv()


@app.route('/api', methods=['POST'])
def apiHandler():


    if request.method == 'OPTIONS':
        # Allows GET requests from any origin with the Content-Type
        # header and caches preflight response for an 3600s
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': '3600'
        }

        return ('', 204, headers)

    # Set CORS headers for the main request
    headers = {
        'Access-Control-Allow-Methods': 'POST',
        'Access-Control-Allow-Origin': '*'
    }
    try:
    #    if "apiKey" in request.headers and request.headers.get("apiKey") ==  os.getenv("API_KEY"):
           json = request.get_json();
           data = None
           if "data" in json:
               data = json.get('data')
               return getAnalysisReport(data).markdownContent ,200,headers
           else :
               return "Invalid request",400,headers
    #    else : 
    #        return "Access Forbidden",403,headers        
    except Exception as e:
        print(e)
        return "An error Occured",500,headers
    
    
if __name__ == '__main__':
    app.run(debug=True)


'''
/POST api/?type=views-per-page
/POST api/?type=views-by-day
/POST api/?type=views-per-city-page

'''