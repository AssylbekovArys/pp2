import json 
with open('C:/Users/acer/Desktop/git lessin/L4/laboratory work/JSON/sample-data.json', 'r', encoding='UTF8') as read:
    data = json.load(read)
    print("Interface Status")
    print("================================================================================")
    print("DN                                                       Description           Speed        MTU  ")
    print("--------------------------------------------------   --------------------      ------      ------")
    for s in range(18):
        for x, y in data["imdata"][s]['l1PhysIf']["attributes"].items():
            if x == 'dn':
                print(y, end="                                    ")
            if x == "mtu":
                print(y, end="")
            if x == "fecMode":
                print(y, end="       ")
        print("\n")