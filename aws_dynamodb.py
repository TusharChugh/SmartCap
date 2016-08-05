#The code reads the input from output.txt and inserts it in the dynamoDb

from __future__ import print_function # Python 2/3 compatibility
import boto3
import json
import decimal
import fcntl
import struct
import time
import ssl
import datetime
import calendar

userId = "Your user ID here. Get it using the instruction from alexa"

# Helper class to convert a DynamoDB item to JSON.
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)

#Update the item on AWS
#For that we need guid, timestamp and message
def call_aws(message):
	now = datetime.datetime.utcnow()
	timestamp = int(round((now - datetime.datetime(2016, 1 , 1)).total_seconds()))
	#days = (now - datetime.datetime(2016, 1 , 1)).days + id
	dynamodb = boto3.resource('dynamodb', region_name='us-east-1', endpoint_url="https://dynamodb.us-east-1.amazonaws.com")
	table = dynamodb.Table('smartcap')
	# your logic here...
	try:
		print("Trying to print " + message)
		response = table.update_item(
		Key={
		     'guid' : userId
		     #'command' : message,
		    },
		    UpdateExpression="set tstamp= :t, command =:r",
		    ExpressionAttributeValues={
		    ':r': message,
		    ':t': str(timestamp) 
		    },
		    ReturnValues="UPDATED_NEW"
		)
		print("PutItem succeeded:")
		return 1
	except Exception, e:
		print (e)
		fol = open("awserror.txt", "wb")
		fol.write(str(e))
		fol.close()
		return e

#print(json.dumps(response, indent=4, cls=DecimalEncoder))

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
#Main function
def main():
	ssl._create_default_https_context = ssl._create_unverified_context
	#Open the output.txt file in the read mode"
	fo = open("output.txt", "rt")
	try:			
		e = call_aws(str(fo.read()))						
	except Exception, e:
		print (e)
		time.sleep(.5)
# Close opend file
	fo.close()


if __name__ == "__main__":
    main()
    
