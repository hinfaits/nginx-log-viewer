from nginx_log_viewer.models import Log, Record, Request
import nginx_log_viewer.utils as utils
import os
import gzip

import logging

logger = logging.getLogger(__name__)


def build_db(session):
    """
    Read all the files in the log directory and
    write each entry to our database
    """
    logger.info("Begin building database")
    files_processed = 0
    args = utils.get_args()
    path = args.log_dir
    for name in os.listdir(path):
        pathname = path + name
        if name.startswith("access.log"):
            log = Log(path=path, name=name)
            session.add(log)
            if name.endswith(".gz"):
                process_file_gz(log, session)
            else:
                process_file(log, session)
            files_processed += 1
    logger.info("Loaded {} files in to database".format(files_processed))


def process_file(log, session):
    """
    Add each line from a non-gzipped log file to a session
    """
    with open(log.pathname) as log_file:
        for line in log_file:
            write_to_db(line, session)


def process_file_gz(log, session):
    """
    Add each line from a gzipped log file to a session
    """
    with gzip.open(log.pathname,'r') as log_file:
        for line in log_file:
            write_to_db(line.decode(), session)


def write_to_db(line, session):
    """
    Parse a log line and add it to the current session
    """
    parsed_line = utils.parse_log_line(line)
    parsed_request = utils.parse_http_request(parsed_line['request'])
    if parsed_line and parsed_request:
        record = Record(
            raw=line,
            ip_int=utils.ip_to_int(parsed_line['ip']),
            user=parsed_line['user'],
            time=parsed_line['time'],
            status=parsed_line['status'],
            bytes_sent=parsed_line['bytes_sent'],
            referrer=parsed_line['referrer'],
            user_agent=parsed_line['user_agent']
        )
        request = Request(
            method=parsed_request['method'],
            resource=parsed_request['resource'],
            protocol=parsed_request['protocol'],
            record=record
        )
        session.add(record, request)
    else:
        logger.warning("Failed to parse {}".format(line))
