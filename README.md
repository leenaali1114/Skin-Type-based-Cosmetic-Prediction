# BeautyMatch - Cosmetics Recommendation System

A Flask-based web application that recommends cosmetic products based on skin type and preferences. BeautyMatch uses machine learning to analyze product ingredients and their compatibility with different skin types to provide personalized recommendations.

## Features

- **Personalized Product Recommendations**: Get customized cosmetic product suggestions based on your skin type
- **Interactive Skin Type Quiz**: Determine your skin type through a series of questions about your skin characteristics
- **Advanced Filtering**: Filter recommendations by product category and price range
- **Ingredient Analysis**: Recommendations based on ingredient compatibility with different skin types
- **Responsive Design**: Optimized for all devices from mobile to desktop

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/beautymatch.git
   cd beautymatch
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the data preparation script to generate the dataset:
   ```
   python data_preparation.py
   ```

4. Train the recommendation model:
   ```
   python model.py
   ```

5. Run the application:
   ```
   python app.py
   ```

6. Access the application at http://localhost:5000

## Project Structure

- `app.py`: Flask application with routes and controllers
- `model.py`: Recommendation engine using machine learning
- `data_preparation.py`: Data processing and enhancement
- `generate_synthetic_data.py`: Creates synthetic cosmetics data for testing
- `templates/`: HTML templates for the web interface
  - `layout.html`: Base template with common elements
  - `index.html`: Home page with recommendation form
  - `skin_quiz.html`: Interactive quiz to determine skin type
  - `quiz_result.html`: Shows quiz results and recommendations
  - `about.html`: Information about the application
- `static/`: CSS and JavaScript files
  - `css/style.css`: Styling for the application
  - `js/script.js`: Client-side functionality

## How It Works

1. **Data Collection**: The system uses a dataset of cosmetic products with details about ingredients, product types, and prices.

2. **Data Processing**: The `data_preparation.py` script enhances the dataset by:
   - Cleaning text data
   - Extracting ingredients
   - Calculating skin type compatibility scores
   - Categorizing products by price

3. **Recommendation Engine**: The system uses a nearest neighbors algorithm to find products that are most compatible with a user's skin type:
   - Products are represented as feature vectors combining numerical and text features
   - Numerical features include skin type compatibility scores
   - Text features are extracted from product descriptions and ingredients
   - The model finds the most similar products to a query vector representing the user's preferences

4. **User Interface**: The web interface allows users to:
   - Select their skin type directly
   - Take a quiz to determine their skin type
   - Filter recommendations by category and price
   - View detailed product information and compatibility scores

## Technologies Used

- **Backend**: Python, Flask
- **Data Processing**: Pandas, NumPy
- **Machine Learning**: Scikit-learn
- **Frontend**: HTML, CSS, JavaScript
- **Data Generation**: Faker

## Future Enhancements

- User accounts and saved preferences
- Product reviews and ratings
- Image recognition for skin analysis
- Integration with e-commerce platforms
- Mobile application

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Skin type compatibility algorithms based on dermatological research
- Product data structure inspired by cosmetics industry standards 