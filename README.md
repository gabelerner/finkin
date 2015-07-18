# finkin
Yodlee-like OFX API

## Requirements
- Currently (but not for long) hosted at finkin.com
- A web server
- MySQL database server
- Python, so that you can run [web.py](http://webpy.org/)

## Supports
- Institution Search
- Account Search
- Transaction Search
- Parse Transaction OFX/QFX 

## Instructions
- Create a MYSQL database
- Import the [dump](https://github.com/gabelerner/finkin/blob/master/db/mysql-dump.sql)
- Change the [db configuration](https://github.com/gabelerner/finkin/blob/master/api/finkin.py#L245) to point to your database
- Point your web server to the `/api` folder
- Try running [the client](https://github.com/gabelerner/finkin/blob/master/client/FinkinClient.py) with the test user's token in the database ('8a52ca7d-9694-4f90-a443-c4744bda0355')
- Download and read [the documentation](https://github.com/gabelerner/finkin/blob/master/api/api-documentation.htm)
