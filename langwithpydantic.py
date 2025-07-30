import re
from langchain_aws import ChatBedrock
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain.docstore.document import Document
from credentials import get_bedrock_client
from pyvis.network import Network
import json

def merge_graph_documents(issue_docs, graph_docs):
    """
    Merge multiple graph documents into a single graph document by deduplicating
    nodes and relationships.
    """
    merged_nodes = {}
    merged_relationships = set()

    def add_node(node):
        if node.id not in merged_nodes:
            merged_nodes[node.id] = node

    def add_relationship(rel):
        key = (rel.source.id, rel.target.id, rel.type)
        merged_relationships.add((key, json.dumps(rel.properties, ensure_ascii=False)))

    # Add all nodes and relationships from issue_docs (e.g. Article -> Issue)
    for doc in issue_docs:
        for node in doc.nodes:
            add_node(node)
        for rel in doc.relationships:
            add_relationship(rel)

    # Add all nodes and relationships from graph_docs (e.g. Issue -> Position -> Arguments)
    for doc in graph_docs:
        for node in doc.nodes:
            add_node(node)
        for rel in doc.relationships:
            add_relationship(rel)

    # Convert to list
    merged_node_list = list(merged_nodes.values())
    merged_rel_list = []
    for (src_tgt_type, props_json) in merged_relationships:
        src_id, tgt_id, rel_type = src_tgt_type
        props = json.loads(props_json)
        merged_rel_list.append({
            'source_id': src_id,
            'target_id': tgt_id,
            'type': rel_type,
            'properties': props
        })

    merge_graph = {
        'nodes': merged_node_list,
        'relationships': merged_rel_list
    }

    return merge_graph


def position_argument_extraction(issue_nodes, comments, index):
    # It's recommended to specify the region, otherwise it will be inferred from your environment
    bedrock_runtime = get_bedrock_client()

    standard_model_id = "anthropic.claude-3-5-sonnet-20240620-v1:0"
    llm = ChatBedrock(
        client=bedrock_runtime,
        model_id=standard_model_id,
        model_kwargs={"temperature": 0, "max_tokens": 131072},
    )

    issues = []
    for doc in issue_nodes:
        for node in doc.nodes:
            if node.type == "Issue":
                issues.append(node.id)

    # Option 1
    transformer = LLMGraphTransformer(
        llm=llm,
        allowed_nodes=["Issue", "Position", "Supported_Arguments", "Object_Arguments"],
        allowed_relationships=["has_position", "supported_because", "is_not_supported_because"],
        additional_instructions=f'''
        Issue List:
        {issues}
        
        <Format>:
          <Issue> has_position <Position>
          <Position> supported because <Supporting_Arguments>
          <Position> objected because <Objecting_Arguments>

        <Descriptions>:
        Issue: <The issue that the position belong to>
        Position: <The point of view expressed by the user in the comment. It should respond to the point of the Issue/Article. A comment doesn't mean that will have a position inside>
        Supported_Arguments: <How the user supports his position.>
        Object_Arguments: <How the user Objects to the position>

        <IMPORTANT DIRECTION RULES>:
        - Issue HAS_POSITION Position (Issue -> Position)
        - Position SUPPORTED_BECAUSE Supporting_Arguments (Position -> Supporting_Arguments)  
        - Position IS_NOT_SUPPORTED_BECAUSE Objecting_Arguments (Position -> Objecting_Arguments)
        - NEVER reverse these directions!

        1. All extracted text must be written in Greek.
        2. An issue can have a lot of positions.
        3. A Position could have a lot of arguments. But also none.
        4. If the type of node is Issue then the name/id of the node should be exactly as it is inside the Issue List'''
    )

    all_graph_docs = []
    temp_parts = []

    for idx, comment in enumerate(comments[:30]):
        text = f"""
        Σχολιο {idx + 1}
        {comment}"""
        print(idx + 1, '/', len(comments))

        documents = [Document(page_content=text)]
        graph_documents = transformer.convert_to_graph_documents(documents)
        all_graph_docs.extend(graph_documents)

        comment_section = [f"Comment: {comment}"]

        for graph_document in graph_documents:
            positions = [node.id for node in graph_document.nodes if node.type == 'Position']
            Sup_arguments = [node.id for node in graph_document.nodes if node.type == 'Supported_arguments']
            Obj_arguments = [node.id for node in graph_document.nodes if node.type == 'Object_arguments']

            if positions and Sup_arguments:
                comment_section.append("Position -> Supported Arguments:")
                for p_idx, pos in enumerate(positions):
                    args_list = " | ".join(Sup_arguments)  # Join all arguments
                    comment_section.append(f"{p_idx}.  {pos} -> {args_list}")
            elif positions:
                comment_section.append("Positions (no Supported arguments):")
                comment_section.extend([f"  {pos}" for pos in positions])
            elif Sup_arguments:
                comment_section.append("Arguments (no positions):")
                comment_section.extend([f"  {arg}" for arg in Sup_arguments])

            if positions and Obj_arguments:
                comment_section.append("Position -> Object Arguments:")
                for p_idx, pos in enumerate(positions):
                    args_list = " | ".join(Obj_arguments)  # Join all arguments
                    comment_section.append(f"{p_idx}.  {pos} -> {args_list}")
            elif positions:
                comment_section.append("Positions (no Object arguments):")
                comment_section.extend([f"  {pos}" for pos in positions])
            elif Obj_arguments:
                comment_section.append("Arguments (no positions):")
                comment_section.extend([f"  {arg}" for arg in Obj_arguments])

            comment_section.append("-" * 50)
            temp_parts.append("\n".join(comment_section))

        temp = "\n".join(temp_parts)

    with open("output/response.txt", "w", encoding="utf-8") as f:
        f.write(temp)

    merged_graph = merge_graph_documents(issue_nodes, all_graph_docs)
    all_graph_docs =[merged_graph]
    print("Merged Graph", merged_graph)

    net = Network(notebook=True, cdn_resources="remote", directed=True, height='100vh')
    net.force_atlas_2based()

    if all_graph_docs:
        for graph_document in all_graph_docs:
            for node in graph_document['nodes']:
                label = node.id[:40] + '...' if len(node.id) > 40 else node.id
                if node.type == "Position":
                    color = "#FFCC00"
                elif node.type == "Supported_arguments":
                    color = "#7BE141"
                elif node.type == "Object_arguments":
                    color = "#FF9999"
                elif node.type == "Issue":
                    color = "#97C2FC"
                elif node.type == "Article":
                    color = "#00F8FF"
                net.add_node(node.id, label=label, title=node.id, color=color)

            # Add edges with arrow
            for rel in graph_document['relationships']:
                net.add_edge(rel["source_id"], rel["target_id"], label=rel["type"], arrows='to')

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
