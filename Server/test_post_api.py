import requests

requests.post('http://26.181.221.42:17892/add_fogs/fog',json={'href':"26.181.221.42:19846",
                                                                'ip':"26.181.221.42",
                                                                "port":1883,"is_final":True})
print(requests.get('http://26.181.221.42:17892/get_fog').json())