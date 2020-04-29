# CovidIA Flask App

This folder is the Flask application for the CovidIA team. Further details on mockups and project are available [here](https://docs.google.com/presentation/d/1TY9TrlR02dQ2ocEVyIc62T4F1SxLZowzdtkMpkcMcw0/edit#slide=id.g73216de455_4_490).

## Project setup
### Dependencies
You will need [pipenv](https://pipenv.pypa.io/en/latest/) to setup the required virtual environment
To setup the project, use the following command line
```bash
cd $YOUR_PROJECT_FOLDER # Go to the git directory where the Pipfile.lock lies
pipenv sync # Sync your environment with the lock file
```

This project requires the following dependencies
```python
flask = "*" # Application Creation
azure-storage-blob = "*" # Connection with the Azure Storage Account
pandas = "*" # Data formatting
flask-cors = "*" # Use in local for dev purposes
```

### Environment Variables
To make the application run in you local environment, you need to setup some environment variables. You can either create it as usual or use `.env` file to force it while using `pipenv`

```bash
FLASK_APP=run:app
ENVIRONMENT = [development/production/test]
SECRET_KEY =$FLASK_APP_SECRET_KEY
PYTHONPATH= .
ACTIVATE_MOCKUP = 0
CLOUD_PROVIDER = "AZURE"
CLOUD_CONTAINER_NAME = "covidiaappingestion"
STORAGE_CREDENTIALS = $AZURE_STORAGE_CONNECTION_STRING
API_VERSION = 0.1
```

### Launch the application for development
To launch the application go to your project folder and launch the `run.py` script in a `pipenv shell`
```bash
cd $YOUR_PROJECT_FOLDER
pipenv run python run.py # Activate Debug mode
# OR
pipenv run flask run # Shut down Debug mode
```

## Application Deployment
On every `git push` on branch `origin/master`, a GitHub Action is launched, the workflow is named `Deploy Python package to Azure Web App` and you can find the relative deployment process in `.github/workflows/main.yaml`

## Current Blueprints
```
app: Main Falsk App
|
--- api_bp: Data from data.gouv.fr about Covid19
|
--- api_insee_bp: Data from INSEE about death rates
```