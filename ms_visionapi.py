#This code reads the image and uses Microsoft Cognitive Services API's to get the image
#tag and keywords
#API's code reference taken from Microsoft Github page

# Import library
from __future__ import print_function
import time 
import requests
import cv2
import operator
import numpy as np
import csv
from collections import defaultdict 
#import matplotlib.pyplot as plt
import signal

# Variables

_url = 'https://api.projectoxford.ai/vision/v1/analyses'
#Here you have to paste your primary key
_key = 'your primary key here' 
_maxNumRetries = 10

#To handle the SIGINT when CTRL+C is pressed
def exit_gracefully(signum,frame):
    signal.signal(signal.SIGINT, original_sigint)
    sys.exit(1)

"""
Helper function to process the request to Project Oxford

Parameters:
json: Used when processing images from its URL. See API Documentation
data: Used when processing image read from disk. See API Documentation
headers: Used to pass the key information and the data type request
"""
def processRequest(json, data, headers, params):

    retries = 0
    result = None

    while True:

        response = requests.request('post', _url, json=json, data=data, headers=headers, params=params)

        if response.status_code == 429:

            print("Message: %s" % (response.json()['error']['message']))

            if retries <= _maxNumRetries:
                time.sleep(1)
                retries += 1
                continue
            else:
                print('Error: failed after retrying!')
                break

        elif response.status_code == 200 or response.status_code == 201:

            if 'content-length' in response.headers and int(response.headers['content-length']) == 0:
                result = None
            elif 'content-type' in response.headers and isinstance(response.headers['content-type'], str):
                if 'application/json' in response.headers['content-type'].lower():
                    result = response.json() if response.content else None
                elif 'image' in response.headers['content-type'].lower():
                    result = response.content
        else:
            print("Error code: %d" % (response.status_code))
            print("Message: %s" % (response.json()['error']['message']))

        break

    return result


def getImageTag(data):
    # Computer Vision parameters
    params = {'visualFeatures': 'Description'}

    headers = dict()
    headers['Ocp-Apim-Subscription-Key'] = _key
    headers['Content-Type'] = 'application/octet-stream'

    json = None

    result = processRequest(json, data, headers, params)
    if result is not None:
        # Load the original image, fetched from the URL
        data8uint = np.fromstring(data, np.uint8)  # Convert string to an unsigned int array
        print('Got Results!\n')
        #Get the description/tag
        description = result['description']['captions'][0]['text']
        print(result)
        img = cv2.cvtColor(cv2.imdecode(data8uint, cv2.IMREAD_COLOR), cv2.COLOR_BGR2RGB)

        columns = defaultdict(list)
        
        #Get image captipn and keywords
        #Concatenate them to form a single string 
        awsstring = "I think it is "
        awsstring += description
        awsstring += ". And the keywords are  "
        num_keywords = 5
        for i in range(num_keywords):
            awsstring += result['description']['tags'][i]
            if i != num_keywords - 1:
                awsstring += ', '
      
        return awsstring

#Saves the text to the file                
def saveTextFile(text):
    try:
        print(text)
        text_file = open("output.txt","w+")
        text_file.write(text)
        text_file.close()			 
    except Exception, e:
        print ("Exception occured \n")
        print (e)
        pass 
    
def run_main():
    # Load raw image file into memory
    pathToFileInDisk = r'smart_cap.png'
    with open(pathToFileInDisk, 'rb') as f:
        data = f.read()
        
    #Get the tag
    text = getImageTag(data)
    
    #Save the text in the file
    saveTextFile(text)
    
if __name__ == '__main__':
    original_sigint = signal.getsignal(signal.SIGINT)
    signal.signal(signal.SIGINT,exit_gracefully)
    run_main()
