# NutriPal - AI-Powered Nutrition Coach

NutriPal is an AI-powered nutrition coach designed to help users make informed decisions about their diet and wellness. It provides personalized recipe recommendations based on health profiles and dietary preferences, while also considering environmental impacts.

## Features

- **Recipe Generator**: Upload food images and get personalized recipes based on detected ingredients
- **Next Food Prediction**: AI predicts what you might want to eat next based on your food history
- **Meal Planner**: Plan and track your meals throughout the week
- **Community Recipes**: Share and discover recipes from other users
- **AI Nutritionist**: Chat with an AI nutritionist for personalized nutrition advice

## 🔧 Technologies Used

- **Frontend**: Streamlit
- **Backend**: Python
- **AI Models**: HuggingFace API (Mistral, BLIP)
- **Database**: MongoDB
- **Vector Database**: Qdrant
- **LLM Integration**: LangChain

## 🚀 Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/nutripal.git
   cd nutripal
   ```

2. Install required packages:
   ```
   pip install -r requirements.txt
   ```

3. Set up your secrets:
   - For local development: Create a `.streamlit/secrets.toml` file with:
     ```toml
     mongokey = "your_mongodb_connection_string"
     huggingfaceapikey = "your_huggingface_api_key"
     ```
   - For Streamlit Cloud deployment: Navigate to Streamlit → Manage App → Settings → Secrets and add the same keys.

4. Run the application:
   ```
   streamlit run app.py
   ```

## 🔐 API Key Setup

NutriPal requires the following API keys:

1. **HuggingFace API Key**:
   - Create an account at [HuggingFace](https://huggingface.co/)
   - Get your API key from [HuggingFace Settings](https://huggingface.co/settings/tokens)
   - Add it to your secrets as `huggingfaceapikey`

2. **MongoDB Connection String**:
   - Set up a MongoDB Atlas account
   - Create a cluster and get your connection string
   - Add it to your secrets as `mongokey`

## 📁 Project Structure

