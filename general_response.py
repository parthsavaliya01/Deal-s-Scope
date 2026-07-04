from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

from dotenv import load_dotenv

load_dotenv()

llm0 = ChatGoogleGenerativeAI(
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
            template="""
You are DealScope, an AI-powered chatbot.

Your primary job is to:
- Find the best deals from Flipkart and Croma based on specific product queries.
- Compare prices and match product specifications.
- List all lowest-priced options across platforms.

But you can also handle general-purpose queries like:
- Writing Python code
- Explaining concepts
- Answering general knowledge questions

Now follow this logic:
If the query is asking about you (e.g., "Who are you?", "What can you do?", "What tasks do you perform?", "What is your role?" etc.), respond with:
"Hi! I'm DealScope — an AI assistant that helps users find the best product deals across Flipkart and Croma based on product name and specs for smartphones, TVs, and laptops. Besides that, I can also handle general queries like writing code, explaining things, or answering questions. Feel free to ask me anything!"

If the query is about anything else, just respond to it accordingly:
Query: {query}
"""
)

def generate_general_response(query):
    return run_llm_prompt(llm0, get_prompt(), {'query': query})