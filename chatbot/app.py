import os
import streamlit as st
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from htmlTemplates import css, bot_template, user_template
import account  # Import the account.py module

# Firestore client from account module
db = account.db

# Function to fetch documents from the "documents" folder
def fetch_default_documents():
    documents_folder = "documents"
    default_documents = []
    if os.path.exists(documents_folder) and os.path.isdir(documents_folder):
        files = os.listdir(documents_folder)
        for file in files:
            if file.endswith(".pdf"):
                default_documents.append(os.path.join(documents_folder, file))
    return default_documents

def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

def get_text_chunks(text):
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_text(text)
    return chunks

def get_vectorstore(text_chunks):
    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_texts(texts=text_chunks, embedding=embeddings)
    return vectorstore

def get_conversation_chain(vectorstore):
    llm = ChatOpenAI()
    memory = ConversationBufferMemory(memory_key='chat_history', return_messages=True)
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(),
        memory=memory
    )
    return conversation_chain

def save_chat_history(user_email, session_name, chat_history):
    db.collection('users').document(user_email).collection('chat_sessions').document(session_name).set({
        'chat_history': [message.content for message in chat_history]
    })

def load_chat_history(user_email, session_name):
    doc = db.collection('users').document(user_email).collection('chat_sessions').document(session_name).get()
    if doc.exists:
        return doc.to_dict().get('chat_history', [])
    return []

def handle_userinput(user_question, session, user_email):
    conversation_chain = st.session_state.sessions[session]['conversation']
    if conversation_chain is None:
        st.error("Please process documents first to initialize the conversation.")
        return

    response = conversation_chain({'question': user_question})
    st.session_state.sessions[session]['chat_history'] = response['chat_history']

    save_chat_history(user_email, session, st.session_state.sessions[session]['chat_history'])

    for i, message in enumerate(st.session_state.sessions[session]['chat_history']):
        if i % 2 == 0:
            st.write(user_template.replace("{{MSG}}", message.content), unsafe_allow_html=True)
        else:
            st.write(bot_template.replace("{{MSG}}", message.content), unsafe_allow_html=True)

def main():
    load_dotenv()
    st.set_page_config(page_title="MindMate", page_icon=":books:")
    st.write(css, unsafe_allow_html=True)

    if 'is_authenticated' not in st.session_state:
        st.session_state.is_authenticated = False

    if not st.session_state.is_authenticated:
        account.app()
    else:
        user_email = st.session_state.useremail

        if 'sessions' not in st.session_state:
            st.session_state.sessions = {}

        st.sidebar.subheader("Chat Sessions")
        session_name = st.sidebar.text_input("Enter a session name:")

        if st.sidebar.button("Create new session") and session_name:
            default_documents = fetch_default_documents()
            vectorstore = None
            if default_documents:
                # get pdf text
                raw_text = get_pdf_text(default_documents)

                # get the text chunks
                text_chunks = get_text_chunks(raw_text)

                # create vector store
                vectorstore = get_vectorstore(text_chunks)

            st.session_state.sessions[session_name] = {
                'conversation': get_conversation_chain(vectorstore) if vectorstore else None,
                'chat_history': load_chat_history(user_email, session_name),
                'pdf_docs': default_documents
            }

        session = st.sidebar.selectbox("Select a session:", options=list(st.session_state.sessions.keys()))

        if session:
            st.header(f"MindMate :books: - Session: {session}")
            user_question = st.text_input("Ask a question about your documents:")
            if user_question:
                handle_userinput(user_question, session, user_email)

            st.sidebar.subheader("Your documents")
            upload_option = st.sidebar.checkbox("Upload your own PDFs")
            if upload_option:
                pdf_docs = st.sidebar.file_uploader("Upload your PDFs here and click on 'Process'", accept_multiple_files=True)
                if st.sidebar.button("Process"):
                    if pdf_docs:
                        with st.spinner("Processing"):
                            # get pdf text
                            raw_text = get_pdf_text(pdf_docs)

                            # get the text chunks
                            text_chunks = get_text_chunks(raw_text)

                            # create vector store
                            vectorstore = get_vectorstore(text_chunks)

                            # create conversation chain
                            st.session_state.sessions[session]['conversation'] = get_conversation_chain(vectorstore)
                            st.session_state.sessions[session]['pdf_docs'] = pdf_docs
                    else:
                        st.error("Please upload PDF documents to process.")
            else:
                default_documents = fetch_default_documents()
                st.session_state.sessions[session]['pdf_docs'] = default_documents

        st.sidebar.button('Logout', on_click=account.logout)

if __name__ == '__main__':
    main()