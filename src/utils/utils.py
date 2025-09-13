import os
import re
import json
import logging

def initLog():
    logging.basicConfig(level=logging.ERROR)

def dumpJson(json_str):
    print(json.dumps(json.loads(json_str), sort_keys=True, indent=4, separators=(',', ': ')))

def loadText(filename, strip=True):
    with open(filename, 'r', encoding='utf-8') as file:
        text = file.read()
    return text.strip()

def saveText(filename, text):
    with open(filename, "w", encoding="utf-8") as file:
        file.write(text)

def saveConfig(new_dir, baseurl, email, token):
    new_dir.mkdir(parents=True, exist_ok=True)
    saveText(new_dir / baseurl_filename(), baseurl)
    saveText(new_dir / email_filename(), email)  
    saveText(new_dir / token_filename(), token)
    print(f'Configuration saved in folder: {new_dir}')

def checkError(response, urlpath):
    if response is None:
        logging.error(f"Failed to receive response. URL: {urlpath}")
        return False

    status = response.status_code
    if (status != 200 or response.text is None):
        logging.error(f"Failed to receive response body. URL: {urlpath}, Status: {status}")
        return False

    return True

def listConfigFolders(path):
    try:
        folders = [os.path.join(path, name) for name in os.listdir(path)
                   if os.path.isdir(os.path.join(path, name)) and name.startswith('config')]
        return folders
    except FileNotFoundError:
        print(f"Path not found: {path}")
        return []
    except Exception as e:
        print(f"Error: {e}")
        return []
    
def contains_illegal_filename_chars(filename):
    # Windows forbidden characters: \ / : * ? " < > |
    # POSIX (Linux/macOS) is more permissive, but '/' is still illegal
    illegal_pattern = r'[\\/:*?"<>|]'
    return bool(re.search(illegal_pattern, filename))

def sanitize_filename(filename):
    # Windows forbidden characters: \ / : * ? " < > |
    illegal_pattern = r'[\\/:*?"<>|]'
    return re.sub(illegal_pattern, '-', filename)

def baseurl_filename():
    return 'base-url.txt'

def email_filename():
    return 'email-address.txt'

def token_filename():
    return 'api-token.txt'

def createConfigFolder(base_path):
    while True:
        config_name = str(input("Give a name for new configuration: "))
        config_name = sanitize_filename(config_name)
        new_dir = base_path / f'config{config_name}'
        if new_dir.exists() and new_dir.is_dir():
            print(f"Configuration folder '{new_dir}' already exists. Please choose a different name.")
        else:
            return new_dir
        
class Ticket:
    def __init__(self, key, summary, issue_type, status, due_date, estimated_hours):
        self.key = key
        self.summary = summary
        self.issue_type = issue_type
        self.status = status
        self.due_date = due_date
        self.estimated_hours = estimated_hours

class Project:
    def __init__(self, key, name, type, url):
        self.key = key
        self.name = name
        self.type = type
        self.url = url
        self.tickets = []
        self.id = 0

    def addTickets(self, tickets):
        self.tickets += tickets

