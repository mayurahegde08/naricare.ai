
from flask import Flask, request, jsonify
from flask_cors import CORS
import re

app = Flask(__name__)
CORS(app)

app.config["MAX_CONTENT_LENGTH"] = 16 * 1024

# Supported languages and symptom phrases.
LEXICON = {
    "en": {
        "irregular_periods": [
            "irregular period", "irregular periods",
            "missed period", "missed periods",
            "late period", "late periods",
            "periods are irregular"
        ],
        "acne": ["acne", "pimples", "spots"],
        "oily_skin": ["oily skin"],
        "facial_body_hair": [
            "facial hair", "unwanted hair", "excess hair",
            "unusual facial hair", "body hair"
        ],
        "hair_thinning": [
            "hair thinning", "hair loss", "hair fall"
        ],
        "pelvic_pain": [
            "pelvic pain", "lower abdominal pain",
            "lower belly pain", "stomach pain"
        ],
        "severe": ["severe", "unbearable", "worsening"],
        "faintness": ["faint", "fainting", "dizzy", "lightheaded"],
        "heavy_bleeding": ["heavy bleeding", "bleeding heavily"],
        "breathing_difficulty": [
            "difficulty breathing", "trouble breathing",
            "shortness of breath", "cannot breathe"
        ],
        "confusion": ["sudden confusion", "suddenly confused"]
    },
    "kn": {
        "irregular_periods": [
            "ಅನಿಯಮಿತ ಮಾಸಿಕ", "ಮಾಸಿಕ ಅನಿಯಮಿತ",
            "ಪೀರಿಯಡ್ ಅನಿಯಮಿತ", "ತಿಂಗಳು ತಪ್ಪುತ್ತಿದೆ"
        ],
        "acne": ["ಮೊಡವೆ", "ಮುಖದ ಮೊಡವೆ"],
        "oily_skin": ["ಎಣ್ಣೆಯ ಚರ್ಮ"],
        "facial_body_hair": [
            "ಮುಖದ ಕೂದಲು", "ದೇಹದ ಕೂದಲು", "ಅನಗತ್ಯ ಕೂದಲು"
        ],
        "hair_thinning": ["ಕೂದಲು ಉದುರುವುದು", "ಕೂದಲು ತೆಳುವಾಗುವುದು"],
        "pelvic_pain": ["ಹೊಟ್ಟೆ ನೋವು", "ಕೆಳ ಹೊಟ್ಟೆ ನೋವು", "ಶ್ರೋಣಿಯ ನೋವು"],
        "severe": ["ತೀವ್ರ", "ಹೆಚ್ಚಾಗುತ್ತಿದೆ", "ಸಹಿಸಲಾಗದ"],
        "faintness": ["ಮೂರ್ಛೆ", "ತಲೆಸುತ್ತು", "ಪ್ರಜ್ಞೆ ತಪ್ಪು"],
        "heavy_bleeding": ["ಹೆಚ್ಚು ರಕ್ತಸ್ರಾವ", "ಭಾರೀ ರಕ್ತಸ್ರಾವ"],
        "breathing_difficulty": ["ಉಸಿರಾಟದ ತೊಂದರೆ", "ಉಸಿರಾಡಲು ಕಷ್ಟ"],
        "confusion": ["ಹಠಾತ್ ಗೊಂದಲ", "ಗೊಂದಲ"]
    },
    "hi": {
        "irregular_periods": [
            "अनियमित पीरियड", "अनियमित माहवारी",
            "पीरियड देर से", "मासिक धर्म अनियमित"
        ],
        "acne": ["मुंहासे", "मुँहासे", "पिंपल"],
        "oily_skin": ["तैलीय त्वचा"],
        "facial_body_hair": [
            "चेहरे पर बाल", "अनचाहे बाल", "शरीर पर बाल"
        ],
        "hair_thinning": ["बाल झड़ना", "बाल पतले"],
        "pelvic_pain": ["पेट में दर्द", "निचले पेट में दर्द", "तेज पेट दर्द"],
        "severe": ["तेज", "तेज़", "बहुत गंभीर", "बढ़ता हुआ दर्द"],
        "faintness": ["बेहोश", "चक्कर", "चक्कर आना"],
        "heavy_bleeding": ["भारी रक्तस्राव", "बहुत अधिक रक्तस्राव"],
        "breathing_difficulty": [
            "सांस लेने में दिक्कत", "साँस लेने में कठिनाई"
        ],
        "confusion": ["अचानक भ्रम", "अचानक उलझन"]
    },
    "ta": {
        "irregular_periods": [
            "ஒழுங்கற்ற மாதவிடாய்", "மாதவிடாய் தாமதம்"
        ],
        "acne": ["முகப்பரு", "பருக்கள்"],
        "oily_skin": ["எண்ணெய் பசை சருமம்"],
        "facial_body_hair": ["முகத்தில் முடி", "தேவையற்ற முடி"],
        "hair_thinning": ["முடி உதிர்வு", "முடி மெலிதல்"],
        "pelvic_pain": ["அடிவயிற்று வலி", "வயிற்று வலி", "இடுப்பு வலி"],
        "severe": ["கடுமையான", "மோசமாகிறது", "தாங்க முடியாத"],
        "faintness": ["மயக்கம்", "தலைசுற்றல்", "நினைவிழப்பு"],
        "heavy_bleeding": ["அதிக ரத்தப்போக்கு", "கடுமையான ரத்தப்போக்கு"],
        "breathing_difficulty": ["மூச்சுத்திணறல்", "மூச்சு விடுவதில் சிரமம்"],
        "confusion": ["திடீர் குழப்பம்"]
    },
    "te": {
        "irregular_periods": [
            "క్రమం తప్పిన పీరియడ్స్", "నెలసరి క్రమం తప్పడం",
            "పీరియడ్స్ ఆలస్యం"
        ],
        "acne": ["మొటిమలు", "ముఖంపై మొటిమలు"],
        "oily_skin": ["జిడ్డు చర్మం"],
        "facial_body_hair": [
            "ముఖంపై వెంట్రుకలు", "అవాంఛిత వెంట్రుకలు"
        ],
        "hair_thinning": ["జుట్టు రాలడం", "జుట్టు పలుచబడటం"],
        "pelvic_pain": ["కడుపు నొప్పి", "దిగువ కడుపు నొప్పి"],
        "severe": ["తీవ్రమైన", "మరింత ఎక్కువవుతోంది", "భరించలేని"],
        "faintness": ["మూర్ఛ", "తలతిరగడం", "స్పృహ తప్పడం"],
        "heavy_bleeding": ["అధిక రక్తస్రావం", "భారీ రక్తస్రావం"],
        "breathing_difficulty": [
            "శ్వాస తీసుకోవడంలో ఇబ్బంది", "ఊపిరి తీసుకోవడంలో కష్టం"
        ],
        "confusion": ["అకస్మాత్తుగా గందరగోళం"]
    }
}

LABELS = {
    "en": {
        "irregular_periods": "Irregular or missed periods",
        "acne": "Acne or pimples",
        "oily_skin": "Oily skin",
        "facial_body_hair": "Unusual facial or body hair",
        "hair_thinning": "Scalp hair thinning or loss",
        "pelvic_pain": "Pelvic or lower abdominal pain"
    },
    "kn": {
        "irregular_periods": "ಅನಿಯಮಿತ ಅಥವಾ ತಪ್ಪಿದ ಮಾಸಿಕ",
        "acne": "ಮೊಡವೆ",
        "oily_skin": "ಎಣ್ಣೆಯ ಚರ್ಮ",
        "facial_body_hair": "ಮುಖ ಅಥವಾ ದೇಹದ ಅಸಾಮಾನ್ಯ ಕೂದಲು",
        "hair_thinning": "ತಲೆಯ ಕೂದಲು ತೆಳುವಾಗುವುದು ಅಥವಾ ಉದುರುವುದು",
        "pelvic_pain": "ಶ್ರೋಣಿ ಅಥವಾ ಕೆಳ ಹೊಟ್ಟೆ ನೋವು"
    },
    "hi": {
        "irregular_periods": "अनियमित या छूटी हुई माहवारी",
        "acne": "मुंहासे",
        "oily_skin": "तैलीय त्वचा",
        "facial_body_hair": "चेहरे या शरीर पर असामान्य बाल",
        "hair_thinning": "सिर के बाल पतले होना या झड़ना",
        "pelvic_pain": "श्रोणि या निचले पेट में दर्द"
    },
    "ta": {
        "irregular_periods": "ஒழுங்கற்ற அல்லது தவறிய மாதவிடாய்",
        "acne": "முகப்பரு",
        "oily_skin": "எண்ணெய் பசை சருமம்",
        "facial_body_hair": "முகம் அல்லது உடலில் வழக்கத்திற்கு மாறான முடி",
        "hair_thinning": "தலையில் முடி மெலிதல் அல்லது உதிர்தல்",
        "pelvic_pain": "இடுப்பு அல்லது அடிவயிற்று வலி"
    },
    "te": {
        "irregular_periods": "క్రమం తప్పిన లేదా రాని పీరియడ్స్",
        "acne": "మొటిమలు",
        "oily_skin": "జిడ్డు చర్మం",
        "facial_body_hair": "ముఖం లేదా శరీరంపై అసాధారణ వెంట్రుకలు",
        "hair_thinning": "తలపై జుట్టు పలుచబడటం లేదా రాలడం",
        "pelvic_pain": "పొత్తికడుపు లేదా దిగువ కడుపు నొప్పి"
    }
}

NEGATIONS = {
    "en": ["no", "not", "never", "without", "don't", "do not"],
    "kn": ["ಇಲ್ಲ", "ಇಲ್ಲದೆ", "ಆಗಿಲ್ಲ", "ಅಲ್ಲ"],
    "hi": ["नहीं", "बिना", "नहीं है"],
    "ta": ["இல்லை", "இல்லாமல்", "இல்லாத"],
    "te": ["లేదు", "లేకుండా", "కాదు"]
}

ALTERNATIVE_CAUSES = {
    "en": (
        "Irregular periods may have several causes, including pregnancy, "
        "stress, weight or exercise changes, hormonal contraception, "
        "and thyroid conditions. These are possibilities, not conclusions."
    ),
    "kn": (
        "ಅನಿಯಮಿತ ಮಾಸಿಕಕ್ಕೆ ಗರ್ಭಧಾರಣೆ, ಒತ್ತಡ, ತೂಕದ ಬದಲಾವಣೆ "
        "ಅಥವಾ ಥೈರಾಯ್ಡ್ ಸಮಸ್ಯೆಗಳು ಸೇರಿದಂತೆ ಹಲವು ಕಾರಣಗಳಿರಬಹುದು."
    ),
    "hi": (
        "अनियमित माहवारी के कई कारण हो सकते हैं, जैसे गर्भावस्था, "
        "तनाव, वजन में बदलाव या थायरॉइड की समस्या।"
    ),
    "ta": (
        "ஒழுங்கற்ற மாதவிடாய்க்கு கர்ப்பம், மனஅழுத்தம், "
        "எடை மாற்றங்கள் அல்லது தைராய்டு பிரச்சினைகள் காரணமாக இருக்கலாம்."
    ),
    "te": (
        "క్రమం తప్పిన పీరియడ్స్‌కు గర్భధారణ, ఒత్తిడి, "
        "బరువు మార్పులు లేదా థైరాయిడ్ సమస్యలు కారణాలు కావచ్చు."
    )
}

URGENT_GUIDANCE = {
    "en": (
        "Your answers include a possible warning sign. Contact your local "
        "emergency service or go to the nearest emergency department now. "
        "Do not drive yourself if faint or severely unwell."
    ),
    "kn": (
        "ನಿಮ್ಮ ಉತ್ತರಗಳಲ್ಲಿ ಅಪಾಯದ ಸೂಚನೆ ಇರಬಹುದು. ತಕ್ಷಣ ಸ್ಥಳೀಯ "
        "ತುರ್ತು ವೈದ್ಯಕೀಯ ಸೇವೆಯನ್ನು ಸಂಪರ್ಕಿಸಿ ಅಥವಾ ಹತ್ತಿರದ ತುರ್ತು "
        "ಚಿಕಿತ್ಸಾ ವಿಭಾಗಕ್ಕೆ ಹೋಗಿ."
    ),
    "hi": (
        "आपके उत्तरों में एक संभावित चेतावनी संकेत है। स्थानीय "
        "आपातकालीन सेवा से संपर्क करें या निकटतम आपातकालीन विभाग जाएँ।"
    ),
    "ta": (
        "உங்கள் பதில்களில் எச்சரிக்கை அறிகுறி இருக்கலாம். உள்ளூர் "
        "அவசர மருத்துவ சேவையைத் தொடர்புகொள்ளவும் அல்லது அருகிலுள்ள "
        "அவசர சிகிச்சைப் பிரிவுக்குச் செல்லவும்."
    ),
    "te": (
        "మీ సమాధానాల్లో హెచ్చరిక సంకేతం ఉండవచ్చు. స్థానిక అత్యవసర "
        "వైద్య సేవను సంప్రదించండి లేదా సమీప అత్యవసర విభాగానికి వెళ్లండి."
    )
}


def phrase_present(text, phrase, lang):
    """Match a known phrase while checking for simple nearby negations."""
    text = text.casefold()
    phrase = phrase.casefold()

    start = 0
    while True:
        pos = text.find(phrase, start)

        if pos == -1:
            return False

        prefix = text[max(0, pos - 70):pos]
        clause = re.split(r"[.!?;،。！？]+", prefix)[-1]

        negated = False

        for marker in NEGATIONS[lang]:
            matches = list(re.finditer(
                r"(?<!\w)" + re.escape(marker) + r"(?!\w)",
                clause
            ))

            if matches:
                match = matches[-1]
                between = clause[match.end():]
                words = re.findall(r"[^\W_]+", between)

                if len(words) <= 3:
                    negated = True
                    break

        if not negated:
            return True

        start = pos + len(phrase)


def analyze_text(text, lang):
    vocab = LEXICON[lang]

    found = {
        category
        for category, phrases in vocab.items()
        if category in LABELS[lang]
        and any(phrase_present(text, p, lang) for p in phrases)
    }

    pain = any(
        phrase_present(text, p, lang)
        for p in vocab["pelvic_pain"]
    )

    severe = any(
        phrase_present(text, p, lang)
        for p in vocab["severe"]
    )

    faintness = any(
        phrase_present(text, p, lang)
        for p in vocab["faintness"]
    )

    other_red_flags = any(
        phrase_present(text, p, lang)
        for category in (
            "heavy_bleeding",
            "breathing_difficulty",
            "confusion"
        )
        for p in vocab[category]
    )

    urgent = (pain and (severe or faintness)) or other_red_flags

    return found, urgent


@app.get("/")
def home():
    return jsonify({
        "project": "NariCare AI",
        "status": "running"
    })


@app.get("/api/health")
def health():
    return jsonify({
        "status": "healthy",
        "supported_languages": list(LEXICON.keys())
    })


@app.post("/api/analyze")
def analyze():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Send a valid JSON object."}), 400

    symptoms = data.get("symptoms", "")
    language = data.get("language", "en")

    if not isinstance(symptoms, str) or not symptoms.strip():
        return jsonify({"error": "Please describe your symptoms."}), 400

    if not isinstance(language, str) or language not in LEXICON:
        return jsonify({
            "error": "Language must be en, kn, hi, ta, or te."
        }), 400

    if len(symptoms) > 4000:
        return jsonify({"error": "Description is too long."}), 400

    symptoms = symptoms.strip()

    answers = data.get("answers", {})
    if not isinstance(answers, dict):
        return jsonify({"error": "Answers must be a JSON object."}), 400

    menstrual = answers.get("menstrual", "choose")
    urgent_answer = answers.get("urgent_answer", "choose")

    if menstrual not in [
        "choose", "regular", "irregular", "absent", "varies", "unsure"
    ]:
        return jsonify({"error": "Invalid menstrual answer."}), 400

    if urgent_answer not in ["choose", "yes", "no", "unsure"]:
        return jsonify({"error": "Invalid urgent answer."}), 400

    found, urgent_from_description = analyze_text(symptoms, language)

    if menstrual in ["irregular", "absent"]:
        found.add("irregular_periods")

    answer_categories = {
        "acne_answer": "acne",
        "oily_skin_answer": "oily_skin",
        "facial_hair_answer": "facial_body_hair",
        "hair_thinning_answer": "hair_thinning"
    }

    for answer_key, category in answer_categories.items():
        value = answers.get(answer_key, "choose")

        if value not in ["choose", "yes", "no", "unsure"]:
            return jsonify({
                "error": f"Invalid value for {answer_key}."
            }), 400

        if value == "yes":
            found.add(category)

    categories = [
        "irregular_periods", "acne", "oily_skin",
        "facial_body_hair", "hair_thinning", "pelvic_pain"
    ]

    summary = [
        LABELS[language][category]
        for category in categories
        if category in found
    ]

    urgent = urgent_answer == "yes" or urgent_from_description
    urgent_unsure = urgent_answer == "unsure"

    associated = "irregular_periods" in found
    other_feature = any(
        item in found
        for item in (
            "acne", "oily_skin",
            "facial_body_hair", "hair_thinning"
        )
    )

    if urgent:
        care_level = "emergency"
        guidance = URGENT_GUIDANCE[language]
    elif urgent_unsure:
        care_level = "uncertain"
        guidance = (
            "You are unsure whether a warning sign is present. "
            "If severe or worsening pain, faintness, heavy bleeding, "
            "breathing difficulty, or sudden confusion may be happening, "
            "seek urgent medical care now."
        )
    else:
        care_level = "routine"
        guidance = (
            "If symptoms persist, affect daily life, or concern you, "
            "arrange an appointment with a qualified healthcare professional."
        )

    if not urgent and not urgent_unsure and associated and other_feature:
        association = (
            "Some reported features can occur with PCOS/PMOS, but they "
            "can also have other causes. This tool cannot diagnose or "
            "rule out a condition."
        )
    else:
        association = (
            "This limited symptom summary cannot establish a specific "
            "condition. Symptoms can have multiple causes."
        )

    response = {
        "project": "NariCare AI",
        "language": language,
        "summary": summary,
        "matched_categories": sorted(found),
        "recognized_phrases_only": True,
        "care_level": care_level,
        "urgent_warning": urgent,
        "urgent_uncertain": urgent_unsure,
        "pcos_information": association,
        "alternative_causes": (
            ALTERNATIVE_CAUSES[language] if associated else None
        ),
        "next_steps": [guidance],
        "disclaimer": (
            "Educational information only. This tool does not diagnose, "
            "rule out a condition, or replace professional medical care."
        )
    }

    return jsonify(response), 200


@app.errorhandler(413)
def request_too_large(error):
    return jsonify({"error": "Request is too large."}), 413


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False
    )
