# Flower Control Center
The FCC is served up using the fcc.py flask application in ../code

### Directory Structure
* css: duh
* img: static image files including flowers and the site favicon
* js:  javascript files including main.js and associated support pages
* lib: third-party libraries
* pages:  html pages for the other....erm...pages

### Libraries

Both of these libraries are copied directly into the `flower_conrol_center/lib/` subdirectory, and referenced from `index.html` using the relative path `lib/`. This is for simplicity. No library management, no internet needed, and we don't care about getting updated versions.  For both, I used the non-minified versions, so the library code is readable as documentation.

### MQTT

The two most prominent choices were [MQTT.js](https://github.com/mqttjs/MQTT.js) and the [Paho Javascript Client](https://www.eclipse.org/paho/index.php?page=clients/js/index.php). I chose Paho, because it's much lighter weight, a single stand-alone javascript file that would be easy to just copy into our `lib/` directory. MQCC.js has a dependency on Node.

- [Getting Started](https://www.eclipse.org/paho/index.php?page=clients/js/index.php)
- [API Docs](https://www.eclipse.org/paho/files/jsdoc/index.html)

### Javascript utility

I'm using [jQuery](https://jquery.com/), the non-slim (includes effects) build, v3.6.4, which was the latest available in early April.

- [Documentation](https://api.jquery.com/)


### Bootstrap
We've added bootstrap to make things just a bit prettier.
