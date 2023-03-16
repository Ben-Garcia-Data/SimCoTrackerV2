import json
import os
import time
import requests
import shutil
import math

from Classes import Sale


def TakeExchangeSnapshot(realm):
    # Pick a realm
    # Load a list of all product DB numbers that we search for in this realm.
    # Filter this list to products which haven't recently been refreshed- use some clever math to work out what the normal rate of change is and search those which change less frequently, less often.
    # Move the previous product snapshots into the 'previous' folder, overwriting the file already there.
    # Request data of filtered product list via DB number & save that data into 'latest'
    # Work out all the products which have left the exchange since we last checked. Ideally also filter out potential 'removed' rather than 'sold' products, but be careful of quality implications.
    print("Taking a snapshot of the", realm, "Realm")

    if realm == "Entrepreneurs":
        realmID = "1"
    elif realm == "Magnates":
        realmID = "0"
    else:
        print(realm, "is not a valid input for realm type.")
        raise ValueError

    data_Dir = os.path.join(os.getcwd(), "Data", realm + " Realm")
    exchange_Dir = os.path.join(data_Dir, "Exchange")
    encyclopedia_Dir = os.path.join(data_Dir, "Encyclopedia")
    building_Dir = os.path.join(encyclopedia_Dir, "Buildings")
    resources_Dir = os.path.join(encyclopedia_Dir, "Resources")

    # Load a list of all product DB numbers that we search for in this realm.
    f = open(os.path.join(resources_Dir, "Resource_List.json"), "r")
    resourceList = json.load(f)
    f.close()

    for resource in resourceList:
        t = time.time()
        name = resource['name']
        # print(f"Starting {name}")
        product_DB_Num = resource["db_letter"]
        url = f"https://www.simcompanies.com/api/v3/market/{realmID}/{product_DB_Num}/"
        old_resource_path = os.path.join(exchange_Dir, "Previous", name + " Exchange Snapshot.json")
        new_resource_path = os.path.join(exchange_Dir, "Latest", name + " Exchange Snapshot.json")

        # Time to reference when creating a best estimate of the sale time/date of the product.
        newTime = int(time.time())
        try:
            oldTime = os.path.getmtime(new_resource_path)
            saleTime = newTime - (0.5 * (newTime - oldTime))
        except FileNotFoundError:
            print("Couldn't find file to get timestamp. Assuming this is our first run. I will assign a value to "
                  "saleTime here but it shouldn't actually be referenced because there won't be any sales.")
            saleTime = newTime
            pass

        # We need to check the previous time we recorded this product and if it is within N seconds skip the product.


        # Move the previous product snapshots into the 'previous' folder, overwriting the file already there.
        try:
            shutil.move(new_resource_path, old_resource_path)
        except Exception as e:
            print(e)

        # Request data of filtered product list via DB number & save that data into 'latest'
        print(url, name)
        try:
            response = requests.get(url)
            newSnapshot = response.json()
        except requests.exceptions.JSONDecodeError as e:
            print(e)
            print(response)
            time.sleep(10)
            continue


        # print(newSnapshot)

        json_object = json.dumps(newSnapshot, indent=4)
        with open(new_resource_path, "w") as outfile:
            outfile.write(json_object)

        # Work out all the products which have left the exchange since we last checked. Ideally also filter out
        # potential 'removed' rather than 'sold' products, but be careful of quality implications.

        # I have lists NEW (A) and OLD (B). I want what was in OLD and not in NEW, which will give me a list of items
        # which have left the exchange since last scan. Using set notation, this is the same as B∩A'.

        # ---------------------------------------------------------------------------
        # Can't do sets of dicts. Could i make each dict a tuple and do sets of tuples?

        try:
            f = open(old_resource_path)
            data = json.load(f)
            f.close()
        except FileNotFoundError:
            f.close()
            print(
                "File not found to compate to. As long as this is the first time this product has been run, this is okay. If this error reapeats for the same product there is an issue.")
            data = []

        # Sort both lists by ID so we can iterate through them without time wasting.

        newSnapshot = sorted(newSnapshot, key=lambda d: d['id'])
        oldSnapshot = sorted(data, key=lambda d: d['id'])

        sales = []

        # TODO-- Add in something which will filter out products that have been removed but
        #  lower price & quality products haven't, indicating manual removals.
        #


        # These are all debug bits. helping to make this algo more efficent.
        # countA = 0
        # countC = 0
        # print("Big O of N is",len(oldSnapshot))
        # print("Big O of Nlog(N) is", len(oldSnapshot) * math.log(len(oldSnapshot)))
        # print("Big O of N^2 is", math.pow(len(oldSnapshot),2))


        for x in oldSnapshot:
            # print("Looking at",x['id'])
            # print(str(100*countA/len(oldSnapshot))[:4],"%")
            # countA += 1
            # countB = 0
            Old_id = x['id']
            Old_quantity = x['quantity']

            for y in newSnapshot:
                # print(str(100*countB/len(oldSnapshot))[:4],"%")
                # countC += 1
                # countB += 1
                New_id = y['id']
                New_quantity = y['quantity']

                if New_id == Old_id:
                    # Matched ID's
                    if New_quantity == Old_quantity:
                        # Exact match. No chance, skip to next product in old snapshot.
                        # print("Broke due to exact match")
                        break
                    elif New_quantity > Old_quantity:
                        # print("Quantity of product has increased. Not possible to tell if sales were made.")
                        break
                    else:
                        # ID matches but quantity doesn't- means a partial sale.
                        quantity = x['quantity'] - y['quantity']
                        sold = Sale(x['kind'], x['seller'], quantity, x['price'], x['quality'], saleTime, x['id'])
                        # print(sold.__str__())
                        sales.append(sold)
                        # print("Broke due to finding a partial sale")
                        break

                if New_id > Old_id:
                    # We have passed any chance of matching an ID on this loop on the old snapshot.
                    # Therefore this entry is in the OLD snapshot only and should be recorded as a complete sale.
                    sold = Sale(x['kind'], x['seller'], x['quantity'], x['price'], x['quality'], saleTime, x['id'])
                    # print(sold.__str__())
                    sales.append(sold)
                    # print("Broke due to finding a complete sale")
                    break

        # print(countC, "is my Big O number.")



        # Attempted to implement differences using sets.
        """for i in [tuple(x.values()[:4]) for x in newSnapshot]:
            print(i)

        newSnapshot = set([tuple(x.values()[:4]) for x in newSnapshot])
        oldSnapshot = set([tuple(x.values()[:4]) for x in data])
        differenceProducts = oldSnapshot.difference(newSnapshot)

        print(newSnapshot)
        print(oldSnapshot)
        print(differenceProducts)"""

        # Attempted to implement differences using many loops of O(n). Adding 'in' to some of these meant to went to
        # O(n^2)
        """oldSnapshot = data

        # Generate a ID-Quantity identified for each sale, so we can compare these. If the ID-Quantity is the same
        # then no sale has happened and we can discard it.
        #
        print("Generting new IDs")

        newID_QuantitiesIDs = [str(x['id']) + str(x['quantity']) for x in newSnapshot]
        newIDs = [x['id'] for x in newSnapshot]
        oldID_QuantitiesIDs = [str(x['id']) + str(x['quantity']) for x in oldSnapshot]

        print("Removing exact duplicates")

        for x in newID_QuantitiesIDs:
            if x in oldID_QuantitiesIDs:
                oldID_QuantitiesIDs.remove(x)

        # If the ID-Quantity is unique then either the item is new in the NEW snapshot or has sold out or been
        # removed. We aren't interested in items which are new in the new snapshot, so by only removing them from the
        # old snapshot and moving on with those, we are left with just newID's which have either completely or
        # partially sold out.
        #
        # We can now restore the ID's (first 8 digits). If ID is in both then just the quantity has changed. If the
        # ID is in the first only then it is a complete sale.

        print("Restoring IDs")

        productsWithDifference = [x[:8] for x in oldID_QuantitiesIDs]
        print(productsWithDifference)

        completeSales = []
        partialSales = []

        for x in productsWithDifference:
            if x in newIDs:
                partialSales.append(x)
            else:
                completeSales.append(x)
                
                
        # Now we have to loop thru original dataset again matching ID's to either list of sales.
        # THEN we have to difference partial sales."""
        def reportAndSleep():
            print("Found", len(sales), "sales, took", time.time() - t, "seconds.")
            print("")
            time.sleep(1)


        if len(sales) == 0:
            reportAndSleep()
            # Skip writing to appending to the file as we have nothing to say!
            continue

        # This is the point where instead of using text files to record our JSON we should be using a database. Would
        # we rather store all recorded sales in RAM somehow (massive list of tuples & payloads) or open/close the
        # database frequently?


        # print("Writing to file")
        filePath = os.path.join(exchange_Dir,"Historical", f"{name}_ All recorded sales.json")

        def append_record(record):
            with open(filePath, 'a') as f:
                json.dump(record, f)
                f.write(os.linesep)

        # We iterate through each sale record and append each one to the file.
        for i in sales:
            append_record(i.__dict__)

        reportAndSleep()
        # print("Finished writing to file")



TakeExchangeSnapshot("Entrepreneurs")
