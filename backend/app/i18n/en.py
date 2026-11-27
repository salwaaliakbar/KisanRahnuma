"""English bot wording. *text* is WhatsApp-style bold."""

STRINGS: dict[str, str] = {
    # Onboarding / consent
    "welcome": "Welcome to *Farmer Assistant*! I can help with weather, crop rates, credit and certifications.",
    "consent_q": (
        "Before we start, two permissions:\n"
        "*1.* Record your usage *anonymously* for project reporting. Your phone number is never stored.\n"
        "*2.* Send you *weekly farming updates* (crop rates and weather).\n"
        "You can use the assistant either way."
    ),
    "consent_both": "Yes to both",
    "consent_usage_only": "Only 1 (no updates)",
    "consent_none": "No to both",
    "consent_reask": "Please tap one of the buttons below.",
    "consent_done": "Thank you! Your choices are saved.",
    # Main menu
    "main_menu": "*Main menu*\nWhat would you like to know? Choose an option, or type any farming question.",
    "menu_weather": "Weather",
    "menu_crop_rates": "Crop Rates",
    "menu_credit": "Credit Information",
    "menu_certifications": "Certifications",
    "menu_ask": "Ask Anything",
    "menu_district": "My district",
    "district_pick": "*My district*\nSelect your district. I will remember it for weather and crop rates.",
    "district_saved": "📍 Your district is now *{district}*.",
    "yes": "Yes",
    "no": "No",
    "home": "Home",
    "feedback_yes": "Yes, helpful",
    "feedback_no": "Not helpful",
    "list_button": "Choose",  # WhatsApp list-message button
    "feedback_thanks": "Thank you for your feedback!",
    # Weather
    "weather_pick_district": "*Weather*\nSelect your district:",
    "weather_header": "*3-day weather forecast: {district}*",
    "weather_day": "*{day}* ({date}): {condition}, {temp_min}–{temp_max}°C, rain {rain} mm, wind {wind} km/h",
    "weather_advice": "*Farm advice:* {advice}",
    "weather_followup": "📍 For another district, tap *Home* and choose *My district*.",
    "advice_rain": "Rain is expected. Delay irrigation and pesticide sprays, and keep harvested produce covered.",
    "advice_heat": "Very hot days ahead. Irrigate in the evening or early morning and avoid spraying in the afternoon.",
    "advice_frost": "Cold nights expected. Give a light irrigation to protect young crops from frost.",
    "advice_wind": "Strong wind expected. Avoid spraying and irrigate after the wind calms down.",
    "advice_humid": "Fog or high humidity. Check wheat and vegetables for fungal disease such as rust.",
    "advice_default": "Good conditions for field work. Irrigate in the early morning to reduce water loss.",
    "today": "Today",
    "tomorrow": "Tomorrow",
    # Crop rates
    "crop_pick_crop": "*Crop rates*\nSelect a crop:",
    "crop_pick_crop_in": "*Crop rates: {district}*\nSelect a crop:",
    "crop_pick_district": "*{crop}*\nSelect a district:",
    "crop_rate": (
        "*{crop} rate: {district}*\n"
        "Rate: *PKR {rate}* per {unit}\n"
        "Source: {source}\n"
        "Date: {date}"
    ),
    "crop_trend": (
        "*Seasonal trend*\n"
        "Summer (Kharif) average: PKR {summer}\n"
        "Winter (Rabi) average: PKR {winter}\n"
        "{note}"
    ),
    "crop_expected": "*Expected price, {season}*\nPKR {low} – {high} per {unit}\n_{basis}_",
    "crop_followup": "📍 For another crop or district, tap *Home*.",
    "crop_unavailable": "Sorry, no rate is available for {crop} in {district} yet.",
    # Credit & certifications
    "credit_menu": "*Credit information*\nWhich programme would you like to know about?",
    "cert_menu": "*Certifications*\n{intro}\n\nChoose your crop below to see which certificate is realistic for it.",
    "credit_disclaimer": "_From the project credit booklet (November 2026). Terms change and some details are still being checked. Confirm with the bank or office before you apply. We do not recommend any one bank or lender._",
    "cert_disclaimer": "_From the project certification notes (October 2026). Some details are still being checked. Confirm with Agriculture Extension or your buyer before you spend money._",
    "info_followup": "Tap *Home* to see other options.",
    # Ask anything
    "ask_prompt": "*Ask Anything*\nType your farming question. I answer only from the project's knowledge base.",
    "ask_source": "_Source: {source}_",
    "ask_fallback": (
        "Sorry, this information is not currently available in my knowledge base.\n"
        "Try rephrasing, or use the main menu for weather, crop rates, credit and certifications."
    ),
    # Voice and errors
    "voice_unsupported": (
        "Voice notes are not supported yet. Please type your question, or tap Home for the menu."
    ),
    "not_understood": "Sorry, I did not understand that. Please choose an option or tap Home.",
    # Language
    "menu_language": "Language",
    "language_prompt_line": "Please choose your language:",
    "language_changed": "Language changed to English.",
    # Weather conditions (provider condition codes)
    "cond_sunny": "Sunny",
    "cond_partly_cloudy": "Partly cloudy",
    "cond_hazy": "Hazy",
    "cond_cloudy": "Cloudy",
    "cond_light_rain": "Light rain",
    "cond_fog_then_sunny": "Foggy morning, sunny later",
    "cond_fog": "Fog",
    "cond_drizzle": "Drizzle",
    "cond_rain": "Rain",
    "cond_heavy_rain": "Heavy rain",
    "cond_thunderstorm": "Thunderstorm",
    "cond_snow": "Snow",
    "weather_unavailable": "Sorry, the weather forecast is not available right now. Please try again later.",
    # Weekdays (Monday = 0) and months
    "weekday_0": "Monday",
    "weekday_1": "Tuesday",
    "weekday_2": "Wednesday",
    "weekday_3": "Thursday",
    "weekday_4": "Friday",
    "weekday_5": "Saturday",
    "weekday_6": "Sunday",
    "month_1": "Jan",
    "month_2": "Feb",
    "month_3": "Mar",
    "month_4": "Apr",
    "month_5": "May",
    "month_6": "Jun",
    "month_7": "Jul",
    "month_8": "Aug",
    "month_9": "Sep",
    "month_10": "Oct",
    "month_11": "Nov",
    "month_12": "Dec",
}
