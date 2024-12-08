import argparse
import os
import shutil
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema.document import Document
from get_embedding_function import get_embedding_function
from langchain_chroma import Chroma
from pymongo import MongoClient
import torch


CHROMA_PATH = "chroma"
DATA_PATH = "data"
MONGO_URI = "mongodb://localhost:27017/"
MONGO_DB_NAME = "crawler_db"
MONGO_COLLECTION_NAME = "webpages"


def main():

    # Check if the database should be cleared (using the --clear flag).
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true", help="Reset the database.")
    args = parser.parse_args()
    if args.reset:
        print("✨ Clearing Database")
        clear_database()

    # Create (or update) the data store.
    pdf_documents = load_pdf_documents()
    mongodb_documents = load_mongodb_documents()
    # print(f"PDF Documents: {len(pdf_documents)}")
    # print(f"MongoDB Documents: {len(mongodb_documents)}")
    documents = pdf_documents + mongodb_documents
    # print(f"Total Documents: {len(documents)}")

    chunks = split_documents(documents)
    print(f"Total Chunks: {len(chunks)}")
    add_to_chroma(chunks)


def load_pdf_documents():
    document_loader = PyPDFDirectoryLoader(DATA_PATH)
    return document_loader.load()

def load_mongodb_documents():
    client = MongoClient(MONGO_URI)
    db = client[MONGO_DB_NAME]
    collection = db[MONGO_COLLECTION_NAME]

    documents = []

    cursor = collection.find()
    for doc in cursor:
        document_id = doc.get('_id', "unknown_id")
        url = doc.get('url', "unknown_url")
        parent = doc.get('parent', "")
        child = doc.get('child', "")
        nested_data = doc.get('data', [])

        # Combine all text from the nested `Text` arrays
        combined_text = ""
        for item in nested_data:
            text_content = item.get('Text', [])
            combined_text += " ".join(text_content) + " "

        # Skip if no meaningful text is found
        if not combined_text.strip():
            print(f"⚠️ Skipping document without text: {document_id}")
            continue

        # Create metadata and Document object
        metadata = {
            "source": f"mongodb:{document_id}",
            "url": url,
            "parent": parent,
            "child": child,
        }
        documents.append(Document(page_content=combined_text.strip(), metadata=metadata))

    print(f"Loaded {len(documents)} documents from MongoDB")
    return documents

def split_documents(documents: list[Document]):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=80,
        length_function=len,
        is_separator_regex=False,
    )
    return text_splitter.split_documents(documents)

def clean_metadata(metadata):
    """ Recursively clean metadata to ensure it only contains basic types (str, int, float, bool), 
    and remove or replace None values. """
    if isinstance(metadata, dict):
        # Recursively clean dictionary keys and values
        return {key: clean_metadata(value) for key, value in metadata.items()}
    elif isinstance(metadata, list):
        # Clean each element in the list
        return [clean_metadata(item) for item in metadata]
    else:
        # Replace None with an empty string or other placeholder
        return metadata if metadata is not None else ""

def split_batches(documents, ids, batch_size=41666):
    """
    Splits the documents and their corresponding IDs into smaller batches.
    """
    for i in range(0, len(documents), batch_size):
        yield ids[i:i + batch_size], documents[i:i + batch_size]

def add_to_chroma(chunks: list):
    # Load the existing database.
    db = Chroma(
        persist_directory=CHROMA_PATH, embedding_function=get_embedding_function()
    )

    # Calculate Chunk IDs.
    chunks_with_ids = calculate_chunk_ids(chunks)  # Ensure this is a list of Document objects

    # Clean metadata for each chunk (remove complex structures and replace None values)
    for chunk in chunks_with_ids:
        chunk.metadata = clean_metadata(chunk.metadata)

    # Add or Update the documents.
    existing_items = db.get(include=[])  # IDs are always included by default
    existing_ids = set(existing_items["ids"])
    print(f"Number of existing documents in DB: {len(existing_ids)}")

    # Only add documents that don't exist in the DB.
    new_chunks = []
    for chunk in chunks_with_ids:
        chunk_id = chunk.metadata.get("id")
        if chunk_id not in existing_ids:
            new_chunks.append(chunk)

    if len(new_chunks):
        print(f"👉 Adding new documents: {len(new_chunks)}")
        
        new_chunk_ids = [chunk.metadata["id"] for chunk in new_chunks]
        # Assuming your chunks are simple strings, use them directly as documents
        new_chunks_texts = [chunk for chunk in new_chunks]  # Use chunk directly if it's a string
        new_chunk_metadatas = [chunk.metadata for chunk in new_chunks]

        # Split the data into smaller batches
        for batch_ids, batch_docs in split_batches(new_chunks_texts, new_chunk_ids):
            db.add_documents(batch_docs, ids=batch_ids)
        
        db.persist()
    else:
        print("✅ No new documents to add")


def calculate_chunk_ids(chunks):

    # This will create IDs like "data/monopoly.pdf:6:2"
    # Page Source : Page Number : Chunk Index

    last_page_id = None
    current_chunk_index = 0

    for chunk in chunks:
        source = chunk.metadata.get("source")
        page = chunk.metadata.get("page", "unknown")
        current_page_id = f"{source}:{page}"

        # If the page ID is the same as the last one, increment the index.
        if current_page_id == last_page_id:
            current_chunk_index += 1
        else:
            current_chunk_index = 0

        # Calculate the chunk ID.
        chunk_id = f"{current_page_id}:{current_chunk_index}"
        last_page_id = current_page_id

        # Add it to the page meta-data.
        chunk.metadata["id"] = chunk_id

    return chunks


def clear_database():
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)


if __name__ == "__main__":

    if not torch.cuda.is_available():
        print("⚠️ GPU not available. Using CPU instead.")

    main()