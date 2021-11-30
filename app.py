import os
from random import randint
from time import sleep
import logging

from flask import Flask, jsonify, request
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from prometheus_client import make_wsgi_app, Summary, Gauge, Counter
import requests
from elasticapm.contrib.flask import ElasticAPM
import ecs_logging
from pythonjsonlogger import jsonlogger

from custom_logger import getStructLogger


s = Summary('request_latency_seconds', 'RPS and Response time', ["path", "method"])
g = Gauge('inprogress_requests', 'In progress requests', ["path", "method"])
c = Counter('group_created', 'Created Groups')

service = os.getenv("name", "service_name")
app = Flask(service)

app.config['ELASTIC_APM'] = {
'SERVICE_NAME': service,
'SECRET_TOKEN': '',
'SERVER_URL': 'https://87b44754de3b4705b610c9722148f608.apm.eastus2.azure.elastic-cloud.com:443',
'ENVIRONMENT': 'production',
}

apm = ElasticAPM(app)

logger_py = logging.getLogger(f"{service}_py")
logger_py.setLevel(logging.DEBUG)
handler_py = logging.FileHandler(f"{service}_py.log")
handler_py.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger_py.addHandler(handler_py)

logger_ecs = logging.getLogger(f"{service}_ecs")
logger_ecs.setLevel(logging.DEBUG)
handler_ecs = logging.FileHandler(f"{service}_ecs.log")
handler_ecs.setFormatter(ecs_logging.StdlibFormatter())
logger_ecs.addHandler(handler_ecs)

logger_jf = logging.getLogger(f"{service}_jf")
logger_jf.setLevel(logging.DEBUG)
handler_jf = logging.FileHandler(f"{service}_jf.log")
handler_jf.setFormatter(jsonlogger.JsonFormatter())
logger_jf.addHandler(handler_jf)

logger_custom = getStructLogger(f"{service}_custom")


app.wsgi_app = DispatcherMiddleware(
    app.wsgi_app, {"/metrics": make_wsgi_app()}
)

def logger(level, msg):
    getattr(logger_py, level)(f"Logger PY: {msg}")
    getattr(logger_ecs, level)(msg=f"Logger ECS: {msg}")
    getattr(logger_jf, level)(msg=f"Logger JF: {msg}")
    getattr(logger_custom, level)(f"Logger Custom: {msg}")

def alter_rute(f):
    def wrapper(*args, **kwargs):
        with g.labels(request.path, request.method).track_inprogress():
            with s.labels(request.path, request.method).time():
                sleep(randint(0,100)/100)
                if randint(0, 30) == 5:
                    logger(level="error", msg="BOOM")
                    return jsonify({"Error": "BOOM"}), 500
                a = f(*args, **kwargs)
                logger(level="info", msg=str(a.get_json()))
        return a
    wrapper.__name__ = f.__name__
    return wrapper


@app.route("/", methods=['POST'])
@alter_rute
def index():
    if service == "service_a":
        ra = do_call("http://service_aa:5000/")
        da = do_something()
        rb = do_call("http://service_ab:5000/")
        rc = do_call("http://service_ac:5000/")
        return jsonify({"service": service, "flow": f"{ra}, {da}, {rb}, {rc}"})
    elif service == "service_aa":
        da = do_something()
        return jsonify({"service": service, "flow": f"{da}"})
    elif service == "service_ab":
        ra = do_call("http://service_aba:5000/")
        rb = do_call("http://service_abb:5000/")
        da = do_something()
        return jsonify({"service": service, "flow": f"{ra}, {rb}, {da}"})
    elif service == "service_ac":
        da = do_something()
        ra = do_call("http://service_aca:5000/")
        rb = do_call("http://service_acb:5000/")
        return jsonify({"service": service, "flow": f"{da}, {ra}, {rb}"})
    elif service == "service_aba":
        ra = do_call(f"http://service_abaa:5000/")
        da = do_something()
        return jsonify({"service": service, "flow": f"{ra}, {da}"})
    elif service == "service_abb":
        da = do_something()
        return jsonify({"service": service, "flow": f"{da}"})
    elif service == "service_aca":
        da = do_something()
        return jsonify({"service": service, "flow": f"{da}"})
    elif service == "service_acb":
        da = do_something()
        return jsonify({"service": service, "flow": f"{da}"})
    elif service == "service_abaa":
        da = do_something()
        return jsonify({"service": service, "flow": f"{da}"})
    else:
        da = do_something()
        return jsonify({"unknown_service": service, "flow": f"{da}"})
    

def do_call(url):
    logger(level="debug", msg=f"Calling {url}")
    response = requests.post(url)
    response.raise_for_status()
    return response.json()

def do_something():
    return {"do": f"something on {service}"}

@app.errorhandler(Exception)
def handle_bad_request(e):
    logger(level="error", msg=f"ERROR: {e}")
    return f'Error {e}', 500