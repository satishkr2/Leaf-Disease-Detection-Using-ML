"""Farming help chatbot with rule-based responses."""
import random

FARMING_KB = {
    "water": "Water plants early morning at the base. Avoid wetting leaves to reduce fungal diseases. Most vegetables need 1-2 inches per week.",
    "fertilizer": "Use balanced NPK (10-10-10) during vegetative growth. Switch to lower nitrogen during fruiting. Organic compost improves soil structure.",
    "pest": "Integrated Pest Management: inspect weekly, use neem oil for soft-bodied pests, introduce beneficial insects, rotate crops annually.",
    "soil": "Test soil pH annually. Tomatoes prefer 6.0-6.8. Add lime to raise pH, sulfur to lower. Ensure good drainage with organic matter.",
    "tomato": "Tomatoes need full sun, support with stakes, prune suckers, and watch for early/late blight in humid weather.",
    "potato": "Plant certified seed potatoes, hill soil as plants grow, and harvest when vines die back. Store in cool dark place.",
    "pepper": "Peppers need warm soil above 65°F. Avoid overhead watering. Bacterial spot spreads in wet conditions - use copper sprays preventively.",
    "organic": "Organic options: neem oil, copper fungicides, compost tea, companion planting with marigolds and basil.",
    "default": "I'm your PlantCare farming assistant! Ask about watering, fertilizer, pests, soil, tomatoes, potatoes, peppers, or organic farming.",
}


def get_chat_response(message: str, language: str = "en") -> str:
    msg = message.lower()
    for keyword, response in FARMING_KB.items():
        if keyword != "default" and keyword in msg:
            if language == "es":
                return response + " (Traducción completa próximamente)"
            if language == "hi":
                return response + " (पूर्ण अनुवाद जल्द उपलब्ध)"
            return response
    return FARMING_KB["default"] + " " + random.choice(
        [
            "How can I help your crops today?",
            "Upload a leaf image for disease detection!",
            "Prevention is better than cure - monitor leaves weekly.",
        ]
    )
