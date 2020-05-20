import requests
import urllib3
from requests.auth import HTTPBasicAuth


DNAC_URL = "https://dnac-assurance.ciscolab.dk"
DNAC_USER = "XXXXX" #Username for DNAC
DNAC_PASS = "XXXXX" #Password for DNAC

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)  #Don't show Insecure warnings when communicating with DNAC

def get_token (user,password,dnac_url):
    url = dnac_url + "/api/system/v1/auth/token"
    response = requests.post(url, auth=HTTPBasicAuth(username=user,password=password), verify=False)
    return (response.json()["Token"])

def get_pid_role():
    info ={}
    pid = input("Write Product ID: ")
    role = input("Write network role: ")
    site = input("Write site name: ")
    info["pid"]=pid
    info["role"]=role
    info["site"]=site
    #info["site"]="Cisco Denmark"  #Hardcoded for testing
    return(info)

def get_site_id (token,dnac_url,site_name):
    url = dnac_url + "/dna/intent/api/v1/site?name=Global/" + site_name
    headers = {"X-Auth-Token": token}
    response = requests.get(url, headers=headers, verify=False)
    id = response.json()["response"][0]["id"]
    return(id)

def get_SWIM_list (token,dnac_url,info):    #Using the URL below, we search SW details per site
    url = dnac_url + "/api/v1/image/importation/site/" + info["site_id"] + "?isTaggedGolden=TRUE"
    headers = {"X-Auth-Token": token}
    response = requests.get(url, headers=headers, verify=False)
    return(response.json()["response"])

def find_Golden_Image (info,list):
    match = 0
    sw_image = {}
    for family in list: #SELECT EACH OF THE FAMILIES IN THE SWIM FOR THE SITE
        #print(str(family))
        #print("Inside for family in list")
        if match == 1:  #SIMPLE CHECK IF WE FOUND CORRECT SW IMAGE IN PREVIOUS ITERATION
            break

        for item in family["runningImageList"][0]["applicableDevicesForImage"]: #RUN THROUGH THE BLOCK OF LISTS OF PIDS AVAILABLE

            if len(item) > 2:       #PREVENT ERROR IN LIST OF PIDS IS MISSING
                for pid in item["productId"]:   #RUN THOUGH EACH PID IN THE BLOCK LIST
                    if info["pid"] == pid:      #COMPARE IF WE CAN FIND THE PID INTRIDUCED BY USER
                        match = 1               #PARAMETER TO ESCAPE LOOPS

                        for tag in family["runningImageList"][0]["tagList"]:    #CHECK IF WE HAVE A GOLDEN IMAGE FOR ANY OF THE ROLES
                            if tag["role"] == info["role"]:                     #COMPARE TO ROLE WE ARE LOOKING FOR INTRODUCED BY USER
                                if tag["taggedGolden"] == True:                 #IF ROLE IS TAGGED AS GOLDEN, GET DETAILS
                                    sw_image["name"] = family["runningImageList"][0]["name"]
                                    sw_image["version"] = family["runningImageList"][0]["version"]
                                    sw_image["softwareType"] = family["softwareType"]
                                    break
                            else:
                                match = 0
                    #else:
                        #print("Product ID: " + pid)
                if match == 1:
                    #print("inside IF BREAK")
                    break

    return (sw_image)


TOKEN = get_token(DNAC_USER,DNAC_PASS,DNAC_URL)
device_info = get_pid_role()
#print ("device info: " + str(device_info))
device_info["site_id"] = get_site_id(TOKEN,DNAC_URL,device_info["site"])
#print("Site ID: " + device_info["site_id"])
SWIM_list = get_SWIM_list(TOKEN,DNAC_URL,device_info)
Golden_image = find_Golden_Image(device_info,SWIM_list)
print ("\n\nResult: " + str(Golden_image) + "\n\n")
