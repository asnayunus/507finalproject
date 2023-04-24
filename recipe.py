import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import base64
from flask import Flask, request, render_template, send_file
import matplotlib.pyplot as plt
import io

app = Flask(__name__)

# Load data
df = pd.read_csv('recipe_data.csv')

# Convert the 'nutrition' column from list to string format
df['nutrition'] = df['nutrition'].apply(lambda x: ','.join(map(str, x)))

# Remove columns with non-numeric values
df = df.drop(columns=['submitted', 'tags', 'steps', 'description', 'ingredients'])

# Define feature and target columns
target_col = df.columns[-1]
feature_cols = [col for col in df.columns if col != target_col and col != 'name']

# Convert nutrition values to float
df['nutrition'] = df['nutrition'].apply(lambda x: x.replace('[', '').replace(']', '').replace(' ', '').split(','))
df['nutrition'] = df['nutrition'].apply(lambda x: [float(i) if i not in ['', '.'] else 0 for i in x])
df = df.explode('nutrition')

# Fit LabelEncoder to target column
le = LabelEncoder()
df[target_col] = le.fit_transform(df[target_col])

# Split data into train and test sets
train_df, test_df = train_test_split(df, test_size=0.2)

# Train the decision tree
clf = DecisionTreeClassifier()
clf.fit(train_df[feature_cols], train_df[target_col])

# Group recipes by number of ingredients
ingredient_counts = df.groupby('n_ingredients').size().reset_index(name='counts')

def recommend_recipe(nutrition_values):
    nutrition_values = [float(x) if x!='' else 0 for x in nutrition_values.split(',')]
    # Drop additional feature columns
    nutrition_values = [nutrition_values[i] for i in range(len(nutrition_values)) if feature_cols[i] in df.columns]
    prediction = clf.predict([nutrition_values])[0]
    recipe_name = df[df[target_col] == prediction]['name'].iloc[0]
    return recipe_name

# Define a Flask route to render the HTML form
@app.route('/')
def home():
    return render_template('index.html')

# Define a Flask route to handle form submission
@app.route('/', methods=['POST'])
# Define a Flask route to handle form submission
@app.route('/', methods=['POST'])
def recommend():
    nutrition_values = request.form['nutrition_values']
    prediction = recommend_recipe(nutrition_values)

    # Create a new plot image buffer for every prediction
    ingredient_counts = df.groupby('n_ingredients').size().reset_index(name='counts')
    fig, ax = plt.subplots()
    ax.bar(ingredient_counts['n_ingredients'], ingredient_counts['counts'], alpha=0.7)

    ax.set_xlabel('Number of Ingredients')
    ax.set_ylabel('Number of Recipes')
    ax.set_title('Recipe Ingredient Counts')
    
    # Save the chart to a byte buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()

    # Pass the URL of the chart to the HTML template
    plot_url = base64.b64encode(buf.read()).decode('utf-8')
    plot_url = 'data:image/png;base64,{}'.format(plot_url)

    return render_template('index.html', prediction=prediction, plot_url=plot_url)


if __name__ == '__main__':
    app.run(debug=True)
