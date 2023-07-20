# fof_tests
Test and exploration scripts for [Field of Flowers project](https://www.campjobi.com/).

If you want to contribute to this repo, please let me know!

Be sure to check out [the wiki](https://github.com/vm-wylbur-pi/fof_tests/wiki)! That's where lots of the startup thinking is happening. 

## Docker Info
The service has been containerized via the docker-compose.yaml file.  

This will bring up the FOF services as well as an mqtt and ntp server.

In order to open up low-numbered ports for ntp you may need to give your Docker Engine permissions in Settings -> Advanced -> [Enable Priviliged Port Mappings](https://docs.docker.com/desktop/settings/mac/)

Steps to bring up the dockerized service
* ``cd fof_tests`` 
* ``docker-compose build`` to build the containers locally
* ``docker-compose up`` to launch the container, open ports, and mount local volumes

Once started, you can go to http://127.0.0.1:8000 to see the flower control center.
Clicking on the Status page from the header will run a set of internal self-tests to let you know if the various services are running.

The docker compose file mounts several directories from your filesystem into the docker container.  This allows you to make changes to those files using your editor of choice and have them be used by the running server instance - useful if you're doing development on the FCC where the changes will be picked up right away.  

If you're writing python or other things that need to be run from the command-line you'll need to shell into the server to test them out.
* ``docker ps`` which will list the running containers, yours will likely end with the name fof_tests-server-1
* ``docker exec -it \<container name> /bin/bash``

Once you've made your changes you can stop your running instance, rebuild the container and verify that things work as expected.
