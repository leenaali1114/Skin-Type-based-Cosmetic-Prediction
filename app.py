from flask import Flask, render_template, request, jsonify
import os
import pandas as pd
from model import CosmeticsRecommender

app = Flask(__name__)

# Initialize the recommender model
recommender = CosmeticsRecommender()

# Only delete the model file if explicitly requested (e.g., via an environment variable)
if os.environ.get('RETRAIN_MODEL') == 'true':
    if os.path.exists('cosmetics_recommender_model.pkl'):
        try:
            os.remove('cosmetics_recommender_model.pkl')
            print("Deleted existing model file to ensure fresh training")
        except:
            print("Could not delete existing model file")

# Try to load a saved model, or train a new one if needed
if not recommender.load_model():
    print("No saved model found. Training a new model...")
    if not recommender.load_data():
        print("No dataset found. Generating synthetic data...")
        from generate_synthetic_data import generate_synthetic_cosmetics_data
        df = generate_synthetic_cosmetics_data(2500)
        recommender.df = df
    
    recommender.preprocess()
    recommender.train()
    recommender.save_model()
else:
    print("Model loaded successfully. Ready to make recommendations!")

@app.route('/')
def index():
    # Get unique categories and price categories for filters
    categories = sorted(recommender.df['Category'].unique())
    price_categories = ['budget', 'affordable', 'premium', 'luxury']
    
    return render_template('index.html', categories=categories, price_categories=price_categories)

@app.route('/recommend', methods=['POST'])
def recommend():
    try:
        data = request.form
        print(f"Received recommendation request: {data}")
        
        skin_type = data.get('skin_type', 'normal')
        category = data.get('category', None)
        price_category = data.get('price_category', None)
        
        try:
            num_recommendations = int(data.get('num_recommendations', 5))
        except ValueError:
            num_recommendations = 5
            
        print(f"Looking for recommendations with: skin_type={skin_type}, category={category}, price_category={price_category}")
        
        # Get recommendations
        recommendations = recommender.recommend_products(
            skin_type=skin_type,
            category=category if category and category != 'all' else None,
            price_category=price_category if price_category and price_category != 'all' else None,
            num_recommendations=num_recommendations
        )
        
        print(f"Found {len(recommendations)} recommendations")
        
        # Format recommendations for display
        formatted_recommendations = []
        for rec in recommendations:
            try:
                # Print the raw recommendation for debugging
                print(f"Processing recommendation: {rec}")
                
                # Handle potential missing or invalid values
                name = rec.get('Name', 'Unknown Product')
                brand = rec.get('Brand', 'Unknown Brand')
                category = rec.get('Category', 'Unknown Category')
                
                # Handle price formatting
                try:
                    price = f"${float(rec.get('Price', 0)):.2f}"
                except (ValueError, TypeError):
                    price = "Price not available"
                
                # Handle compatibility score
                try:
                    compatibility = f"{float(rec.get(f'{skin_type}_skin_compatibility', 0)) * 100:.0f}%"
                except (ValueError, TypeError):
                    compatibility = "0%"
                
                formatted_rec = {
                    'name': name,
                    'brand': brand,
                    'category': category,
                    'price': price,
                    'rating': rec.get('Rating', 'N/A'),
                    'description': rec.get('Description', 'No description available'),
                    'compatibility': compatibility,
                    'ingredients': rec.get('Ingredients', 'Ingredients not listed')
                }
                formatted_recommendations.append(formatted_rec)
                print(f"Formatted recommendation: {formatted_rec}")
            except Exception as e:
                print(f"Error formatting recommendation: {e}")
                continue
        
        return jsonify({'recommendations': formatted_recommendations})
    except Exception as e:
        import traceback
        print(f"Error in recommend route: {e}")
        print(traceback.format_exc())
        return jsonify({'error': str(e), 'recommendations': []})

@app.route('/skin_quiz')
def skin_quiz():
    return render_template('skin_quiz.html')

@app.route('/quiz_result', methods=['POST'])
def quiz_result():
    data = request.form
    
    # Process quiz answers to determine skin type
    answers = {
        'skin_feel': data.get('skin_feel', ''),
        'skin_look': data.get('skin_look', ''),
        'skin_concern': data.get('skin_concern', ''),
        'reaction': data.get('reaction', ''),
        'climate': data.get('climate', '')
    }
    
    # Simple algorithm to determine skin type from quiz answers
    skin_type = determine_skin_type(answers)
    
    # Get recommendations based on determined skin type
    recommendations = recommender.recommend_products(
        skin_type=skin_type,
        num_recommendations=5
    )
    
    # Format recommendations for display
    formatted_recommendations = []
    for rec in recommendations:
        formatted_rec = {
            'name': rec.get('Name', 'Unknown Product'),
            'brand': rec.get('Brand', 'Unknown Brand'),
            'category': rec.get('Category', 'Unknown Category'),
            'price': f"${rec.get('Price', 0):.2f}",
            'rating': rec.get('Rating', 'N/A'),
            'description': rec.get('Description', 'No description available'),
            'compatibility': f"{rec.get(f'{skin_type}_skin_compatibility', 0) * 100:.0f}%",
            'ingredients': rec.get('Ingredients', 'Ingredients not listed')
        }
        formatted_recommendations.append(formatted_rec)
    
    return render_template('quiz_result.html', 
                          skin_type=skin_type, 
                          recommendations=formatted_recommendations)

def determine_skin_type(answers):
    # Simple scoring system for skin type determination
    scores = {
        'dry': 0,
        'oily': 0,
        'combination': 0,
        'sensitive': 0,
        'normal': 0
    }
    
    # Analyze skin feel
    if answers['skin_feel'] == 'tight':
        scores['dry'] += 2
    elif answers['skin_feel'] == 'greasy':
        scores['oily'] += 2
    elif answers['skin_feel'] == 'both':
        scores['combination'] += 2
    elif answers['skin_feel'] == 'comfortable':
        scores['normal'] += 2
    
    # Analyze skin look
    if answers['skin_look'] == 'flaky':
        scores['dry'] += 2
    elif answers['skin_look'] == 'shiny':
        scores['oily'] += 2
    elif answers['skin_look'] == 'shiny_t_zone':
        scores['combination'] += 2
    elif answers['skin_look'] == 'balanced':
        scores['normal'] += 2
    
    # Analyze skin concern
    if answers['skin_concern'] == 'dryness':
        scores['dry'] += 1
    elif answers['skin_concern'] == 'acne':
        scores['oily'] += 1
    elif answers['skin_concern'] == 'both':
        scores['combination'] += 1
    elif answers['skin_concern'] == 'redness':
        scores['sensitive'] += 2
    
    # Analyze reaction to products
    if answers['reaction'] == 'often':
        scores['sensitive'] += 2
    
    # Analyze climate effect
    if answers['climate'] == 'drier':
        scores['dry'] += 1
    elif answers['climate'] == 'oilier':
        scores['oily'] += 1
    
    # Find the skin type with the highest score
    max_score = 0
    determined_type = 'normal'  # Default
    
    for skin_type, score in scores.items():
        if score > max_score:
            max_score = score
            determined_type = skin_type
    
    return determined_type

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True) 