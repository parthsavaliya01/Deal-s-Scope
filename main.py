import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
import os
import time
from dotenv import load_dotenv

load_dotenv()

from extract_product_name import getProductName
from general_response import generate_general_response, get_prompt
from give_specific_product_name import ask_for_specific_product_name
from scrape_flipkart_data import get_flipkart_data
from scrape_croma_data import get_croma_data
from find_relevent_search_results import get_relevent_search_results_based_on_description, get_indexes_of_relevent_search_result
from generate_response_from_relevent_results import get_filtered_data, generate_product_name_based_final_resposne, reduce_filtered_data

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

# Initialize session state for caching
if 'last_query' not in st.session_state:
    st.session_state.last_query = None
    st.session_state.last_results = None

st.set_page_config(page_title="DealScope", layout="wide")
st.title('🛍️ DealScope: AI-Powered Best Deal Finder')
st.markdown("Find the best deals on your favorite products across Flipkart and Croma")

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.7,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)

query = st.text_input(label='🔍 Enter Product Name:', placeholder='e.g., iPhone 16, Samsung Galaxy S25...')

if query:
    # Check if we have cached results for this query
    if st.session_state.last_query == query and st.session_state.last_results:
        results = st.session_state.last_results
        st.info("✓ Using cached results")
    else:
        results = None

    if not results:
        # Create containers for status updates
        status_container = st.container()
        progress_bar = st.progress(0)
        
        try:
            with status_container:
                # Step 1: Product Name Extraction
                status_text = st.empty()
                status_text.info("🔄 Step 1/4: Analyzing your request...")
                progress_bar.progress(20)
                
                product_name = getProductName(query)

                if product_name == 'No Product Name Detected':
                    status_text.warning("⚠️ No specific product detected in your query")
                    st.markdown("---")
                    st.markdown("### 💭 General Response:")
                    response = generate_general_response(query)
                    st.markdown(response)
                    
                elif product_name == 'Give Specefic Product Name':
                    status_text.warning("⚠️ Please be more specific about the product")
                    st.markdown("---")
                    st.markdown("### 💡 Suggestion:")
                    response = ask_for_specific_product_name(query)
                    st.markdown(response)
                    
                else:
                    # Step 2: Scrape Flipkart
                    status_text.info(f"🔄 Step 2/4: Searching Flipkart for '{product_name}'...")
                    progress_bar.progress(40)
                    flipkart_list = get_flipkart_data(product_name)
                    
                    # Step 3: Scrape Croma
                    status_text.info(f"🔄 Step 3/4: Searching Croma for '{product_name}'...")
                    progress_bar.progress(60)
                    croma_list = get_croma_data(product_name)
                    
                    # Step 4: Filter & Generate Response
                    status_text.info("🔄 Step 4/4: Analyzing products and generating response...")
                    progress_bar.progress(80)
                    
                    description_data = flipkart_list[0] + '\n' + croma_list[0]
                    filtered_results = get_relevent_search_results_based_on_description(description_data, query)
                    
                    if filtered_results[0] == 'None':
                        filtered_data = 'None'
                    else:
                        filtered_data_index_dict = get_indexes_of_relevent_search_result(filtered_results)
                        filtered_data = get_filtered_data(filtered_data_index_dict, flipkart_list[1], croma_list[1])
                    
                    progress_bar.progress(100)
                    status_text.success("✅ Analysis complete! Here are your results:")
                    
                    # Display results in nice format
                    st.markdown("---")
                    
                    # Create columns for product summary
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Flipkart Results", len(flipkart_list[1]))
                    with col2:
                        st.metric("Croma Results", len(croma_list[1]))
                    
                    st.markdown("---")
                    st.markdown("### 🏆 Best Deals for You:")
                    st.markdown("")
                    
                    # If LLM disabled or unavailable, the response may be generated locally
                    response = generate_product_name_based_final_resposne(filtered_data, query)
                    if os.getenv('DISABLE_LLM', '').lower() in ('1', 'true', 'yes') or not os.getenv('GOOGLE_API_KEY'):
                        st.info('Note: using local summarizer (LLM disabled or API key missing). Results are computed locally without Gemini.')
                    if not response or response.strip() == '':
                        st.warning('The AI returned no summary; showing best candidate deals directly.')
                        response = reduce_filtered_data(filtered_data, max_items=8)
                    st.markdown(response)
                    
                    # Cache the results
                    st.session_state.last_query = query
                    st.session_state.last_results = True
                    
        except Exception as e:
            progress_bar.progress(0)
            error_msg = str(e)
            
            if "quota" in error_msg.lower() or "429" in error_msg:
                st.error("""
                ⚠️ **API Quota Exceeded**
                
                The Google Gemini API free tier limit (20 requests/day) has been reached.
                
                **Solutions:**
                1. **Upgrade to Gemini API Plan** - Get higher quotas and paid tier support
                2. **Try again tomorrow** - Quota resets daily
                3. **Use alternative API key** - Add a new API key with available quota
                
                Please visit: [Google AI Studio](https://aistudio.google.com) to manage your quotas.
                """)
            elif "API key" in error_msg:
                st.error("❌ **API Key Error**: Please check your GOOGLE_API_KEY in the .env file")
            else:
                st.error(f"❌ **Error**: {error_msg[:200]}...")
                st.write("Please try again or contact support if the issue persists.")

