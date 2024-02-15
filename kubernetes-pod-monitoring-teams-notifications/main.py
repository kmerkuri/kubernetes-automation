import os
from flask import Flask
from kubernetes import client, config
from kubernetes.client.models import V1PodStatus
import pymsteams
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)

CLUSTER_NAME = os.environ.get('CLUSTER_NAME')
TEAMS_WEBHOOK_URL = os.environ.get('TEAMS_WEBHOOK_URL')

def monitor_pods():
    config.load_incluster_config()
    api_client = client.CoreV1Api()
    pods = api_client.list_pod_for_all_namespaces(watch=False)
    not_running_pods = []
    for pod in pods.items:
        if pod.status.phase != 'Running' or pod.status.phase != 'Succeeded':
            pod_name = pod.metadata.name
            pod_status = pod.status.phase
            pod_namespace = pod.metadata.namespace
            not_running_pods.append((pod_name, pod_status, pod_namespace))

    teams_connector = pymsteams.connectorcard(TEAMS_WEBHOOK_URL)
    teams_card = pymsteams.cardsection()
    teams_card.title("Non Running Pod Alert")
    teams_card.text("Some pods are not running")
    teams_card.addImage("http://i.imgur.com/c4jt321l.png", ititle="This Is Fine")
    teams_card.addFact("Cluster Name", CLUSTER_NAME)
    teams_card.activityText("Pod Name   Pod Status  Namespace")
    message = "The following pods are not running:\n"
    for pod, status, namespace in not_running_pods:
        message += f"- {pod}  {status}  {namespace}\n"
    teams_card.text(message)
    teams_connector.addSection(teams_card)
    teams_connector.summary("Fix ASAP")
    teams_connector.send()
@app.route("/test")
def test():
    config.load_incluster_config()
    api_client = client.CoreV1Api()
    pods = api_client.list_pod_for_all_namespaces(watch=False)
    not_running_pods = []
    for pod in pods.items:
        if pod.status.phase != 'Running' or pod.status.phase != 'Succeeded':
            pod_name = pod.metadata.name
            pod_status = pod.status.phase
            pod_namespace = pod.metadata.namespace
            not_running_pods.append((pod_name, pod_status, pod_namespace))
    teams_connector = pymsteams.connectorcard(TEAMS_WEBHOOK_URL)
    teams_card = pymsteams.cardsection()
    teams_card.title("Non Running Pod Alert")
    teams_card.text("Some pods are not running")
    teams_card.addImage("http://i.imgur.com/c4jt321l.png", ititle="This Is Fine")
    teams_card.addFact("Cluster Name", CLUSTER_NAME)
    teams_card.activityText("Pod Name   Pod Status  Namespace")
    message = "The following pods are not running:\n"
    for pod, status, namespace in not_running_pods:
        message += f"- {pod}  {status}  {namespace})\n"
    teams_card.text(message)
    teams_connector.addSection(teams_card)
    teams_connector.summary("Fix ASAP")
    teams_connector.send()
    return "Success", 200

@app.route("/")
def index():
    return "Monitoring pods..."

if __name__ == "__main__":
    scheduler = BackgroundScheduler()
    scheduler.add_job(monitor_pods, 'interval', minutes=10)
    scheduler.start()
    app.run()
