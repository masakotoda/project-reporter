import json
import logging
import os
import requests
import re
import sys
from pathlib import Path
from requests.auth import HTTPBasicAuth

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'utils')))
import utils

class JiraInstance:
    def __init__(self, config_folder):
        self.config_folder = Path(config_folder)

    def run(self):
        self.projects = self.fetchAllProject()
        for prj in self.projects:
            print(f'Fetching {prj.key}...')
            prj.addTickets(self.fetchAllTickets(prj.key))

    def baseUrl(self):
        return utils.loadText(self.config_folder / utils.baseurl_filename())

    def getResponse(self, urlpath, params):
        baseurl = self.baseUrl()
        email = utils.loadText(self.config_folder / utils.email_filename())
        token = utils.loadText(self.config_folder / utils.token_filename())

        headers = { "Accept": "application/json" }
        auth = HTTPBasicAuth(email, token)
        url = f"http://{baseurl}/{urlpath}"

        response = requests.request("GET", url, headers=headers, auth=auth, params=params)
        return response

    def fetchAllProject(self):
        urlpath = "rest/api/latest/project"
        response = self.getResponse(urlpath, {})

        if utils.checkError(response, urlpath) == False:
            return []

        # utils.dumpJson(response.text)

        items = json.loads(response.text)

        projects = []
        for item in items:
            project_type_key = item["projectTypeKey"]
            project = utils.Project(item['key'], item['name'], project_type_key, item['self'])
            #project.url = item['self'].replace('/rest/api/latest/project/', '/projects/')
            pattern = r'/rest/api/(latest|\d+)/project/'
            project.url = re.sub(pattern, '/projects/', item['self'])
            projects.append(project)
        return projects


    def fetchAllTickets(self, project_key):
        jql_query = f"project = {project_key} AND issuetype != Epic"
        params = {
            "jql": jql_query,
            "maxResults": 500,  # adjust as needed
            "fields": ["summary", "issuetype", "status"]
        }
        urlpath = f"rest/api/latest/search"
        response = self.getResponse(urlpath, params);

        if utils.checkError(response, urlpath) == False:
            return []
        if response.status_code == 200:
            issues = response.json().get("issues", [])
            tickets = []
            for issue in issues:
                key = issue["key"]
                summary = issue["fields"]["summary"]
                issue_type = issue["fields"]["issuetype"]["name"]
                status = issue["fields"]["status"]["name"]
                ticket = utils.Ticket(key, summary, issue_type, status, None, None)
                tickets.append(ticket)
                #print(f"- {key}: [{issue_type}] {summary} (Status: {status})")
            return tickets
        else:
            return []
        
class JiraManager:
    def __init__(self):
        self.name = "jira"
        self.instances = []
        folders = utils.listConfigFolders(Path(__file__).resolve().parent)
        for folder in folders:
            self.instances.append(JiraInstance(folder))

    def configure(self):
        baseurl = input("Enter Jira URL (eg. your-company.atlassian.net): ")
        email = input("Enter your email address associated with Jira: ")
        token = input("Enter your API token (see https://id.atlassian.com/manage-profile/security/api-tokens): ")
        headers = { "Accept": "application/json" }
        auth = HTTPBasicAuth(email, token)
        url = f"http://{baseurl}/rest/api/latest/myself"

        # Check if the credentials are valid
        response = requests.request("GET", url, headers=headers, auth=auth)
        if utils.checkError(response, url) == False:
            return
        
        # If valid, let the user choose a config folder name
        new_dir = utils.createConfigFolder(Path(__file__).resolve().parent)
        if new_dir is None:
            return
        
        # Create the new config folder and save the details
        utils.saveConfig(new_dir, baseurl, email, token)

    def run(self):
        for instance in self.instances:
            instance.run()

def main():
    utils.initLog()
    manager = JiraManager()
    actions = {
        0: manager.configure,
        1: manager.run
    }
    choice = int(input("Do you want to configure for Jira or run existing configuration? (0: configure, 1: run): "))
    actions.get(choice, lambda: print("Unknown"))()

if __name__ == "__main__":
    main()
