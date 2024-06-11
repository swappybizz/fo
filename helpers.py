import os.path
import streamlit as st
from openai import OpenAI
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import datetime

import pandas as pd
import random
import numpy as np


def get_document_id(link):
    return link.split('/')[-2]



SCOPES = ['https://www.googleapis.com/auth/documents.readonly']

def save_credentials(creds):
    st.session_state['gcp_token'] = creds.token
    st.session_state['gcp_refresh_token'] = creds.refresh_token
    st.session_state['gcp_token_uri'] = creds.token_uri
    st.session_state['gcp_client_id'] = creds.client_id
    st.session_state['gcp_client_secret'] = creds.client_secret
    st.session_state['gcp_expiry'] = creds.expiry.isoformat()

def load_credentials():
    return Credentials(
        token=st.session_state.get('gcp_token'),
        refresh_token=st.session_state.get('gcp_refresh_token'),
        token_uri=st.session_state.get('gcp_token_uri'),
        client_id=st.session_state.get('gcp_client_id'),
        client_secret=st.session_state.get('gcp_client_secret'),
        expiry=datetime.datetime.fromisoformat(st.session_state.get('gcp_expiry')) if 'gcp_expiry' in st.session_state else None
    )

def get_google_docs_content(document_id):
    creds = None

    if 'gcp_token' in st.session_state:
        creds = load_credentials()

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_config(
                {
                    "installed": {
                        "client_id": st.secrets["gcp_oauth"]["gcp_client_id"],
                        "client_secret": st.secrets["gcp_oauth"]["gcp_client_secret"],
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob"],
                    }
                },
                SCOPES,
            )
            creds = flow.run_local_server(port=0)
            save_credentials(creds)

    try:
        service = build("docs", "v1", credentials=creds)
        document = service.documents().get(documentId=document_id).execute()
        content = document.get('body').get('content')
        return document, content, service
    except HttpError as err:
        st.error(f"An error occurred: {err}")
        return None, None, None
    
    
    
def parse_document_content(content):
    text = ""
    images = []
    for element in content:
        if 'paragraph' in element:
            for para_element in element['paragraph']['elements']:
                text += para_element.get('textRun', {}).get('content', '')
        if 'inlineObjectElement' in element:
            inline_object_id = element['inlineObjectElement']['inlineObjectId']
            images.append(inline_object_id)
    return text, images

def extract_image_urls(inline_objects):
    image_urls = []
    for obj_id, obj in inline_objects.items():
        image_properties = obj.get('inlineObjectProperties', {}).get('embeddedObject', {}).get('imageProperties', {})
        content_uri = image_properties.get('contentUri')
        if content_uri:
            # print(f"Detected image: {content_uri}")
            image_urls.append(content_uri)
    return image_urls
