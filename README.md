# Information-Extraction-Graph
A basic template for extracting structured information from public deliberations. We use the `LLMGraphTransformer` from LangChain with Claude 3.5 (hosted on AWS Bedrock). The data source is [OpenGov](https://www.opengov.gr/home/)

#### Pipeline
1. Retrieve the article title, content, and comments from the selected deliberation.
2. For the chosen deliberation, create a dictionary for each article containing:
   - `title`
   - `content`
   - `comments`
3. Use `LLMGraphTransformer` to extract Issues based on the article.
4. Based on the extracted Issues, identify the Position and Arguments from each comment. The model follows this reasoning:
   - Article -> Issue
   - Issue -> Position
   - Position -> Arguments
5. Merge the two graphs:
   - Article -> Issue
   - Issue -> Position -> Arguments
6. Generate an HTML file that visualizes the complete graph structure.

#### Important Note
We currently do not have an automated evaluation method for assessing the accuracy or quality of the extracted graph.
