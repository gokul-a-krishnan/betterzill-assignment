import os
from transformers import AutoTokenizer, GPTQConfig
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_community.llms.huggingface_pipeline import HuggingFacePipeline
from langchain_community.document_loaders import PyPDFLoader, TextLoader, Docx2txtLoader, CSVLoader
from langchain import hub

from dotenv import load_dotenv
load_dotenv()


def split_docs(docs, chunk_size=1000, chunk_overlap=20):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    docs = text_splitter.split_documents(docs)
    return docs


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


embedding_model_name = os.environ["ST_EMBEDDING_MODEL"]
hf_llm = os.environ["HF_LLM"]

max_new_tokens = int(os.environ["max_new_tokens"])
do_sample = bool(os.environ["do_sample"])
temperature = float(os.environ["temperature"])
top_p = float(os.environ["top_p"])
top_k = int(os.environ["top_k"])
repetition_penalty = float(os.environ["repetition_penalty"])

quantization_loading_config = GPTQConfig(bits=4, disable_exllama=True)
tokenizer = AutoTokenizer.from_pretrained(
    hf_llm)

embedding_model = SentenceTransformerEmbeddings(
    model_name=embedding_model_name)

llm = HuggingFacePipeline.from_model_id(
    model_id=hf_llm,
    task="text-generation",
    device=0,
    model_kwargs={
        "quantization_config": quantization_loading_config
    },
    pipeline_kwargs={
        "max_new_tokens": max_new_tokens,
        "do_sample": do_sample,
        "temperature": temperature,
        "top_p": top_p,
        "top_k": top_k,
        "repetition_penalty": repetition_penalty
    },
)


def file_reader(XLoader, file_path):
    loader = XLoader(file_path)
    pages = loader.load_and_split()
    docs = split_docs(pages)
    return docs


def llm_processor(file_path, file_type, query):
    documents = []
    if file_type == "pdf":
        documents = file_reader(PyPDFLoader, file_path)
    elif file_type == "doc" or file_type == "docx":
        documents = file_reader(Docx2txtLoader, file_path)
    elif file_type == "txt":
        documents = file_reader(TextLoader, file_path)
    elif file_type == "csv":
        documents = file_reader(CSVLoader, file_path)
    else:
        print("Unsupported")
    db = Chroma.from_documents(documents, embedding_model)
    # "what happen leadsulphide treated with oxygen"
    chroma_retriever = db.as_retriever()
    prompt = hub.pull("rlm/rag-prompt")
    rag_chain = (
        {
            "context": chroma_retriever | format_docs,
            "question": RunnablePassthrough()
        }
        | prompt
        | llm
        | StrOutputParser()
    )
    return rag_chain.invoke(query)
