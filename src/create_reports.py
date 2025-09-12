import json
import logging
import os
import requests
import sys
import webbrowser
from datetime import datetime
from pathlib import Path
from requests.auth import HTTPBasicAuth

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'utils')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'jira')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'redmine')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'backlog')))
import utils
import jira
import redmine
import backlog

class Controller:
    def __init__(self):
        return

    def configure(self):
        jira.JiraManager().configure()
        redmine.RedmineManager().configure()
        backlog.BacklogManager().configure()
        return

    def run(self):
        head_file = Path(__file__).resolve().parent.parent / 'html' / 'sample_head.html'
        content = utils.loadText(head_file, False)

        managers = [jira.JiraManager(), redmine.RedmineManager(), backlog.BacklogManager()]
        for manager in managers:
            manager.run()
            for instance in manager.instances:
                for prj in instance.projects:
                    content += f'<tr><td>{manager.name}</td><td><a href="{prj.url}">{prj.name}</a></td><td>{len(prj.tickets)} tickets</td></tr>\n'

        tail_file = Path(__file__).resolve().parent.parent / 'html' / 'sample_tail.html'
        content += utils.loadText(tail_file, False)


        now = datetime.now()
        report_file = Path(__file__).resolve().parent.parent / 'html' / f'report-{now.strftime("%Y-%m-%d=%H-%M-%S")}.html'
        utils.saveText(report_file, content)

        webbrowser.open(f"file://{report_file}")
        return


def main():
    utils.initLog()
    controller = Controller()
    actions = {
        0: controller.configure,
        1: controller.run
    }
    choice = int(input("Do you want to configure or run projects report creation? (0: configure, 1: run): "))
    actions.get(choice, lambda: print("Unknown"))()

if __name__ == "__main__":
    main()
