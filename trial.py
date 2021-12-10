from itsdangerous import TimedJSONWebSignatureSerializer as token
# Get the serializer to store the data 
import time

serializer  = token('hello', 40)
# pass an expiration time and the secret key to access thedata
token_stored = serializer.dumps({'Name':'George'}).decode('utf-8')
# Decode the data dumped into the toke in order to ensure that its not in bytes



# obtain the stored data
# Load the data if the toke is valid otherwise ignore the token
print(serializer.loads(token_stored).get('Name'))