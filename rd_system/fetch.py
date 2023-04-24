import requests
import pandas as pd

# Spoonacular API credentials
api_key = '654780eed1e84966880bfd5299afaa20'
base_url = 'https://api.spoonacular.com/recipes/'

# Number of recipes to retrieve
num_recipes = 100000

# List to store recipe data
recipes_data = []

# Loop through recipe IDs to retrieve recipe data
for recipe_id in range(1, num_recipes+1):
    # Send request to Spoonacular API
    url = base_url + str(recipe_id) + '/information?654780eed1e84966880bfd5299afaa20=' + api_key
    response = requests.get(url)
    
    # If the request is successful, extract recipe data
    if response.status_code == 200:
        recipe = response.json()
        
        # Extract relevant recipe data
        recipe_id = recipe['id']
        name = recipe['title']
        submitted = recipe['dateModified']
        tags = recipe['dishTypes']
        steps = [step['step'] for step in recipe['analyzedInstructions'][0]['steps']]
        description = recipe['summary']
        ingredients = [ingredient['name'] for ingredient in recipe['extendedIngredients']]
        nutrition = [nutrient['amount'] for nutrient in recipe['nutrition']['nutrients']]
        
        # Add recipe data to list
        recipes_data.append({
            'recipe_id': recipe_id,
            'name': name,
            'submitted': submitted,
            'tags': tags,
            'steps': steps,
            'description': description,
            'ingredients': ingredients,
            'nutrition': nutrition
        })
        
    # Print progress every 1000 recipes
    if recipe_id % 1000 == 0:
        print(f"Retrieved data for {recipe_id} recipes.")

# Convert recipe data to DataFrame
df = pd.DataFrame(recipes_data)

# Save DataFrame to CSV file
df.to_csv('recipes_data.csv', index=False)

print("Done!")
