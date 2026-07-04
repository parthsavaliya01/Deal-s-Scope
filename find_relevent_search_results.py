from langchain.prompts import PromptTemplate
from langchain.prompts.few_shot import FewShotPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
import os

from dotenv import load_dotenv

load_dotenv()

llm3 = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.7,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)

def load_data_for_few_shot_template(file_name):
  base_dir = os.path.dirname(__file__)
  path = os.path.join(base_dir, 'Data for Find Relevent Descriptions', file_name)
  with open(path, 'r', encoding='utf-8') as file:
    data = file.read()
  return data

# First, create list of few shot examples.
def get_examples():

  croma_samsung_s25_ultra = load_data_for_few_shot_template('croma samsung galaxy s25 ultra.txt')
  flipkart_samsung_s25_ultra = load_data_for_few_shot_template('flipkart samsung galaxy s25 ultra.txt')
  data_samsung_s25_ultra = croma_samsung_s25_ultra + '\n\n' + flipkart_samsung_s25_ultra

  flipkart_iphone_16 = load_data_for_few_shot_template('flipkart iphone 16.txt')
  croma_iphone_16 = load_data_for_few_shot_template('croma iphone 16.txt')
  data_iphone_16 = flipkart_iphone_16 + '\n\n' + croma_iphone_16

  examples = [
    {'data': f'{data_samsung_s25_ultra}', 'query': 'I want to buy samsung s25 ultra 256gb', 'answer': 'Croma Search Result 1,Croma Search Result 3,Croma Search Result 4,Croma Search Result 6,Flipkart Search Result 2,Flipkart Search Result 4,Flipkart Search Result 8,Flipkart Search Result 9'},
    {'data': f'{data_iphone_16}', 'query': 'my friend is looking for iphone 16 with pink color', 'answer': 'Flipkart Search Result 6,Croma Search Result 7,Croma Search Result 9'},
    {'data': f'{data_iphone_16}', 'query': 'check for iphone 16 plus 256 gb', 'answer': 'Flipkart Search Result 10,Flipkart Search Result 15,Flipkart Search Result 17,Croma Search Result 17'},
    {'data': f'{data_samsung_s25_ultra}', 'query': 'looking for samsung s25 ultra 128 gb', 'answer': 'None'},
    {'data': f'{data_samsung_s25_ultra}', 'query': 'samsung s25 ultra black', 'answer': 'Croma Search Result 1,Croma Search Result 2,Flipkart Search Result 1,Flipkart Search Result 9,Flipkart Search Result 11'},
    {'data': f'{data_samsung_s25_ultra}', 'query': 'can you check for samsung s25 ultra gray 512 gb', 'answer': 'Croma Search Result 0,Flipkart Search Result 0'},
    {'data': f'{data_iphone_16}', 'query': 'find best deal on iphone 16 1 tb with white color only.', 'answer': 'None'}
  ]

  return examples

def get_chain(llm):
  example_formatter_template = '''
    data: {data}
    query: {query}
    answer: {answer}
  '''

  example_prompt = PromptTemplate(
      input_variables = ['data', 'query', 'answer'],
      template = example_formatter_template
  )

  few_shot_prompt = FewShotPromptTemplate(
      # This are the examples that we want to insert into the prompt.
      examples = get_examples(),

      # This is how we want to format the examples when we insert them into the prompt.
      example_prompt = example_prompt,

      # The prefix is some text that goes before the examples in the prompt.
      # Usually, this consists of intructions.
      prefix = """You are an intelligent assistant that reads product listings from different e-commerce platforms and selects all the results that match the user's query.

        Each product listing block contains results from Flipkart and Croma. Your task is to identify the relevant search results based on user intent — such as storage, color, model variant, or price.

        If none of the search results match the user's query, respond with 'None'.

        Provide your final answer as a comma-separated list of matching result identifiers like 'Flipkart Search Result 4' or 'Croma Search Result 2'.

        You are allowed to only generate comma-separated list of matching result identifiers or 'None',

        Do not generate any other text. (Strictly Follow)

        Below are a few examples:""",


      # The suffix is some text that goes after the examples in the prompt.
      # Usually, this is where the user input will go
      suffix = 'data: {data}\nquery: {query}\nanswer: ',

      # The input variables are the variables that the overall prompt expects.
      input_variables = ['data', 'query'],

      # The example_separator is the string we will use to join the prefix, examples
      example_separator = '\n'
    )

  return few_shot_prompt

def get_relevent_search_results_based_on_description(data : str, query : str) -> list:
  # If LLM usage is disabled or API key missing, use a lightweight local heuristic matcher
  if os.getenv('DISABLE_LLM', '').lower() in ('1', 'true', 'yes') or not os.getenv('GOOGLE_API_KEY'):
    # data is expected to be lines like: '\'Flipkart Search Result 0\' : <desc>,\n' joined
    entries = [e.strip() for e in data.split(',\n') if e.strip()]
    results = []
    import re

    # normalize and extract tokens from query
    q_tokens = re.findall(r"\w+", query.lower())
    stopwords = set(['find','best','deal','looking','for','check','can','you','the','and','with','only','my','i','want','to','buy','please','look'])
    q_tokens = [t for t in q_tokens if t not in stopwords]
    if not q_tokens:
      return ['None']

    for entry in entries:
      try:
        # entry format: '\'Flipkart Search Result 0\' : description'
        parts = entry.split(':', 1)
        if len(parts) < 2:
          continue
        key = parts[0].strip().strip("'")
        desc = parts[1].lower()

        # token matching: consider token matched if present in desc
        match_count = 0
        for t in q_tokens:
          if t in desc:
            match_count += 1
          else:
            # allow numeric storage matches like '256' matching '256gb' in desc
            if re.search(rf"\b{re.escape(t)}(gb|tb)?\b", desc):
              match_count += 1

        # include if at least half of query tokens match (heuristic)
        if match_count >= max(1, (len(q_tokens) + 1) // 2):
          results.append(key)
      except Exception:
        continue

    if not results:
      return ['None']
    return results

  few_shot_prompt = get_chain(llm3)
  prompt_value = few_shot_prompt.format_prompt(data=data, query=query)
  text = prompt_value.to_string() if hasattr(prompt_value, 'to_string') else str(prompt_value)
  response = llm3.predict(text)
  relevent_results = response.split('\n')[0]
  
  return relevent_results.split(',')

def get_indexes_of_relevent_search_result(filtered_results : list) -> dict:
  all_set = True
  for i in filtered_results:
    if i.find('Croma Search Result') != 0 and i.find('Flipkart Search Result') != 0:
      all_set = False
      break
  if all_set:
    dict_of_index = {'Croma' : [], 'Flipkart' : []}
    for i in filtered_results:
      li = i.split()
      if li[0] == 'Croma':
        dict_of_index['Croma'].append(int(li[-1]))
      else:
        dict_of_index['Flipkart'].append(int(li[-1]))
    return dict_of_index
  else:
    raise Exception('Unexpected output of find_relevent_result_chain please try again!!')
