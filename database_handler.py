import os
import json


# Recipes

def does_recipe_exist(recipe):

    recipe_url_transformed = recipe['url_original_website'].replace('/', '').replace('.', '').replace(':', '')[34:]
    return os.path.isdir(os.path.join('_data/recipes/', recipe_url_transformed))


def save_recipe(recipe):

    recipe_url_transformed = recipe['url_original_website'].replace('/', '').replace('.', '').replace(':', '')[34:]
    path = os.path.join('_data/recipes/', recipe_url_transformed)

    if not os.path.exists(path):
        print('path : ', path)
        os.makedirs(path)

    filename_html = 'html'
    filename_features = 'features'
    filename_steps = 'steps'
    filename_quantity = 'quantity'
    filename_ingredients = 'ingredients'
    filename_ustensiles = 'ustensiles'
    filename_duration = 'duration'

    f = open(os.path.join(path, filename_html), 'w')
    f.write(recipe['html'])
    f.close()

    f = open(os.path.join(path, filename_features), 'w')
    f.write(recipe['url_original_website'] + '\n')
    f.write(recipe['url_image_original_website'] + '\n')
    f.write(recipe['title'] + '\n')
    f.write(recipe['difficulty'] + '\n')
    f.write(recipe['price'])
    f.close()

    f = open(os.path.join(path, filename_steps), 'w')
    f.write('\n'.join([str(step) for step in recipe['steps']]).replace('\'', '"'))
    f.close()

    f = open(os.path.join(path, filename_quantity), 'w')
    f.write(str(recipe['quantity']).replace('\'', '"'))
    f.close()

    f = open(os.path.join(path, filename_ingredients), 'w')
    f.write('\n'.join([ingredient.name.lower().strip() for ingredient in recipe['ingredients']]))
    f.close()

    f = open(os.path.join(path, filename_ustensiles), 'w')
    f.write('\n'.join([ustensile.name.lower().strip() for ustensile in recipe['ustensiles']]))
    f.close()

    f = open(os.path.join(path, filename_duration), 'w')
    f.write(str(recipe['duration']).replace('\'', '"'))
    f.close()

    for ingredient in recipe['ingredients']:
        if not does_ingredient_exist(ingredient):
            save_ingredient(ingredient)

    for ustensile in recipe['ustensiles']:
        if not does_ustensile_exist(ustensile):
            save_ustensile(ustensile)



# Ingredients

def does_ingredient_exist(ingredient):

    ingredient_name = ingredient.name.lower().strip()

    return os.path.isdir(os.path.join('_data/ingredients', ingredient_name))


def save_ingredient(ingredient):

    path = os.path.join('_data/ingredients/', ingredient.name.lower().strip())
    if not os.path.exists(path):
        print('path : ', path)
        os.makedirs(path)
    else:
        existing_ingredient = get_ingredient(path=path)
        ingredient.quantity_names = list(set(existing_ingredient.quantity_names + ingredient.quantity_names))
        ingredient.complements = list(set(existing_ingredient.complements + ingredient.complements))

    filename_features = 'features'
    filename_quantity_names = 'quantity_names'
    filename_complements = 'complements'

    f = open(os.path.join(path, filename_features), 'w')
    f.write(ingredient.name.strip())
    f.close()

    f = open(os.path.join(path, filename_quantity_names), 'w')
    f.write('\n'.join(ingredient.quantity_names))
    f.close()

    f = open(os.path.join(path, filename_complements), 'w')
    f.write('\n'.join(ingredient.complements))
    f.close()


def get_ingredient(path=None, name=None):

    if path is None and name is None:
        raise ValueError('The arguments are invalid')

    if name is None:
        try:
            name = path.split('/')[2]
        except:
            raise Exception('Path is not good : ', path)

    ingredient = Ingredient(name=name)
    if not does_ingredient_exist(ingredient):
        return None

    filename_features = 'features'
    filename_quantity_names = 'quantity_names'
    filename_complements = 'complements'

    f = open(os.path.join(path, filename_features), 'r')
    ingredient.name = [l.replace('\n', '') for l in f][0]
    f.close()

    f = open(os.path.join(path, filename_quantity_names), 'r')
    ingredient.quantity_names = [l.replace('\n', '') for l in f]
    f.close()

    f = open(os.path.join(path, filename_complements), 'r')
    ingredient.complements = [l.replace('\n', '') for l in f]
    f.close()

    return ingredient


# Ustensile

def does_ustensile_exist(ustensile):

    ustensile_name = ustensile.name.lower().strip()
    return os.path.isdir(os.path.join('_data/ustensiles', ustensile_name))


def save_ustensile(ustensile):

    path = os.path.join('_data/ustensiles/', ustensile.name.lower().strip())
    if not os.path.exists(path):
        print('path : ', path)
        os.makedirs(path)

    filename_features = 'features'

    f = open(os.path.join(path, filename_features), 'w')
    f.write(ustensile.name)
    f.close()
