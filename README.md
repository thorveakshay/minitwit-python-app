# MiniTwit Python Application

Minitwit application is example application that ships with the Flask microframework for Python. It implements a subset of Twitter’s functionality, allowing users to post new messages and follow messages posted by other users.

## New features added to MiniTwit
  * RESTful API routes
  * Nginx as reverse proxy and load balancer (Deployed on 3 servers)
  * SQLAlchemy - The Python SQL Toolkit and Object Relational Mapper.
  * Flask-BasicAuth - Authentication
  * MongoDB - NoSQL document-oriented database
  * Redis -  Used for storing and retriving objects from cache
  * Twit “Like” and “Unlike” functionality
  * Leaderboard functionality - most liked Twits will be on top.
 

## Note

I tried same application in SQLite3 as well as MongoDB. All SQL queries are commented in code and latest version of code is running on MongoDB and Redis.


### Prerequisites

Python, Flask, Nginx, SQLAlchemy, MongoDB, Redis Flask-BasicAuth should be installed on system.

I used one plugin python-pymongo for flexibility. You can install using below command.

```
sudo apt install -y mongodb python-pymongo
```

## Core file and all business login
```
https://github.com/thorveakshay/minitwit-python-app/blob/master/minitwit/minitwit.py
```
## Deployment

Simplified deployment using single script. Which will load few users and comments and run tests and deploy application on Nginx cluster of 3 servers.


## Authors

* **Akshay Thorve** - *Initial work* - [Flask](https://github.com/pallets/flask)

## License

This project is licensed under the MIT License.

## Acknowledgments

* Boilerplate - [Flask](https://github.com/pallets/flask)
* Thanks for guide - Prof. Kenytt Avery

