import re
from langchain_aws import ChatBedrock
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain.docstore.document import Document
from credentials import get_bedrock_client
from pyvis.network import Network


def issue_extraction(article):
    # It's recommended to specify the region, otherwise it will be inferred from your environment
    bedrock_runtime = get_bedrock_client()

    standard_model_id = "anthropic.claude-3-5-sonnet-20240620-v1:0"
    llm = ChatBedrock(
        client=bedrock_runtime,
        model_id=standard_model_id,
        model_kwargs={"temperature": 0, "max_tokens": 131072},
    )

    # Option 1
    transformer = LLMGraphTransformer(
        llm=llm,
        allowed_nodes=["Article", "Issue"],
        allowed_relationships=["has"],
        additional_instructions=f'''

        <Issue>:
          The question or problem posed by the Article.

        <Format>:
          <Article> has <Issue>

        <Descriptions>:
        Issue: The question or problem that the Article referring to. Issue questions or is questioned by the <Position> and the <Supported_Arguments/ Object_Arguments>

        <IMPORTANT DIRECTION RULES>:
        - Article HAS Issue (Article -> Issue)

        1. All extracted text must be written in Greek.
        2. Article can have a lot of issues'''
    )

    text = f"""
    The article is always one. Article:
    Title of the Article: {article}
    """

    documents = [Document(page_content=text)]
    graph_documents = transformer.convert_to_graph_documents(documents)

    print(graph_documents)

    return graph_documents