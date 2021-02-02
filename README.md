[![Build Status](https://www.travis-ci.com/giobart/image-registration-service.svg?token=77HjjGKzi8yfh9qk7axg&branch=main)](https://www.travis-ci.com/giobart/image-registration-service.svg?token=77HjjGKzi8yfh9qk7axg&branch=main)

# Image service for who's that pokmeon project
Service used by the [who's that pokemon](https://github.com/giobart/whos_that_pokemon/tree/develop) project.

This service is used for all the operations related to a facial Image.

- Store and manage the extracted features from an image
- Compare an incoming image to the ones stored
    - The 'transformation' and the 'face recognition model' proposed into the **Who's that pokemon** research block are used
- Trigger the liveness detection service if requested

## Environment setup

Install the requirements with:

```
pip install -r requirements
```

Setup the environment variables for the external liveness detection service:

```
export LIVENESS_SERVICE_URL='<external address to the service or the broker'
```

Then setup the environment variables for the Mongo DB instance that the service must use as storage.
Further information inside the **Database Setup** section.

## Database Setup
Initialize a MongoDB instance with a collection named `whosthatpokemon`

Before running the image registration service you have to setup the following environment variables to plug the DB into the service. 

- DB location

    ```
    export MONGO_DB_URL='<MONGO DB URL>'
    ```

- DB connection protocol

    `
    export MONGO_DB_PROTOCOL='mongodb+srv'
    ` or `
    export MONGO_DB_PROTOCOL='mongodb'
    `

- Username

    ```
    export MONGO_DB_USERNAME='<MONGO DB USERNAME>'
    ```

- Password

    ```
    export MONGO_DB_USERNAME='<MONGO DB PASSWORD>'
    ```

## Tuning the login accuracy threshold
Is possible to tune the login accuracy threshold with a value ⍺ ∈ [0,1], by default ⍺ = 0.8
edit the threshold with the following environment variable.

```
    export LOGIN_MATCH_THRESHOLD=<value>
```

This value also depends on the quality of the acquisition mean, with an HD input is possible to obtain matches with values lower than 0.7

# API Exposed

This service exposes the following HTTP methods:

- POST http://127.0.0.1:5000/api/store/<int:employee_id>
    - Method used to extract the features from a facial image and store them into the database
	- Payload:
    ```
    {
        "name":"giovanni",
        "surname":"bartolomeo",
        "img_features":[[float],[float]], 
        "img_base64":"base64 encoded image"
    }
    ``` 
    if the image features are already available is possible to populate the **img_features** float vector, otherwise sending the base64 encoded image, through the **img_base64** string field, the serivce will extract the features on his own and store them on the db. <br>

- POST http://127.0.0.1:5000/api/find_match
	- Takes a base_64 encoded picture as input (`img_base64`) and return a matching user if any. Is possible to toggle the image cropping system (crops and align the image to the center) and the liveness detection system.
	- If liveness is true, `frames must contain 15 base64 encoded pictures that are used for the liveness detection test.
	- Payload:
    ```
    {
        "img_crop":bool,
            "fraud_detection":bool,
        "liveness":bool,
        "img_base64":"base64 encoded image",
        "frames":[string]
    }
    ``` 
    - Response:
        - if match found
        ```
        Code 200
        {
            "_id": 1,
            "name": "string",
            "surname": "string"
        }
        ``` 
        - otherwise
        ```
        Code 406
        "no matches found"
        ``` 

- GET http://127.0.0.1:5000/api/get_all/<page_size>/<page_number>
	- If for example we want to get the first batch of 10 elements from the stored images we call `api/get_all/10/1`
	- For the second batch of 10 elements we type `api/get_all/10/2`
- DELETE http://127.0.0.1:5000/api/<employee_id> to delete an entry from the db using the id

# Running the service locally
Simply run

```
~# python entry.py
```
All the model's weights will be downloaded during the first run, please be patient. 

# Openshift deployment
In order to deploy this service on Openshift the following config files must be updated

- The build configuration YAML file must be updated accordingly
    ```
     spec:
      strategy:
        type: Source
        sourceStrategy:
          from:
            kind: ImageStreamTag
            namespace: openshift
            name: 'python:3.6'
          env:
            - name: MONGO_DB_PROTOCOL
              value: mongodb
            - name: MONGO_DB_URL
              value: <openshift db instance cluster>:<exposed cluster sb port>/whosthatpokemon
            - name: MONGO_DB_USERNAME
              value: <db instance username>
            - name: MONGO_DB_PASSWORD
              value: <db instance password>
            - name: LIVENESS_SERVICE_URL
              value: 'http://<cluster address of the deployed liveness detection service>:8080' 
    ```
- Inside the service configuration YAML file update the route target port for the 8080-tcp spec
    ```
    spec:
      ports:
        - name: 8080-tcp
          protocol: TCP
          port: 8080
          targetPort: 5005
    ```