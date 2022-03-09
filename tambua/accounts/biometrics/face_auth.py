import asyncio
import io
import glob
import os
import sys
import time
import uuid
import requests
from urllib.parse import urlparse
from io import BytesIO
# To install this module, run:
# python -m pip install Pillow
from PIL import Image, ImageDraw
from azure.cognitiveservices.vision.face import FaceClient
from msrest.authentication import CognitiveServicesCredentials
from azure.cognitiveservices.vision.face.models import TrainingStatusType, Person, QualityForRecognition
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient, __version__
import matplotlib.pyplot as plt

# This key will serve all examples in this document.
KEY = "5d7dba6e3b714344b44a2394ee2fb2e3"

# This endpoint will be used in all examples in this quickstart.
ENDPOINT = "https://phoenixfacerecognition.cognitiveservices.azure.com/"

# Create an authenticated FaceClient.
face_client = FaceClient(ENDPOINT, CognitiveServicesCredentials(KEY))

def download(container_name, blob_file_to_download):
    connect_str = 'DefaultEndpointsProtocol=https;AccountName=bioauthdata;AccountKey=vq7bM1uKYcyvulbif+wlm0gYmSXvaR184deCBE4WNX5ILuqxmQebPujz9CSZRNbdESMr+QfgTLt/gc6GyfoJXw==;EndpointSuffix=core.windows.net'
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_file_to_download)

    try:
        #with open(target_download_file_path, "wb") as download_file:
        image_bytes = blob_client.download_blob().readall()
        # download_file.write(blob_client.download_blob().readall())
        return image_bytes
    except Exception as e:
        pass


def verify(source_image_file_path, target_image_file_path):

	source_image = BytesIO(download('photos', source_image_file_path))
	target_image = open(target_image_file_path, "rb")

	#Image.open(source_image)

	# Detect face(s) from source image 1, returns a list[DetectedFaces]
	# We use detection model 3 to get better performance.
	source_detected_faces = face_client.face.detect_with_stream(source_image, detection_model='detection_03')
	# Add the returned face's face ID
	source_image_id = source_detected_faces[0].face_id
	print('{} face(s) detected from image {}.'.format(len(source_detected_faces), source_image_file_path))

	# Detect face(s) from source image 2, returns a list[DetectedFaces]
	target_detected_faces = face_client.face.detect_with_stream(target_image, detection_model='detection_03')
	# Add the returned face's face ID
	target_image_id = target_detected_faces[0].face_id
	print('{} face(s) detected from image {}.'.format(len(target_detected_faces), target_image_file_path))


	# Verification example for faces of the same person. The higher the confidence, the more identical the faces in the images are.
	# Since target faces are the same person, in this example, we can use the 1st ID in the detected_faces_ids list to compare.
	verify_result_same = face_client.face.verify_face_to_face(source_image_id, target_image_id)
	print('Faces from {} & {} are of the same person, with confidence: {}'
	    .format(source_image_file_path, target_image_file_path, verify_result_same.confidence)
	    if verify_result_same.is_identical
	    else 'Faces from {} & {} are of a different person, with confidence: {}'
	        .format(source_image_file_path, target_image_file_path, verify_result_same.confidence))

	if verify_result_same.is_identical:
		print("PASSED")
		source_img = Image.open(source_image)
		target_img = Image.open(target_image_file_path)
		return [True,[source_img, target_img]]
	else:
		print("FAILED")
		#source_img = Image.open(source_image_file_path)
		source_img = Image.open(source_image)
		target_img = Image.open(target_image_file_path)
		return [False,[source_img, target_img]]

if __name__ == '__main__':
	# The source photos contain this person
	source_image_file_path = 'dwayne.jpg'
	target_image_file_path = 'Samples\\african2.jpg'

	ret, data = verify(source_image_file_path, target_image_file_path)  # data contains two images [source, test]

	#data[0].show()  # Show source image