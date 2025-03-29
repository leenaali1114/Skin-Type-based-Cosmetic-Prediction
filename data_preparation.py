import pandas as pd
import numpy as np
import re
from sklearn.preprocessing import LabelEncoder
import os

def clean_text(text):
    if isinstance(text, str):
        # Remove special characters and extra spaces
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    return ""

def extract_ingredients(ingredients_str):
    if isinstance(ingredients_str, str):
        # Split by commas and clean each ingredient
        ingredients = [i.strip() for i in ingredients_str.split(',')]
        return ingredients
    return []

def create_enhanced_dataset():
    # Check if the original dataset exists
    if not os.path.exists('cosmetics_dataset.csv'):
        print("Original dataset 'cosmetics_dataset.csv' not found.")
        print("Generating synthetic data instead...")
        from generate_synthetic_data import generate_synthetic_cosmetics_data
        df = generate_synthetic_cosmetics_data(2500)
        print("Synthetic data generated successfully!")
    else:
        # Load the original dataset
        df = pd.read_csv('cosmetics_dataset.csv')
        print("Original dataset loaded successfully!")
    
    # Clean text columns
    text_columns = ['Name', 'Brand', 'Description', 'Ingredients']
    for col in text_columns:
        if col in df.columns:
            df[col] = df[col].apply(clean_text)
    
    # Extract product categories if not already present
    if 'Category' not in df.columns:
        df['Category'] = df['Name'].apply(lambda x: x.split()[0] if isinstance(x, str) and len(x.split()) > 0 else "Unknown")
    
    # Map common ingredients to skin types they're good for
    skin_friendly_ingredients = {
        'dry': ['hyaluronic acid', 'glycerin', 'shea butter', 'ceramides', 'squalane', 'jojoba oil', 'aloe vera'],
        'oily': ['salicylic acid', 'niacinamide', 'tea tree oil', 'clay', 'zinc', 'witch hazel', 'charcoal'],
        'sensitive': ['aloe vera', 'chamomile', 'oatmeal', 'calendula', 'centella asiatica', 'green tea', 'allantoin'],
        'combination': ['niacinamide', 'hyaluronic acid', 'glycerin', 'vitamin e', 'jojoba oil', 'aloe vera'],
        'normal': ['vitamin c', 'vitamin e', 'peptides', 'antioxidants', 'coenzyme q10', 'aloe vera']
    }
    
    # Function to determine skin type compatibility
    def get_skin_compatibility(ingredients_str):
        if not isinstance(ingredients_str, str):
            return {'dry': 0, 'oily': 0, 'sensitive': 0, 'combination': 0, 'normal': 0}
        
        ingredients_lower = ingredients_str.lower()
        compatibility = {}
        
        for skin_type, friendly_ingredients in skin_friendly_ingredients.items():
            score = sum([1 for ing in friendly_ingredients if ing in ingredients_lower])
            compatibility[skin_type] = min(score / 2, 1.0)  # Normalize to 0-1
            
        return compatibility
    
    # Add skin type compatibility scores
    compatibilities = df['Ingredients'].apply(get_skin_compatibility)
    
    for skin_type in ['dry', 'oily', 'sensitive', 'combination', 'normal']:
        df[f'{skin_type}_skin_compatibility'] = compatibilities.apply(lambda x: x.get(skin_type, 0))
    
    # Add price category if Price column exists
    if 'Price' in df.columns:
        # Convert to numeric, coercing errors to NaN
        df['Price'] = pd.to_numeric(df['Price'], errors='coerce')
        
        # Handle any NaN values by filling with median
        if df['Price'].isna().any():
            df['Price'] = df['Price'].fillna(df['Price'].median())
            
        # Create price categories
        df['price_category'] = pd.qcut(df['Price'], 
                                      q=4, 
                                      labels=['budget', 'affordable', 'premium', 'luxury'])
    
    # Save the enhanced dataset
    df.to_csv('enhanced_cosmetics_dataset.csv', index=False)
    print("Enhanced dataset created successfully!")
    
    return df

if __name__ == "__main__":
    create_enhanced_dataset() 