class Node:
    def __init__(self, name, cpu, memory):
        self.name = name
        self.cpu = cpu
        self.memory = memory

class Pod:
    def __init__(self, name, namespace, cpu, memory, containers):
        self.name = name
        self.namespace = namespace
        self.cpu = cpu
        self.memory = memory
        self.containers = containers

class Container:
    def __init__(self, name, cpu, memory):
        self.name = name
        self.cpu =  cpu
        self.memory = memory

class Stats:
    def __init__(self, node, pods):
        self.node = node
        self.pods = pods