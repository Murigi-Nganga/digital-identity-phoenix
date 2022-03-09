import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.metrics import accuracy_score
import seaborn as sns
from shutil import copy
from tensorflow.keras.preprocessing.image import load_img, img_to_array
from sklearn.model_selection import train_test_split
from skimage.metrics import structural_similarity
import matplotlib.pyplot as plt
from sklearn.utils import shuffle
import random
import os
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient, __version__
from io import BytesIO
import cv2
# To install this module, run:
# python -m pip install Pillow
from PIL import Image, ImageDraw
np.random.seed(42)

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

def mse(A, B):
    """
        Computes Mean Squared Error between two images. (A and B)
        
        Arguments:
            A: numpy array
            B: numpy array
        Returns:
            err: float
    """
    
    # sigma(1, n-1)(a-b)^2)
    err = np.sum((A - B) ** 2)
    
    # mean of the sum (r,c) => total elements: r*c
    err /= float(A.shape[0] * B.shape[1])
    
    return err


def ssim(A, B):
    """
        Computes SSIM between two images.
        
        Arguments:
            A: numpy array
            B: numpy array
            
        Returns:
            score: float
    """
    
    return structural_similarity(A, B)

def verify(original_img_path, test_img_path):

    source_image = download('signatures', original_img_path)

    nparr = np.frombuffer(source_image, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
    img = cv2.resize(img, (150, 150))
    original_img = Image.fromarray(img)

    #original_img = load_img(img,color_mode="grayscale", target_size=(150,150))
    test_img = load_img(test_img_path,color_mode="grayscale", target_size=(150,150))

    A = img_to_array(original_img) # 2 by 21 person
    B = img_to_array(test_img) # 2 by 2 [real]

    A_array = img_to_array(A[0])
    B_array = img_to_array(B[0])

    MSE = mse(A_array, B_array)
    SSIM = ssim(A_array.flatten(),B_array.flatten())
    
    print ("MSE Error: {}".format(MSE))
    print("SSIM: {}".format(SSIM))

    THRESHOLD = 20

    if MSE < THRESHOLD:
        print("PASSED")
        return [True,[original_img, test_img]]
    else:
        print("FAILED")
        return [False,[original_img, test_img]]


if __name__ == '__main__':
    original_img_path = "photo_2022-03-08_10-26-59.jpg"
    test_img_path = "08_049.png"

    ret, data = verify(original_img_path, test_img_path)  # data contains two images [original, test]
    
    #data[1].show() display an image
