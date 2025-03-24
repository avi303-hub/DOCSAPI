from bs4 import BeautifulSoup
from googleapiclient.discovery import build
from django.conf import settings
from .google_auth import get_user_credentials

from bs4 import BeautifulSoup

def html_to_google_docs_format(html_content):
    soup = BeautifulSoup(html_content, 'html5lib')
    requests = []
    current_index = 1  

    def add_text(text, style=None, paragraph_style=None):
        nonlocal current_index
        if not text.strip():
            return
        
        requests.append({
            'insertText': {
                'text': text,
                'location': {'index': current_index}
            }
        })

        end_index = current_index + len(text)
        
        # Apply text style if needed
        if style:
            requests.append({
                'updateTextStyle': {
                    'range': {'startIndex': current_index, 'endIndex': end_index},
                    'textStyle': style,
                    'fields': ','.join(style.keys())
                }
            })
        
        # Apply paragraph style (for headings)
        if paragraph_style:
            requests.append({
                'updateParagraphStyle': {
                    'range': {'startIndex': current_index, 'endIndex': end_index},
                    'paragraphStyle': paragraph_style,
                    'fields': 'namedStyleType'
                }
            })
        
        current_index += len(text.replace('\n', '')) + text.count('\n')

    for element in soup.find_all(True):
        text = element.get_text() + '\n'

        if element.name == 'h1':
            add_text(text, paragraph_style={'namedStyleType': 'HEADING_1'})
        elif element.name == 'h2':
            add_text(text, paragraph_style={'namedStyleType': 'HEADING_2'})
        elif element.name == 'h3':
            add_text(text, paragraph_style={'namedStyleType': 'HEADING_3'})
        elif element.name == 'p':
            add_text(text)
        elif element.name == 'b':
            add_text(text.strip(), {'bold': True})
        elif element.name == 'i':
            add_text(text.strip(), {'italic': True})
        elif element.name == 'u':
            add_text(text.strip(), {'underline': True})
        elif element.name == 'br':
            add_text('\n')  

    return requests



def create_google_doc(user, html_content, title="New Document"):
    auth = get_user_credentials(user)
    if not auth:
        raise Exception("User not authenticated with Google")
    
    service = build('docs', 'v1', credentials=auth)
    
    # Create blank document
    doc = service.documents().create(body={'title': title}).execute()
    doc_id = doc['documentId']
    
    # Apply formatting
    requests = html_to_google_docs_format(html_content)
    if requests:
        service.documents().batchUpdate(
            documentId=doc_id,
            body={'requests': requests}
        ).execute()
    
    return f"https://docs.google.com/document/d/{doc_id}/edit"