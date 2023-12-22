"""Load html from files, clean up, split, ingest into Weaviate."""
import pickle

import os

import torch
from tqdm import tqdm

from langchain.document_loaders import PyPDFLoader
from langchain.embeddings import HuggingFaceEmbeddings, HuggingFaceInstructEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS

from langchain.document_loaders import ReadTheDocsLoader, TextLoader, UnstructuredFileLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores.faiss import FAISS

def get_embedding():
    if torch.cuda.is_available():
        # https://www.anyscale.com/blog/turbocharge-langchain-now-guide-to-20x-faster-embedding
        model_kwargs = {"device": "cuda"}
        embeddings = HuggingFaceInstructEmbeddings(model_name='hkunlp/instructor-xl', model_kwargs=model_kwargs)
        # embeddings = HuggingFaceEmbeddings(model_name=model_name, model_kwargs=model_kwargs)
    else:
        embeddings = OpenAIEmbeddings()
    return embeddings


def ingest_docs():
    """Get documents from web pages."""
    loader = TextLoader("./local/docs/content.txt")
    raw_documents = loader.load()
    print(f'raw_documents:{len(raw_documents)}')
    print(f'raw_documents:{raw_documents[0]}')
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
    )
    documents = text_splitter.split_documents(raw_documents)
    embeddings = get_embedding()
    # embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_documents(documents, embeddings)
    print(f"DistanceStrategy = {vectorstore.distance_strategy}, {vectorstore.override_relevance_score_fn}")
    # vectorstore.distance_strategy = DistanceStrategy.EUCLIDEAN_DISTANCE

    return vectorstore


if __name__ == "__main__":
    vectorstore = ingest_docs()
    question_list = [
        "What is black body radiation?",
        "Who is Ubix"
    ]
    for question in question_list:
        res = vectorstore.similarity_search_with_relevance_scores(question)
        print(f'{question}, {res}')

"""
python test/ingest.py
"""




