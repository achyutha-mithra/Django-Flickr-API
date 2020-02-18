# Django-Flickr-API

assignment project has two applications: 
	i) data_load
	ii) api

	i) data_load:
		(has to login first, either login here: /api/v1/login)
		a. Go to /data/get, and then enter the api_key and group_id (This step is not required as database is populated already and the media/ folder has the required images downloaded.
		b. uses /templates/getPhotosByGroups.html, the appropriate view is present in views.get()
		c. services.py has helper functions to get the xml file and parse through it, then get the required images downloaded to /media folder and finally insert to database.

	ii) api:
		a. Go to /api/v1 which will take you to the API root.
		b.  login: /api/v1/login
		c. other endpoints:
			/api/v1/groups  
			/api/v1/<groupId>  : ex: http://0.0.0.1:8000/api/v1/groups/34427469792%40N01/
			/api/v1/photos  
			/api/v1/photos/<photoId>  ex: http://0.0.0.1:8000/api/v1/photos/31732858850/
			/api/v1/photos/?group=<groupId>  Shows images. ex: http://0.0.0.1:8000/api/v1/photos/?group=34427469792@N01/
					use ?page=1 at the end to view in paginated mode. ex: http://0.0.0.1:8000/api/v1/photos/?group=34427469792@N01/?page=1
					to navigate, click on next, previous, first and last. 

3. login/logout:
	1. I have created 2 users, only one user has access to those records (other has to login first then download his data from /data/get), because the table has a field "userId".
	2. /api/v1/login : post request with below mentioned credentials.
	3. /api/v1/logout: empty post request.
