"""
Process run on UI startup.

- Get Project Settings
"""
import json
from os import path

from controls import PROJECTS_FOLDER 

def get_project_settings(project_name):
    global PROJECTS_FOLDER 
    
    with open(path.join(PROJECTS_FOLDER, project_name + ".txt")) as f: 
        project_str = f.read()
        try: 
            return json.loads(project_str)[0]
        except KeyError:
            print(f"Project information not found in {project_name}.")