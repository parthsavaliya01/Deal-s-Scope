from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts.few_shot import FewShotPromptTemplate

import os

from dotenv import load_dotenv

load_dotenv()

llm2 = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.7,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)

# First, create list of few shot examples.
def get_examples():

  examples = [
    {'prompt': 'I want to buy iphone 16 white color with 256 GB RAM.', 'Product Name': 'iphone 16 white 256 GB'},
    {'prompt': 'give me information about iphone 14 pro max.', 'Product Name': 'iphone 14 pro max'},
    {'prompt': 'Suggest me a Redmi note 13 pro back cover', 'Product Name': 'Redmi note 13 pro back cover'},
    {'prompt': 'Suggest me a Wind', 'Product Name': 'No Product Name Detected'},
    {'prompt': 'looking for HP Victus intel 13th Generation', 'Product Name': 'HP Victus intel 13th Generation'},
    {'prompt': 'buying HP Victus Gaming Ryzen 5500U', 'Product Name': 'HP Victus Gaming HP Victus Gaming Ryzen 5500U'},
    {'prompt': 'College Bag', 'Product Name': 'Give Specefic Product Name'},
    {'prompt': 'Zebronics Juke BAR 9552 with Dolby Audio', 'Product Name': 'Zebronics Juke BAR 9552 with Dolby Audio'},
    {'prompt': 'Find best deal for Lavie Sport 47cm Osprey 28 litres laptop backpack', 'Product Name': 'Lavie Sport 47cm Osprey 28 litres laptop backpack'},
    {'prompt': 'Hello, How are you?', 'Product Name': 'No Product Name Detected'},
    {'prompt': 'write python code to swap 2 numbers', 'Product Name': 'No Product Name Detected'},
    {'prompt': 'tell me which number is greater, 2 or 3', 'Product Name': 'No Product Name Detected'},
    {'prompt': 'I am going to buy iphone find best deal on samsung.', 'Product Name': 'Give Specefic Product Name'},
    {'prompt': 'Which Zebronics speakers deal is best for me?', 'Product Name': 'Give Specefic Product Name'},
    {'prompt': 'Which Samsung S25 Ultra 12 GB RAM deal is best for me?', 'Product Name': 'Samsung S25 Ultra 12 GB RAM'},
    {'prompt': 'I am looking for Nothing smartphone.', 'Product Name': 'Give Specefic Product Name'},
    {'prompt': 'I am searching for OPPO smartphone.', 'Product Name': 'Give Specefic Product Name'},
    {'prompt': 'Give me best deal on ASUS Laptop.', 'Product Name': 'Give Specefic Product Name'},
    {'prompt': 'Mac book.', 'Product Name': 'Give Specefic Product Name'},
    {'prompt': 'finding a best android TV.', 'Product Name': 'Give Specefic Product Name'},
  ]

  return examples

def get_chain(llm):

  # Next, we specify the template to format the examples we have provided.
  # We use the `PromptTemplate` class for this.

  example_formatter_template = '''
    Prompt: {prompt}
    Product Name: {Product Name}
  '''
  example_prompt = PromptTemplate(
      input_variables = ['prompt', 'Product Name'],
      template = example_formatter_template
  )

  # Finally, we create the `FewShotPromptTemplate` Object.

  few_shot_prompt = FewShotPromptTemplate(
      # This are the examples that we want to insert into the prompt.
      examples = get_examples(),

      # This is how we want to format the examples when we insert them into the prompt.
      example_prompt = example_prompt,

      # The prefix is some text that goes before the examples in the prompt.
      # Usually, this consists of intructions.
      prefix = 'Find out Product Name in prompt\n Just give answer to my prompt do not generate any single word other than Product Name',

      # The suffix is some text that goes after the examples in the prompt.
      # Usually, this is where the user input will go
      suffix = 'Prompt: {input}\nProduct Name:',

      # The input variables are the variables that the overall prompt expects.
      input_variables = ['input'],

      # The example_separator is the string we will use to join the prefix, examples
      example_separator = '\n'
    )

  return few_shot_prompt

def getProductName(prompt):
  # Use local heuristic when LLM disabled or API key missing
  if os.getenv('DISABLE_LLM', '').lower() in ('1', 'true', 'yes') or not os.getenv('GOOGLE_API_KEY'):
    import re
    q = prompt.lower().strip()
    # quick checks for non-product conversational prompts
    conversational = ['how are you', 'hello', 'write code', 'tell me', 'which number', 'swap 2 numbers']
    for phrase in conversational:
      if phrase in q:
        return 'No Product Name Detected'

    # try to extract brand-based product phrases
    brands = r"iphone|samsung|redmi|oneplus|oppo|vivo|realme|mi|hp|dell|lenovo|asus|macbook|zebronics|lavie|pixel|nothing|google"
    m = re.search(rf"(?i)\b({brands})\b[\w\s\-\./#]*", prompt)
    if m:
      # return the substring starting at brand to end, trimmed
      s = prompt[m.start():].strip()
      # truncate at common sentence delimiters
      s = re.split(r'[\.,;\?\!]', s)[0].strip()
      return s

    # fallback: return top content words (remove stopwords)
    tokens = re.findall(r"\w+", prompt)
    stop = set(['find','best','deal','looking','for','check','can','you','the','and','with','only','my','i','want','to','please','look','give','me','which','is','a'])
    tokens = [t for t in tokens if t.lower() not in stop]
    if not tokens:
      return 'No Product Name Detected'
    # return up to first 6 tokens as product name
    return ' '.join(tokens[:6])

  few_shot_prompt = get_chain(llm2)
  prompt_value = few_shot_prompt.format_prompt(input=prompt)
  text = prompt_value.to_string() if hasattr(prompt_value, 'to_string') else str(prompt_value)
  response = llm2.predict(text)
  product_name = response.split('\n')[0]
  return product_name
