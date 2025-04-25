import recipe as recipe_sql

def create(record):
    recipe_id = int(record[0])
    recipe = {
        "id": recipe_id,
        "name": record[1],
        "servings": record[2],
        "prep_time": record[3],
        "cook_time": record[4],
        "instructions": record[5],
        # true if the user made the recipe else false (if default)
        "personal": True if record[6] else False,
        "tool_ids": [],
        "missing_tool_ids": [],
        "ingredients": [],
        # ingredients that are in the users inventory
        "inventory_ingredients": [],
        # ingredients that have insufficient quantity or are missing from inventory
        "shopping_list": [],
        # flags for filtering 
        "insufficient_ingredients": False,
        "missing_ingredients": False
    }

    result = recipe_sql.get_recipe_tools(recipe_id)
    if result.get("success"):
        recipe["tool_ids"] = result.get("tool_ids", [])
    else:
        return result

    result = recipe_sql.get_recipe_items(recipe_id)
    if result.get("success"):
        recipe["ingredients"] = result.get("items", [])
    else:
        return result

    return {"success": True, "recipe": recipe}


# sets the list of the ids for any tools required for a recipe that a user doesn't own
# only passes tool_ids to front end as sets are used to calculate, which has a faster time complexity
def calculate_missing_tools(recipe, user_tool_ids):
    recipe["missing_tool_ids"] = list(set(recipe["tool_ids"]) - set(user_tool_ids))


def find_items_in_inventory(recipe, user_id):
    for ingredient in recipe["ingredients"]:
        ingredient_name = ingredient[0]
        # item must have at least 95% of the needed quantity to match
        quantity_threshold = ingredient[1] * 0.95
        # finds the best match in inventory
        result = recipe_sql.strict_search(user_id, ingredient_name, quantity_threshold)
        if not result.get("success"):
            return result
        inv_item = result.get("item")

        if not inv_item:
            # empty item so it can be replaced if user wants to substitute ingredient in create stage
            recipe["inventory_ingredients"].append([])
            recipe["shopping_list"].append(ingredient)
            # adds attribute to each ingredient so it can be highlighted
            # a different colour based on how good the match to the inventory was
            ingredient.append("missing")
            # sets missing flag
            recipe["missing_ingredients"] = True
        elif inv_item[4] >= quantity_threshold:
            recipe["inventory_ingredients"].append(inv_item)
            ingredient.append("matched")
        else:
            recipe["inventory_ingredients"].append(inv_item)
            recipe["shopping_list"].append(ingredient)
            ingredient.append("insufficient")
            # sets insufficient flag
            recipe["insufficient_ingredients"] = True
    
    return {"success": True}

def strip_recipe_flags(recipe):
    recipe.pop("missing_ingredients", None)
    recipe.pop("insufficient_ingredients", None)