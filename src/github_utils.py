from github import Github
from collections.abc import MutableMapping
import base64

def get_all_files(repo, path=""):
    
    files = {}
    contents = repo.get_contents(path)
    for content in contents:
        if content.type == "dir":
            files[content.path] = get_all_files(repo, content.path)
        else:
            files[content.path] = content.content # base64
    return files

def decode_files(files):
    
    decoded_files = {}
    for path, content in files.items():
        if isinstance(content, dict):
            # Recursively decode nested dictionaries
            decoded_files[path] = decode_files(content)
        else:
            # Decode the base64-encoded content
            decoded_files[path] = base64.b64decode(content.encode('utf-8')).decode('utf-8')
    return decoded_files

def flatten(dictionary, parent_key='', separator='_'):
    
    items = []
    for key, value in dictionary.items():
        if isinstance(value, MutableMapping):
            items.extend(flatten(value, key, separator=separator).items())
        else:
            items.append((key, value))
    return dict(items)