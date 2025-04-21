from recipe import Recipe

class recipe_object(Recipe):
    def __init__(self, recipe):
        super().__init__()
        self.id = int(recipe[0])
        self.name = recipe[1]
        self.servings = recipe[2]
        self.prep_time = recipe[3]
        self.cook_time = recipe[4]
        self.instructions = recipe[5]
        # true if the user made the recipe else false (if default)
        self.personal = True if recipe[6] else False
        self.tool_ids = self.get_recipe_tools(self.id)
        self.missing_tool_ids = []
        self.ingredients = self.get_recipe_items(self.id)
        # ingredients that are in the users inventory
        self.found_ingredients = []
        # ingredients that have insufficient quantity but are in users inventory
        self.insufficient_ingredients = []
        # ingredients that are not in the users inventory
        self.missing_ingredients = []

    # sets the list of the ids for any tools required for a recipe that a user doesn't own
    # only passes tool_ids to front end as sets are used to calculate, which has a faster time complexity
    def calculate_missing_tools(self, user_tool_ids):
        self.missing_tool_ids = list(set(self.tool_ids) - set(user_tool_ids))
    
    def find_items_in_inventory(self, user_id):
        for ingredient in self.ingredients:
            ingredient_name = ingredient[0]
            # item must have atleast 95% of the needed quantity to match
            quantity_threshold = ingredient[1] * 0.95
            inv_item = self.strict_search(user_id, ingredient_name, quantity_threshold)
            if not inv_item:
                self.missing_ingredients.append(ingredient)
                # adds attribute to each ingredient so it can be highlighted
                # a different colour based on how good the match to the inventory was
                ingredient.append("missing")
            # if quantity bigger than threshold
            elif inv_item[3] >= quantity_threshold:
                self.found_ingredients.append(inv_item)
                ingredient.append("matched")
            else:
                # not high enough quantity to use in recipe
                self.insufficient_ingredients.append(inv_item)
                ingredient.append("insufficient")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "instructions": self.instructions,
            "servings": self.servings,
            "prep_time": self.prep_time,
            "cook_time": self.cook_time,
            "personal": self.personal,
            "tool_ids": self.tool_ids,
            "missing_tool_ids": self.missing_tool_ids,
            "ingredients": self.ingredients,
            "matched_ingredients": self.found_ingredients,
            "understock_ingredients": self.insufficient_ingredients,
            "missing_ingredients": self.missing_ingredients
        }