import requests
import json
import math
from pymongo import Connection

default_data = {
    "kubeAPI": "http://192.168.1.2:8081",
    "mongoDB": "mongodb://192.168.1.2:31007/",
    "reqData": {
        "cpu": 1500,
        "mem": 2
    }
}


def sortNodes(nodesRaw):
    returnArr = []

    for node in nodesRaw["items"]:
        # Check if node is gameNode
        gameNode = False
        if "taints" in node["spec"]:
            for e in node["spec"]["taints"]:
                if e["key"] == "gameServer" and e["value"] == "True":
                    gameNode = True
        if not gameNode:
            continue
        capCpu = int(node["status"]["capacity"]["cpu"]) * 1000
        capMem = round(float(node["status"]["capacity"]
                       ["memory"].split("Ki")[0]) / 1000000)
        nodeName = node["metadata"]["name"]
        #print("CAP CPU: ", capCpu, "CAP MEM: ", capMem)

        returnArr.append({
            "cpu": capCpu,
            "mem": capMem,
            "nodeName": nodeName
        })

    return (returnArr)


def sortPods(podsRaw, data):
    returnArr = []
    runningServers = 0
    activeServers = 0

    for pod in podsRaw["items"]:
        # only getting server pods
        if "mc-server-" not in pod["metadata"]["name"]:
            continue
        runningServers += 1
        cpu = int(pod["spec"]["containers"][0]["resources"]
                  ["limits"]["cpu"].replace("m", "")) * 1000
        mem = int(pod["spec"]["containers"][0]["resources"]
                  ["limits"]["memory"].replace("Gi", ""))
        nodeName = pod["spec"]["nodeName"]

        # checking if cpu is displayed as whole CPUs or "m"s
        if "m" in pod["spec"]["containers"][0]["resources"]["limits"]["cpu"]:
            cpu = int(pod["spec"]["containers"][0]["resources"]
                      ["limits"]["cpu"].replace("m", ""))

        returnArr.append({
            "cpu": cpu,
            "mem": mem,
            "nodeName": nodeName
        })

    # mongoClient = Connection("mongodb://192.168.1.2:31007/")
    # for user in mongoClient["user"]["userschemas"].find():
    #     activeServers += len(user["servers"])

    # check if active servers (servers that are bought and not too old) and running servers (servers currently running) are equal, if not, re calculate and use active servers metic
    # currently not implemented, remove option to delete pods instead
    if activeServers == runningServers or True:
        return(returnArr)

    returnArr = []

    print("activeServers: ", activeServers,
          " runningServers: ", runningServers)

    for user in mongoClient["user"]["userschemas"].find():
        for server in user["servers"]:
            for product in mongoClient["user"]["products"].find():
                cpu = product[server["plan"].lower()]["cpuLim"]
                mem = product[server["plan"].lower()]["memLim"]
                returnArr.append({
                    "cpu": cpu,
                    "mem": mem,
                    "nodeName": None
                })

    return(returnArr)


def calcFreeSpace(nodeList, podList, data):
    capLeft = {}

    for node in nodeList:  # calculating capacity in cluster
        capLeft[node["nodeName"]] = {
            "cpu": node["cpu"],
            "mem": node["mem"]
        }

    for node in nodeList:
        for pod in podList:
            if pod["nodeName"] in node["nodeName"]:  # if pod running on node
                cpu = node["cpu"] - pod["cpu"]
                mem = node["mem"] - pod["mem"]
                capLeft[node["nodeName"]] = {
                    "cpu": cpu,
                    "mem": mem,
                }
    result = 0

    for node in nodeList:
        cpuLeft = capLeft[node["nodeName"]]["cpu"]
        memLeft = capLeft[node["nodeName"]]["mem"]
        cpu = data["reqData"]["cpu"]
        mem = data["reqData"]["mem"]

        if math.floor(cpuLeft/cpu) > math.floor(memLeft/mem):
            result += math.floor(memLeft/mem)
            continue
        result += math.floor(cpuLeft/cpu)

    print("capLeft: ", capLeft)

    returnObj = {
        "value": result >= 1,
        "total": result
    }

    return(returnObj)


def getCapacityFunc(input_data):
    data = default_data
    if input_data != "":
        print("New data detected implementing...")
        for element in input_data:
            if not element in default_data:
                print('DATA: "', element, '" is faulty')
                continue
            data[element] = input_data[element]
    #print("DATA RESULT: ", data)

    # getting nodes raw
    nodesRaw = requests.get(data["kubeAPI"] + "/api/v1/nodes")
    nodes_parsed = json.loads(nodesRaw.text)

    print("sortNodes: ", sortNodes(nodes_parsed))

    podsRaw = requests.get(
        data["kubeAPI"] + "/api/v1/namespaces/mc-servers/pods")
    pods_parsed = json.loads(podsRaw.text)

    print("sortPods: ", sortPods(pods_parsed, data))

    print("RESULT: ", calcFreeSpace(
        sortNodes(nodes_parsed), sortPods(pods_parsed, data), data))

    return calcFreeSpace(
        sortNodes(nodes_parsed), sortPods(pods_parsed, data), data)

    print(json.dumps(parsed, indent=4, sort_keys=True))
