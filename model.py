import pandas as pd
import numpy as np
import pickle
import os
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class CosmeticsRecommender:
    def __init__(self):
        self.df = None
        self.tfidf_matrix = None
        self.feature_matrix = None
        self.scaler = StandardScaler()
        self.model = NearestNeighbors(n_neighbors=10, algorithm='auto', metric='cosine')
        self.feature_names = []  # Store feature names for validation
        
    def load_data(self, filepath='enhanced_cosmetics_dataset.csv'):
        try:
            self.df = pd.read_csv(filepath)
            print(f"Loaded dataset with {len(self.df)} products")
            return True
        except FileNotFoundError:
            try:
                self.df = pd.read_csv('synthetic_cosmetics_dataset.csv')
                print(f"Loaded synthetic dataset with {len(self.df)} products")
                return True
            except FileNotFoundError:
                print("No dataset found. Please run data preparation scripts first.")
                return False
    
    def preprocess(self):
        if self.df is None:
            print("No data loaded. Please load data first.")
            return False
        
        # Process text data (ingredients and descriptions)
        # Make sure both columns exist, if not create empty ones
        if 'Ingredients' not in self.df.columns:
            self.df['Ingredients'] = ''
        if 'Description' not in self.df.columns:
            self.df['Description'] = ''
            
        text_data = self.df['Ingredients'].fillna('') + ' ' + self.df['Description'].fillna('')
        
        # Create TF-IDF features
        tfidf = TfidfVectorizer(max_features=100, stop_words='english')
        self.tfidf_matrix = tfidf.fit_transform(text_data)
        
        # Prepare numerical features
        numerical_features = ['dry_skin_compatibility', 'oily_skin_compatibility', 
                             'sensitive_skin_compatibility', 'combination_skin_compatibility', 
                             'normal_skin_compatibility']
        
        # Check if all features exist
        self.feature_names = [f for f in numerical_features if f in self.df.columns]
        
        if not self.feature_names:
            print("Required skin compatibility features not found in dataset.")
            return False
        
        # Scale numerical features
        numerical_data = self.df[self.feature_names].fillna(0)
        scaled_numerical = self.scaler.fit_transform(numerical_data)
        
        # Combine features
        # Convert sparse matrix to dense for hstack
        tfidf_dense = self.tfidf_matrix.toarray()
        self.feature_matrix = np.hstack([scaled_numerical, tfidf_dense])
        
        print(f"Preprocessed data: {self.feature_matrix.shape} features")
        return True
    
    def train(self):
        if self.feature_matrix is None:
            print("No preprocessed data. Please preprocess data first.")
            return False
        
        # Fit the model
        self.model.fit(self.feature_matrix)
        print("Model trained successfully!")
        return True
    
    def recommend_products(self, skin_type='normal', category=None, price_category=None, num_recommendations=5):
        if self.feature_matrix is None or self.df is None or self.model is None:
            print("Model not ready. Please load data, preprocess, and train first.")
            return []
        
        # Create a query vector based on skin type
        skin_type_features = self.feature_names  # Use stored feature names
        
        if not skin_type_features:
            print("No skin type features available.")
            return []
        
        # Create a query vector with high value for the selected skin type
        query = np.zeros((1, len(skin_type_features)))
        
        # Find the index of the selected skin type
        try:
            skin_type_idx = skin_type_features.index(f'{skin_type}_skin_compatibility')
            query[0, skin_type_idx] = 1.0  # Set high preference for the selected skin type
        except ValueError:
            print(f"Skin type '{skin_type}' not found in features.")
            # Default to equal weights if skin type not found
            query = np.ones((1, len(skin_type_features))) / len(skin_type_features)
        
        # Scale the query vector
        scaled_query = self.scaler.transform(query)
        
        # Create a full query vector with text features (zeros for text features)
        if self.tfidf_matrix is not None:
            full_query = np.hstack([scaled_query, np.zeros((1, self.tfidf_matrix.shape[1]))])
            
            # Verify dimensions match
            if full_query.shape[1] != self.feature_matrix.shape[1]:
                print(f"Feature dimension mismatch: query has {full_query.shape[1]} features, model expects {self.feature_matrix.shape[1]}")
                print("Rebuilding model to match current data...")
                # Rebuild the model if dimensions don't match
                if self.preprocess() and self.train():
                    # Try again with the new model
                    return self.recommend_products(skin_type, category, price_category, num_recommendations)
                else:
                    return []
        else:
            print("Warning: TF-IDF matrix is None. Using only numerical features.")
            full_query = scaled_query
            
            # Verify dimensions match
            if full_query.shape[1] != self.feature_matrix.shape[1]:
                print(f"Feature dimension mismatch: query has {full_query.shape[1]} features, model expects {self.feature_matrix.shape[1]}")
                print("Rebuilding model to match current data...")
                # Rebuild the model if dimensions don't match
                if self.preprocess() and self.train():
                    # Try again with the new model
                    return self.recommend_products(skin_type, category, price_category, num_recommendations)
                else:
                    return []
        
        # Get recommendations
        try:
            distances, indices = self.model.kneighbors(full_query)
            
            # Convert to list of dictionaries
            recommendations = []
            
            for i in range(len(indices[0])):
                idx = indices[0][i]
                product = self.df.iloc[idx].to_dict()
                
                # Apply filters
                if category and product.get('Category') != category:
                    continue
                    
                if price_category and product.get('price_category') != price_category:
                    continue
                    
                recommendations.append(product)
                
                if len(recommendations) >= num_recommendations:
                    break
            
            return recommendations
        except Exception as e:
            print(f"Error getting recommendations: {e}")
            return []
    
    def save_model(self, filepath='cosmetics_recommender_model.pkl'):
        if self.model is None:
            print("No trained model to save.")
            return False
        
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'feature_matrix': self.feature_matrix,
            'df': self.df,
            'tfidf_matrix': self.tfidf_matrix,
            'feature_names': self.feature_names
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)
        
        print(f"Model saved to {filepath}")
        return True
    
    def load_model(self, filepath='cosmetics_recommender_model.pkl'):
        try:
            if not os.path.exists(filepath):
                print(f"Model file {filepath} not found.")
                return False
                
            with open(filepath, 'rb') as f:
                model_data = pickle.load(f)
            
            self.model = model_data['model']
            self.scaler = model_data['scaler']
            self.feature_matrix = model_data['feature_matrix']
            self.df = model_data['df']
            self.tfidf_matrix = model_data.get('tfidf_matrix')  # Handle older saved models
            self.feature_names = model_data.get('feature_names', [])  # Handle older saved models
            
            print(f"Model loaded from {filepath}")
            return True
        except Exception as e:
            print(f"Error loading model: {e}")
            # If there's an error loading the model, delete the file and return False
            if os.path.exists(filepath):
                try:
                    os.remove(filepath)
                    print(f"Deleted corrupted model file: {filepath}")
                except:
                    print(f"Could not delete corrupted model file: {filepath}")
            return False

# Train and save the model
if __name__ == "__main__":
    recommender = CosmeticsRecommender()
    
    # Try to load the enhanced dataset, if not available use synthetic data
    if not recommender.load_data('enhanced_cosmetics_dataset.csv'):
        print("Enhanced dataset not found. Generating synthetic data...")
        from generate_synthetic_data import generate_synthetic_cosmetics_data
        df = generate_synthetic_cosmetics_data(2500)
        recommender.df = df
    
    if recommender.preprocess() and recommender.train():
        recommender.save_model()
        
        # Test the model
        print("\nTesting recommendations for dry skin:")
        recommendations = recommender.recommend_products('dry')
        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. {rec.get('Name')} - Compatibility: {rec.get('dry_skin_compatibility', 0):.2f}") 