import os
from langchain.document_loaders.base import BaseLoader
from langchain.chat_models import ChatOpenAI
from langchain.prompts.chat import ChatPromptTemplate
import src.ai_outputparsers as parsers

class CustomCodeLoader(BaseLoader):
    
    # Mapping of file extensions to their corresponding languages
    extension_to_language = {
        '.py': 'python',
        '.ipynb': 'jupyter notebook',
        '.r': 'R',
        '.js': 'javascript',
        # Add more mappings as needed
    }

    def __init__(self, files):
        
        self.files = files

    def get_language_from_extension(self, file_path):
        
        _, extension = os.path.splitext(file_path)
        return self.extension_to_language.get(extension.lower(), 'unknown')

    def load(self):
       
        for path, content in self.files.items():
            if isinstance(content, str):
                language = self.get_language_from_extension(path)
                document = {
                    'page_content': content,
                    'metadata': {
                        'path': path,
                        'language': language
                    }
                }
                yield document

    
def get_repo_overview(documents, openai_api_key):
    
    template = """
    You are a helpful assistant who generates summarizations of code to build a README file. 
    Give me a one paragraph with a brief overview of what is the repo for. 
    """
    human_template = "Repo content: {documents}"

    chat_prompt = ChatPromptTemplate.from_messages([
        ("system", template),
        ("human", human_template),
    ])
    
    chain = chat_prompt | ChatOpenAI(openai_api_key = openai_api_key) | parsers.FormattedOutputConvertToText()
    answer = chain.invoke({"documents": documents})

    return(answer)


def get_repo_structure(documents, openai_api_key):  

    template = """
    You are a helpful assistant who helps to build a README file. 
    Return your answer as a tree generator with no further explanations. 
    """

    human_template = """
    This are the list of paths of the reposoitory files: {list_of_paths}.
    Give me the repo structure.
    """

    chat_prompt = ChatPromptTemplate.from_messages([
        ("system", template),
        ("human", human_template),
    ])

    chain = chat_prompt | ChatOpenAI(openai_api_key=openai_api_key) | parsers.MarkdownTreeStructureOutputParser()
    answer = chain.invoke({"list_of_paths": [document["metadata"]["path"] for document in documents]})

    return(answer)


def getting_started(repo_name, documents, openai_api_key):
    
    template = """
    You are a helpful assistant who helps built a README file for a Github repository. 
    Give me instructions on how to to get started. detailing the steps for cloning the repository 
    and the steps for installing dependencies. 
    """

    human_template = """
    Repo Name: {repo}. 
    List of files: {file_paths}. 
    Content of files: {contents}
    """

    chat_prompt = ChatPromptTemplate.from_messages([
        ("system", template),
        ("human", human_template),
    ])

    chain = chat_prompt | ChatOpenAI(openai_api_key = openai_api_key) | parsers.FormattedOutputConvertToText()
    answer = chain.invoke({"repo": repo_name, "file_paths": [doc["metadata"]["path"] for doc in documents],"contents": [doc["page_content"] for doc in documents]})

    return answer


def get_file_summaries(documents, openai_api_key):
    
    template = """
    You are a helpful assistant who generates summarizations of code to build a README file. 
    Return your response in the format File Path: the_file_path Summary: the_summary
    """
    human_template = "The file {path} has this content: {content}"
    
    chat_prompt = ChatPromptTemplate.from_messages([
        ("system", template),
        ("human", human_template),
    ])

    chain = chat_prompt | ChatOpenAI(openai_api_key = openai_api_key) | parsers.FormattedOutputParserSummary()

    # List of summaries
    summaries = []

    for document in documents:
        # Extract the path and code content from each document
        path = document["metadata"]["path"]
        content = document["page_content"]

        # Invoke the chain for each document
        response = chain.invoke({"path": path, "content": content})

        # Append the generated summary to the summaries list
        summaries.append(response)

    return summaries
        