import streamlit as st
from PIL import Image
from ocr_model import OCRModel
import json

def search_text(text, keyword):
    if not text or not keyword:
        return []
    lines = text.lower().split('\n')
    keyword = keyword.lower()
    results = [line for line in lines if keyword in line]
    return results

@st.cache_resource
def get_ocr_model():
    return OCRModel()

st.title("Hindi-English OCR with Search")

ocr_model = get_ocr_model()

uploaded_file = st.file_uploader("Choose an image file", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_column_width=True)
    
    if st.button("Perform OCR"):
        try:
            with st.spinner("Processing OCR..."):
                ocr_text = ocr_model.process_image(image)
            
            st.subheader("Extracted Text:")
            st.text_area("", ocr_text, height=200)
            
            # Save extracted text as JSON
            json_output = json.dumps({"extracted_text": ocr_text}, ensure_ascii=False, indent=2)
            st.download_button(
                label="Download JSON",
                data=json_output,
                file_name="extracted_text.json",
                mime="application/json"
            )
            
            st.subheader("Search in Extracted Text")
            search_keyword = st.text_input("Enter a keyword to search")
            
            if search_keyword:
                search_results = search_text(ocr_text, search_keyword)
                if search_results:
                    st.subheader("Search Results:")
                    for result in search_results:
                        highlighted_result = result.replace(search_keyword.lower(), f"<mark>{search_keyword.lower()}</mark>")
                        st.markdown(f"- {highlighted_result}", unsafe_allow_html=True)
                else:
                    st.info("No matching results found.")
        except Exception as e:
            st.error(f"An error occurred during OCR processing: {str(e)}")

st.markdown("---")
st.markdown("Developed using EasyOCR")