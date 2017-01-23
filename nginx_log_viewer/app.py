from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy

import nginx_log_viewer.utils as utils
import nginx_log_viewer.parser as parser
from nginx_log_viewer.models import Base, Log, Record, Request
from nginx_log_viewer.config import Config

from urllib.parse import urlparse
from datetime import datetime

import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

args = utils.get_args()

app = Flask(__name__)
app.config.from_object(Config)
app.config['SQLALCHEMY_DATABASE_URI'] = args.database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

@app.before_first_request
def setup():
    # Move these calls outside of a function to build 
    #   the database upon startup so the first request
    #   can be served instantly
    Base.metadata.create_all(bind=db.engine)
    parser.build_db(db.session)
    db.session.commit()

@app.before_request
def before_request():
    logger.info("{} requested {}".format(request.remote_addr, request.url))


@app.context_processor
def processors():
    def time_now():
        dt = datetime.now()
        return dt.strftime("%d-%b-%y %H:%M:%S")
    return dict(time_now=time_now)


@app.route('/')
def home():
    records = db.session.query(Record).order_by(Record.time.desc()).all()
    return render_template("base.html", records=records)


@app.route('/resource/')
def resource_lookup():
    # Parse the resource path from the request,
    #   strip GET parameters from the path
    path = request.args.get("path")
    resource = urlparse(path).path

    records = db.session.query(Record).join(Record.request).filter(
                    Request.resource.like('{}?%'.format(resource)) |
                    Request.resource.like(resource)
                ).order_by(
                    Record.time.desc()
                ).all()
    return render_template("base.html", header="Resource", subheader=resource, records=records)


@app.route('/ip/<string:ip>')
def ip_lookup(ip):
    args = utils.get_args()
    if args.geo_ip:
        ip_info = utils.ip_geo(ip)
    else:
        ip_info = None
    ip_host = utils.host_ip_lookup(ip)
    ip_int = utils.ip_to_int(ip)
    records = db.session.query(Record).filter_by(
                    ip_int=ip_int
                ).order_by(
                    Record.time.desc()
                ).all()
    return render_template("base.html", header="IP", subheader=ip, ip_host=ip_host, ip_info=ip_info, records=records)
