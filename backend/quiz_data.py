"""
Quiz questions for EcoMitra
Each quiz has 5 questions with 4 options each
"""

QUIZ_QUESTIONS = {
    "en": [
        {
            "question": "What percentage of plastic waste in India is recycled?",
            "options": ["60%", "30%", "15%", "5%"],
            "correct": 0,
            "explanation": "India recycles approximately 60% of its plastic waste, though informal sector plays a major role."
        },
        {
            "question": "Which color dustbin is used for wet/biodegradable waste?",
            "options": ["Blue", "Green", "Red", "Yellow"],
            "correct": 1,
            "explanation": "Green dustbins are designated for wet/biodegradable waste like food scraps and garden waste."
        },
        {
            "question": "LED bulbs use how much less energy than incandescent bulbs?",
            "options": ["25%", "50%", "75%", "90%"],
            "correct": 2,
            "explanation": "LED bulbs use approximately 75% less energy than traditional incandescent bulbs."
        },
        {
            "question": "What is the primary cause of air pollution in Indian cities?",
            "options": ["Industrial emissions", "Vehicle emissions", "Crop burning", "Construction dust"],
            "correct": 1,
            "explanation": "Vehicle emissions are the primary contributor to urban air pollution in most Indian cities."
        },
        {
            "question": "Which gas is the main component of biogas produced from waste?",
            "options": ["Carbon dioxide", "Methane", "Oxygen", "Nitrogen"],
            "correct": 1,
            "explanation": "Methane (CH4) is the primary component of biogas, typically making up 50-70% of the gas mixture."
        }
    ],
    "hi": [
        {
            "question": "भारत में कितने प्रतिशत प्लास्टिक कचरा रीसायकल होता है?",
            "options": ["60%", "30%", "15%", "5%"],
            "correct": 0,
            "explanation": "भारत अपने लगभग 60% प्लास्टिक कचरे को रीसायकल करता है।"
        },
        {
            "question": "गीले/बायोडिग्रेडेबल कचरे के लिए किस रंग का डस्टबिन इस्तेमाल होता है?",
            "options": ["नीला", "हरा", "लाल", "पीला"],
            "correct": 1,
            "explanation": "हरे डस्टबिन का उपयोग गीले/बायोडिग्रेडेबल कचरे जैसे खाद्य अपशिष्ट के लिए किया जाता है।"
        },
        {
            "question": "LED बल्ब साधारण बल्ब से कितनी कम ऊर्जा का उपयोग करते हैं?",
            "options": ["25%", "50%", "75%", "90%"],
            "correct": 2,
            "explanation": "LED बल्ब पारंपरिक बल्बों की तुलना में लगभग 75% कम ऊर्जा का उपयोग करते हैं।"
        },
        {
            "question": "भारतीय शहरों में वायु प्रदूषण का मुख्य कारण क्या है?",
            "options": ["औद्योगिक उत्सर्जन", "वाहन उत्सर्जन", "फसल जलाना", "निर्माण धूल"],
            "correct": 1,
            "explanation": "वाहन उत्सर्जन भारतीय शहरों में वायु प्रदूषण का प्रमुख कारण है।"
        },
        {
            "question": "कचरे से उत्पन्न बायोगैस में मुख्य घटक कौन सी गैस है?",
            "options": ["कार्बन डाइऑक्साइड", "मीथेन", "ऑक्सीजन", "नाइट्रोजन"],
            "correct": 1,
            "explanation": "मीथेन बायोगैस का मुख्य घटक है, जो आमतौर पर 50-70% होता है।"
        }
    ],
    "mr": [
        {
            "question": "भारतात किती टक्के प्लास्टिक कचरा पुनर्वापर केला जातो?",
            "options": ["60%", "30%", "15%", "5%"],
            "correct": 0,
            "explanation": "भारत अंदाजे 60% प्लास्टिक कचरा पुनर्वापर करतो."
        },
        {
            "question": "ओले/बायोडिग्रेडेबल कचऱ्यासाठी कोणत्या रंगाची डस्टबिन वापरली जाते?",
            "options": ["निळा", "हिरवा", "लाल", "पिवळा"],
            "correct": 1,
            "explanation": "हिरव्या रंगाची डस्टबिन ओले/बायोडिग्रेडेबल कचऱ्यासाठी नियुक्त केली आहे."
        },
        {
            "question": "LED बल्ब सामान्य बल्बपेक्षा किती कमी ऊर्जा वापरतात?",
            "options": ["25%", "50%", "75%", "90%"],
            "correct": 2,
            "explanation": "LED बल्ब पारंपरिक बल्बच्या तुलनेत सुमारे 75% कमी ऊर्जा वापरतात."
        },
        {
            "question": "भारतीय शहरांमध्ये वायू प्रदूषणाचे मुख्य कारण काय आहे?",
            "options": ["औद्योगिक उत्सर्जन", "वाहन उत्सर्जन", "पीक जाळणे", "बांधकाम धूळ"],
            "correct": 1,
            "explanation": "वाहन उत्सर्जन हे भारतीय शहरांमध्ये वायू प्रदूषणाचे प्रमुख कारण आहे."
        },
        {
            "question": "कचऱ्यापासून तयार होणाऱ्या बायोगॅसमधील मुख्य घटक कोणता आहे?",
            "options": ["कार्बन डायऑक्साइड", "मिथेन", "ऑक्सिजन", "नायट्रोजन"],
            "correct": 1,
            "explanation": "मिथेन हा बायोगॅसचा मुख्य घटक आहे, जो साधारणपणे 50-70% असतो."
        }
    ]
}


def get_quiz_questions(language: str = "en"):
    """Get quiz questions in specified language"""
    return QUIZ_QUESTIONS.get(language, QUIZ_QUESTIONS["en"])
