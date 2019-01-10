class Node:
    def __init__(self, name, cpu, availableMemory, workingSetMemory):
        self.name = name
        self.cpu = cpu
        self.availableMemory = availableMemory
        self.workingSetMemory = workingSetMemory

class Pod:
    def __init__(self, name, namespace, cpu, workingSetMemory, containers):
        self.name = name
        self.namespace = namespace
        self.cpu = cpu
        self.workingSetMemory = workingSetMemory
        self.containers = containers

class Container:
    def __init__(self, name, cpu, workingSetMemory):
        self.name = name
        self.cpu =  cpu
        self.workingSetMemory = workingSetMemory

class Stats:
    def __init__(self, node, pods):
        self.node = node
        self.pods = pods
        