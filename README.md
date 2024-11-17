****Project Overview****
This is a web-based tool built with Streamlit that performs automated web scraping and analysis using multiple APIs and data sources. The key features include:
a) API Integration & Security:
    Securely stores API keys in session state
    Password masking for sensitive inputs
    Persists throughout the session
b) Multiple Data Source Support
    Supports CSV and Excel file uploads
    Google Sheets integration
c) Google Sheets Authentication
    Secure OAuth2 authentication
    Credential persistence in session state
    Automatic token refresh
d) Robust Error Handling
   Retry mechanism for failed requests
   Timeout handling
   Clear error messages to users
   Exception catching at multiple levels
e) Progress Tracking
  Real-time progress bar
  Status updates for each entity
  Clear process visualization
f) AI Integration (GROQ)
  Handle MUltiple prompts
  Integration with GROQ's LLM
  Structured prompt formatting
  Error handling with retries
g) Data Export Features
  CSV export functionality
  Interactive download button
  Formatted output

****Setup Instructions:****
Run the Requirements.txt file
Also for the Google Sheets feature you will require a JSON file that can be downloaded through:
Go to Google Cloud Console:

Visit https://console.cloud.google.com/
Sign in with your Google account

Create a new project (or select existing):

CopyClick on the project dropdown in the top bar
Click "New Project"
Give it a name
Click "Create"

Enable the Google Sheets API:

CopyIn the left sidebar, click "APIs & Services" → "Library"
Search for "Google Sheets API"
Click on it and click "Enable"

Create credentials:

CopyGo to "APIs & Services" → "Credentials"
Click "Create Credentials" → "OAuth client ID"
If prompted, configure the OAuth consent screen first:
- Choose "External" or "Internal" (depending on your use case)
- Fill in the required fields (app name, user support email, developer contact)
- Add necessary scopes (Google Sheets API read)
- Add test users if needed

Configure OAuth client:

CopyFor Application type, select "Desktop application"
Give it a name
Click "Create"

Download the credentials:

CopyYou'll see a modal with your client ID and secret
Click "Download JSON"
This is your credentials.json file that you'll need for the application


****Usage Guide:****
Using CSV file:
First input your API keys in the fields provided to the left 
upload your csv file select the main column
enter your prompt to get the results 
view the results and download if required
Using Google sheets:
First input your API keys in the fields provided to the left 
give the google sheets link in the field
then upload your JSON file and complete next google auth steps 
select the main column
enter your prompt to get the results 
view the results and download if required

****API Keys and Environment Variables:****
API keys are to be provided in the fields to the right


****Optional Features:****
Saving the session so that user need not upload the files several times
proper error handling and automatic retries
progress tracking for the number of entities completed


****LOOM VIDEO LINK****
https://www.loom.com/share/63bb40708a894e5fbe69f95d482828f9?sid=00557ab1-3029-4a2e-a696-706a8cf568ba


Result screenshots
![image](https://github.com/user-attachments/assets/18461d8e-f289-4a62-8297-8b4ec99a8a2c)
![image](https://github.com/user-attachments/assets/8b492233-a0ec-4543-8da8-b087349ff3ce)
