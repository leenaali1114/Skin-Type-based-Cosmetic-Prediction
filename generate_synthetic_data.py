import pandas as pd
import numpy as np
import random
from faker import Faker

fake = Faker()

def generate_synthetic_cosmetics_data(num_samples=2500):
    # Product categories
    categories = ['Moisturizer', 'Cleanser', 'Serum', 'Mask', 'Sunscreen', 
                 'Foundation', 'Lipstick', 'Eyeshadow', 'Blush', 'Concealer']
    
    # Brands
    brands = ['Glossier', 'The Ordinary', 'Fenty Beauty', 'Rare Beauty', 'CeraVe', 
             'Neutrogena', 'L\'Oreal', 'Maybelline', 'NYX', 'Estee Lauder',
             'Clinique', 'Drunk Elephant', 'Tatcha', 'Laneige', 'Innisfree']
    
    # Common ingredients for different skin types
    ingredients_by_skin_type = {
        'dry': ['Hyaluronic Acid', 'Glycerin', 'Shea Butter', 'Ceramides', 'Squalane', 
               'Jojoba Oil', 'Aloe Vera', 'Vitamin E', 'Argan Oil', 'Avocado Oil'],
        'oily': ['Salicylic Acid', 'Niacinamide', 'Tea Tree Oil', 'Clay', 'Zinc', 
                'Witch Hazel', 'Charcoal', 'Glycolic Acid', 'Retinol', 'Kaolin'],
        'sensitive': ['Aloe Vera', 'Chamomile', 'Oatmeal', 'Calendula', 'Centella Asiatica', 
                     'Green Tea', 'Allantoin', 'Bisabolol', 'Panthenol', 'Madecassoside'],
        'combination': ['Niacinamide', 'Hyaluronic Acid', 'Glycerin', 'Vitamin E', 
                       'Jojoba Oil', 'Aloe Vera', 'Squalane', 'Green Tea', 'Ceramides'],
        'normal': ['Vitamin C', 'Vitamin E', 'Peptides', 'Antioxidants', 'Coenzyme Q10', 
                  'Aloe Vera', 'Hyaluronic Acid', 'Niacinamide', 'Ceramides']
    }
    
    # Generate data
    data = []
    
    for i in range(num_samples):
        # Randomly select primary skin type for this product
        primary_skin_type = random.choice(list(ingredients_by_skin_type.keys()))
        
        # Select 3-7 ingredients, biased toward the primary skin type
        num_ingredients = random.randint(3, 7)
        primary_type_ingredients = random.sample(ingredients_by_skin_type[primary_skin_type], 
                                               min(num_ingredients-1, len(ingredients_by_skin_type[primary_skin_type])))
        
        # Add 1-2 ingredients from other skin types
        other_ingredients = []
        for skin_type, ingredients in ingredients_by_skin_type.items():
            if skin_type != primary_skin_type and random.random() < 0.3:
                other_ingredients.extend(random.sample(ingredients, 1))
        
        all_ingredients = primary_type_ingredients + other_ingredients[:2]
        random.shuffle(all_ingredients)
        ingredients_str = ', '.join(all_ingredients)
        
        # Calculate compatibility scores
        compatibility = {}
        for skin_type, skin_ingredients in ingredients_by_skin_type.items():
            matches = sum([1 for ing in all_ingredients if ing in skin_ingredients])
            compatibility[f'{skin_type}_skin_compatibility'] = min(matches / len(all_ingredients), 1.0)
        
        # Generate other product details
        category = random.choice(categories)
        brand = random.choice(brands)
        name = f"{brand} {category} {fake.word().capitalize()}"
        price = round(random.uniform(5.99, 89.99), 2)
        rating = round(random.uniform(3.0, 5.0), 1)
        
        # Create product description
        benefits = ["hydrating", "nourishing", "brightening", "clarifying", "soothing", 
                   "anti-aging", "mattifying", "pore-minimizing", "calming", "revitalizing"]
        selected_benefits = random.sample(benefits, 2)
        description = f"A {selected_benefits[0]} and {selected_benefits[1]} {category.lower()} enriched with {all_ingredients[0]} and {all_ingredients[1]}."
        
        # Determine price category
        if price < 15:
            price_category = 'budget'
        elif price < 30:
            price_category = 'affordable'
        elif price < 50:
            price_category = 'premium'
        else:
            price_category = 'luxury'
        
        # Create product entry
        product = {
            'Name': name,
            'Brand': brand,
            'Category': category,
            'Price': price,
            'Rating': rating,
            'Ingredients': ingredients_str,
            'Description': description,
            'price_category': price_category
        }
        
        # Add compatibility scores
        product.update(compatibility)
        
        data.append(product)
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Save to CSV
    df.to_csv('synthetic_cosmetics_dataset.csv', index=False)
    print(f"Generated {num_samples} synthetic cosmetic products!")
    
    return df

if __name__ == "__main__":
    generate_synthetic_cosmetics_data(500) 