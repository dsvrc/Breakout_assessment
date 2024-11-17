import requests
from bs4 import BeautifulSoup
import pandas as pd
import streamlit as st
from groq import Groq
import os
import time
from io import StringIO
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pickle
import json

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

st.title("Web Scraping and Analysis Tool")

st.sidebar.header("API Configuration")

if 'groq_key' not in st.session_state:
    st.session_state.groq_key = ''
if 'serp_key' not in st.session_state:
    st.session_state.serp_key = ''
if 'google_creds' not in st.session_state:
    st.session_state.google_creds = None

groq_api_key = st.sidebar.text_input(
    "Enter GROQ API Key",
    type="password",
    value=st.session_state.groq_key,
    help="Enter your GROQ API key for LLM processing"
)

serp_api_key = st.sidebar.text_input(
    "Enter SERP API Key",
    type="password",
    value=st.session_state.serp_key,
    help="Enter your SERP API key for web search"
)

st.session_state.groq_key = groq_api_key
st.session_state.serp_key = serp_api_key

def LLM_result(prompt, content, max_retries=3):
    client = Groq(api_key=st.session_state.groq_key)
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        'role': 'system',
                        'content': content,
                    },
                    {
                        'role': 'user',
                        'content': "Extract these from given content" + prompt + "Provide a concise and direct response. Do not include follow-up questions or additional offers.",
                    },
                ],
                model="llama3-8b-8192",
                stream=False,
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            retry_count += 1
            if retry_count == max_retries:
                st.error(f"Failed to get LLM response after {max_retries} attempts: {str(e)}")
                return "Error: Unable to process content"
            time.sleep(2)  # Wait before retrying

def get_google_creds():
    creds = None
    if st.session_state.google_creds:
        creds = Credentials.from_authorized_user_info(json.loads(st.session_state.google_creds))
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            st.sidebar.header("Google Sheets Authentication")
            credentials_file = st.sidebar.file_uploader(
                "Upload Google Sheets credentials JSON file",
                type=['json'],
                help="Upload the credentials.json file from Google Cloud Console. In the left sidebar, click APIs & Services → Library Search for GoogleSheetsAPI You'll see a modal with your client ID and secret Click Download JSON"
            )
            
            if credentials_file is not None:
                credentials_content = json.loads(credentials_file.getvalue().decode())
                flow = InstalledAppFlow.from_client_config(credentials_content, SCOPES)
                creds = flow.run_local_server(port=0)
                
                st.session_state.google_creds = creds.to_json()
    
    return creds

def get_sheet_data(sheet_url):
    try:
        sheet_id = sheet_url.split('/d/')[1].split('/')[0]
        
        creds = get_google_creds()
        if not creds:
            st.error("Please authenticate with Google Sheets first")
            return None
            
        service = build('sheets', 'v4', credentials=creds)
        
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=sheet_id, range='A:ZZ').execute()
        values = result.get('values', [])
        
        if not values:
            st.error('No data found in the sheet')
            return None
            
        df = pd.DataFrame(values[1:], columns=values[0])
        return df
        
    except Exception as e:
        st.error(f"Error accessing Google Sheet: {str(e)}")
        return None

def safe_request(url, params=None, max_retries=3):
    retry_count = 0
    while retry_count < max_retries:
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            retry_count += 1
            if retry_count == max_retries:
                st.warning(f"Failed to fetch data from {url}: {str(e)}")
                return None
            time.sleep(2)  
def search_and_scrape(user_prompt, main_column, df):
    table = pd.DataFrame(columns=['main_column', 'data'])
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    total_entities = len(df[main_column].dropna().unique())
    for index, entity in enumerate(df[main_column].dropna().unique()):
        try:
            query = user_prompt.replace("{entity}", entity)
            status_text.text(f"Processing {index + 1}/{total_entities}: {entity}")
            
            # Search parameters for the SERP API
            params = {
                "q": query,
                "api_key": st.session_state.serp_key,
            }
            
            response = safe_request("https://serpapi.com/search", params=params)
            if not response:
                continue
                
            results = response.json().get("organic_results", [])[:5]
            company_content = ""
            Result = ""
            
            for result in results:
                try:
                    link = result.get("link")
                    page_response = safe_request(link)
                    
                    if page_response:
                        soup = BeautifulSoup(page_response.content, "html.parser")
                        headings = [h.get_text() for h in soup.find_all("h1")]
                        paragraphs = [p.get_text() for p in soup.find_all("p")]
                        content = "\n".join(headings) + "\n" + "\n".join(paragraphs)
                        Result += content
                except Exception as e:
                    st.warning(f"Error processing link for {entity}: {str(e)}")
                    continue
            
            if Result:
                company_content = LLM_result(user_prompt, Result)
                new_row = pd.DataFrame([{'main_column': entity, 'data': company_content}])
                table = pd.concat([table, new_row], ignore_index=True)
            
            # Update progress
            progress_bar.progress((index + 1) / total_entities)
            
        except Exception as e:
            st.error(f"Error processing entity {entity}: {str(e)}")
            continue
    
    progress_bar.empty()
    status_text.empty()
    return table

# File upload options
st.subheader("Choose Data Source")
data_source = st.radio(
    "Select data source:",
    ("Upload File", "Google Sheets")
)

df = None

if data_source == "Upload File":
    uploaded_file = st.file_uploader("Choose a CSV or XLSX file", type=["csv", "xlsx"])
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            elif uploaded_file.name.endswith('.xlsx'):
                df = pd.read_excel(uploaded_file)
        except Exception as e:
            st.error(f"Error reading file: {str(e)}")
else:
    sheet_url = st.text_input(
        "Enter Google Sheets URL",
        help="Enter the full URL of your Google Sheet"
    )
    if sheet_url:
        df = get_sheet_data(sheet_url)

if df is not None:
    st.write("Available columns:")
    st.write(df.columns.tolist())
    
    st.write("Preview of the uploaded data:")
    st.write(df.head(5))
    
    main_column = st.selectbox("Select the main column", df.columns)
    
    st.write("Preview of the selected main column:")
    st.write(df[[main_column]].head())
    
    user_prompt = st.text_input("Enter your custom prompt (use {entity} as a placeholder):")
    
    if user_prompt:
        if not (st.session_state.groq_key and st.session_state.serp_key):
            st.warning("Please enter both API keys in the sidebar before proceeding")
        else:
            results_table = search_and_scrape(user_prompt, main_column, df)
            
            if not results_table.empty:
                st.write("Results:")
                st.write(results_table)
                
                # Add download button
                csv = results_table.to_csv(index=False)
                st.download_button(
                    label="Download results as CSV",
                    data=csv,
                    file_name="scraping_results.csv",
                    mime="text/csv"
                )
            else:
                st.warning("No results were found. Please try adjusting your search criteria.")