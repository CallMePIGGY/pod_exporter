from urllib.request import urlopen
from stats import Node
from stats import Pod
from stats import Container
from stats import Stats
import json
import asyncio
import prometheus_client as prom
import logging

def getMetrics(url):
    # Get the dataset
    try:
        response = urlopen(url)
    except Exception:
        print('Access 10255 Port Failure.')
    else:
        # Convert bytes to string type and string type to dict
        string = response.read().decode('utf-8')
        json_obj = json.loads(string)
        node = Node('','','', '')
        node.name = json_obj['node']['nodeName']
        node.cpu = json_obj['node']['cpu']['usageCoreNanoSeconds'] / 1000000000
        node.availableMemory = json_obj['node']['memory']['availableBytes']
        node.workingSetMemory = json_obj['node']['memory']['workingSetBytes']

        pods_array = json_obj['pods']

        pods_list = []

        for p_item in pods_array:
            pod = Pod('','','','','')
            pod.name = p_item['podRef']['name']
            pod.namespace = p_item['podRef']['namespace']
            pod.cpu = p_item['cpu']['usageCoreNanoSeconds'] / 1000000000
            pod.workingSetMemory = p_item['memory']['workingSetBytes']
            containers_array = p_item['containers']
            containers_list = []
            for c_item in containers_array:
                container = Container('','','')
                container.name = c_item['name']
                container.cpu = c_item['cpu']['usageCoreNanoSeconds'] / 1000000000
                container.workingSetMemory = c_item['memory']['workingSetBytes']
                containers_list.append(container)
            pod.containers = containers_list
            pods_list.append(pod)

        stats = Stats('','')
        stats.node = node
        stats.pods = pods_list
        return stats


format = "%(asctime)s - %(levelname)s [%(name)s] %(threadName)s %(message)s"
logging.basicConfig(level=logging.INFO, format=format)

g1 = prom.Gauge('node_cpu_usage_seconds_total', 'CPU useage of the node', labelnames=['node_name'])
g2 = prom.Gauge('node_memory_available_bytes', 'Memory available of the node', labelnames=['node_name'])
g3 = prom.Gauge('node_memory_usage_bytes', 'Memory useage of the node', labelnames=['node_name'])
g4 = prom.Gauge('pod_cpu_usage_seconds_total', 'CPU useage of the node', labelnames=['namespace', 'pod_name'])
g5 = prom.Gauge('pod_memory_usage_bytes', 'Memory useage of the node', labelnames=['namespace', 'pod_name'])
g6 = prom.Gauge('container_cpu_usage_seconds_total', 'CPU useage of the node', labelnames=['namespace', 'pod_name','container_name'])
g7 = prom.Gauge('container_memory_usage_bytes', 'Memory useage of the node', labelnames=['namespace', 'pod_name','container_name'])
g8 = prom.Gauge('kube_pod_container_info', 'Info of the pod', labelnames=['namespace', 'node_name', 'pod_name','container_name'])

async def expose_stats(url):
    while True:
        stats = getMetrics(url)
        if type(stats) == Stats:
            logging.info("nodename: {} value {}".format(stats.node.name, stats.node.cpu))
            g1.labels(node_name=stats.node.name).set(stats.node.cpu)
            g2.labels(node_name=stats.node.name).set(stats.node.availableMemory)
            g3.labels(node_name=stats.node.name).set(stats.node.workingSetMemory)
            pods_array = stats.pods
            for p_item in pods_array:
                g4.labels(namespace=p_item.namespace, pod_name=p_item.name).set(p_item.cpu)
                g5.labels(namespace=p_item.namespace, pod_name=p_item.name).set(p_item.workingSetMemory)
                containers_array = p_item.containers
                for c_item in containers_array:
                    g6.labels(namespace=p_item.namespace, pod_name=p_item.name, container_name=c_item.name).set(c_item.cpu)
                    g7.labels(namespace=p_item.namespace, pod_name=p_item.name, container_name=c_item.name).set(c_item.workingSetMemory)
                    g8.labels(namespace=p_item.namespace, node_name=stats.node.name, pod_name=p_item.name, container_name=c_item.name)
        await asyncio.sleep(1)
if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    # Start up the server to expose metrics.
    prom.start_http_server(9183)
    url = 'http://localhost:10255/stats/summary'
    tasks = [loop.create_task(expose_stats(url))]
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        loop.close()

