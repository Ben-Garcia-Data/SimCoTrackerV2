def GetLatestData(realm):

    if realm == "Entrepreneurs":
        realmID = "1"
    elif realm == "Magnates":
        realmID = "0"
    else:
        print(realm, "is not a valid input for realm type.")
        raise ValueError

    url = f"www.simcompanies.com/api/v3/market/{realmID}/{product_DB_Num}/"

