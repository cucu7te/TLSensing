README
======

TLSensing is a web application for CoAP-based interaction with IoT motes.
Its main goal is to retrieve sensor readings from devices in a Low power and 
Lossy Network (LLN) and display them in a user-friendly fashion.


## Supported devices

- [The OpenMote family][openmote]
- [TelosB][telosb]

TLSensing queries target devices for the `/sens` CoAP resource, which is
installed by the *sensordata* OpenWSN app.
For information on how to integrate the app in an OpenWSN binary image,
extract the `openwsn-fw.zip` archive, included with this release, and see

    openwsn-fw/openapps/sensordata/README.md


## Involved technlogies

TLSensing uses free and open source software:

- [Django][django], Python web framework;
- [MongoEngine][mongoengine], an Object-Document Mapper for interfacing with MongoDB;
- [MongoDB][mongodb], a NoSQL database;
- [Redis][redis], a key-value cache and store server;
- Berkeley's [CoAP Python library][coap] for exchanging messages with the CoAP endpoint installed by the *sensordata* OpenWSN app.


## Testing locally

### Installing on Ubuntu 14.04+

Install MongoDB:

    sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 7F0CEB10
    echo 'deb http://downloads-distro.mongodb.org/repo/ubuntu-upstart dist 10gen' | sudo tee /etc/apt/sources.list.d/mongodb.list
    sudo apt-get update
    sudo apt-get install mongodb

Install Redis:

    sudo apt-get install redis-server

Download and install additional required software:

    sudo apt-get install python-virtualenv
    virtualenv --distribute TLSEnv
    mv TLSensing TLSEnv/
    cd TLSEnv
    git clone https://github.com/openwsn-berkeley/openwsn-sw
    source bin/activate
    cd TLSensing
    sudo apt-get install python-dev libpng* libfreetype6-dev
    pip install -r requirements.txt

### Running the server

Create the directory where you want the MongoDB data to be stored, then run
the database:

    mkdir dbdir
    mongod --dbpath ./dbdir

Run Redis:

    redis-server

Run the TLSensing development server:

    python manage.py runserver 0.0.0.0:8000 --insecure

The web-based interface is now available at `http://localhost:8000`.

 [openmote]: http://openmote.com/hardware.html
 [telosb]: https://openwsn.atlassian.net/wiki/display/OW/TelosB
 [django]: https://www.djangoproject.com
 [mongoengine]: http://mongoengine.org
 [mongodb]: https://www.mongodb.org
 [redis]: http://redis.io
 [coap]: https://github.com/openwsn-berkeley/coap
