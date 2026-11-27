"""Sindhi bot wording. *text* is WhatsApp-style bold.\n\nMachine-drafted translation: have a native speaker (ideally an agriculture extension\nworker) review it before any pilot.\n"""

STRINGS: dict[str, str] = {
    # Onboarding / consent
    "welcome": "*فارمر اسسٽنٽ* ۾ ڀليڪار! مان موسم، فصلن جي اگهن، قرض ۽ سرٽيفڪيشن بابت مدد ڪري سگهان ٿو.",
    "consent_q": (
        "شروع ڪرڻ کان اڳ ٻه اجازتون:\n"
        "*1.* پروجيڪٽ جي رپورٽنگ لاءِ توهان جو استعمال *گمنام طور* رڪارڊ ڪيو وڃي. توهان جو فون نمبر ڪڏهن به محفوظ نه ڪيو ويندو.\n"
        "*2.* توهان کي *هفتيوار زرعي معلومات* (فصلن جا اگهه ۽ موسم) موڪليون وڃن.\n"
        "توهان ٻنهي صورتن ۾ اسسٽنٽ استعمال ڪري سگهو ٿا."
    ),
    "consent_both": "ٻنهي جي اجازت",
    "consent_usage_only": "صرف 1، معلومات نه",
    "consent_none": "ٻئي نه",
    "consent_reask": "مهرباني ڪري هيٺ ڏنل بٽڻن مان هڪ دٻايو.",
    "consent_done": "مهرباني! توهان جون چونڊون محفوظ ٿي ويون آهن.",
    # Main menu
    "main_menu": "*مک مينيو*\nتوهان ڇا ڄاڻڻ چاهيو ٿا؟ ڪو آپشن چونڊيو، يا پوک بابت ڪو به سوال لکو.",
    "menu_weather": "موسم",
    "menu_crop_rates": "فصلن جا اگهه",
    "menu_credit": "قرض جي معلومات",
    "menu_certifications": "سرٽيفڪيشن",
    "menu_ask": "ڪجهه به پڇو",
    "menu_district": "منهنجو ضلعو",
    "district_pick": "*منهنجو ضلعو*\nپنهنجو ضلعو چونڊيو. موسم ۽ فصلن جي اگهن لاءِ اهو ياد رکيو ويندو.",
    "district_saved": "📍 توهان جو ضلعو هاڻي *{district}* آهي.",
    "yes": "ها",
    "no": "نه",
    "home": "مک مينيو",
    "feedback_yes": "ها، فائديمند",
    "feedback_no": "فائديمند ناهي",
    "list_button": "چونڊيو",  # WhatsApp list-message button
    "feedback_thanks": "توهان جي راءِ جي مهرباني!",
    # Weather
    "weather_pick_district": "*موسم*\nپنهنجو ضلعو چونڊيو:",
    "weather_header": "*3 ڏينهن جي موسمي اڳڪٿي: {district}*",
    "weather_day": "*{day}* ({date}): {condition}، {temp_min}–{temp_max}°C، مينهن {rain} ملي ميٽر، هوا {wind} ڪلوميٽر في ڪلاڪ",
    "weather_advice": "*زرعي صلاح:* {advice}",
    "weather_followup": "📍 ٻئي ضلعي لاءِ *مک مينيو* دٻايو ۽ *منهنجو ضلعو* چونڊيو.",
    "advice_rain": "مينهن جو امڪان آهي. پاڻي ڏيڻ ۽ جيت مار اسپري ملتوي ڪريو، ۽ لڻيل فصل کي ڍڪي رکو.",
    "advice_heat": "ايندڙ ڏينهن تمام گرم آهن. شام يا صبح سوير پاڻي ڏيو ۽ منجهند جو اسپري نه ڪريو.",
    "advice_frost": "راتيون ٿڌيون ٿيڻ جو امڪان آهي. ننڍن فصلن کي پاري کان بچائڻ لاءِ هلڪو پاڻي ڏيو.",
    "advice_wind": "تيز هوا جو امڪان آهي. اسپري نه ڪريو ۽ هوا بيهڻ کان پوءِ پاڻي ڏيو.",
    "advice_humid": "ڌنڌ يا وڌيڪ نمي. ڪڻڪ ۽ ڀاڄين ۾ ڪنگي (رسٽ) جهڙي فنگس جي بيماري چيڪ ڪريو.",
    "advice_default": "پوک جي ڪم لاءِ موسم سٺو آهي. پاڻي جو زيان گهٽائڻ لاءِ صبح سوير پاڻي ڏيو.",
    "today": "اڄ",
    "tomorrow": "سڀاڻي",
    # Crop rates
    "crop_pick_crop": "*فصلن جا اگهه*\nفصل چونڊيو:",
    "crop_pick_crop_in": "*فصلن جا اگهه: {district}*\nفصل چونڊيو:",
    "crop_pick_district": "*{crop}*\nضلعو چونڊيو:",
    "crop_rate": (
        "*{crop} جو اگهه: {district}*\n"
        "اگهه: *{rate} رپيا* في {unit}\n"
        "ذريعو: {source}\n"
        "تاريخ: {date}"
    ),
    "crop_trend": (
        "*موسمي رجحان*\n"
        "اونهاري (خريف) جو سراسري اگهه: {summer} رپيا\n"
        "سياري (ربيع) جو سراسري اگهه: {winter} رپيا\n"
        "{note}"
    ),
    "crop_expected": "*متوقع قيمت، {season}*\n{low} – {high} رپيا في {unit}\n_{basis}_",
    "crop_followup": "📍 ٻئي فصل يا ضلعي لاءِ *مک مينيو* دٻايو.",
    "crop_unavailable": "معاف ڪجو، {district} ۾ {crop} جو اگهه اڃا موجود ناهي.",
    # Credit & certifications
    "credit_menu": "*قرض جي معلومات*\nتوهان ڪهڙي پروگرام بابت ڄاڻڻ چاهيو ٿا؟",
    "cert_menu": "*سرٽيفڪيشن*\n{intro}\n\nهيٺ پنهنجو فصل چونڊيو ۽ ڏسو ته ان لاءِ ڪهڙو سرٽيفڪيٽ ممڪن آهي.",
    "credit_disclaimer": "_هي معلومات منصوبي جي قرض ڪتابچي (نومبر 2026) مان آهي. شرطون بدلجنديون رهن ٿيون ۽ ڪجهه تفصيلن جي تصديق جاري آهي. درخواست کان اڳ بئنڪ يا آفيس کان تصديق ڪريو. اسان ڪنهن هڪ بئنڪ يا اداري جي سفارش نٿا ڪريون._",
    "cert_disclaimer": "_پروجيڪٽ جي سرٽيفڪيشن نوٽس مان (آڪٽوبر 2026). ڪجهه تفصيلن جي اڃا تصديق ٿي رهي آهي. پئسا خرچ ڪرڻ کان اڳ زراعت کاتي (توسيع) يا پنهنجي خريدار سان تصديق ڪريو._",
    "info_followup": "ٻيا آپشن ڏسڻ لاءِ *مک مينيو* دٻايو.",
    # Ask anything
    "ask_prompt": "*ڪجهه به پڇو*\nپوک بابت پنهنجو سوال لکو. مان صرف پروجيڪٽ جي معلوماتي ذخيري مان جواب ڏيان ٿو.",
    "ask_source": "_ذريعو: {source}_",
    "ask_fallback": (
        "معاف ڪجو، هي معلومات هن وقت منهنجي معلوماتي ذخيري ۾ موجود ناهي.\n"
        "سوال ٻين لفظن ۾ لکو، يا موسم، فصلن جي اگهن، قرض ۽ سرٽيفڪيشن لاءِ مک مينيو استعمال ڪريو."
    ),
    # Voice and errors
    "voice_unsupported": "وائس نوٽ اڃا موجود ناهن. مهرباني ڪري پنهنجو سوال لکو، يا مک مينيو تي ٽيپ ڪريو.",
    "not_understood": "معاف ڪجو، مان سمجهي نه سگهيس. مهرباني ڪري ڪو آپشن چونڊيو يا مک مينيو تي ٽيپ ڪريو.",
    # Language
    "menu_language": "ٻولي (Language)",
    "language_prompt_line": "مهرباني ڪري پنهنجي ٻولي چونڊيو:",
    "language_changed": "ٻولي سنڌي ڪئي وئي آهي.",
    # Weather conditions
    "cond_sunny": "اُس",
    "cond_partly_cloudy": "ٿورا ڪڪر",
    "cond_hazy": "ڌنڌلو موسم",
    "cond_cloudy": "ڪڪر",
    "cond_light_rain": "هلڪو مينهن",
    "cond_fog_then_sunny": "صبح جو ڌنڌ، پوءِ اُس",
    "cond_fog": "ڌنڌ",
    "cond_drizzle": "هلڪي ڦڙ ڦڙ",
    "cond_rain": "مينهن",
    "cond_heavy_rain": "تيز مينهن",
    "cond_thunderstorm": "گجگوڙ سان مينهن",
    "cond_snow": "برفباري",
    "weather_unavailable": "معاف ڪجو، موسم جي اڳڪٿي هن وقت موجود ناهي. مهرباني ڪري ڪجهه دير کانپوءِ ٻيهر ڪوشش ڪريو.",
    # Weekdays (Monday = 0) and months
    "weekday_0": "سومر",
    "weekday_1": "اڱارو",
    "weekday_2": "اربع",
    "weekday_3": "خميس",
    "weekday_4": "جمعو",
    "weekday_5": "ڇنڇر",
    "weekday_6": "آچر",
    "month_1": "جنوري",
    "month_2": "فيبروري",
    "month_3": "مارچ",
    "month_4": "اپريل",
    "month_5": "مئي",
    "month_6": "جون",
    "month_7": "جولاءِ",
    "month_8": "آگسٽ",
    "month_9": "سيپٽمبر",
    "month_10": "آڪٽوبر",
    "month_11": "نومبر",
    "month_12": "ڊسمبر",
}
