#MP2 Data Processing REST API

this project is a fastAPI application where clients can upload a csv dataset that is cleaned using my MP1 Data Pipeline and retrieve the results over HTTP. 'post/upload' stores csv in memory and returns its ID and metadata, 'get/datasets/{dataset_id}' returns the rows and 'get/health confirms that the API is running.

'post/datasets/{dataset_id}/process' takes a JSON configuration in the same format as the MP1 'config.yaml' the mp1 validation and cleaning functions are ran and saves the data back to storage and returns a cleaning report. bad uploads return a 400, unknown ids are a 404, and malformed requests are a 422. Failed processing requests never change the stored data. 'src/' package holds the request and response models. The in-memory storage, logging setup and middleware logs every quests witha unique request ID. While 'data-pipeline/' contains the reused mp1 modules and 'test/' contains pytest test for api
