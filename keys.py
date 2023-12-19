
import os

import supabase
from dotenv import load_dotenv
from supabase import Client, create_client
from supabase.lib.client_options import ClientOptions

load_dotenv()

OPENAI_API_KEY:str = os.getenv("OPENAI_API_KEY")
SUPABASE_CLIENT =  supabase.Client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'),options=ClientOptions(
                headers={
                        # "apikey":os.getenv('SUPABASE_KEY'),
                        "Authorization":"Bearer {}".format(os.getenv("SUPABASE_KEY"))
                }
                ))