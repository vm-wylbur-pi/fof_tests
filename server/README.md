# FOF:  Server Side

Welcome to the exciting world of server-side FOF development.

Here's some notes on what's going on.

The server container contains:
* Configuration Detection Center - Reads the inventory and deployment config
* Flower Control Center - the web UI
* Mosquitto Server - which provides the centralized mqtt broker

Directory Structure
* code:  python scripts for the various services
* config:  static configuration files for mosquitto, anythinge else
* flower_control_center:  duh

During operation, the docker-compose mounts a deployments directory containing the deployment configuration files needed to operate the current field.

