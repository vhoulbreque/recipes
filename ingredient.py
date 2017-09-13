
class Ingredient():

    def __init__(self, name, quantity_names=None, complements=None):

        self.name = name.lower().strip()
        if quantity_names is None: quantity_names = []
        self.quantity_names = list(set(quantity_names))
        if complements is None: complements = []
        self.complements = list(set(complements))

    def save(self):
        save_ingredient(self)

    def copy(self):
        return Ingredient(self.name, self.quantity_names, self.complements)


class IngredientRecipe():

    def __init__(self, name, quantity_name=None, quantity=None):
        self.name = name.lower().strip()
        self.quantity_name = '' if quantity_name is None else quantity_name
        if quantity is None:
            self.quantity = ''
        else:
            try:
                self.quantity = float(quantity)
            except:
                self.quantity = ''

    def copy(self):
        return Ingredient(self.name, self.quantity_names, self.complements)


class Ustensile():

    def __init__(self, name):
        self.name = name

    def save(self):
        save_ustensile(self)

    def copy(self):
        return Ustensile(self.name)


class Recipe():

    def __init__(self, title):
        self.title = title
        self.html = None
        self.url_original_website = None
        self.url_image_original_website = None
        self.difficulty = None
        self.price = None
        self.steps = None
        self.quantity = None
        self.ingredients_recipe = None
        self.ingredients = None
        self.ustensiles = None
        self.duration = None
