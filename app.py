import os
import json
import streamlit as st
from pypdf import PdfReader
from groq import Groq
from dotenv import load_dotenv
load_dotenv()
def extract_text_from_pdf(uploaded_file):
    reader = PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            text+=extracted + "\n"
    return text
def generate_flashcards(text,num_cards):
    client = Groq(api_key = os.getenv("GROQ_API_KEY"))
    prompt = f"""
    Create {num_cards} high-yeild study flashcards from the following text.
    Focus on key concepts,definitions, and important relationships.
    Return ONLY valid JSON in this exact format:
    {{"cards":[{{"question":"...","answer":"..."}}]}}
    Text :
    {text[:25000]}
    """
    response = client.chat.completions.create(
        model = "openai/gpt-oss-20b",
        messages = [{"role":"user","content":prompt}],
        response_format={"type":"json_object"},
    )
    return json.loads(response.choices[0].message.content)["cards"]
st.set_page_config(page_title="AI PDF Flashcard Generator",page_icon = "Page_Icon")
uploaded_file = st.file_uploader("Upload your pdf notes",type=["pdf"])
num_cards = st.slider("Number of flashcards",min_value=5,max_value=20,value=10)
if uploaded_file and st.button("Generate Flashcards"):
    with st.spinner("Reading PDF and generating cards..."):
        raw_text  = extract_text_from_pdf(uploaded_file)
        if not raw_text.strip():
            st.error("COuld not extract text.Make sure the PDF is not the scanned image.")
        else :
            st.session_state.cards = generate_flashcards(raw_text,num_cards)

if "cards" in st.session_state:
    st.subheader(f"Generated{len(st.session_state.cards)} FlashCards")
    for i,card in enumerate(st.session_state.cards,1):
        with st.expander(f"Card {i} :{card['question']}"):
            st.write(f"**Answer:** {card['answer']}")
