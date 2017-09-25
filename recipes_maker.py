from database_handler import get_all_recipes
from ingredient import Ingredient, IngredientRecipe, Recipe


def make_recipes(ingredients, interdictions=None, kind_of_recipe=None, all_ingredients_needed=True):
    # kind_of_recipe is dessert, main, entrée etc.

    if kind_of_recipe is None:
        kind_of_recipe = ['entrée', 'main dish', 'cheese', 'dessert']
    if interdictions is None:
        interdictions = []

    good_recipes = []
    recipes = get_all_recipes()

    for recipe in recipes:

        # if recipe.kind_of_recipe not in kind_of_recipe:
        #     continue

        gr = True

        for ingredient_recipe in recipe.ingredients_recipe:
            if ingredient_recipe not in ingredients or ingredient_recipe in interdictions:
                gr = False
                break

        if gr: good_recipes.append(recipe)

    return good_recipes



if __name__ == '__main__':

    # Tests

    bananes = Ingredient(name='bananes')
    chocolat_noir = Ingredient(name='chocolat noir')

    ingredients = [bananes, chocolat_noir]

    recipe = make_recipes(ingredients)[0]

    print(recipe)
