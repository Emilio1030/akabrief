import streamlit as st
import numpy as np
from langchain.callbacks.base import BaseCallbackHandler
from langchain_openai import OpenAIEmbeddings
import os
from dotenv import load_dotenv

load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv('OPENAI_API_KEY')
embeddings_model = OpenAIEmbeddings(model="text-embedding-3-large")

# Chat model stream handler
class StreamHandler(BaseCallbackHandler):
    def __init__(
        self, container: st.delta_generator.DeltaGenerator, initial_text: str = ""
    ):
        self.container = container
        self.text = initial_text
        self.run_id_ignore_token = None

    def on_llm_start(self, serialized: dict, prompts: list, **kwargs):
        # Workaround to prevent showing the rephrased question as output
        if prompts[0].startswith("Human"):
            self.run_id_ignore_token = kwargs.get("run_id")

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        if self.run_id_ignore_token == kwargs.get("run_id", False):
            return
        self.text += token
        self.container.markdown(self.text)


# Retrieval handler
class PrintRetrievalHandler(BaseCallbackHandler):
    def __init__(self, container, msgs, calculate_similarity=False):
        # self.status = container.status("**Context Retrieval**")
        # self.msgs = msgs
        self.container = container
        self.msgs = msgs
        self.embeddings = embeddings_model
        self.calculate_similarity = calculate_similarity

    def on_retriever_start(self, serialized: dict, query: str, **kwargs):
        self.status.update(label=f"**Context Retrieval:** {query}")
        self.msgs.add_ai_message(f"Query: {query}")
        if self.calculate_similarity:
            self.query_embedding = self.embeddings.embed_query(query)

    def on_retriever_end(self, documents, **kwargs):
        source_msgs = ""
        for idx, doc in enumerate(documents):
            contents = doc.page_content

            similarity_txt = ""
            if self.calculate_similarity:
                content_embedding = self.embeddings.embed_query(contents)
                similarity = round(
                    self.cosine_similarity(self.query_embedding, content_embedding)
                    * 100
                )
                similarity_txt = f" \n* **Similarity score: {similarity}%**"

            source_msg = f"# Retrieval {idx+1}\n {similarity_txt}\n\n {contents}\n\n"

            self.status.write(source_msg, unsafe_allow_html=True)
            source_msgs += source_msg
        self.msgs.add_ai_message(source_msgs)
        self.status.update(state="complete")

    def cosine_similarity(self, embedding1, embedding2):
        return np.dot(embedding1, embedding2) / (
            np.linalg.norm(embedding1) * np.linalg.norm(embedding2)
        )


class DocProcessStreamHandler(BaseCallbackHandler):
    def __init__(
        self,
        container: st.delta_generator.DeltaGenerator,
        msgs,
        initial_text: str = "",
    ):
        self.container = container
        self.msgs = msgs
        self.text = initial_text

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        self.text += token
        self.container.markdown(self.text)

    def on_llm_end(self, response, **kwargs):
        self.msgs.add_ai_message(response)
        self.container.empty()
