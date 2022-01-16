import requests
import json
import math

default_data = {
    "kubeAPI": "http://192.168.1.2:8081",
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


def sortPods(podsRaw):
    returnArr = []

    for pod in podsRaw["items"]:
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

    return(returnArr)


def calcFreeSpace(nodeList, podList, data):
    capLeft = {}

    for node in nodeList:  # calculating capacity left in cluster
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

    print("sortPods: ", sortPods(pods_parsed))

    print("RESULT: ", calcFreeSpace(
        sortNodes(nodes_parsed), sortPods(pods_parsed), data))

    return calcFreeSpace(
        sortNodes(nodes_parsed), sortPods(pods_parsed), data)

    print(json.dumps(parsed, indent=4, sort_keys=True))
