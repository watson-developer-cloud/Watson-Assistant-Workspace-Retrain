# Retrain Workspace Script

## Purpose
This script is used to automate the process of retraining workspaces in your Watson Assistant instance.

This script utilizes the [Watson Python SDK](https://github.com/watson-developer-cloud/python-sdk) to communicate with the Watson Assistant service.
The endpoints that are utilized are:
   1. [list_workspaces()](https://cloud.ibm.com/apidocs/assistant/assistant-v1?code=python#listworkspaces)
   2. [list_intents()](https://cloud.ibm.com/apidocs/assistant/assistant-v1?code=python#listintents)
   3. [update_intent()](https://cloud.ibm.com/apidocs/assistant/assistant-v1?code=python#updateintent)

Note that for instances for that have more than 30 workspaces, updating all the workspaces will take time because of the `30 requests / 30 minutes` rate limit. Therefore after every 30 workspaces are updated, the script sleeps for 30 minutes to reset the rate limit window.

### Things To Know
- Retraining workspaces may change the behavior of your workspace. IBM makes regular updates to improve the Watson Assistant service, and you can see the latest changes by going to the release notes: [https://cloud.ibm.com/docs/assistant?topic=assistant-release-notes#](https://cloud.ibm.com/docs/assistant?topic=assistant-release-notes#).
- IBM regularly retrains workspaces that are older than 6 months. You can see this policy here: [https://cloud.ibm.com/docs/assistant?topic=assistant-skill-auto-retrain](https://cloud.ibm.com/docs/assistant?topic=assistant-skill-auto-retrain)

### How It Works
The script uses the endpoints listed above to get the workspaces and intents. Next, the script appends `"RETRAINED"` to the description of the **first intent** returned. This causes a retraining event to occur, and the workspace is retrained. If the workspace does not contain intents, then the entities are retrieved, and the first entity's description is updated to `"RETRAINED"`. 

## Requirements and Running the Script
### Requirements:
- `python 3.9`
- `pip`
- `conda` (or another virtual environment. The steps shown below are for `conda`.)

1. `conda create -n update-workspace python=3.9 -y`
2. `conda activate update-workspace`
3. `pip install -r requirements.txt`

Next, go to this link: https://cloud.ibm.com/apidocs/assistant/assistant-v1?code=python#endpoint-cloud. Copy the URL where your Watson Assistant instance is located and paste it next to `URL` in the `config.ini` file. Second, grab the API key for your instance and paste it to the `API_KEY` field in `config.ini`. You **don't** need to worry about the `AUTH_URL`

See the `example_config.ini` for reference.

### Running the Script
1. `cd retrain`
2. `python retrain_wksp.py`

### Errors
During the update process, if an error is encountered, the `workspace_id` is saved to `"retrain_manually.txt"` These workspaces will require you to retrain the workspace manually.