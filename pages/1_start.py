import os.path
import streamlit as st
from openai import OpenAI
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError




from st_paywall import add_auth

import pandas as pd
import random
import numpy as np
from helpers import get_document_id, get_google_docs_content, parse_document_content, extract_image_urls


st.set_page_config(layout="wide")
if "generated_docs" not in st.session_state:
    st.session_state.generated_docs = ""
    
if "document_text" not in st.session_state:
    st.session_state.document_text = ""


add_auth(required=True)
SCOPES = ["https://www.googleapis.com/auth/documents.readonly"]



def generate_docs(links, text):
    if links is None:
        links = st.session_state.image_urls
    if text in ["", None]:
        text = st.session_state.document_text
    
    if "generated_docs" not in st.session_state:
        st.session_state.generated_docs = ""
    
    prompt = f"""
    You have been provided with some content and optionally some images. You will summarize the content and images into a document.
    You will include a title of the document.
    You will use the following content and images to generate the document:
    ###
    Content:
    {text}
    ###
    You will only return the content of the document.
    """
    
    messages_pmt = [
        {"role": "system", "content": "You are a documenter. You only respond with documents"},
        {"role": "user", "content": prompt},
    ]
    
    for link in links:
        messages_pmt.append({"role": "user", "content": [
            {"type": "image_url", "image_url": {"url": link}}
        ]}) 

    print("§§§§ $$$ CAUTION: A DOC GEN COSTING CALL#### IS BEING MADE $$$ §§§§")

    client = OpenAI(api_key=st.secrets["openai_api_key"])
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=messages_pmt,
    )
    generated_doc = str(completion.choices[0].message.content)
    st.session_state.generated_docs = generated_doc
    print(generated_doc)
    st.toast(f"Document generated successfully{st.session_state.generated_docs}", icon="✍️")


@st.experimental_fragment(run_every=500)
def fetch_and_display_content():
    print("Attempting Refreshing content")
    if "link" in st.session_state:
        link = st.session_state.link
        print(f"link detected: {link}")
    else:
        print("No link detected returning...")
        return
        
    if len(link) > 0:
        document_id = get_document_id(link)
        document, content, service = get_google_docs_content(document_id)
        
        if content:
            document_text, image_ids = parse_document_content(content)
            
            # Check if the document text is different
            text_is_different = 'document_text' not in st.session_state or st.session_state.document_text != document_text
            
            inline_objects = document.get('inlineObjects', {})
            image_urls = extract_image_urls(inline_objects)
            
            # Check if any of the image URLs are unique
            unique_images = [url for url in image_urls if 'image_urls' not in st.session_state or url not in st.session_state.image_urls]

            if text_is_different or unique_images:
                st.session_state.document_text = document_text
                st.session_state.image_urls = image_urls if 'image_urls' not in st.session_state else list(set(st.session_state.image_urls + unique_images))
                
                st.session_state.image_urls = image_urls
                st.session_state.document_text = document_text
                
                # Call the generate_docs function with updated data
                generate_docs(st.session_state.image_urls, st.session_state.document_text)





@st.experimental_fragment(run_every=3)
def fragment():
    st.write(f"Fragment with random {random.randint(1, 100)}")


@st.experimental_dialog("Setup new Flow", width="large")
def setup_new_flow():
    st.write("Setup new flow")
    st.text_input("Flow name")
    st.text_area("Description")
    st.button("Create flow")


@st.experimental_dialog("Setup new Flow", width="large")
def setup_new_interaction():
    st.write("Setup new Interaction")
    
    
@st.experimental_dialog("Setup new Flow", width="large")
def setup_new_featureRequest():
    st.write("Setup new featureRequest")


with st.sidebar:
    with st.container(height=150, border=False):
        st.text_area(
            "Search and lookup",
            max_chars=100,
            placeholder="Lookup data, doc or related info",
        )
    with st.container(
        height=250,
        border=True,
    ):
        for i in range(15):
            st.button(f"History Item {i}", use_container_width=True)

    with st.container( border=False):
        selected_options = st.multiselect(
            "injectWith", ["Option 1", "Option 2", "Option 3"]
        )
    if st.button("Feature Request", use_container_width=True):
        setup_new_featureRequest()

    st.divider()
    "Assistit Mainface Lite"
    f"Token uses : 12345"
    "©️ nooffice 2025"
    f"Login: {st.session_state.email}"

tabs = st.tabs(([
                 "JIT🔳Editor", 
                 "🔶Dashboard",
                 "⭕Colab", "📗Flows"]))



with tabs[0]:
    col1, col2 = st.columns([2, 1])
    with col1:
        with st.container(border=True,height=600):
            for i in reversed(range(4)):
                with st.container(border=False, height=420):
                    st.write("This will be a widget")
                    fragment()
                        
         
                    
        with st.expander("Deliverable", expanded=False,):
            with st.form(border=True,key=f"deliverable_form_{i}"):
                doc_name = st.text_input("Doc Name", key="doc_name")
                doc_instructions = st.text_area("Instructions", key="doc_instructions")
                del_date = st.date_input("Delivery Date", key="delivey_date")
                tags = st.text_input("Tags", key="tags")
                submit = st.form_submit_button("Add New Deliverable")
                
            
            data = []
            # Create 3 random entries
            for k in range(1):
                colu = {
                    "Doc": "Doc 1",
                    "isntructions": "What the file must contain",
                    "instructional_value": random.randint(0, 100),
                    "completion": random.randint(0, 100),
                    "accountability": random.randint(0, 100),
                    "validation": random.randint(0, 100),
                    "Action": "KEEP"
                }
                data.append(colu)
                                    
            # Create a DataFrame
            df = pd.DataFrame(data)
            # Display the DataFrame using st.data_editor with column configurations
            st.data_editor(
                df,
                hide_index=True,
                use_container_width=True,
                key=f"data_editor_deliverable",
                column_config={
                    "Doc": st.column_config.TextColumn(),
                    "isntructions": st.column_config.TextColumn(),
                    "instructional_value": st.column_config.ProgressColumn(),
                    "completion": st.column_config.ProgressColumn(),
                    "accountability": st.column_config.ProgressColumn(),
                    "validation": st.column_config.ProgressColumn(),
                    "Action": st.column_config.TextColumn(),
                },
            )
            if st.button("Generate Docs", use_container_width=True):
                print("Pushed")
                st.code(st.session_state.generated_docs)
        
    with col2:
        fetch_and_display_content()    
        with st.form(border=True, key="docsLink"):
            link = st.text_input("Enter Google Docs link:",
                          key="link")
            if st.form_submit_button("Connect"):
                # save the link in session state
                if "knowledge_link" not in st.session_state:
                    st.session_state.knowledge_link = ""
                
                st.session_state.knowledge_link = link
                
        if st.session_state.document_text:
            st.text_area("Document Content", st.session_state.document_text, height=400,key = "document_text")
            
                    
                    
        # sribbleBoard= st.text_area(
        #         "use",
        #         placeholder="""
        #         Scribble board for You and Assistant
        #         """,
        #         height=250,
        #         key="monospace-textarea",
        #         label_visibility="hidden",
                
        #     )
            # st.button("Push", use_container_width=True)

        if st.button("Setup New", use_container_width=True):
            setup_new_flow()
        if st.button("Interact", use_container_width=True):
            setup_new_interaction()
        uploaded_files = st.file_uploader(
            "Choose a file",
            accept_multiple_files=True,
            key="file_uploader",
            label_visibility="hidden"
        )
        with st.container(
            border=False,
            height=350,
        ):
            # Define the column names and default values
            columns = {
                "file_name": [],
                "instructional_value": [],
                "UserMultiplierX": [],
                "Knowledge_completeness": [],
                "UserMultiplierY": [],
                "accountability": [],
                "Command": "",
            }

            # Create 5 random entries
            for i in range(5):
                columns["file_name"].append(f"file_{i+1}.txt")
                columns["instructional_value"].append(random.randint(0, 100))
                columns["UserMultiplierX"].append(0)
                columns["Knowledge_completeness"].append(random.randint(0, 100))
                columns["UserMultiplierY"].append(0)
                columns["accountability"].append(None)
                columns["Command"] = "KEEP"

            # Create a DataFrame
            df = pd.DataFrame(columns)

            # Display the DataFrame using st.data_editor with column configurations
            # st.divider()
            st.data_editor(
                df,hide_index=True,
                column_config={
                    "instructional_value": st.column_config.ProgressColumn(),
                    "Knowledge_completeness": st.column_config.ProgressColumn(),
                    "UserMultiplierX": st.column_config.NumberColumn(default=0,min_value=-1,max_value=1,width=50),
                    "UserMultiplierY": st.column_config.NumberColumn(default=0,min_value=-1,max_value=1,width=50),
                    "accountability": st.column_config.TextColumn(default=None),
                    "Command": st.column_config.TextColumn(),
                },
            )
