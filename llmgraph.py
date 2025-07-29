import boto3
from langchain_aws import ChatBedrock
from langchain_community.graphs import graph_document
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain.docstore.document import Document
from credentials import get_bedrock_client
from pyvis.network import Network


def merge_graph_documents(graph_docs):
    """Merge multiple graph documents into one, based on node types and semantic similarity"""
    merged_nodes = {}  # original_node_id -> merged_node
    unique_nodes = []  # List of unique merged nodes
    merged_relationships = []
    article_node = None  # There should be only one article node

    # Collect all nodes first
    all_nodes = []
    all_relationships = []

    for graph_doc in graph_docs:
        all_nodes.extend(graph_doc.nodes)
        all_relationships.extend(graph_doc.relationships)

    # First pass: identify unique nodes and create mapping
    for node in all_nodes:
        # Special handling for Article nodes - should be unique
        if node.type == "Article":
            if article_node is None:
                article_node = node
                unique_nodes.append(article_node)
            # Map ALL article nodes to the first one
            merged_nodes[node.id] = article_node
            continue

        # Add as new unique node
        unique_nodes.append(node)
        merged_nodes[node.id] = node

    # Second pass: create relationships with proper mapping
    for rel in all_relationships:
        # Get the mapped nodes
        source_node = merged_nodes.get(rel.source.id, rel.source)
        target_node = merged_nodes.get(rel.target.id, rel.target)

        # print(f"{source_node.id} ({source_node.type}) -> {target_node.id} ({target_node.type})")
        # if source_node.type == 'Position' and target_node.type == 'Article':
        #     print(f"Types: ({source_node.type}) -> ({target_node.type})")
        #     temp = source_node
        #     source_node = target_node
        #     target_node = temp

        # Create new relationship with mapped node references
        # Use a more robust way to create the relationship
        new_rel = type(rel)(
            source=source_node,
            target=target_node,
            type=rel.type
        )

        merged_relationships.append(new_rel)

    # Remove duplicate relationships
    unique_relationships = []
    seen_rels = set()

    for rel in merged_relationships:
        # Create a unique identifier for the relationship
        rel_id = (rel.source.id, rel.target.id, rel.type)
        if rel_id not in seen_rels:
            unique_relationships.append(rel)
            seen_rels.add(rel_id)

    # Create merged graph document
    first_graph = graph_docs[0]

    # Create a dictionary with all the original attributes
    graph_dict = {
        'nodes': unique_nodes,
        'relationships': unique_relationships
    }

    # Add any additional fields that exist in the original graph document
    for attr in ['source', 'page_content', 'metadata']:
        if hasattr(first_graph, attr):
            graph_dict[attr] = getattr(first_graph, attr)

    merged_graph = type(first_graph)(**graph_dict)

    return merged_graph


def llmgraph(article, comments, index):
    # It's recommended to specify the region, otherwise it will be inferred from your environment
    bedrock_runtime = get_bedrock_client()
    model_id = "arn:aws:bedrock:us-east-1:043309345392:inference-profile/us.anthropic.claude-3-5-sonnet-20240620-v1:0"

    standard_model_id = "anthropic.claude-3-5-sonnet-20240620-v1:0"
    llm = ChatBedrock(
        client=bedrock_runtime,
        model_id=standard_model_id,
        model_kwargs={"temperature": 0, "max_tokens": 131072},
    )

    # Option 1
    transformer = LLMGraphTransformer(
        llm=llm,
        allowed_nodes=["Article", "Position", "Supported_Arguments", "Object_Arguments"],
        allowed_relationships=["has", "supported_because", "is_not_supported_because"],
        additional_instructions='''
        <Issue>:
          The question or problem posed by the Article.
        
        <Format>:
          Issue has <Position>
          <Position> supported because <Supporting_Arguments>
          <Position> objected because <Objecting_Arguments>

        <Descriptions>:
        Issue: The question or problem posed by the Article.
        Position: <The point of view expressed by the user in the comment. It should respond to the point of the Issue/Article.>
        Supported_Arguments: <How the user supports his position.>
        Object_Arguments: <How the user Objects to the position>
        
        <IMPORTANT DIRECTION RULES>:
        - Article HAS Position (Article -> Position)
        - Position SUPPORTED_BECAUSE Supporting_Arguments (Position -> Supporting_Arguments)  
        - Position IS_NOT_SUPPORTED_BECAUSE Objecting_Arguments (Position -> Objecting_Arguments)
        - NEVER reverse these directions!
        
        1. All extracted text must be written in Greek.'''
    )

    all_graph_docs = []
    for idx, comment in enumerate(comments):
        text = f"""
        Άρθρο
        {article}
        Σχολιο {idx+1}
        {comment}"""
        print(idx+1, '/', len(comments))

        documents = [Document(page_content=text)]
        graph_documents = transformer.convert_to_graph_documents(documents)
        all_graph_docs.extend(graph_documents)

    if all_graph_docs:
        merged_graph = merge_graph_documents(all_graph_docs)
        graph_documents = [merged_graph]

    # Create a Pyvis network object
    # Create Pyvis network with better layout
    net = Network(notebook=True, cdn_resources="remote", directed=True, height='100vh')
    net.force_atlas_2based()

    # Add nodes with color coding
    if graph_documents:

        graph_document = graph_documents[0]
        for node in graph_document.nodes:
            label = node.id[:40] + '...' if len(node.id) > 40 else node.id
            # color = "#97C2FC"
            if node.type == "Position":
                color = "#FFCC00"
            elif node.type == "Supported_arguments":
                color = "#7BE141"
            elif node.type == "Object_arguments":
                color = "#FF9999"
            else:
                color = "#97C2FC"
            net.add_node(node.id, label=label, title=node.id, color=color)

        # Add edges with arrow
        for rel in graph_document.relationships:
            net.add_edge(rel.source.id, rel.target.id, label=rel.type, arrows='to')

    # Optional advanced styling
    net.set_options("""
    var options = {
      "nodes": {
        "shape": "box",
        "font": {
          "face": "arial",
          "size": 14,
          "multi": "html"
        }
      },
      "edges": {
        "arrows": {
          "to": {
            "enabled": true
          }
        },
        "smooth": {
          "enabled": true
        }
      },
      "physics": {
        "enabled": true,
        "barnesHut": {
          "gravitationalConstant": -8000,
          "springLength": 250
        }
      }
    }
    """)

    # Show
    net.show(f"output/article{index}.html")