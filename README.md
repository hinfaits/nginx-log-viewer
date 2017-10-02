# nginx-log-viewer

**nginx-log-viewer** displays nginx access logs over http. All (uncompressed and gzipped) access logs are compiled in to a single webpage, filterable by IP or accessed resource.

### Minimal Installation
These instructions have been tested on Ubuntu 16.04, but should work on any Debian Linux.
```sh
$ git clone https://github.com/hinfaits/nginx-log-viewer.git
$ cd nginx-log-viewer/
$ pip3 install --user -r requirements.txt
$ python3 runserver.py
```
Navigate to http://127.0.0.1:8181/

#### GeoIP lookups
Basic GeoIP lookups can be done via [MaxMind](https://dev.maxmind.com/geoip/geoip2/geolite2/).To enable lookups

1. Download the [MaxMind GeoLite2 City database](http://geolite.maxmind.com/download/geoip/database/GeoLite2-City.mmdb.gz)
2. Extract the database. On Ubuntu: ```gzip -d GeoLite2-City.mmdb.gz```
3. Run nginx-log-viewer using ```python runserver.py -G /path/to/GeoLite2-City.mmdb```

### Caveats
1. If logs are not in the default nginx format, ```parse_log_line()``` in ```nginx_log_viewer/utils.py``` may require editing. 
2. The author does not recommend running nginx-log-viewer on the open web as efforts to secure the application have been minimal.
