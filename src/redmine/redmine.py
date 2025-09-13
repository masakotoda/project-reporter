import json
import logging
import os
import requests
import sys
from pathlib import Path
from requests.auth import HTTPBasicAuth

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'utils')))
import utils

class RedmineInstance:
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
        token = utils.loadText(self.config_folder / utils.token_filename())

        #auth = HTTPBasicAuth(email, token)
        headers = { 'Accept': 'application/json', 'X-Redmine-API-Key': token }
        url = f"https://{baseurl}/{urlpath}"

        response = requests.request("GET", url, headers=headers,  params=params)
        return response


    def fetchAllProject(self):
        urlpath = "projects.json"
        response = self.getResponse(urlpath, {})

        if utils.checkError(response, urlpath) == False:
            return []

        utils.dumpJson(response.text)

        obj = json.loads(response.text)
        total_count = obj.get('total_count', 0)

        if total_count == 0:
            print("No projects found.")
            return []

        items = obj.get('projects', [])

        projects = []
        for item in items:
            project = utils.Project(item['identifier'], item['name'], '', '')
            project.url = f'https://{self.baseUrl()}/projects/{item["identifier"]}'
            projects.append(project)
        return projects


    def fetchAllTickets(self, project_key):
        urlpath = "issues.json?offset=0&limit=100&project_id=" + project_key
        response = self.getResponse(urlpath, {})

        if utils.checkError(response, urlpath) == False:
            return []

        # utils.dumpJson(response.text)

        if response.status_code == 200:
            issues = response.json().get("issues", [])
            tickets = []
            for issue in issues:
                key = issue["id"]
                summary = issue["subject"]
                issue_type = issue["tracker"]["name"]
                status = issue["status"]["name"]
                due_date = issue["due_date"]
                estimated_hours = issue["estimated_hours"]
                # print(f"- {key}: [{issue_type}] {summary} (Status: {status})")
                ticket = utils.Ticket(key, summary, issue_type, status, due_date, estimated_hours)
                tickets.append(ticket)
            return tickets
        else:
            return []
    
class RedmineManager:
    def __init__(self):
        self.name = "redmine"
        self.instances = []
        folders = utils.listConfigFolders(Path(__file__).resolve().parent)
        for folder in folders:
            self.instances.append(RedmineInstance(folder))

    def configure(self):
        baseurl = input("Enter Planio Redmine URL (eg. your-company.planio.jp): ")
        token = input("Enter your API token (see https://your-company.planio.jp/my/account): ")
        headers = { 'Accept': 'application/json', 'X-Redmine-API-Key': token}
        url = f'https://{baseurl}/users/current.json'

        # Check if the credentials are valid
        response = requests.request("GET", url, headers=headers)
        if utils.checkError(response, url) == False:
            return
        
        # If valid, let the user choose a config folder name
        new_dir = utils.createConfigFolder(Path(__file__).resolve().parent)
        if new_dir is None:
            return
        
        # Create the new config folder and save the details
        utils.saveConfig(new_dir, baseurl, "", token)

    def run(self):
        for instance in self.instances:
            instance.run()


def main():
    utils.initLog()
    manager = RedmineManager()
    actions = {
        0: manager.configure,
        1: manager.run
    }
    choice = int(input("Do you want to configure for Redmine or run existing configuration? (0: configure, 1: run): "))
    actions.get(choice, lambda: print("Unknown"))()

if __name__ == "__main__":
    main()
