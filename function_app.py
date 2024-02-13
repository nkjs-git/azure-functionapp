import azure.functions as func
import logging
import requests
import os
from requests.auth import HTTPBasicAuth

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

base_url = f"https://dev.azure.com/{os.environ.get('ENV_DEVOPS_ORG')}"
# Personal Access Token (PAT) with necessary permissions
pat = os.environ.get('ENV_PAT')

# Azure DevOps project name
project = os.environ.get('ENV_PROJ')

# Repository name
repository = os.environ.get('ENV_REPO')

# Source branch to create the release branch from
source_branch = os.environ.get('ENV_SORCE_BRANCH')

# New release branch name
release_branch = "release/5.0"

@app.route(route="nkjs_http_app")
def nkjs_http_app(req: func.HttpRequest) -> func.HttpResponse:
    try: 
        logging.info('Python HTTP trigger function processed a request.')

        url = f"{base_url}/{project}/_apis/git/repositories/{repository}/commits?searchCriteria.itemVersion.version={source_branch}&$top=1&api-version=7.1"
        
        headers = {
            "Content-Type": "application/json",
        }

        auth = HTTPBasicAuth("", pat)
        logging.info(f'Python HTTP trigger function: PAT is {pat}')
        logging.info(f'Python HTTP trigger function: repo url is {url}')
        # print(f"{url}")
        # Get the latest commit SHA for the source branch
        response = requests.get(url, headers=headers, auth=auth)
        # print(f"{response}")
        response.raise_for_status()
        source_commit_sha = response.json()["value"][0]["commitId"]
        logging.info(f'Python HTTP trigger function: latest commit id is {source_commit_sha}')
        # return func.HttpResponse(f"Python HTTP trigger function: latest commit id is {source_commit_sha}.")
        # print(f"{source_commit_sha}")

        # Create the release branch using the latest commit SHA of the source branch
        url = f"{base_url}/{project}/_apis/git/repositories/{repository}/refs?api-version=7.1"
        
        logging.info(f'Python HTTP trigger function: branch create url is {url}')

        payload = [
            {
                "name": f"refs/heads/{release_branch}",
                "oldObjectId": "0000000000000000000000000000000000000000",
                "newObjectId": source_commit_sha
            }
        ]

        response = requests.post(url, json=payload, headers=headers, auth=auth)
        response.raise_for_status()

        print(f"Release branch '{release_branch}' created successfully.")
        return func.HttpResponse(f"Python HTTP trigger function: Release branch '{release_branch}' created successfully.")
    except:
        logging.warn('Python HTTP trigger function: Error occured')
        return func.HttpResponse( "Python HTTP trigger function: Error occured", status_code=400)