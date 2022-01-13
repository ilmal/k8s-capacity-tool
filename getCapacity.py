import requests


default_data = {
    "kubeAPI": "192.168.1.2:8081",
    "nameSpace": "mc-servers",
    "taint": "gameServer",
    "reqData":{
        "basic": "",
        "normal": "",
        "premium": ""
    }
}


def getCapacityFunc(data):
    print("1")
    if data != "":
        print("New data detected implementing...")
        for element in data:
            print("ELEMENT: ", element)
            if not default_data[element]:
                return print("DATA: ", element, " is faulty")
            
        
    print("No data provided, assuming with default values")

    


    print("DATA FROM GET CAPACITY", data)
