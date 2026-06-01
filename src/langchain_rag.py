from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
import json

load_dotenv()


def load_documents(path: str = "data/documents.json") -> list[dict]:
    with open(path) as f:
        return json.load(f)


def build_vectorstore(documents: list[dict], persist_dir: str = ".chroma_lc") -> Chroma:
    """
    Build a Chroma vector store using LangChain's components.
    Maps to: your embedder.py + vector_store.py + chunker.py combined.
    """
    # LangChain's text splitter — same concept as your chunker.py
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100,
        separators=["\n\n", "\n", ". ", " ", ""]
    )

    # Convert your JSON docs to LangChain Document objects
    from langchain_core.documents import Document
    lc_docs = []
    for doc in documents:
        chunks = splitter.split_text(doc["text"])
        for chunk in chunks:
            lc_docs.append(Document(
                page_content=chunk,
                metadata={
                    "source": doc["source"],
                    "category": doc["category"],
                    "id": doc["id"]
                }
            ))

    print(f"Created {len(lc_docs)} LangChain document chunks.")

    # LangChain's embedding wrapper — same as your embedder.py
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    # Build and persist the vector store
    vectorstore = Chroma.from_documents(
        documents=lc_docs,
        embedding=embeddings,
        persist_directory=persist_dir,
        collection_name="techflow_lc"
    )
    print(f"Vector store built at {persist_dir}.")
    return vectorstore


def load_vectorstore(persist_dir: str = ".chroma_lc") -> Chroma:
    """Load an existing vector store without rebuilding."""
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    return Chroma(
        persist_directory=persist_dir,
        embedding_function=embeddings,
        collection_name="techflow_lc"
    )


def build_rag_chain(vectorstore: Chroma):
    """
    Build a RAG chain using LangChain Expression Language (LCEL).
    The | operator connects steps into a pipeline — same as your rag.py
    but expressed as a composable chain.
    """
    # Retriever wraps the vector store — same as your retrieve() function
    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 5}
    )

    # Prompt template — same as your system_prompt in rag.py
    prompt = ChatPromptTemplate.from_template("""
You are a helpful support assistant for TechFlow.
Answer the user's question using ONLY the information in the provided context.
Always cite your source using the format [Source: X].
If the context does not contain enough information to answer, say so clearly.

Context:
{context}

Question: {question}
""")

    # LLM — same as your OpenAI client calls
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    # Format retrieved docs into a single context string
    def format_docs(docs) -> str:
        return "\n\n".join([
            f"[Source: {doc.metadata.get('source', 'Unknown')} | "
            f"Category: {doc.metadata.get('category', 'Unknown')}]\n{doc.page_content}"
            for doc in docs
        ])

    # LCEL chain: input → retrieve → format → prompt → LLM → parse output
    # RunnablePassthrough passes the question through unchanged to the prompt
    chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    return chain, retriever


def ask_langchain(query: str, chain) -> dict:
    """Run a query through the LangChain RAG chain."""
    answer = chain.invoke(query)
    return {
        "query": query,
        "answer": answer
    }