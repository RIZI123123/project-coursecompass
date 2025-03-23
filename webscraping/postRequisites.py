import json

with open("data.json", 'r') as read:
    data = json.load(read)

for i in data[0:]:
    print(i['code'])
    i['postrequisites'] = []
    for j in data[0:]:
        if(str(j['prerequisites']).__contains__(str(i['code']))):
            i['postrequisites'].append(j['code'])

with open("data.json", 'w') as f:
    f.write(json.dumps(data, indent= 1))