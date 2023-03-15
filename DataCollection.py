import os
import requests
import time
import json

# Directories commonly used
data_Dir = os.path.join(os.getcwd(), "Data")
encyclopedia_Dir = os.path.join(data_Dir, "Encyclopedia")
building_Dir = os.path.join(encyclopedia_Dir, "Buildings")
resources_Dir = os.path.join(encyclopedia_Dir, "Resources")

# The game uses an economy state, to change how various things are calculated.
economy_State = 0

# URL's commonly used
base_URL = "https://www.simcompanies.com/api/v4/en/0"
encyclopedia_URL = base_URL + "/encyclopedia"
buildings_URL = encyclopedia_URL + "/buildings/"
resources_URL = encyclopedia_URL + "/resources/"

# Download all recipes

def UpdateEncyclopedia():

    def UpdateResources():
        errors = 0
        count = 1
        economy_States = [0, 1,2]
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

            # Iterate through every product.
            for resource in all_Resources:

                # print(resource)
                # print(type(resource))

                # The resource URL + directory
                url = resources_URL+str(economy_State)+"/"+str(resource["db_letter"])
                dir = os.path.join(resources_Dir, "Economy_" +str(economy_State),str(resource["db_letter"]).zfill(3)+" "+resource["name"] +".json")

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

    UpdateResources()


UpdateEncyclopedia()