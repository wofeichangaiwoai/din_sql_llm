

from langchain.callbacks import StreamingStdOutCallbackHandler
from langchain.callbacks.manager import AsyncCallbackManager, CallbackManager
from langchain.chains import ConversationalRetrievalChain
from langchain.vectorstores import VectorStore

from test.ingest import ingest_docs
from ubix.common.llm import get_llm
from ubix.common.logHander import LogHandler


class ConversationalRetrievalChainExt(ConversationalRetrievalChain):
    def prep_inputs(self, inputs: str):
        return super().prep_inputs({"question": inputs, "chat_history": []})


def get_kb_chain(llm
) -> ConversationalRetrievalChain:
    """Create a ChatVectorDBChain for question/answering."""
    # Construct a ChatVectorDBChain with a streaming llm for combine docs
    # and a separate, non-streaming llm for question generation
    manager = AsyncCallbackManager([])

    from langchain.chains import (
        LLMChain
    )
    from langchain.prompts import PromptTemplate

    combine_docs_chain = get_stuff_chain(llm)
    # vectorstore = ...
    vectorstore = ingest_docs()
    vectorstore._select_relevance_score_fn
    retriever = vectorstore.as_retriever(search_type="similarity_score_threshold",
                                         search_kwargs={"score_threshold": 0.6,  "k": 3})



# This controls how the standalone question is generated.
    # Should take `chat_history` and `question` as input variables.
    template = (
        "Combine the chat history and follow up question into "
        "a standalone question. Chat History: {chat_history}"
        "Follow up question: {question}"
    )
    prompt = PromptTemplate.from_template(template)
    question_generator_chain = LLMChain(llm=llm, prompt=prompt)
    question_generator_chain.callbacks = CallbackManager([StreamingStdOutCallbackHandler()])
    qa = ConversationalRetrievalChainExt(
        combine_docs_chain=combine_docs_chain,
        retriever=retriever,
        question_generator=question_generator_chain,
        callback_manager=manager,
    )

    qa.callbacks = CallbackManager([StreamingStdOutCallbackHandler(), LogHandler("conversation")])

    # qa = ChatVectorDBChainExt(
    #     vectorstore=vectorstore,
    #     combine_docs_chain=doc_chain,
    #     question_generator=question_generator,
    #     callback_manager=manager,
    # )
    return qa


def get_stuff_chain(llm):
    from langchain.chains import StuffDocumentsChain, LLMChain
    from langchain.prompts import PromptTemplate

    # This controls how each document will be formatted. Specifically,
    # it will be passed to `format_document` - see that function for more
    # details.
    document_prompt = PromptTemplate(
        input_variables=["page_content"],
        template="{page_content}"
    )
    document_variable_name = "context"
    # The prompt here should take as an input variable the
    # `document_variable_name`
    prompt = PromptTemplate.from_template(
        "Answer this question:{question}, Content: {context}"
    )
    llm_chain = LLMChain(llm=llm, prompt=prompt)
    llm_chain.callbacks = CallbackManager([StreamingStdOutCallbackHandler(), LogHandler("StuffDocuments")])

    chain = StuffDocumentsChain(
        llm_chain=llm_chain,
        document_prompt=document_prompt,
        document_variable_name=document_variable_name,
    )

    return chain


if __name__ == '__main__':
    llm = get_llm()
    print(f'LLM type:{type(llm)}')
    kb_chain = get_kb_chain(llm)
    question_list = [
        "What is black body radiation?",
        "Who is Ubix"
    ]
    for question in question_list:
        print(f"Begin: " + "====="*10)
        answer = kb_chain.run(question)
        print(answer)
        print(f"End: " + "====="*10)

"""
python ubix/chain/chain_kb_ubix.py
"""
