while true; do
	echo "Starting MS API"
	sudo python ms_visionapi.py
	sudo python aws_dynamodb.py
	sleep 0.25 
done 
