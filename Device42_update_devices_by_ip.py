#    ███╗   ██╗ ██████╗    \     
#    ████╗  ██║██╔════╝     \      Made by : Noe Gebert
#    ██╔██╗ ██║██║  ███╗     \
#    ██║╚██╗██║██║   ██║     /
#    ██║ ╚████║╚██████╔╝    /      Made on : 20/08/2024
#    ╚═╝  ╚═══╝ ╚═════╝    /

import requests
import urllib3
from colorama import Fore, Style
# uncomment next for basic auth
#from requests.auth import HTTPBasicAuth

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning) #avoids warnings

base_url = "your URL"
client_key = "Your client key"
client_secret = "your secret"
#if you don't have a client key, use basic authentification such as :
# auth=HTTPBasicAuth('user', 'password')

# Make the POST request to get the token
def get_identification_token():
    token_url = f'{base_url}/tauth/1.0/token/'
    response = requests.post(token_url, auth=(client_key, client_secret), verify=False)
    if response.status_code == 200:
        token = response.json().get('token')
        return token
    else:
        print(f"Failed to get token: {response.status_code} - {response.text}")

def get_by_ip(token, ip):
    url = f"{base_url}/api/2.0/ips/?ip={ip}"
    headers = {'Authorization' : f'Bearer {token}',}
    response = requests.get(url,  verify=False, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return 0, data["ips"]
    else:
        return 1, f"Invalid IP : {response.status_code} - {response.text}"
    
def update_device(id, token, input_data):
    url = f'{base_url}/api/2.0/devices/{id}/'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json',
        'Authorization' : f'Bearer {token}'
    }
    response = requests.put(url, headers=headers, data=input_data, verify=False)
    if response.status_code == 200:
        return 0, 'update successfull!'
    else:
        return 1, f'Failed to update device. Status code: {response.status_code}'
    
def compute_data(data, ip, token, input_data):
    device_lst = ""
    failed = 0
    completed = 0

    if data[0] == 1:
        print(f"{ip} : {data[1]}")
    else:
        elem = data[1][0]
        if not elem["devices"]:
            print(f"{ip} : {Fore.RED}NO DEVICES{Style.RESET_ALL}")
            return 1, 0, completed
        for device in elem["devices"]:
            output = update_device(int(device["device_id"]), token, input_data)
            if output[0] == 0:
                device_lst = device_lst + f"{device["name"]}({Fore.GREEN}OK{Style.RESET_ALL}) / "
                completed += 1
            else:
                device_lst = device_lst + f"{device["name"]}({Fore.RED}FAIL{Style.RESET_ALL}) / "
                failed += 1
        print(f"{ip} : {device_lst}")
    return 0, failed, completed

def print_result(count_ip, completed, no_device_count, failed):
    print(f"\n{Fore.GREEN}### TOTAL IPs : {count_ip}")
    print(f"### COMPLETED DEVICE UPDATES : {completed}{Style.RESET_ALL}")
    print(f"{Fore.RED}### NO DEVICE : {no_device_count}")
    print(f"### FAILED DEVICE UPDATES : {failed}{Style.RESET_ALL}")

def update_devices_by_ip(ip_lst, input_data):
    token = get_identification_token()
    failed = 0
    no_device_count = 0
    count_ip = 0
    completed = 0

    for ip in ip_lst:
        data = get_by_ip(token, ip)
        output = compute_data(data, ip, token, input_data)
        failed += output[1]
        no_device_count += output[0]
        completed += output[2]
        count_ip += 1
    print_result(count_ip, completed, no_device_count, failed)
    
ip_lst = ['255.255.255.255','000.000.000.000'] #Change IP list to match the devices you want to update
input_data = {'tags': 'YOUR_TAG'} #Modify to change the value you wish to

update_devices_by_ip(ip_lst, input_data)
