from web_app.database import get_cursor, commit, safe_rollback
import logging

recipes = [
    {
        "name": "Butter Chicken",
        "servings": 4,
        "prep_time": "20 min",
        "cook_time": "35 min",
        "instructions": "Cut chicken into cubes. In a bowl, mix yogurt, ginger-garlic paste, chili powder, turmeric, and salt. Marinate chicken for 1 hour. Heat butter in a frying pan. Add chopped onions and saute until golden. Add tomato puree, garam masala, cumin, and coriander powder. Cook the sauce for 10 minutes. Add marinated chicken and cook until done. Stir in cream and simmer for 5 minutes. Garnish with fresh coriander and serve hot with rice or naan.",
        "ingredients": [
            {"name": "Chicken Breast", "quantity": "500", "unit": "g"},
            {"name": "Yogurt", "quantity": "100", "unit": "g"},
            {"name": "Ginger-Garlic Paste", "quantity": "1", "unit": "tbsp"},
            {"name": "Red Chili Powder", "quantity": "1", "unit": "tsp"},
            {"name": "Turmeric Powder", "quantity": "0.5", "unit": "tsp"},
            {"name": "Salt", "quantity": "1", "unit": "tsp"},
            {"name": "Butter", "quantity": "50", "unit": "g"},
            {"name": "Onion", "quantity": "1", "unit": "piece"},
            {"name": "Tomato Puree", "quantity": "200", "unit": "ml"},
            {"name": "Garam Masala", "quantity": "1", "unit": "tsp"},
            {"name": "Cumin Powder", "quantity": "0.5", "unit": "tsp"},
            {"name": "Coriander Powder", "quantity": "0.5", "unit": "tsp"},
            {"name": "Cream", "quantity": "100", "unit": "ml"},
            {"name": "Fresh Coriander", "quantity": "2", "unit": "tbsp"}
        ],
        "utensils/appliances": [8, 11, 9]
    },
    {
        "name": "Spaghetti Bolognese",
        "servings": 4,
        "prep_time": "15 min",
        "cook_time": "45 min",
        "instructions": "Heat olive oil in a saucepan. Add chopped onions and garlic. Cook until soft. Add minced beef and cook until browned. Stir in tomato puree, oregano, basil, salt, and pepper. Simmer for 30 minutes. Boil spaghetti until al dente. Drain and combine with sauce. Serve with grated Parmesan.",
        "ingredients": [
            {"name": "Spaghetti", "quantity": "300", "unit": "g"},
            {"name": "Minced Beef", "quantity": "400", "unit": "g"},
            {"name": "Onion", "quantity": "1", "unit": "piece"},
            {"name": "Garlic", "quantity": "3", "unit": "cloves"},
            {"name": "Tomato Puree", "quantity": "250", "unit": "ml"},
            {"name": "Olive Oil", "quantity": "2", "unit": "tbsp"},
            {"name": "Dried Oregano", "quantity": "1", "unit": "tsp"},
            {"name": "Dried Basil", "quantity": "1", "unit": "tsp"},
            {"name": "Salt", "quantity": "1", "unit": "tsp"},
            {"name": "Black Pepper", "quantity": "0.5", "unit": "tsp"},
            {"name": "Parmesan Cheese", "quantity": "50", "unit": "g"}
        ],
        "utensils/appliances": [9, 11, 16]
    },
    {
        "name": "Vegetable Biryani",
        "servings": 5,
        "prep_time": "25 min",
        "cook_time": "40 min",
        "instructions": "Wash and soak basmati rice for 20 minutes. Heat ghee in a saucepan. Saute sliced onions, ginger-garlic paste, and green chilies. Add chopped vegetables, yogurt, turmeric, red chili powder, and salt. Cook until vegetables are half done. In another pan, boil rice with whole spices until 70% cooked. Layer rice and vegetable curry in a pot. Top with saffron milk and fried onions. Cover and steam cook for 15 minutes. Let it rest before serving.",
        "ingredients": [
            {"name": "Basmati Rice", "quantity": "2", "unit": "cups"},
            {"name": "Mixed Vegetables", "quantity": "300", "unit": "g"},
            {"name": "Onion", "quantity": "2", "unit": "pieces"},
            {"name": "Yogurt", "quantity": "100", "unit": "g"},
            {"name": "Ginger-Garlic Paste", "quantity": "1", "unit": "tbsp"},
            {"name": "Green Chili", "quantity": "2", "unit": "pieces"},
            {"name": "Turmeric Powder", "quantity": "0.5", "unit": "tsp"},
            {"name": "Red Chili Powder", "quantity": "1", "unit": "tsp"},
            {"name": "Salt", "quantity": "1.5", "unit": "tsp"},
            {"name": "Ghee", "quantity": "2", "unit": "tbsp"},
            {"name": "Saffron Milk", "quantity": "2", "unit": "tbsp"},
            {"name": "Whole Spices (Bay Leaf, Cinnamon, Cloves)", "quantity": "1", "unit": "tbsp"}
        ],
        "utensils/appliances": [9, 10, 24]
    },
        {
        "name": "Fish Tacos",
        "servings": 4,
        "prep_time": "20 min",
        "cook_time": "15 min",
        "instructions": "Marinate fish fillets with lime juice, cumin, paprika, salt, and pepper. Let sit for 15 minutes. Heat a frying pan and cook the fish for 3-4 minutes per side. Warm taco shells. Prepare a slaw with shredded cabbage, mayonnaise, and vinegar. Assemble tacos with fish and slaw. Garnish with fresh cilantro and serve.",
        "ingredients": [
            {"name": "Fish Fillet", "quantity": "400", "unit": "g"},
            {"name": "Lime Juice", "quantity": "2", "unit": "tbsp"},
            {"name": "Ground Cumin", "quantity": "1", "unit": "tsp"},
            {"name": "Paprika", "quantity": "1", "unit": "tsp"},
            {"name": "Salt", "quantity": "1", "unit": "tsp"},
            {"name": "Black Pepper", "quantity": "0.5", "unit": "tsp"},
            {"name": "Taco Shells", "quantity": "8", "unit": "pieces"},
            {"name": "Cabbage", "quantity": "200", "unit": "g"},
            {"name": "Mayonnaise", "quantity": "3", "unit": "tbsp"},
            {"name": "White Vinegar", "quantity": "1", "unit": "tbsp"},
            {"name": "Fresh Cilantro", "quantity": "2", "unit": "tbsp"}
        ],
        "utensils/appliances": [8, 11]
    },
    {
        "name": "Pasta Carbonara",
        "servings": 3,
        "prep_time": "10 min",
        "cook_time": "20 min",
        "instructions": "Boil pasta in salted water until al dente. In a bowl, whisk together eggs, grated Parmesan, and black pepper. Fry chopped pancetta until crispy. Drain pasta and immediately toss with pancetta and its fat. Stir in egg mixture quickly to coat the pasta without scrambling the eggs. Serve immediately.",
        "ingredients": [
            {"name": "Spaghetti", "quantity": "250", "unit": "g"},
            {"name": "Pancetta", "quantity": "100", "unit": "g"},
            {"name": "Eggs", "quantity": "2", "unit": "pieces"},
            {"name": "Parmesan Cheese", "quantity": "50", "unit": "g"},
            {"name": "Black Pepper", "quantity": "0.5", "unit": "tsp"},
            {"name": "Salt", "quantity": "1", "unit": "tsp"}
        ],
        "utensils/appliances": [9, 8, 16]
    },
    {
        "name": "Tomato Soup",
        "servings": 4,
        "prep_time": "15 min",
        "cook_time": "30 min",
        "instructions": "Heat olive oil in a saucepan. Add chopped onions and garlic, cook until soft. Add chopped tomatoes, tomato paste, salt, sugar, black pepper, and vegetable broth. Simmer for 20 minutes. Blend until smooth. Return to heat and add cream. Simmer briefly and serve hot.",
        "ingredients": [
            {"name": "Tomatoes", "quantity": "600", "unit": "g"},
            {"name": "Onion", "quantity": "1", "unit": "piece"},
            {"name": "Garlic", "quantity": "2", "unit": "cloves"},
            {"name": "Olive Oil", "quantity": "1", "unit": "tbsp"},
            {"name": "Tomato Paste", "quantity": "2", "unit": "tbsp"},
            {"name": "Salt", "quantity": "1", "unit": "tsp"},
            {"name": "Sugar", "quantity": "1", "unit": "tsp"},
            {"name": "Black Pepper", "quantity": "0.5", "unit": "tsp"},
            {"name": "Vegetable Broth", "quantity": "500", "unit": "ml"},
            {"name": "Cream", "quantity": "100", "unit": "ml"}
        ],
        "utensils/appliances": [9, 17, 11]
    },
        {
        "name": "Cheesy Potato Bake",
        "servings": 6,
        "prep_time": "20 min",
        "cook_time": "50 min",
        "instructions": "Peel and slice potatoes thinly. In a saucepan, melt butter and saute garlic until fragrant. Add cream, salt, pepper, and nutmeg. Layer potatoes in a baking dish with shredded cheese. Pour cream mixture over. Cover and bake until potatoes are tender. Uncover, sprinkle cheese on top, and bake until golden.",
        "ingredients": [
            {"name": "Potatoes", "quantity": "1.2", "unit": "kg"},
            {"name": "Butter", "quantity": "50", "unit": "g"},
            {"name": "Garlic", "quantity": "2", "unit": "cloves"},
            {"name": "Cream", "quantity": "300", "unit": "ml"},
            {"name": "Salt", "quantity": "1.5", "unit": "tsp"},
            {"name": "Black Pepper", "quantity": "1", "unit": "tsp"},
            {"name": "Nutmeg", "quantity": "0.25", "unit": "tsp"},
            {"name": "Cheddar Cheese", "quantity": "200", "unit": "g"}
        ],
        "utensils/appliances": [9, 21, 16]
    },
    {
        "name": "Spinach Omelette",
        "servings": 2,
        "prep_time": "10 min",
        "cook_time": "5 min",
        "instructions": "Wash and chop spinach. Beat eggs in a bowl with salt and pepper. Heat butter in a frying pan. Add spinach and cook briefly. Pour in the eggs. Cook until set, then fold the omelette and serve hot.",
        "ingredients": [
            {"name": "Spinach", "quantity": "100", "unit": "g"},
            {"name": "Eggs", "quantity": "3", "unit": "pieces"},
            {"name": "Salt", "quantity": "0.5", "unit": "tsp"},
            {"name": "Black Pepper", "quantity": "0.25", "unit": "tsp"},
            {"name": "Butter", "quantity": "1", "unit": "tbsp"}
        ],
        "utensils/appliances": [8, 11]
    },
    {
        "name": "Grilled Cheese Sandwich",
        "servings": 1,
        "prep_time": "5 min",
        "cook_time": "5 min",
        "instructions": "Spread butter on one side of each bread slice. Place cheese between slices with buttered sides out. Heat a pan and grill sandwich until golden brown on both sides. Serve immediately.",
        "ingredients": [
            {"name": "Bread Slices", "quantity": "2", "unit": "pieces"},
            {"name": "Cheddar Cheese", "quantity": "2", "unit": "slices"},
            {"name": "Butter", "quantity": "1", "unit": "tbsp"}
        ],
        "utensils/appliances": [8, 22]
    },
        {
        "name": "Mushroom Risotto",
        "servings": 4,
        "prep_time": "15 min",
        "cook_time": "40 min",
        "instructions": "Heat olive oil in a pan and sauté chopped onions and garlic. Add sliced mushrooms and cook until soft. Stir in arborio rice and cook for 1 minute. Gradually add warm broth, stirring constantly. Continue until rice is tender and creamy. Stir in butter and Parmesan. Serve immediately.",
        "ingredients": [
            {"name": "Arborio Rice", "quantity": "300", "unit": "g"},
            {"name": "Mushrooms", "quantity": "200", "unit": "g"},
            {"name": "Onion", "quantity": "1", "unit": "piece"},
            {"name": "Garlic", "quantity": "2", "unit": "cloves"},
            {"name": "Olive Oil", "quantity": "2", "unit": "tbsp"},
            {"name": "Vegetable Broth", "quantity": "1", "unit": "L"},
            {"name": "Parmesan Cheese", "quantity": "50", "unit": "g"},
            {"name": "Butter", "quantity": "20", "unit": "g"}
        ],
        "utensils/appliances": [9, 11]
    },
    {
        "name": "Lamb Curry",
        "servings": 5,
        "prep_time": "25 min",
        "cook_time": "60 min",
        "instructions": "Marinate lamb with yogurt, turmeric, chili powder, and salt for 30 minutes. Heat oil in a pan. Sauté onions until golden, add ginger-garlic paste and tomatoes. Cook until soft. Add spices and cook briefly. Add lamb and cook covered until tender. Serve hot with rice or naan.",
        "ingredients": [
            {"name": "Lamb", "quantity": "600", "unit": "g"},
            {"name": "Yogurt", "quantity": "100", "unit": "g"},
            {"name": "Turmeric Powder", "quantity": "0.5", "unit": "tsp"},
            {"name": "Red Chili Powder", "quantity": "1", "unit": "tsp"},
            {"name": "Salt", "quantity": "1.5", "unit": "tsp"},
            {"name": "Onion", "quantity": "2", "unit": "pieces"},
            {"name": "Tomatoes", "quantity": "2", "unit": "pieces"},
            {"name": "Ginger-Garlic Paste", "quantity": "1", "unit": "tbsp"},
            {"name": "Coriander Powder", "quantity": "1", "unit": "tsp"},
            {"name": "Cumin Powder", "quantity": "1", "unit": "tsp"},
            {"name": "Oil", "quantity": "2", "unit": "tbsp"}
        ],
        "utensils/appliances": [9, 11, 8]
    },
    {
        "name": "Veggie Lasagna",
        "servings": 6,
        "prep_time": "30 min",
        "cook_time": "45 min",
        "instructions": "Preheat oven. Sauté onions, garlic, and vegetables in olive oil. Add tomato sauce, salt, pepper, oregano, and simmer. Prepare béchamel sauce with butter, flour, and milk. Layer lasagna sheets with veggie sauce, béchamel, and cheese. Repeat layers. Top with cheese and bake until golden.",
        "ingredients": [
            {"name": "Lasagna Sheets", "quantity": "9", "unit": "pieces"},
            {"name": "Mixed Vegetables", "quantity": "300", "unit": "g"},
            {"name": "Tomato Sauce", "quantity": "400", "unit": "ml"},
            {"name": "Onion", "quantity": "1", "unit": "piece"},
            {"name": "Garlic", "quantity": "2", "unit": "cloves"},
            {"name": "Olive Oil", "quantity": "2", "unit": "tbsp"},
            {"name": "Salt", "quantity": "1", "unit": "tsp"},
            {"name": "Black Pepper", "quantity": "0.5", "unit": "tsp"},
            {"name": "Dried Oregano", "quantity": "1", "unit": "tsp"},
            {"name": "Butter", "quantity": "30", "unit": "g"},
            {"name": "Flour", "quantity": "30", "unit": "g"},
            {"name": "Milk", "quantity": "300", "unit": "ml"},
            {"name": "Mozzarella Cheese", "quantity": "200", "unit": "g"}
        ],
        "utensils/appliances": [21, 9, 11]
    },
        {
        "name": "Teriyaki Salmon",
        "servings": 2,
        "prep_time": "15 min",
        "cook_time": "15 min",
        "instructions": "Marinate salmon fillets in soy sauce, mirin, brown sugar, and ginger for 15 minutes. Heat a grill or pan. Cook salmon on each side for 4–5 minutes until caramelized and flaky. Reduce leftover marinade in a saucepan until thickened. Drizzle sauce over salmon and serve with steamed rice.",
        "ingredients": [
            {"name": "Salmon Fillets", "quantity": "300", "unit": "g"},
            {"name": "Soy Sauce", "quantity": "3", "unit": "tbsp"},
            {"name": "Mirin", "quantity": "2", "unit": "tbsp"},
            {"name": "Brown Sugar", "quantity": "1.5", "unit": "tbsp"},
            {"name": "Ginger", "quantity": "1", "unit": "tsp"},
            {"name": "Rice", "quantity": "1", "unit": "cup"}
        ],
        "utensils/appliances": [22, 24, 9]
    },
    {
        "name": "Pancakes",
        "servings": 4,
        "prep_time": "10 min",
        "cook_time": "20 min",
        "instructions": "Mix flour, baking powder, salt, and sugar in a bowl. In another bowl, whisk milk, eggs, and melted butter. Combine wet and dry ingredients. Heat a pan and pour batter. Cook until bubbles form, flip and cook until golden. Serve with syrup or toppings.",
        "ingredients": [
            {"name": "Flour", "quantity": "200", "unit": "g"},
            {"name": "Baking Powder", "quantity": "2", "unit": "tsp"},
            {"name": "Salt", "quantity": "0.5", "unit": "tsp"},
            {"name": "Sugar", "quantity": "2", "unit": "tbsp"},
            {"name": "Milk", "quantity": "250", "unit": "ml"},
            {"name": "Eggs", "quantity": "2", "unit": "pieces"},
            {"name": "Butter", "quantity": "2", "unit": "tbsp"}
        ],
        "utensils/appliances": [8, 16, 11]
    },
    {
        "name": "Garlic Bread",
        "servings": 6,
        "prep_time": "10 min",
        "cook_time": "12 min",
        "instructions": "Preheat oven. Mix softened butter with minced garlic, parsley, and salt. Slice baguette and spread garlic butter on each slice. Place on baking tray. Bake until crispy and golden. Serve warm.",
        "ingredients": [
            {"name": "Baguette", "quantity": "1", "unit": "loaf"},
            {"name": "Butter", "quantity": "80", "unit": "g"},
            {"name": "Garlic", "quantity": "4", "unit": "cloves"},
            {"name": "Parsley", "quantity": "2", "unit": "tbsp"},
            {"name": "Salt", "quantity": "0.5", "unit": "tsp"}
        ],
        "utensils/appliances": [21, 16]
    },
        {
        "name": "Egg Fried Rice",
        "servings": 4,
        "prep_time": "15 min",
        "cook_time": "15 min",
        "instructions": "Cook rice and let it cool. Beat eggs and scramble in a hot wok with oil. Set aside. Sauté garlic and vegetables. Add rice, soy sauce, salt, and pepper. Toss to mix. Return eggs to the wok and stir through. Serve hot.",
        "ingredients": [
            {"name": "Cooked Rice", "quantity": "3", "unit": "cups"},
            {"name": "Eggs", "quantity": "3", "unit": "pieces"},
            {"name": "Mixed Vegetables", "quantity": "200", "unit": "g"},
            {"name": "Garlic", "quantity": "2", "unit": "cloves"},
            {"name": "Soy Sauce", "quantity": "2", "unit": "tbsp"},
            {"name": "Salt", "quantity": "0.5", "unit": "tsp"},
            {"name": "Black Pepper", "quantity": "0.25", "unit": "tsp"},
            {"name": "Oil", "quantity": "1", "unit": "tbsp"}
        ],
        "utensils/appliances": [8, 11, 24]
    },
    {
        "name": "Steamed Dumplings",
        "servings": 4,
        "prep_time": "30 min",
        "cook_time": "10 min",
        "instructions": "Prepare filling with minced meat, cabbage, garlic, soy sauce, sesame oil, and seasonings. Place a spoonful in each wrapper, fold and seal. Steam for 10 minutes until cooked through. Serve with dipping sauce.",
        "ingredients": [
            {"name": "Dumpling Wrappers", "quantity": "30", "unit": "pieces"},
            {"name": "Minced Meat", "quantity": "300", "unit": "g"},
            {"name": "Cabbage", "quantity": "100", "unit": "g"},
            {"name": "Garlic", "quantity": "2", "unit": "cloves"},
            {"name": "Soy Sauce", "quantity": "1.5", "unit": "tbsp"},
            {"name": "Sesame Oil", "quantity": "1", "unit": "tsp"},
            {"name": "Salt", "quantity": "0.5", "unit": "tsp"},
            {"name": "Pepper", "quantity": "0.25", "unit": "tsp"}
        ],
        "utensils/appliances": [10, 12]
    },
    {
        "name": "Beef Tacos",
        "servings": 4,
        "prep_time": "15 min",
        "cook_time": "15 min",
        "instructions": "Cook ground beef with onion and garlic until browned. Add taco seasoning, water, and simmer. Warm taco shells. Fill with beef, lettuce, cheese, and salsa. Serve immediately.",
        "ingredients": [
            {"name": "Ground Beef", "quantity": "400", "unit": "g"},
            {"name": "Onion", "quantity": "1", "unit": "piece"},
            {"name": "Garlic", "quantity": "2", "unit": "cloves"},
            {"name": "Taco Seasoning", "quantity": "2", "unit": "tbsp"},
            {"name": "Water", "quantity": "0.5", "unit": "cup"},
            {"name": "Taco Shells", "quantity": "8", "unit": "pieces"},
            {"name": "Lettuce", "quantity": "100", "unit": "g"},
            {"name": "Cheddar Cheese", "quantity": "100", "unit": "g"},
            {"name": "Salsa", "quantity": "100", "unit": "g"}
        ],
        "utensils/appliances": [8, 11]
    },
        {
        "name": "Chicken Noodle Soup",
        "servings": 6,
        "prep_time": "20 min",
        "cook_time": "40 min",
        "instructions": "In a large pot, sauté onions, garlic, carrots, and celery in olive oil. Add diced chicken and cook until white. Pour in chicken broth and bring to a boil. Add noodles and cook until tender. Season with salt and pepper. Garnish with parsley and serve hot.",
        "ingredients": [
            {"name": "Chicken Breast", "quantity": "300", "unit": "g"},
            {"name": "Onion", "quantity": "1", "unit": "piece"},
            {"name": "Garlic", "quantity": "2", "unit": "cloves"},
            {"name": "Carrot", "quantity": "2", "unit": "pieces"},
            {"name": "Celery", "quantity": "2", "unit": "stalks"},
            {"name": "Chicken Broth", "quantity": "1.5", "unit": "L"},
            {"name": "Egg Noodles", "quantity": "200", "unit": "g"},
            {"name": "Salt", "quantity": "1.5", "unit": "tsp"},
            {"name": "Black Pepper", "quantity": "1", "unit": "tsp"},
            {"name": "Olive Oil", "quantity": "1", "unit": "tbsp"},
            {"name": "Fresh Parsley", "quantity": "1", "unit": "tbsp"}
        ],
        "utensils/appliances": [9, 11]
    },
    {
        "name": "Shrimp Scampi",
        "servings": 3,
        "prep_time": "10 min",
        "cook_time": "15 min",
        "instructions": "Cook pasta until al dente. In a pan, melt butter with olive oil. Sauté garlic and add shrimp. Cook until pink. Stir in lemon juice and cooked pasta. Toss to coat and garnish with parsley. Serve hot.",
        "ingredients": [
            {"name": "Shrimp", "quantity": "300", "unit": "g"},
            {"name": "Garlic", "quantity": "3", "unit": "cloves"},
            {"name": "Butter", "quantity": "2", "unit": "tbsp"},
            {"name": "Olive Oil", "quantity": "1", "unit": "tbsp"},
            {"name": "Lemon Juice", "quantity": "2", "unit": "tbsp"},
            {"name": "Spaghetti", "quantity": "200", "unit": "g"},
            {"name": "Salt", "quantity": "1", "unit": "tsp"},
            {"name": "Fresh Parsley", "quantity": "1", "unit": "tbsp"}
        ],
        "utensils/appliances": [8, 9, 11]
    },
    {
        "name": "Quiche Lorraine",
        "servings": 6,
        "prep_time": "25 min",
        "cook_time": "40 min",
        "instructions": "Preheat oven. Prepare pastry crust using flour, butter, and water. Line a pie dish and blind bake. Whisk eggs, cream, salt, and pepper. Add cooked bacon and cheese. Pour mixture into crust. Bake until set and golden. Let cool slightly before serving.",
        "ingredients": [
            {"name": "Flour", "quantity": "200", "unit": "g"},
            {"name": "Butter", "quantity": "100", "unit": "g"},
            {"name": "Cold Water", "quantity": "3", "unit": "tbsp"},
            {"name": "Eggs", "quantity": "3", "unit": "pieces"},
            {"name": "Cream", "quantity": "200", "unit": "ml"},
            {"name": "Salt", "quantity": "0.5", "unit": "tsp"},
            {"name": "Black Pepper", "quantity": "0.25", "unit": "tsp"},
            {"name": "Bacon", "quantity": "100", "unit": "g"},
            {"name": "Gruyere Cheese", "quantity": "100", "unit": "g"}
        ],
        "utensils/appliances": [7, 21, 16]
    },
        {
        "name": "Miso Soup",
        "servings": 4,
        "prep_time": "10 min",
        "cook_time": "10 min",
        "instructions": "Bring water to a gentle simmer. Add dashi granules and stir to dissolve. Add cubed tofu and wakame seaweed. Reduce heat. Dissolve miso paste in a ladleful of broth and return to pot. Do not boil. Garnish with green onions and serve.",
        "ingredients": [
            {"name": "Water", "quantity": "1", "unit": "L"},
            {"name": "Dashi Granules", "quantity": "2", "unit": "tsp"},
            {"name": "Miso Paste", "quantity": "3", "unit": "tbsp"},
            {"name": "Tofu", "quantity": "200", "unit": "g"},
            {"name": "Wakame Seaweed", "quantity": "10", "unit": "g"},
            {"name": "Green Onions", "quantity": "2", "unit": "stalks"}
        ],
        "utensils/appliances": [9, 23]
    },
    {
        "name": "Pad Thai",
        "servings": 4,
        "prep_time": "20 min",
        "cook_time": "15 min",
        "instructions": "Soak rice noodles in warm water. Stir-fry garlic, tofu, and shrimp in oil. Push aside, scramble eggs in same pan. Add noodles and sauce. Toss everything together. Add bean sprouts and peanuts. Garnish with lime wedges and serve.",
        "ingredients": [
            {"name": "Rice Noodles", "quantity": "200", "unit": "g"},
            {"name": "Shrimp", "quantity": "200", "unit": "g"},
            {"name": "Tofu", "quantity": "100", "unit": "g"},
            {"name": "Garlic", "quantity": "2", "unit": "cloves"},
            {"name": "Eggs", "quantity": "2", "unit": "pieces"},
            {"name": "Pad Thai Sauce", "quantity": "4", "unit": "tbsp"},
            {"name": "Bean Sprouts", "quantity": "100", "unit": "g"},
            {"name": "Peanuts", "quantity": "2", "unit": "tbsp"},
            {"name": "Lime Wedges", "quantity": "4", "unit": "pieces"},
            {"name": "Oil", "quantity": "2", "unit": "tbsp"}
        ],
        "utensils/appliances": [8, 11]
    },
    {
        "name": "Chicken Satay",
        "servings": 4,
        "prep_time": "30 min",
        "cook_time": "15 min",
        "instructions": "Marinate chicken pieces in coconut milk, curry powder, garlic, and soy sauce for at least 30 minutes. Thread onto skewers. Grill or pan-fry until golden and cooked through. Serve with warm peanut dipping sauce.",
        "ingredients": [
            {"name": "Chicken Thighs", "quantity": "500", "unit": "g"},
            {"name": "Coconut Milk", "quantity": "100", "unit": "ml"},
            {"name": "Curry Powder", "quantity": "1", "unit": "tbsp"},
            {"name": "Garlic", "quantity": "2", "unit": "cloves"},
            {"name": "Soy Sauce", "quantity": "1.5", "unit": "tbsp"},
            {"name": "Peanut Sauce", "quantity": "100", "unit": "g"}
        ],
        "utensils/appliances": [22, 12]
    },
        {
        "name": "Lentil Soup",
        "servings": 6,
        "prep_time": "15 min",
        "cook_time": "45 min",
        "instructions": "Heat olive oil in a pot. Sauté onions, carrots, and garlic until soft. Add lentils, cumin, salt, pepper, and vegetable broth. Bring to a boil, then simmer for 30 minutes. Blend part of the soup for a thicker texture. Stir in lemon juice and serve.",
        "ingredients": [
            {"name": "Red Lentils", "quantity": "300", "unit": "g"},
            {"name": "Onion", "quantity": "1", "unit": "piece"},
            {"name": "Carrots", "quantity": "2", "unit": "pieces"},
            {"name": "Garlic", "quantity": "3", "unit": "cloves"},
            {"name": "Olive Oil", "quantity": "2", "unit": "tbsp"},
            {"name": "Ground Cumin", "quantity": "1", "unit": "tsp"},
            {"name": "Salt", "quantity": "1.5", "unit": "tsp"},
            {"name": "Black Pepper", "quantity": "0.5", "unit": "tsp"},
            {"name": "Vegetable Broth", "quantity": "1.5", "unit": "L"},
            {"name": "Lemon Juice", "quantity": "2", "unit": "tbsp"}
        ],
        "utensils/appliances": [9, 17]
    },
    {
        "name": "Falafel",
        "servings": 4,
        "prep_time": "25 min",
        "cook_time": "10 min",
        "instructions": "Soak chickpeas overnight. Blend with onion, garlic, parsley, cumin, coriander, and salt. Form into balls. Heat oil and fry falafel until golden. Drain and serve with tahini sauce and pita bread.",
        "ingredients": [
            {"name": "Dried Chickpeas", "quantity": "250", "unit": "g"},
            {"name": "Onion", "quantity": "1", "unit": "piece"},
            {"name": "Garlic", "quantity": "3", "unit": "cloves"},
            {"name": "Parsley", "quantity": "1", "unit": "cup"},
            {"name": "Cumin Powder", "quantity": "1", "unit": "tsp"},
            {"name": "Coriander Powder", "quantity": "1", "unit": "tsp"},
            {"name": "Salt", "quantity": "1", "unit": "tsp"},
            {"name": "Oil", "quantity": "500", "unit": "ml"},
            {"name": "Tahini Sauce", "quantity": "100", "unit": "ml"}
        ],
        "utensils/appliances": [18, 8]
    },
    {
        "name": "Hummus",
        "servings": 6,
        "prep_time": "10 min",
        "cook_time": "0 min",
        "instructions": "In a food processor, blend chickpeas, tahini, garlic, lemon juice, salt, and olive oil until smooth. Add water to adjust consistency. Serve drizzled with olive oil and a sprinkle of paprika.",
        "ingredients": [
            {"name": "Cooked Chickpeas", "quantity": "300", "unit": "g"},
            {"name": "Tahini", "quantity": "3", "unit": "tbsp"},
            {"name": "Garlic", "quantity": "2", "unit": "cloves"},
            {"name": "Lemon Juice", "quantity": "2", "unit": "tbsp"},
            {"name": "Salt", "quantity": "1", "unit": "tsp"},
            {"name": "Olive Oil", "quantity": "3", "unit": "tbsp"},
            {"name": "Water", "quantity": "2", "unit": "tbsp"},
            {"name": "Paprika", "quantity": "0.25", "unit": "tsp"}
        ],
        "utensils/appliances": [17]
    }
]

def parse_minutes(time_str):
    return int(time_str.replace("min", "").strip())


cursor = get_cursor()
try:
    for recipe in recipes:
        query = "INSERT INTO recipe (name, servings, prep_time, cook_time, instructions, user_id) VALUES (?, ?, ?, ?, ?, NULL)"
        data = (recipe["name"], recipe["servings"], parse_minutes(recipe["prep_time"]), parse_minutes(recipe["cook_time"]), recipe["instructions"])
        cursor.execute(query, data)

        recipe_id = cursor.lastrowid

        for item in recipe["ingredients"]:
            item_query = "INSERT INTO recipe_items (recipe_id, item_name, unit, quantity) VALUES (?, ?, ?, ?)"
            item_data = (recipe_id, item["name"], item["unit"], item["quantity"])
            cursor.execute(item_query, item_data)
        
        for tool_id in recipe["utensils/appliances"]:
            tool_query = "INSERT INTO recipe_tool (recipe_id, tool_id) VALUES (?, ?)"
            tool_data = (recipe_id, tool_id)
            cursor.execute(tool_query, tool_data)

        print(f"{recipe["name"]} has been inserted.")
    commit()
    logging.info("All recipes inserted successfully.")
except Exception as e:
    logging.error(f"[ERROR] Failed to insert recipes: {e}")