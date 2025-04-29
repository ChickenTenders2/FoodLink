from recipe import get_recipe_tools, get_recipe_items
from inventory import strict_search, format_item
from datetime import date

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
        # sets base value for sorting (incase no items are close to expiry for recipe)
        "sort_value": 0
    }

    result = get_recipe_tools(recipe_id)
    if result.get("success"):
        recipe["tool_ids"] = result.get("tool_ids", [])
    else:
        return result

    result = get_recipe_items(recipe_id)
    if result.get("success"):
        recipe["ingredients"] = result.get("items", [])
    else:
        return result

    return {"success": True, "recipe": recipe}


# sets the list of the ids for any tools required for a recipe that a user doesn't own
# only passes tool_ids to front end as sets are used to calculate, which has a faster time complexity
def calculate_missing_tools(recipe, user_tool_ids):
    missing_tools = list(set(recipe["tool_ids"]) - set(user_tool_ids))
    recipe["missing_tool_ids"] = missing_tools
    # returns if tools are missing
    return len(missing_tools) != 0

DAYS_LEFT_LIMIT = 14
def find_items_in_inventory(recipe, user_id, missing_allowed, insufficient_allowed):
    # for each item, counts for how close the item is to expiring,
    # if its already close to expire (within the limit defined above)
    days_left_count = {}
    
    for ingredient in recipe["ingredients"]:
        ingredient_name = ingredient[0]
        # item must have at least 95% of the needed quantity to match
        quantity_threshold = ingredient[1] * 0.95
        # finds the best match in inventory
        result = strict_search(user_id, ingredient_name, quantity_threshold)
        if not result.get("success"):
            return result
        inv_item = result.get("item")

        if not inv_item:
            # stops searches if missing items are not allowed and one is found
            if not missing_allowed:
                return {"success": True, "allowed": False}
            # empty item so it can be replaced if user wants to substitute ingredient in create stage
            recipe["inventory_ingredients"].append([])
            recipe["shopping_list"].append(ingredient)
            # adds attribute to each ingredient so it can be highlighted
            # a different colour based on how good the match to the inventory was
            ingredient.append("missing")
            continue

        # calculates the days_left and counts it if its soon
        expiry_date = inv_item[6]
        today = date.today()
        days_left = (expiry_date - today).days
        if days_left < DAYS_LEFT_LIMIT:
            if days_left in days_left_count:
                days_left_count[days_left] += 1
            else:
                days_left_count[days_left] = 1
        
        # formats date for front end
        inv_item = format_item(inv_item)
        
        # if item found in inventory and enough quantity
        if inv_item[4] >= quantity_threshold:
            recipe["inventory_ingredients"].append(inv_item)
            ingredient.append("matched")
        # if item found in inventory but not enough quantity
        else:
            # stops searches if insufficient items are not allowed
            if not insufficient_allowed:
                return {"success": True, "allowed": False}
            
            recipe["inventory_ingredients"].append(inv_item)
            recipe["shopping_list"].append(ingredient)
            ingredient.append("insufficient")

    # to prioritise items closer to expiring 
    # 2x 2 days left items = 1x 1 day left item
    # 3x 3 days left items = 1x 1 day left item
    # 4x 4 days left items = 1x 1 day left item
    # etc
    # so weighting of each count is 1/k where k is the days left value (i.e. key)
    
    # sum of close to expire items (with weighting applied)
    # negative value of the sum, so recipes with more close to expire items come first in sort
    # if no items are close to expire sum([]) = 0 (base value)
    recipe["sort_value"]  = -sum(days_left_count[k] / k for k in days_left_count.keys())  


    
    return {"success": True, "allowed": True}
