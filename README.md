## Flask API example
   Simple example of API on flask

### Requirements
 - [Docker](https://docs.docker.com/install/)
 - [Docker Compose](https://docs.docker.com/compose/install/)

### Deploy and Run

run `make deploy`

If browser doesn't open, go to [localhost:5000](localhost:5000)


#### TODO

- switch from sqlite (to postgres)
- switch to proper ids (UUID)
- add seed database
- add migrations (using alembic)
- proper json validation and parsing (with Marshmallow)
- data loading in batches
- proper error handling
- do proper stats with possibility to list all batches per category, list number of products in batches, etc
- split app.py into model, schema, controller
- add tests for each above-mentioned module
- add all actions to history, not only quantity-related (when deleted)
- add more details to swagger doc (with data format, expected responses, etc)
- add automatic actions (delete when quantity 0)
