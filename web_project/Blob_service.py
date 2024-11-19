import json
from azure.storage.blob import BlobServiceClient
from .settings import *
def get_blob_service_client():
    account_name = AZURE_ACCOUNT_NAME
    account_key = AZURE_ACCOUNT_KEY
    connection_string = f"DefaultEndpointsProtocol=https;AccountName={account_name};AccountKey={account_key};EndpointSuffix=core.windows.net"
    return BlobServiceClient.from_connection_string(connection_string)

 
def download_blob2(blob_name,container_client):
    container_client =  get_blob_service_client().get_container_client(container_client)
    blob_client = container_client.get_blob_client(blob_name)
    blob_data = blob_client.download_blob().readall()
    return blob_data

def get_blob_container_client():
    blob_service_client = get_blob_service_client()
    return blob_service_client.get_container_client(AZURE_CONTAINER)

def download_blob(blob_name):
    container_client = get_blob_container_client()
    blob_client = container_client.get_blob_client(blob_name)
    blob_data = blob_client.download_blob().readall()
    return blob_data