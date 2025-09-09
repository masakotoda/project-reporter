import json
import logging
import os
import requests
import sys
from pathlib import Path
from requests.auth import HTTPBasicAuth

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'utils')))
import utils

class BacklogInstance:
    def __init__(self, config_folder):
        self.config_folder = Path(config_folder)

    def run(self):
        self.projects = self.fetchAllProject()
        #for prj in projects:
        #    print(f'Fetching {prj.key}...')
        #    self.fetchAllTickets(prj.key)
        self.fetchMyself()
 
    def getResponse(self, urlpath, params):
        baseurl = utils.loadText(self.config_folder / utils.baseurl_filename())
        token = utils.loadText(self.config_folder / utils.token_filename())

        headers = { "Accept": "application/json" }
        url = f"https://{baseurl}/{urlpath}?apiKey={token}"

        response = requests.request("GET", url, headers=headers, params=params)
        return response

    def fetchMyself(self):
        urlpath = "api/v2/users/myself"
        response = self.getResponse(urlpath, {})

        if utils.checkError(response, urlpath) == False:
            return []

        utils.dumpJson(response.text)
        return []

    def fetchAllProject(self):
        urlpath = "api/v2/projects"
        response = self.getResponse(urlpath, {})

        if utils.checkError(response, urlpath) == False:
            return []

        utils.dumpJson(response.text)

        obj = json.loads(response.text)

        items = obj

        projects = []
        for item in items:
            project = utils.Project(item['projectKey'], item['name'], '', '')
            projects.append(project)
        return projects

class BacklogManager:
    def __init__(self):
        self.name = "backlog"
        self.instances = []
        folders = utils.listConfigFolders(Path(__file__).resolve().parent)
        for folder in folders:
            self.instances.append(BacklogInstance(folder))

    def configure(self):
        baseurl = input("Enter Planio Redmine URL (eg. your-company.backlog.com): ")
        token = input("Enter your API token (see https://masakobear.backlog.com/EditApiSettings.action): ")
        headers = { "Accept": "application/json" }
        url = f'https://{baseurl}/api/v2/users/myself?apiKey={token}'

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
    manager = BacklogManager()
    actions = {
        0: manager.configure,
        1: manager.run
    }
    choice = int(input("Do you want to configure for Redmine or run existing configuration? (0: configure, 1: run): "))
    actions.get(choice, lambda: print("Unknown"))()

if __name__ == "__main__":
    main()
