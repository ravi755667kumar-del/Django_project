import os
import joblib
import pandas as pd
from datetime import datetime
from shop.recommendations.weather import get_weather
from shop.recommendations.processes import MODEL_PATH
from shop.models import Drink, Snacks

# Global cache so we only load the heavy model ONCE from disk
_CACHED_MODEL = None

def get_ml_recommendations(top_n=5):
    """
    Uses the trained Random Forest model to predict the best items 
    based on the current live weather and time of day.
    """
    global _CACHED_MODEL

    if _CACHED_MODEL is None:
        if not os.path.exists(MODEL_PATH):
            # Fallback if model hasn't been trained yet
            return get_fallback_recommendations(top_n)

        try:
            _CACHED_MODEL = joblib.load(MODEL_PATH)
            print("[AI] Model loaded into memory successfully.")
        except Exception as e:
            print(f"Error loading model: {e}")
            return get_fallback_recommendations(top_n)
            
    model = _CACHED_MODEL

    # 1. Get current conditions
    weather_info = get_weather()
    current_hour = datetime.now().hour

    # 2. Prepare the input data for the model
    # Must match the features used in train_model.py:
    # ['temperature', 'humidity', 'hour', 'category']
    input_data = pd.DataFrame([{
        'temperature': weather_info.get('temperature', 25.0),
        'humidity':    weather_info.get('humidity', 50),
        'hour':        current_hour,
        'category':    weather_info.get('category', 'Normal')
    }])

    # 3. Ask the model for probabilities
    # predict_proba returns a list of probabilities for each class the model knows
    try:
        probabilities = model.predict_proba(input_data)[0]
    except Exception as e:
        print(f"Error predicting: {e}")
        return get_fallback_recommendations(top_n)
        
    classes = model.classes_

    # 4. Sort classes by highest probability
    # zip classes and probabilities, sort by prob descending
    class_probs = list(zip(classes, probabilities))
    class_probs.sort(key=lambda x: x[1], reverse=True)

    # Get the top N item names
    top_item_names = [item[0] for item in class_probs[:top_n]]

    # 5. Fetch these items from the database
    recommended_items = []
    
    for name in top_item_names:
        # Check drinks
        drink = Drink.objects.filter(name=name).first()
        if drink:
            recommended_items.append({
                "name": drink.name,
                "price": str(drink.price),
                "type": "drink"
            })
            continue
            
        # Check snacks
        snack = Snacks.objects.filter(name=name).first()
        if snack:
            recommended_items.append({
                "name": snack.name,
                "price": str(snack.price),
                "type": "snack"
            })
            
    # If the model didn't return enough (or items were deleted from DB), fill with fallback
    if len(recommended_items) < top_n:
        fallbacks = get_fallback_recommendations(top_n)
        # Add fallbacks that aren't already in the list
        existing_names = [item["name"] for item in recommended_items]
        for f in fallbacks:
            if f["name"] not in existing_names and len(recommended_items) < top_n:
                recommended_items.append(f)

    return recommended_items

def get_fallback_recommendations(top_n):
    """Fallback recommendations based on live weather (if ML fails or isn't trained)"""
    import random
    from shop.recommendations.weather import get_weather
    
    # Get live weather to make a smart fallback guess
    weather_info = get_weather()
    category = weather_info.get("category", "Normal")
    
    drinks = []
    snacks = list(Snacks.objects.all())
    
    # Filter drinks based on weather category
    if category == "Hot":
        # It's hot outside -> recommend cold drinks
        drinks = list(Drink.objects.filter(category="Cold"))
    elif category in ["Cold", "Rain"]:
        # It's cold or rainy -> recommend hot drinks
        drinks = list(Drink.objects.filter(category="Hot"))
    else:
        # Normal weather -> recommend anything
        drinks = list(Drink.objects.all())
        
    # If the filter returned nothing (e.g. no cold drinks in DB), fallback to all
    if not drinks:
        drinks = list(Drink.objects.all())

    combined = drinks + snacks
    random.shuffle(combined)
    
    items = []
    for item in combined[:top_n]:
        items.append({
            "name":  item.name,
            "price": str(item.price),
            "type":  "drink" if isinstance(item, Drink) else "snack",
        })
    return items
