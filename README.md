[![Build Status](https://www.travis-ci.com/giobart/image-registration-service.svg?token=77HjjGKzi8yfh9qk7axg&branch=main)](https://www.travis-ci.com/giobart/image-registration-service.svg?token=77HjjGKzi8yfh9qk7axg&branch=main)

# Image storage service for who's that pokmeon project
This repository represents the image upload service for who's that pokemon project

# Setup the DB
TODO

# Running the service
setup the environment variables with:
```
~# MONGO_DB_USERNAME='username' 
~# MONGO_DB_PASSWORD='password'
```
then run with 

```
~# python entry.py
```

# API

This service exposes a very simple REST API with 3 methods:

- POST http://127.0.0.1:5000/api/store/<int:employee_id>
	- take as input a JSON of the image data as following:
```
{
	"name":"giovanni",
	"surname":"bartolomeo",
	"img_features":[[float],[float]], 
	"img_base64":"base64 encoded image"
}
``` 
if the image features are already available is possible to populate the **img_features** int vector, otherwise sending the base64 encoded image, through the **img_base64** string field, the serivce will extract the features on his own and store them on the db. <br>

- POST http://127.0.0.1:5000/api/find_match
	- take a picture as input and return a matching user if any. Is possible to toggle the image cropping system (crops and align the image to the center) and the fraud tedection system.
	- if liveness is true, frames contains 15 base64 pictures used for the liveness detection test
```
{
	"img_crop":bool,
    	"fraud_detection":bool,
	"liveness":bool,
	"img_base64":"base64 encoded image",
	"frames":[string]
}
``` 

- GET http://127.0.0.1:5000/api/get_all/<page_size>/<page_number>
	- If for example we want to get the first batch of 10 elements from the image list we call `api/get_all/10/1`
	- For the second batch of 10 elements we type `api/get_all/10/2`
- DELETE http://127.0.0.1:5000/api/<employee_id> to delete an entry from the db using the id

# Openshift deployment