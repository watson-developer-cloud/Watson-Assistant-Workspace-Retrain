import time
import logging

from typing import List
from configparser import ConfigParser
from pathlib import Path

from tqdm import tqdm
from ibm_watson import AssistantV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

class Variables:
    # CONSTANTS
    BASELINE = "baseline"
    BETA = "beta"
    SUCCESS_STATUS = 200
    LIMIT = 30
    SLEEP_THIRTY_MINUTES = 1800
    CHARACTER_LIMIT = 128
    AVAIL = "Available"
    TRAINING = "Training"
    RETRAIN_FILE = "retrain_manually.txt"
    DESCRIPTION = "RETRAINED"
    ENTITY = "entity"
    INTENT = "intent"

    global_wksp_counter = 0

path_cfg = Path(f"{Path(__file__).parents[1]}/config.ini")
config = ConfigParser()
config.read_file(open(path_cfg))
instance_url = config['INSTANCE_PARAMETERS'].get("URL", "")
api_key = config['INSTANCE_PARAMETERS'].get("API_KEY", "")
auth_url = config["AUTHENTICATION"].get("AUTH_URL", "")

if not any(instance_url):
    print("Please provide an instance url in the `config.ini`. See ReadMe for directions.")
    exit()
if not any(api_key):
    print("Please provide an `API KEY` url in the `config.ini`. See ReadMe for directions.")
    exit()
if not any(auth_url):
    print("Please provide an IAM URL in the `config.ini`.\n" +
     "See https://cloud.ibm.com/apidocs/assistant-v1?code=python#authentication for directions.")
    exit()

authenticator = IAMAuthenticator(api_key, url=auth_url)
assistant = AssistantV1(
    version='2021-06-14',
    authenticator = authenticator
)
assistant.set_service_url(instance_url)

def save_workspace(wksp_id, filename):
    with open(Path(filename), mode='a') as f:
        f.writelines(wksp_id + "\n")

def get_workspaces() -> List:
    response = assistant.list_workspaces().get_result()
    return response['workspaces']
    
def get_intents(wksp_id):
    intents = assistant.list_intents(workspace_id=wksp_id).get_result()
    intents = intents['intents']
    if not len(intents):
        return None
    
    return intents[0]

def get_entities(wksp_id):
    entities = assistant.list_entities(workspace_id=wksp_id).get_result()
    entities = entities['entities']
    if not len(entities):
        return None
    
    return entities[0]

def create_new_desc(desc: str):
    if len(desc) == Variables.CHARACTER_LIMIT:
        return desc.upper()
    desc = f"{desc} {Variables.DESCRIPTION}"

    return desc

def update(obj: dict, workspace_id):
    new_desc = create_new_desc(obj.get('description', ''))
    if Variables.ENTITY in obj.keys():
        return update_entity_desc(obj, workspace_id, new_desc)
    if Variables.INTENT in obj.keys():
        return update_intent_desc(obj, workspace_id, new_desc)

def update_intent_desc(intent: dict, workspace_id: str, new_description):
    response = assistant.update_intent(workspace_id=workspace_id, 
                                    intent=intent['intent'], new_description=new_description)

    return response

def update_entity_desc(entity: dict, workspace_id: str, new_description):
    response = assistant.update_entity(workspace_id=workspace_id, 
                                    entity=entity['entity'], new_description=new_description)

    return response

def retrain_wksp():
    """The `retrain_wksp` function works by updating the description
    of a single intent. This causes the workspace to retrain.

    The first intent retrieved by the `get_intents()` function
    is updated with the description, "RETRAINED".
    This script is limited by the fact that there is a rate limit of
    30 requests/30 minutes. Thus, after 30 workspaces, this script sleeps
    for 30 minutes to reset the rate limiting window.
    """

    workspaces = get_workspaces()

    # step 1: go through all workspaces and launch the training
    workspaces_pbar = tqdm(workspaces, desc="Retraining Workspaces")
    for wksp in workspaces_pbar:
        wksp_id = wksp['workspace_id']
        workspaces_pbar.set_description(f"Processing Workspace: {wksp_id}")
        obj = get_intents(wksp_id)
        if obj is None:
            logging.warning("Workspace doesn't have intents. Trying to get entities")
            obj = get_entities(wksp_id)
            if obj is None:
                logging.warning("Workspace doesn't have intents nor entities.\n" + 
                         "Going to next workspace...")
                continue

        try:
            response = update(obj=obj, workspace_id=wksp_id)
            failure = False
            if response.get_status_code() != Variables.SUCCESS_STATUS:
                failure = True
        except Exception:
            # some other exception is hit
            logging.exception(f"Exception encountered for workspace: {wksp_id}")
            failure = True
        
        if failure:
            logging.warn(f"An error occurred while trying to update the workspace: {wksp_id}. \n" + 
                            "Adding this workspace to `retrain_manually.txt`.")
            save_workspace(wksp_id=wksp_id, filename=Variables.RETRAIN_FILE)

        Variables.global_wksp_counter += 1
        if Variables.global_wksp_counter == Variables.LIMIT:
            logging.warning("Sleeping to reset rate limiting counter")
            Variables.global_wksp_counter = 0
            time.sleep(Variables.SLEEP_THIRTY_MINUTES)

if __name__ == "__main__":
    retrain_wksp()