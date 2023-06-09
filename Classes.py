from typing import Type

class Recipe:

    # Recipe is a summary of how to produce a product. It contains a list of dictionary of ingredients (

    def __init__(self,
                 product,
                 ingredients,
                 building
                 ):

        self.product = product
        self.ingredients = ingredients

    # Ingredients should be a list of resources

class Building:

    pass

class Resource:
    def __init__(self,
                 name: Type[str],
                 image: Type[str],
                 db_letter: Type[str],
                 transportation: Type[float],
                 retailable: Type[bool],
                 research: Type[bool],
                 exchangeTradable: Type[bool],
                 realmAvailable: Type[bool],
                 producedFrom: Type[Recipe],
                 soldAt: Type[Building],
                 soldAtRestaurant: Type[Building],
                 producedAt: Type[Building],
                 neededFor: Type[list],
                 # producedAnHour should be a dictionary with keys 0,1,2 representation the different values at
                 # different market status'
                 producedAnHour: Type[dict],
                 baseSalary: Type[float],
                 averageRetailPrice: Type[float],
                 marketSaturation: Type[float],
                 marketSaturationLabel: Type[str],
                 # retailModeling should be a dictionary with keys 0,1,2 representation the different values at
                 # different market status'
                 retailModeling: Type[dict],
                 storeBaseSalary: Type[float],
                 retailData: Type[list],
                 improvesQualityOf: Type[list]


                 ):

        self.name = name
        self.image = image
        self.db_letter = db_letter
        self.transportation = transportation
        self.retailable = retailable
        self.research = research
        self.db_letter = db_letter
        self.exchangeTradable = exchangeTradable
        self.realmAvailable = realmAvailable
        self.producedFrom = producedFrom
        self.soldAt = soldAt
        self.soldAtRestaurant = soldAtRestaurant
        self.producedAt = producedAt
        self.neededFor = neededFor
        self.producedAnHour = producedAnHour
        self.baseSalary = baseSalary
        self.averageRetailPrice = averageRetailPrice
        self.marketSaturation = marketSaturation
        self.marketSaturationLabel = marketSaturationLabel
        self.retailModeling = retailModeling
        self.storeBaseSalary = storeBaseSalary
        self.retailData = retailData
        self.improvesQualityOf = improvesQualityOf

    # Products should be a list of items that this can be used for.
    # Recipe sould be a recipe class

class Sale:
    # Sale is a summary of a sale.

    def __init__(self,
                 productID,
                 seller,
                 quantity,
                 price,
                 quality,
                 sale_Time,
                 ID
                 ):

        self.productID = productID
        self.sellerInfo = seller
        self.quantity = quantity
        self.price = price
        self.quality = quality
        self.time = int(sale_Time)
        self.ID = ID

        self.SumPrice = int(quantity * price)
        self.sellerName = seller['company'].replace(" ","_")

        # self.productName = productID
        # Would love to find a way to add nice text to this withbout having to load the
        # whole encyclopedia of ID's & names every time it is called?

    def __str__(self):
        return f"{self.quantity} of Q{self.quality} #{self.productID} for {self.price} each sold by {self.sellerName}."

    def SQLInput(self):
        s = (
          self.productID,
          self.quantity,
          self.price,
          self.quality,
          self.time,
          self.ID,
          self.SumPrice,
          self.sellerName
        )

        return s