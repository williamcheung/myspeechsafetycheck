from dotenv import load_dotenv
load_dotenv()

import os

from langchain_openai import ChatOpenAI
from openai import RateLimitError
from tenacity import retry, retry_if_exception_type, stop_never, wait_exponential

MIN_WAIT_SECS = 2

llm = ChatOpenAI(temperature=0, api_key=os.getenv('OPENAI_API_KEY'),
                 model=os.getenv('OPENAI_MODEL'), base_url=os.getenv('OPENAI_BASE_URL'),
                 max_tokens=int(os.getenv('OPENAI_MAX_TOKENS')))

@retry(wait=wait_exponential(min=MIN_WAIT_SECS), stop=stop_never, retry=retry_if_exception_type(RateLimitError))
def invoke_llm(prompt: str):
    return llm.invoke(prompt)

llm2 = ChatOpenAI(temperature=0, api_key=os.getenv('OPENAI_API_KEY2'),
                 model=os.getenv('OPENAI_MODEL2'), base_url=os.getenv('OPENAI_BASE_URL2'),
                 max_tokens=int(os.getenv('OPENAI_MAX_TOKENS2')))

@retry(wait=wait_exponential(min=MIN_WAIT_SECS), stop=stop_never, retry=retry_if_exception_type(RateLimitError))
def invoke_llm2(prompt: str):
    return llm2.invoke(prompt)
