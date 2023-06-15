# Installing and Running the FOF

The server-side configuration has been bundled together in a docker-compose.yml file.

If you're not familiar with docker, it can take some getting used to. Here's a few bits of core information.

Docker spins up micro-virtual machines called containers.  Each container is based on a simplified linux distribution where a set of programs and configurations are pre-installed.  Docker container configurations are specified in a Dockerfile.  You can see the one that we're using for the server in the /server directory.

In our case we're using two separate docker containers:
* Server - the FOF server which will contain all the fancy programs we've written
* Redis - a pre-built redis container

At some point I may simplify this a bit further to eliminate the need for the redis container and install it straight on the server, but that's an optimization for another day.

Docker Compose is a program to quickly spin up a set of docker containers, mount the appropriate filesystem volumes and expose the necessary ports.  The FOF Docker Compose file in the root of this directory contains instructions to bring up the server and redis containers, wire them together, and get everything running.

## Installation Prerequisites
You'll need to have Docker installed on your computer, which should bring in all the necessary utilities as well as the docker-compose command.  If you're on Mac this is included when you install [Docker Desktop](https://docs.docker.com/compose/install/).

## Running the FOF
Download the contents of this repo then run docker-compose.

```
# git clone https://github.com/vm-wylbur-pi/fof_tests.git

# docker-compose up
```

This should generate the local server container (a build step that you won't need to do everytime you start) and open the FCC on localhost:8000

## Code Development
In the current configuration this will also expose the web server, mosquitto, and redis ports on your local machine's interface so they'll be accessible to the network.  The compose file also mounts code-containing directories on your local repo to make it much, much easier for debugging.  Once the volumes are mounted you can edit the code on your local filesystem using an IDE and then reload your web browser (for FCC work) or let the flask app auto-detect the changes (for the fcc.py).  

If you change other bits of the code that aren't automagically re-loaded then you can restart the server container.

## Troubleshooting
What, something went wrong?  Shocker.

### Docker Desktop
Take a look at your Docker Desktop application's Containers screen.  It should show a fof_tests server icon (a set of stacked squares).  Clicking on that icon should open up the container links for redis and server.

Clicking on any of the container icons should take you to the Logs page where you can see what was printed out when the container started up.  It's much more likely that the server container is where the error is.

You can also click the "Terminal" tab to open up a shell directly on the running container.  This can be useful for interactive debugging.