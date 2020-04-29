import os
from libs.connectors.azure_blob_connector import AzureBlobConnector

ConnectorStorage = {
    "AZURE": AzureBlobConnector
}

STORAGE_CONNECTOR = ConnectorStorage[os.getenv('CLOUD_PROVIDER')](credentials=os.getenv('STORAGE_CREDENTIALS'), storage_name=os.getenv('CLOUD_CONTAINER_NAME'))