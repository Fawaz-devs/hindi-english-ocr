import streamlit as st
from PIL import Image
from ocr_model import OCRModel
import json
import re

def search_and_highlight(text, keyword):
    if not text or not keyword:
        return text, []
    
    pattern = re.compile(re.escape(keyword), re.IGNORECASE)
    highlighted_text = pattern.sub(lambda m: f"<mark>{m.group()}</mark>", text)
    
    lines = text.lower().split('\n')
    keyword = keyword.lower()
    results = [i for i, line in enumerate(lines) if keyword in line]
    
    return highlighted_text, results

@st.cache_resource
def get_ocr_model():
    return OCRModel()

st.title("Hindi-English OCR with Search")

# Initialize session state
if 'ocr_text' not in st.session_state:
    st.session_state.ocr_text = ""
if 'image' not in st.session_state:
    st.session_state.image = None
if 'last_uploaded_file' not in st.session_state:
    st.session_state.last_uploaded_file = None

ocr_model = get_ocr_model()

uploaded_file = st.file_uploader("Choose an image file", type=["jpg", "jpeg", "png"])

if uploaded_file is not None and uploaded_file != st.session_state.last_uploaded_file:
    st.session_state.image = Image.open(uploaded_file)
    st.session_state.ocr_text = ""  # Reset OCR text when a new image is uploaded
    st.session_state.last_uploaded_file = uploaded_file

if st.session_state.image is not None:
    st.image(st.session_state.image, caption="Uploaded Image", use_column_width=True)

    if st.button("Perform OCR") or st.session_state.ocr_text:
        if not st.session_state.ocr_text:
            with st.spinner("Processing OCR..."):
                st.session_state.ocr_text = ocr_model.process_image(st.session_state.image)

        st.subheader("Extracted Text:")
        text_area = st.empty()
        text_area.text_area("", st.session_state.ocr_text, height=200)
        
        # Save extracted text as JSON
        json_output = json.dumps({"extracted_text": st.session_state.ocr_text}, ensure_ascii=False, indent=2)
        st.download_button(
            label="Download JSON",
            data=json_output,
            file_name="extracted_text.json",
            mime="application/json"
        )
        
        st.subheader("Search in Extracted Text")
        search_keyword = st.text_input("Enter a keyword to search")
        
        if search_keyword:
            highlighted_text, search_results = search_and_highlight(st.session_state.ocr_text, search_keyword)
            if search_results:
                st.markdown(f"Found {len(search_results)} matches.")
                text_area.markdown(highlighted_text, unsafe_allow_html=True)
                
                st.subheader("Search Results:")
                lines = st.session_state.ocr_text.split('\n')
                for i in search_results:
                    st.markdown(f"- Line {i+1}: {lines[i]}")
            else:
                st.info("No matching results found.")

st.markdown("---")
st.markdown("Developed using EasyOCR")