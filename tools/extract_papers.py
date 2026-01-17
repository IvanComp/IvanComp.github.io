import os
import json
import glob
import numpy as np

try:
    from pypdf import PdfReader
    from sentence_transformers import SentenceTransformer
except ImportError:
    print("Error: Missing dependencies. Please run: pip install pypdf sentence-transformers")
    exit(1)

# Configuration
PDF_DIR = "../assets/file"
OUTPUT_FILE = "../assets/data/rag_data.json"
TARGET_FILES = [
    "BIR.pdf", "BISE.pdf", "BPMN-Inspector.pdf", "DTBP.pdf", 
    "FL.pdf", "JSS-FL.pdf", "MIDAS.pdf", "MODELS1.pdf", 
    "MODELS2.pdf", "SLR1.pdf", "SLR2.pdf"
]

MODEL_NAME = 'all-MiniLM-L6-v2'
CHUNK_SIZE = 500  # characters
OVERLAP = 50      # characters

def extract_text_from_pdf(pdf_path):
    try:
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            t = page.extract_text()
            if t:
                text += t + "\n"
        return text
    except Exception as e:
        print(f"Error reading {pdf_path}: {e}")
        return ""

def create_chunks(text, chunk_size, overlap):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        # cleanup whitespace in chunk
        chunk = " ".join(chunk.split())
        if len(chunk) > 50: # filter very short chunks
            chunks.append(chunk)
        start += (chunk_size - overlap)
    return chunks

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    pdf_dir_path = os.path.join(base_dir, PDF_DIR)
    output_dir = os.path.dirname(os.path.join(base_dir, OUTPUT_FILE))
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print(f"Loading embedding model: {MODEL_NAME}...")
    model = SentenceTransformer(MODEL_NAME)
    
    all_chunks = []
    
    print(f"Scanning {pdf_dir_path}...")
    
    for filename in TARGET_FILES:
        filepath = os.path.join(pdf_dir_path, filename)
        if os.path.exists(filepath):
            print(f"Processing {filename}...")
            text = extract_text_from_pdf(filepath)
            chunks = create_chunks(text, CHUNK_SIZE, OVERLAP)
            
            for chunk in chunks:
                all_chunks.append({
                    "text": chunk,
                    "source": filename
                })
        else:
            print(f"Warning: File not found {filename}")

    print(f"Generated {len(all_chunks)} chunks. Computing embeddings...")
    
    # Compute embeddings in batch
    texts = [c["text"] for c in all_chunks]
    embeddings = model.encode(texts)
    
    # Prepare output data
    # We serialize embeddings as lists for JSON
    rag_data = []
    for i, chunk in enumerate(all_chunks):
        rag_data.append({
            "id": i,
            "text": chunk["text"],
            "source": chunk["source"],
            "embedding": embeddings[i].tolist()
        })
        
    output_path = os.path.join(base_dir, OUTPUT_FILE)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(rag_data, f)
        
    print(f"Successfully saved RAG data to {output_path}")

if __name__ == "__main__":
    main()
