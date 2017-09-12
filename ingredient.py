
class Ingredient():

    def __init__(self, name, quantity_names=None, complements=None):

        self.name = name
        if quantity_names is None: quantity_names = []
        self.quantity_names = list(set(quantity_names))
        if complements is None: complements = []
        self.complements = list(set(complements))

    def save(self):
        save_ingredient(self)

    def copy(self):
        return Ingredient(self.name, self.quantity_names, self.complements)


class Ustensile():

    def __init__(self, name):
        self.name = name

    def save(self):
        save_ustensile(self)

    def copy(self):
        return Ustensile(self.name)
