import streamlit as st
import json
import os

# Import libraries for document processing
import PyPDF2
import pdfplumber
import pandas as pd
from ebooklib import epub
from bs4 import BeautifulSoup

st.set_page_config(layout="wide", page_title="RAG Document Converter")

def convert_pdf_to_json(file_path):
    data = []
    with pdfplumber.open(file_path) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            if text:
                data.append({
                    "page_number": i + 1,
                    "content": text
                })
    return data

def convert_epub_to_json(file_path):
    book = epub.read_epub(file_path)
    data = []
    for item in book.get_items():
        if item.get_type() == epub.ITEM_DOCUMENT:
            soup = BeautifulSoup(item.content, 'html.parser')
            text = soup.get_text()
            if text:
                data.append({
                    "chapter": item.file_name,
                    "content": text
                })
    return data

def convert_excel_to_json(file_path):
    df = pd.read_excel(file_path)
    return {
        "columns": df.columns.tolist(),
        "row_count": len(df),
        "data": df.to_dict(orient="records")
    }

def convert_dta_to_json(file_path):
    df = pd.read_stata(file_path)
    return {
        "columns": df.columns.tolist(),
        "row_count": len(df),
        "data": df.to_dict(orient="records")
    }

def main():
    st.title("RAG Document Converter")
    st.write("Unggah dokumen Anda (PDF, EPUB, XLSX, DTA) untuk dikonversi ke format JSON yang siap untuk RAG.")

    uploaded_file = st.file_uploader("Pilih file", type=["pdf", "epub", "xlsx", "dta", "csv"])

    if uploaded_file is not None:
        file_details = {"filename": uploaded_file.name, "filetype": uploaded_file.type, "filesize": uploaded_file.size}
        st.write(file_details)

        # Save the uploaded file temporarily
        with open(os.path.join("temp_uploaded_file", uploaded_file.name), "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        file_path = os.path.join("temp_uploaded_file", uploaded_file.name)

        converted_data = None
        file_extension = uploaded_file.name.split(".")[-1].lower()

        if file_extension == "pdf":
            converted_data = convert_pdf_to_json(file_path)
        elif file_extension == "epub":
            converted_data = convert_epub_to_json(file_path)
        elif file_extension == "xlsx":
            converted_data = convert_excel_to_json(file_path)
        elif file_extension == "dta":
            converted_data = convert_dta_to_json(file_path)
        elif file_extension == "csv":
            converted_data = convert_csv_to_json(file_path)
        else:
            st.error("Format file tidak didukung.")

        if converted_data:
            json_output_filename = f"rag_ready_{uploaded_file.name}.json"
            json_output_path = os.path.join("temp_uploaded_file", json_output_filename)
            with open(json_output_path, "w", encoding="utf-8") as f:
                json.dump(converted_data, f, ensure_ascii=False, indent=4)
            
            st.success("Konversi berhasil!")
            st.download_button(
                label="Unduh JSON",
                data=open(json_output_path, "rb").read(),
                file_name=json_output_filename,
                mime="application/json"
            )
            st.json(converted_data)

        # Clean up temporary file
        os.remove(file_path)
        if converted_data:
            os.remove(json_output_path)


if __name__ == "__main__":
    # Create a temporary directory if it doesn't exist
    if not os.path.exists("temp_uploaded_file"):
        os.makedirs("temp_uploaded_file")
    main()




def convert_csv_to_json(file_path):
    df = pd.read_csv(file_path)
    return {
        "columns": df.columns.tolist(),
        "row_count": len(df),
        "data": df.to_dict(orient="records")
    }


