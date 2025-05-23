import streamlit as st
import os
import re
import pdfplumber
from docx import Document
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize

import nltk
nltk.download('punkt')
nltk.download('stopwords')

stop_words = set(stopwords.words('english'))

def read_txt(file):
    return file.read().decode('utf-8', errors='ignore')

def read_docx(file):
    doc = Document(file)
    return ' '.join([para.text for para in doc.paragraphs])

def read_pdf(file):
    text = ''
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text
    return text

def clean_words(text):
    words = word_tokenize(text.lower())
    return [w for w in words if w.isalnum() and w not in stop_words]

def find_common_sentences(text1, text2):
    sentences1 = sent_tokenize(text1)
    sentences2 = sent_tokenize(text2)
    common_sentences = []
    for s1 in sentences1:
        s1_clean = re.sub(r'\W+', ' ', s1.lower())
        for s2 in sentences2:
            s2_clean = re.sub(r'\W+', ' ', s2.lower())
            if s1_clean == s2_clean and len(s1_clean.split()) > 3:
                common_sentences.append(s1.strip())
                break
    return common_sentences

def highlight_common_sentences(text, common_sentences):
    for sent in common_sentences:
        text = text.replace(sent, f"**:red[{sent}]**")
    return text

def main():
    st.set_page_config(page_title="Smart Plagiarism Checker", layout="wide")
    st.title("📝 Smart Plagiarism Checker")

    dark_mode = st.sidebar.checkbox("Dark Mode")

    if dark_mode:
        st.markdown(
            """
            <style>
            html, body, [class*="css"]  {
                background-color: #1e272e;
                color: #dcdde1;
            }
            .stButton>button {
                background-color: #718093;
                color: white;
            }
            </style>
            """, unsafe_allow_html=True)
    else:
        st.markdown(
            """
            <style>
            html, body, [class*="css"]  {
                background-color: #f7f9fa;
                color: #2c3e50;
            }
            .stButton>button {
                background-color: #3498db;
                color: white;
            }
            </style>
            """, unsafe_allow_html=True)


    st.sidebar.header("Upload Files")
    file1 = st.sidebar.file_uploader("Upload File 1 (.txt, .pdf, .docx)", type=['txt', 'pdf', 'docx'])
    file2 = st.sidebar.file_uploader("Upload File 2 (.txt, .pdf, .docx)", type=['txt', 'pdf', 'docx'])

    if st.button("🚀 Check Plagiarism"):

        if not file1 or not file2:
            st.error("Please upload both files.")
            return

        ext1 = file1.name.split('.')[-1].lower()
        ext2 = file2.name.split('.')[-1].lower()

        try:
            if ext1 == 'txt':
                text1 = read_txt(file1)
            elif ext1 == 'pdf':
                text1 = read_pdf(file1)
            elif ext1 == 'docx':
                text1 = read_docx(file1)
            else:
                st.error("Unsupported format for File 1")
                return

            if ext2 == 'txt':
                text2 = read_txt(file2)
            elif ext2 == 'pdf':
                text2 = read_pdf(file2)
            elif ext2 == 'docx':
                text2 = read_docx(file2)
            else:
                st.error("Unsupported format for File 2")
                return
        except Exception as e:
            st.error(f"Error reading files: {e}")
            return

        words1 = clean_words(text1)
        words2 = clean_words(text2)

        common_words = list(set(words1).intersection(set(words2)))
        common_word_count = sum(min(words1.count(w), words2.count(w)) for w in common_words)
        total_words = len(words1) + len(words2)

        if total_words == 0:
            st.error("One or both files contain no valid words to compare.")
            return

        plag_percent = round((2 * common_word_count) / total_words * 100)

        common_sentences = find_common_sentences(text1, text2)

        st.subheader(f"Plagiarism Percent: {plag_percent}%")
        st.write(f"Total words in File 1: {len(words1)}")
        st.write(f"Total words in File 2: {len(words2)}")
        st.write(f"Common words count: {common_word_count}")
        st.write("### Common Words:")
        st.write(', '.join(common_words) if common_words else "None")

        st.write(f"### Common Sentences ({len(common_sentences)}):")
        if common_sentences:
            for i, sent in enumerate(common_sentences, 1):
                st.markdown(f"{i}. {sent}")
        else:
            st.write("No common sentences found.")

        st.write("---")
        st.subheader("File 1 Content with Highlighted Common Sentences")
        highlighted_text1 = highlight_common_sentences(text1, common_sentences)
        st.markdown(highlighted_text1, unsafe_allow_html=True)

        st.subheader("File 2 Content with Highlighted Common Sentences")
        highlighted_text2 = highlight_common_sentences(text2, common_sentences)
        st.markdown(highlighted_text2, unsafe_allow_html=True)

        if plag_percent > 60:
            st.warning(f"High Plagiarism: {plag_percent}% plagiarized content detected!")
        elif plag_percent >= 30:
            st.info(f"Moderate Plagiarism: {plag_percent}% plagiarized content detected.")
        else:
            st.success(f"Low Plagiarism: {plag_percent}% plagiarized content detected.")

if __name__ == "__main__":
    main()


# & "C:\Program Files\Python311\python.exe" -m streamlit run "C:\Users\LENOVO\Desktop\Uploaded projects\Python Projects\detect_plagiarism\detect_plagiarism.py"
