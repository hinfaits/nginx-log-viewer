import geoip2.database
import geoip2.errors
from datetime import datetime
import argparse
import socket
import re

def get_args():
    """
    Returns args in a dictionary. This could benefit (marginally) from memoization
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-H', '--host', help='Set web server listening host.',
        default='127.0.0.1'
    )
    parser.add_argument(
        '-P', '--port', type=int,
        help='Set web server listening port.', default=8181
    )
    parser.add_argument(
        '-L', '--log-dir', help='Set log file directory.',
        default='/var/log/nginx/'
    )
    parser.add_argument(
        '-D', '--database', help='Set application database.',
        default="sqlite://"
    )
    parser.add_argument(
        '-G', '--geo-ip', help='Set geoip db filepath, required for geoip lookup.'
    )
    args = parser.parse_args()
    return args


def ip_to_int(ip):
    o = list(map(int, ip.split('.')))
    res = (16777216 * o[0]) + (65536 * o[1]) + (256 * o[2]) + o[3]
    return res


def int_to_ip(ip):
    o1 = int(ip / 16777216) % 256
    o2 = int(ip / 65536) % 256
    o3 = int(ip / 256) % 256
    o4 = int(ip) % 256
    return '%(o1)s.%(o2)s.%(o3)s.%(o4)s' % locals()


def parse_timestamp(timestamp):
    """
    Returns a datetime object from an nginx timestamp
    """
    format = "%d/%b/%Y:%H:%M:%S %z"
    return datetime.strptime(timestamp, format)


def parse_log_line(line):
    pattern = re.compile('^([\d\.]+) - (.*) \[(.+)\] "(.*)" (\d+) (\d+) "(.*)" "(.*)"$')
    res = pattern.match(line)
    if res:
        return dict(
            ip=res.group(1),
            user=res.group(2),
            time=parse_timestamp(res.group(3)),
            request=res.group(4),
            status=res.group(5),
            bytes_sent=res.group(6),
            referrer=res.group(7),
            user_agent=res.group(8)
            # gzip_ratio=res.group(9)
        )
    else:
        return None


def parse_http_request(request):
    pattern = re.compile('^(\S+) (\S+) (\S+)$')
    res = pattern.match(request)
    if res:
        return dict(
            method=res.group(1),
            resource=res.group(2),
            protocol=res.group(3)
        )
    else:
        return None


def host_ip_lookup(ip):
    try:
        return socket.gethostbyaddr(ip)[0]
    except socket.error as e:
        return "Not found."


def ip_geo(ip):
    args = get_args()
    try:
        reader = geoip2.database.Reader(args.geo_ip)
        response = reader.city(ip)
        return dict(
            country=response.country.name,
            state=response.subdivisions.most_specific.name,
            city=response.city.name,
            zip=response.postal.code,
            lat=response.location.latitude,
            lon=response.location.longitude,
        )
    except geoip2.errors.GeoIP2Error as e:
        return None
