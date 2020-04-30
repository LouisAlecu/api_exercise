Deployment:
	docker-compuse build
	docker-compose up

Requests for the endpoints explanation (they`ve been generated with postman and can be uploaded there):
	The example requests are in fca_api.postman_collection.json. The expected input
	of the endpoints are explained in the doc strings in views.py
	
	In the json file with the example requests, they are sorted in an order that makes sense, explained below: 
	
	First requests show how the /books endpoint works. Then, they use the rental_status
	endpoint, which changes the rental status of books.
	
	As a consequence to updating the rental status to unavailable,
	they can be added to a wishlist, so the wishlist endpoint is being used further. 
	
	Next, you can see a request that changes the rental_status 
        of one book to "available" and notifies one user who had it
	on the wishlist in order to show the "emailing" functionality 
        (which just prints to stdout). 
	Lastly, the endpoint for report generation and the endpoint that gets the amazon ids are being shown as examples.

