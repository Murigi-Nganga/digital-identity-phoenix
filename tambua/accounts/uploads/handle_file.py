import os
import uuid
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient

def upload(container_name, file_path, file_name):
    connect_str = 'DefaultEndpointsProtocol=https;AccountName=bioauthdata;AccountKey=vq7bM1uKYcyvulbif+wlm0gYmSXvaR184deCBE4WNX5ILuqxmQebPujz9CSZRNbdESMr+QfgTLt/gc6GyfoJXw==;EndpointSuffix=core.windows.net'
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=file_name)

    try:
        with open(file_path, "rb") as data:
            blob_client.upload_blob(data)
        return True
    except:

        return False