from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
import os
import re

from dotenv import load_dotenv

load_dotenv()

llm4 = ChatGoogleGenerativeAI(
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


def extract_first_price(text: str) -> int | None:
    if not text:
        return None
    prices = re.findall(r'₹[\d,]+', text)
    if not prices:
        return None
    price_text = prices[0]
    try:
        return int(price_text.replace('₹', '').replace(',', ''))
    except ValueError:
        return None


def reduce_filtered_data(filtered_data: str, max_items: int = 8) -> str:
    lines = [line.strip() for line in filtered_data.split('\n') if line.strip()]
    if len(lines) <= max_items:
        return '\n'.join(lines)

    priced_records = []
    for line in lines:
        price_value = extract_first_price(line)
        if price_value is None:
            price_value = 10**12
        priced_records.append((price_value, line))

    priced_records.sort(key=lambda x: x[0])
    selected = [record[1] for record in priced_records[:max_items]]
    return '\n'.join(selected)


def get_prompt():
  return PromptTemplate(
      input_variables = ['filtered_data','query'],
      template="""
You are DealScope, an intelligent shopping assistant. You are given *already filtered* product listings based on the user's query. Do **not** match product features again — this has already been done by a previous step.

Your task is to:
1. From the filtered product listings, **find the result(s) with the lowest price**.
2. By default, for each of the lowest-price results, respond with the following format:

**Product Name:** 
\n
**Platform Name:**
\n  
**Price:**
\n  
**Link:**

However, if the user query explicitly asks to limit the output (e.g., "only show link" or "only platform name and link"), then tailor your response accordingly.

Additional instructions:
- If **multiple results have the same lowest price**, include *all* such results.
- If the **same lowest price** is found on different platforms (e.g., Flipkart and Croma), include results from **all** platforms.
- If the filtered data is 'None' or empty, respond with:
"Sorry, the product matching your query was not found. DealScope performs strict filtering based on product names and specifications. Please recheck your request and try again."

Here is the filtered data:
{filtered_data}

User Query:
{query}

Provide your output below:
"""
)

def get_filtered_data(index_di : dict, flipkart_data: list, croma_data : list) -> str:
  filtered_flipkart_data = ''
  filtered_croma_data = ''

  flipkart_index = index_di['Flipkart']
  croma_index = index_di['Croma']

  for i in flipkart_index:
    filtered_flipkart_data += str(flipkart_data[i]) + '\n'
  
  for i in croma_index:
    filtered_croma_data += str(croma_data[i]) + '\n'

  return filtered_flipkart_data + '\n' + filtered_croma_data

def generate_product_name_based_final_resposne(filtered_data, query):
  # If the environment requests LLM disabled, or there's no API key, use local summarizer
  use_llm = True
  env_disable = os.getenv('DISABLE_LLM', '').lower()
  if env_disable in ('1', 'true', 'yes'):
    use_llm = False
  if not os.getenv('GOOGLE_API_KEY'):
    use_llm = False

  reduced_data = reduce_filtered_data(filtered_data, max_items=8)

  def local_summarize(data_str: str) -> str:
    # Parse each record (one per line) and extract Name, Price, Link
    lines = [l for l in data_str.split('\n') if l.strip()]
    items = []
    price_re = re.compile(r'₹[\d,]+')
    for rec in lines:
      # Try extract Name
      name = None
      link = None
      price = None
      try:
        # Name : ... patterns
        m = re.search(r"Name\s*:\s*(.*?)($|Price\s*:|Features\s*:|Link\s*:)", rec)
        if m:
          name = m.group(1).strip().strip('\"')
      except Exception:
        name = None
      try:
        m = price_re.search(rec)
        if m:
          price = int(m.group(0).replace('₹', '').replace(',', ''))
      except Exception:
        price = None
      try:
        m = re.search(r"Link\s*:\s*(https?://[^\s\']+)", rec)
        if m:
          link = m.group(1).strip()
      except Exception:
        link = None

      items.append({'name': name or 'Unknown', 'price': price, 'link': link or 'Link not available', 'raw': rec})

    # choose lowest price(s)
    priced = [it for it in items if it['price'] is not None]
    if not priced:
      # fallback: return raw items
      return '\n\n'.join([it['raw'] for it in items[:8]])
    priced.sort(key=lambda x: x['price'])
    lowest = priced[0]['price']
    chosen = [it for it in priced if it['price'] == lowest]

    out_lines = []
    for it in chosen:
      out_lines.append(f"**Product Name:** {it['name']}")
      out_lines.append(f"**Platform Name:** (Detected from listing)")
      out_lines.append(f"**Price:** ₹{it['price']:,}")
      out_lines.append(f"**Link:** {it['link']}\n")

    return '\n'.join(out_lines)

  if not use_llm:
    return local_summarize(reduced_data)

  try:
    return run_llm_prompt(llm4, get_prompt(), {'filtered_data': reduced_data, 'query': query})
  except Exception as e:
    # On LLM failure, return local summary instead of error
    fallback = local_summarize(reduced_data)
    return f"⚠️ AI summary unavailable due to error: {str(e)}\n\nShowing best candidate deals instead:\n\n{fallback}"

