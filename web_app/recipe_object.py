from recipe import Recipe

class recipe_object(Recipe):
    def __init__(self, recipe):
        super().__init__
        self.id = recipe[0]
        self.name = recipe[1]
        self.instructions = recipe[2]
        # true if the user made the recipe else false (if default)
        self.personal = True if recipe[3] else False
        self.tool_ids = self.get_recipe_tools(self.id)
        self.missing_tool_ids = []
        self.ingredients = self.get_recipe_items(self.id)
        self.matched_ingredients = []
        self.understock_ingredients = []
        self.missing_ingredients = []

    # sets the list of the ids for any tools required for a recipe that a user doesn't own
    def calculate_missing_tools(self, user_tool_ids):
        self.missing_tool_ids = list(set(self.tool_ids) - set(user_tool_ids))
    
    def find_items_in_inventory(self, user_id):
        for ingredient in self.ingredients:
            ingredient_name = ingredient[0]
            # item must have atleast 95% of the needed quantity to match
            quantity_threshold = ingredient[1] * 0.95
            inv_item = self.strict_search(user_id, ingredient_name, quantity_threshold)
            quantity = inv_item[3]
            if not inv_item:
                self.missing_ingredients.append(ingredient)
                # adds attribute to each ingredient so it can be highlighted
                # a different colour based on how good the match to the inventory was
                ingredient.append("missing")
            elif quantity >= quantity_threshold:
                self.matched_ingredients.append(inv_item)
                ingredient.append("matched")
            else:
                # not high enough quantity to use in recipe
                self.understock_ingredients.append(inv_item)
                ingredient.append("understock")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "instructions": self.instructions,
            "personal": self.personal,
            "tool_ids": self.tool_ids,
            "missing_tool_ids": self.missing_tool_ids,
            "ingredients": self.ingredients,
            "matched_ingredients": self.matched_ingredients,
            "understock_ingredients": self.understock_ingredients,
            "missing_ingredients": self.missing_ingredients
        }