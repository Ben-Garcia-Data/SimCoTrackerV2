import os
import requests
import time
import json


def UpdateEncyclopedia():

    # Disabled- not needed.
    """print("Working on the",realm,"realm.")

    if realm == "Entrepreneurs":
        realmID = "1"
    elif realm == "Magnates":
        realmID = "0"
    else:
        print(realm, "is not a valid input for realm type.")
        raise ValueError"""

    # Directories commonly used
    data_Dir = os.path.join(os.getcwd(), "Data", "Magnates Realm")
    exchange_Dir = os.path.join(data_Dir, "Exchange")
    encyclopedia_Dir = os.path.join(data_Dir, "Encyclopedia")
    building_Dir = os.path.join(encyclopedia_Dir, "Buildings")
    resources_Dir = os.path.join(encyclopedia_Dir, "Resources")

    # The game uses an economy state, to change how various things are calculated.
    economy_State = 0 # This variable currently isn't referenced by anything.

    # The game has 2 'realms'. Entrepreneurs & Magnates. Entrepreneurs is effectively a copy, where less time has
    # passed and not everything has unlocked yet.
    # We can differentiate between the two by appending to the end of the base URL:
    # 0: for Magnates
    # 1: for Entrepreneurs
    # I've decided to go for a 'complete' version of the encyclopedia (using the finished realm) for now but IF I chose
    # to use multiples realm the commented out code below would do this.
    realmID = 0 #Forces the complete encyclopedia

    # URL's commonly used
    base_URL = f"https://www.simcompanies.com/api/v4/en/{realmID}"
    encyclopedia_URL = base_URL + "/encyclopedia"
    buildings_URL = f"https://www.simcompanies.com/api/v3/{realmID}/encyclopedia/buildings/"  # Uses V3 API.
    resources_URL = encyclopedia_URL + "/resources/"

    # Update references to all the resources in the game.
    def UpdateResources():
        print(resources_URL)
        errors = 0
        count = 1
        economy_States = [0, 1, 2]
        print("Updating all resource Encyclopedia entries from website")

        # Get a list of all resources in the game.
        all_Resources = requests.get(resources_URL)
        all_Resources = all_Resources.json()
        json_object = json.dumps(all_Resources, indent=4)
        all_resources = resources_Dir + "\Resource_List.json"
        with open(all_resources, "w") as outfile:
            outfile.write(json_object)

        # Iterate through all 3 economy states
        for economy_State in economy_States:
            print("Economy state", economy_State)
            # Iterate through every product.
            for resource in all_Resources:

                # print(resource)
                # print(type(resource))

                # The resource URL + directory
                url = resources_URL + str(economy_State) + "/" + str(resource["db_letter"])
                dir = os.path.join(resources_Dir, "Economy_" + str(economy_State),
                                   str(resource["db_letter"]).zfill(3) + " " + resource["name"] + ".json")

                print(url, resource["name"])
                # print(dir)

                try:
                    # Making the request for data
                    response = requests.get(url)
                    response = response.json()
                    # print(response)
                    # print(type(response))
                    json_object = json.dumps(response, indent=4)
                except Exception as e:
                    print(e)
                    print("Hit an error fetching data")
                    break

                # Check that the response we got was for a valid file
                unknown_resource_error = json.loads('{"message": "Could not find such resource"}')
                if response == unknown_resource_error:
                    print(count, "Hit an unknnown resource.")
                    errors += 1
                    count += 1
                    time.sleep(0.1)
                    continue

                # Writing the JSON file
                with open(dir, "w") as outfile:
                    outfile.write(json_object)

                time.sleep(0.1)
                count += 1

            print("Completed economy state:", economy_State)

    # Update references to all the buildings in the game.
    def UpdateBuildings():
        # We don't have a URL which gives us ALL the buildings so we have to search through the resources doc and add
        # them to a set.

        print("\nUpdating Buildings info")
        print("Cross referencing resources files")

        buildings_list = []
        files = os.listdir(resources_Dir + "\Economy_0")

        for file in files:
            new_buildings = []
            # print(file)
            path = os.path.join(resources_Dir, "Economy_0", file)
            f = open(path)
            data = json.load(f)
            f.close()
            # print(data)

            if data["soldAt"] != None:
                new_buildings.append(data["soldAt"]['db_letter'])
            new_buildings.append(data["producedAt"]['db_letter'])

            for x in new_buildings:
                if x not in buildings_list:
                    buildings_list.append(x)

        # print(buildings_list)
        errors = 0
        count = 0
        print("Retrieving new building data from server")

        for building in buildings_list:
            url = buildings_URL + building + "/"
            print(url)
            # print(dir)

            try:
                # Making the request for data
                response = requests.get(url)
                response = response.json()
                # print(response)
                # print(type(response))
                json_object = json.dumps(response, indent=4)
            except Exception as e:
                print(e)
                print("Hit an error fetching data")
                break

            dir = os.path.join(building_Dir, response["name"] + ".json")

            # Check that the response we got was for a valid file
            unknown_building_error = json.loads('{"message": "Could not find such building"}')
            if response == unknown_building_error:
                print(count, "Hit an unknnown building.")
                errors += 1
                count += 1
                time.sleep(0.1)
                continue

            # Writing the JSON file
            with open(dir, "w") as outfile:
                outfile.write(json_object)

            count += 1
            time.sleep(0.1)

    # Update references to all the items that can be on the exchange.
    def UpdateExchangeBase():
        # SCOPE: This function will look over current files to look for items which are on the exchange (and hence we can
        # track their price). This function will be actively scanning the exchange for the prices.
        pass

        # Load the resource which is out base reference from the server.
        resources_path = os.path.join(resources_Dir, "Resource_List.json")
        f = open(resources_path)
        data = json.load(f)
        f.close()

        exchangeProducts = []
        # Check if each product can be traded on the exchange.
        for resource in data:
            # print(resource)
            # print(type(resource))
            if resource['exchangeTradable']:
                exchangeProducts.append(resource)

        # Write the filtered results to it's own file.
        path = os.path.join(exchange_Dir, "Magnates Realm","Exchange_Resource_List.json")
        json_object = json.dumps(exchangeProducts, indent=4)
        with open(path, "w") as outfile:
            outfile.write(json_object)

    def CreateEntrepeneurVersions():
        # Use the url to get a list of entrepeneur products and then filter other files to just these.
        url = "http://www.simcompanies.com/api/v4/en/1/encyclopedia/resources/"
        # url = "http://www.google.com"
        data = requests.get(url)
        data = data.json()
        valid_resources = [x["name"] for x in data]
        print(valid_resources)
        # Directories we need to get files to filter from

        f = open(os.path.join(resources_Dir,"Resource_List.json"), "r")
        allResources = json.load(f)
        f.close()

        entrepeneurResources = []

        for i in allResources:
            if i['name'] in valid_resources:
                entrepeneurResources.append(i)

        print(len(entrepeneurResources))
        json_object = json.dumps(entrepeneurResources, indent=4)
        entrepeneurResourcesPath = os.path.join(os.getcwd(), "Data", "Entrepreneurs Realm", "Encyclopedia","Resources","Resource_List.json")
        with open(entrepeneurResourcesPath, "w") as outfile:
            outfile.write(json_object)

    # UpdateResources()
    # UpdateBuildings()
    # UpdateExchangeBase()
    CreateEntrepeneurVersions()


UpdateEncyclopedia()