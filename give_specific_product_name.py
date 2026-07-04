from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

from dotenv import load_dotenv

load_dotenv()

llm1 = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.7,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)

def run_llm_prompt(llm, prompt, inputs):
    prompt_value = prompt.format_prompt(**inputs)
    text = prompt_value.to_string() if hasattr(prompt_value, 'to_string') else str(prompt_value)
    return llm.predict(text)


def get_prompt():
    return PromptTemplate(
            input_variables = ['query'],
            template = '''User has entered below prompt which does not contains any product name.

User Prompt: "{query}"            
            
Tell user to enter specific product name such that product data can be extracted and you can provide best deal on that specefic product.
            '''
        )


def ask_for_specific_product_name(query):
    return run_llm_prompt(llm1, get_prompt(), {'query': query})
