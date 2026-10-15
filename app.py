from __future__ import annotations
import requests
import re
from typing import Any
import streamlit as st
import streamlit.components.v1 as components


st.set_page_config(
    page_title="NariCare AI | Women's health, one step at a time",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed",
)


LANGUAGES = {
    "English": {"key": "en", "locale": "en-IN", "short": "English"},
    "ಕನ್ನಡ (Kannada)": {"key": "kn", "locale": "kn-IN", "short": "ಕನ್ನಡ"},
    "हिन्दी (Hindi)": {"key": "hi", "locale": "hi-IN", "short": "हिन्दी"},
    "தமிழ் (Tamil)": {"key": "ta", "locale": "ta-IN", "short": "தமிழ்"},
    "తెలుగు (Telugu)": {"key": "te", "locale": "te-IN", "short": "తెలుగు"},
}
LANG_BY_KEY = {value["key"]: value for value in LANGUAGES.values()}

# Deliberately small, transparent phrase matching. This is not translation or
# general language understanding. Every match is shown to the user for review.
LEXICON = {
    "en": {
        "irregular_periods": ["irregular period", "irregular periods", "missed period", "missed periods", "late period", "late periods", "periods are irregular", "period is irregular", "periods are not regular"],
        "acne": ["acne", "pimples", "spots"],
        "oily_skin": ["oily skin"],
        "facial_body_hair": ["facial hair", "face hair", "body hair", "unwanted hair", "excess hair", "hair on my face"],
        "hair_thinning": ["hair thinning", "hair loss", "hair is falling", "hair fall", "thinning hair"],
        "pelvic_pain": ["pelvic pain", "lower abdominal pain", "lower belly pain", "stomach pain", "severe abdominal pain", "severe pelvic pain", "severe belly pain"],
        "severe": ["severe", "worst", "getting worse", "worsening", "unbearable"],
        "faintness": ["faint", "fainting", "passed out", "pass out", "dizzy", "lightheaded", "light-headed"],
        "heavy_bleeding": ["heavy bleeding", "heavy vaginal bleeding", "soaking through pads", "bleeding heavily"],
        "breathing_difficulty": ["difficulty breathing", "trouble breathing", "shortness of breath", "can't breathe", "cannot breathe"],
        "confusion": ["suddenly confused", "sudden confusion"],
    },
    "kn": {
        "irregular_periods": ["ಅನಿಯಮಿತ ಮಾಸಿಕ", "ಮಾಸಿಕ ಅನಿಯಮಿತ", "ಪೀರಿಯಡ್ ಅನಿಯಮಿತ", "ತಿಂಗಳು ತಪ್ಪುತ್ತಿದೆ"],
        "acne": ["ಮೊಡವೆ", "ಮುಖದ ಮೊಡವೆ"],
        "oily_skin": ["ಎಣ್ಣೆಯ ಚರ್ಮ"],
        "facial_body_hair": ["ಮುಖದ ಕೂದಲು", "ದೇಹದ ಕೂದಲು", "ಅನಗತ್ಯ ಕೂದಲು"],
        "hair_thinning": ["ಕೂದಲು ಉದುರುವುದು", "ಕೂದಲು ತೆಳುವಾಗುವುದು"],
        "pelvic_pain": ["ಹೊಟ್ಟೆ ನೋವು", "ಕೆಳ ಹೊಟ್ಟೆ ನೋವು", "ಶ್ರೋಣಿಯ ನೋವು", "ತೀವ್ರ ಹೊಟ್ಟೆ ನೋವು"],
        "severe": ["ತೀವ್ರ", "ಹೆಚ್ಚಾಗುತ್ತಿದೆ", "ಸಹಿಸಲಾಗದ"],
        "faintness": ["ಮೂರ್ಛೆ", "ತಲೆಸುತ್ತು", "ಪ್ರಜ್ಞೆ ತಪ್ಪು"],
        "heavy_bleeding": ["ಹೆಚ್ಚು ರಕ್ತಸ್ರಾವ", "ಭಾರೀ ರಕ್ತಸ್ರಾವ"],
        "breathing_difficulty": ["ಉಸಿರಾಟದ ತೊಂದರೆ", "ಉಸಿರಾಡಲು ಕಷ್ಟ"],
        "confusion": ["ಗೊಂದಲ", "ಗಾಬರಿ"],
    },
    "hi": {
        "irregular_periods": ["अनियमित पीरियड", "अनियमित माहवारी", "पीरियड अनियमित", "मासिक धर्म अनियमित", "पीरियड देर से"],
        "acne": ["मुंहासे", "मुँहासे", "पिंपल"],
        "oily_skin": ["तैलीय त्वचा"],
        "facial_body_hair": ["चेहरे पर बाल", "शरीर पर बाल", "अनचाहे बाल"],
        "hair_thinning": ["बाल झड़ना", "बाल पतले", "बालों का झड़ना"],
        "pelvic_pain": ["पेट में दर्द", "निचले पेट में दर्द", "श्रोणि में दर्द", "तेज़ पेट दर्द", "तेज पेट दर्द"],
        "severe": ["तेज़", "तेज", "बहुत गंभीर", "बढ़ता हुआ दर्द"],
        "faintness": ["बेहोश", "चक्कर", "चक्कर आना"],
        "heavy_bleeding": ["भारी रक्तस्राव", "बहुत अधिक रक्तस्राव"],
        "breathing_difficulty": ["सांस लेने में दिक्कत", "साँस लेने में कठिनाई"],
        "confusion": ["अचानक भ्रम", "अचानक उलझन"],
    },
    "ta": {
        "irregular_periods": ["ஒழுங்கற்ற மாதவிடாய்", "மாதவிடாய் ஒழுங்கற்ற", "மாதவிடாய் தாமதம்"],
        "acne": ["முகப்பரு", "பருக்கள்"],
        "oily_skin": ["எண்ணெய் பசை சருமம்"],
        "facial_body_hair": ["முகத்தில் முடி", "உடலில் முடி", "தேவையற்ற முடி"],
        "hair_thinning": ["முடி உதிர்வு", "முடி மெலிதல்"],
        "pelvic_pain": ["அடிவயிற்று வலி", "வயிற்று வலி", "இடுப்பு வலி", "கடுமையான வயிற்று வலி"],
        "severe": ["கடுமையான", "மோசமாகிறது", "தாங்க முடியாத"],
        "faintness": ["மயக்கம்", "தலைசுற்றல்", "நினைவிழப்பு"],
        "heavy_bleeding": ["அதிக ரத்தப்போக்கு", "கடுமையான ரத்தப்போக்கு"],
        "breathing_difficulty": ["மூச்சுத்திணறல்", "மூச்சு விடுவதில் சிரமம்"],
        "confusion": ["திடீர் குழப்பம்"],
    },
    "te": {
        "irregular_periods": ["క్రమం తప్పిన పీరియడ్స్", "నెలసరి క్రమం తప్పడం", "పీరియడ్స్ ఆలస్యం", "క్రమరహిత పీరియడ్స్"],
        "acne": ["మొటిమలు", "ముఖంపై మొటిమలు"],
        "oily_skin": ["జిడ్డు చర్మం"],
        "facial_body_hair": ["ముఖంపై వెంట్రుకలు", "శరీరంపై వెంట్రుకలు", "అవాంఛిత వెంట్రుకలు"],
        "hair_thinning": ["జుట్టు రాలడం", "జుట్టు పలుచబడటం"],
        "pelvic_pain": ["కడుపు నొప్పి", "దిగువ కడుపు నొప్పి", "పొత్తికడుపు నొప్పి", "తీవ్రమైన కడుపు నొప్పి"],
        "severe": ["తీవ్రమైన", "మరింత ఎక్కువవుతోంది", "భరించలేని"],
        "faintness": ["మూర్ఛ", "తలతిరగడం", "స్పృహ తప్పడం"],
        "heavy_bleeding": ["అధిక రక్తస్రావం", "భారీ రక్తస్రావం"],
        "breathing_difficulty": ["శ్వాస తీసుకోవడంలో ఇబ్బంది", "ఊపిరి తీసుకోవడంలో కష్టం"],
        "confusion": ["అకస్మాత్తుగా గందరగోళం"],
    },
}

NEGATIONS = {
    "en": ["no", "not", "never", "without", "don't", "do not", "doesn't", "does not", "didn't", "did not", "isn't", "is not", "aren't", "are not", "wasn't", "was not"],
    "kn": ["ಇಲ್ಲ", "ಇಲ್ಲದೆ", "ಆಗಿಲ್ಲ", "ಅಲ್ಲ"],
    "hi": ["नहीं", "नहीं है", "बिना", "नहीं होता", "नहीं होती"],
    "ta": ["இல்லை", "இல்லாமல்", "இல்லாத"],
    "te": ["లేదు", "లేకుండా", "కాదు", "లేదు అని"],
}

SYMPTOM_LABELS = {
    "en": {"irregular_periods": "Irregular or missed periods", "acne": "Acne / pimples", "oily_skin": "Oily skin", "facial_body_hair": "Unusual facial or body hair", "hair_thinning": "Scalp hair thinning or loss", "pelvic_pain": "Pelvic or lower abdominal pain"},
    "kn": {"irregular_periods": "ಅನಿಯಮಿತ ಅಥವಾ ತಪ್ಪಿದ ಮಾಸಿಕ", "acne": "ಮೊಡವೆ", "oily_skin": "ಎಣ್ಣೆಯ ಚರ್ಮ", "facial_body_hair": "ಮುಖ ಅಥವಾ ದೇಹದ ಅಸಾಮಾನ್ಯ ಕೂದಲು", "hair_thinning": "ತಲೆಯ ಕೂದಲು ತೆಳುವಾಗುವುದು ಅಥವಾ ಉದುರುವುದು", "pelvic_pain": "ಶ್ರೋಣಿ ಅಥವಾ ಕೆಳ ಹೊಟ್ಟೆ ನೋವು"},
    "hi": {"irregular_periods": "अनियमित या छूटी हुई माहवारी", "acne": "मुंहासे", "oily_skin": "तैलीय त्वचा", "facial_body_hair": "चेहरे या शरीर पर असामान्य बाल", "hair_thinning": "सिर के बाल पतले होना या झड़ना", "pelvic_pain": "श्रोणि या निचले पेट में दर्द"},
    "ta": {"irregular_periods": "ஒழுங்கற்ற அல்லது தவறிய மாதவிடாய்", "acne": "முகப்பரு", "oily_skin": "எண்ணெய் பசை சருமம்", "facial_body_hair": "முகம் அல்லது உடலில் வழக்கத்திற்கு மாறான முடி", "hair_thinning": "தலையில் முடி மெலிதல் அல்லது உதிர்தல்", "pelvic_pain": "இடுப்பு அல்லது அடிவயிற்று வலி"},
    "te": {"irregular_periods": "క్రమం తప్పిన లేదా రాని పీరియడ్స్", "acne": "మొటిమలు", "oily_skin": "జిడ్డు చర్మం", "facial_body_hair": "ముఖం లేదా శరీరంపై అసాధారణ వెంట్రుకలు", "hair_thinning": "తలపై జుట్టు పలుచబడటం లేదా రాలడం", "pelvic_pain": "పొత్తికడుపు లేదా దిగువ కడుపు నొప్పి"},
}

FOLLOWUP_LABELS = {
    "en": {"acne": "Have you noticed acne?", "oily_skin": "Have you noticed oily skin?", "facial_body_hair": "Have you noticed unusual facial or body hair?", "hair_thinning": "Have you noticed scalp hair thinning or loss?"},
    "kn": {"acne": "ಮೊಡವೆ ಗಮನಿಸಿದ್ದೀರಾ?", "oily_skin": "ಚರ್ಮ ಹೆಚ್ಚು ಎಣ್ಣೆಯುಕ್ತವಾಗಿದೆಯೇ?", "facial_body_hair": "ಮುಖ ಅಥವಾ ದೇಹದಲ್ಲಿ ಅಸಾಮಾನ್ಯ ಕೂದಲು ಗಮನಿಸಿದ್ದೀರಾ?", "hair_thinning": "ತಲೆಯ ಕೂದಲು ತೆಳುವಾಗುವುದು ಅಥವಾ ಉದುರುವುದನ್ನು ಗಮನಿಸಿದ್ದೀರಾ?"},
    "hi": {"acne": "क्या आपने मुंहासे देखे हैं?", "oily_skin": "क्या त्वचा तैलीय रहती है?", "facial_body_hair": "क्या चेहरे या शरीर पर असामान्य बाल देखे हैं?", "hair_thinning": "क्या सिर के बाल पतले होना या झड़ना देखा है?"},
    "ta": {"acne": "முகப்பருவைக் கவனித்துள்ளீர்களா?", "oily_skin": "எண்ணெய் பசை சருமத்தைக் கவனித்துள்ளீர்களா?", "facial_body_hair": "முகம் அல்லது உடலில் வழக்கத்திற்கு மாறான முடி உள்ளதா?", "hair_thinning": "தலையில் முடி மெலிதல் அல்லது உதிர்தல் உள்ளதா?"},
    "te": {"acne": "మొటిమలను గమనించారా?", "oily_skin": "జిడ్డు చర్మాన్ని గమనించారా?", "facial_body_hair": "ముఖం లేదా శరీరంపై అసాధారణ వెంట్రుకలు గమనించారా?", "hair_thinning": "తలపై జుట్టు పలుచబడటం లేదా రాలడం గమనించారా?"},
}

ALTERNATIVE_CAUSE_NOTES = {
    "en": "Other possible explanations for irregular or missed periods include pregnancy, stress, changes in weight or exercise, some hormonal contraception, perimenopause, and thyroid conditions. These are examples, not conclusions; a clinician can help assess the cause.",
    "kn": "ಅನಿಯಮಿತ ಅಥವಾ ತಪ್ಪಿದ ಮಾಸಿಕಕ್ಕೆ ಗರ್ಭಧಾರಣೆ, ಒತ್ತಡ, ತೂಕ ಅಥವಾ ವ್ಯಾಯಾಮದ ಬದಲಾವಣೆ, ಕೆಲವು ಹಾರ್ಮೋನ್ ಗರ್ಭನಿರೋಧಕಗಳು, ಪೆರಿಮೆನೋಪಾಸ್ ಅಥವಾ ಥೈರಾಯ್ಡ್ ಸಮಸ್ಯೆಗಳೂ ಕಾರಣವಾಗಿರಬಹುದು. ಇವು ಸಾಧ್ಯತೆಗಳ ಉದಾಹರಣೆಗಳು ಮಾತ್ರ; ಆರೋಗ್ಯ ವೃತ್ತಿಪರರು ಕಾರಣವನ್ನು ಪರಿಶೀಲಿಸುತ್ತಾರೆ.",
    "hi": "अनियमित या छूटी हुई माहवारी के अन्य कारणों में गर्भावस्था, तनाव, वजन या व्यायाम में बदलाव, कुछ हार्मोनल गर्भनिरोधक, पेरिमेनोपॉज़ और थायरॉइड की समस्याएँ शामिल हो सकती हैं। ये केवल उदाहरण हैं; कारण का आकलन स्वास्थ्य पेशेवर करेंगे।",
    "ta": "ஒழுங்கற்ற அல்லது தவறிய மாதவிடாய்க்கு கர்ப்பம், மனஅழுத்தம், எடை அல்லது உடற்பயிற்சி மாற்றங்கள், சில ஹார்மோன் கருத்தடை முறைகள், பெரிமெனோபாஸ் அல்லது தைராய்டு பிரச்சினைகளும் காரணமாக இருக்கலாம். இவை எடுத்துக்காட்டுகள் மட்டுமே; காரணத்தை சுகாதார நிபுணர் மதிப்பிடுவார்.",
    "te": "క్రమం తప్పిన లేదా రాని పీరియడ్స్‌కు గర్భధారణ, ఒత్తిడి, బరువు లేదా వ్యాయామంలో మార్పులు, కొన్ని హార్మోన్ల గర్భనిరోధకాలు, పెరిమెనోపాజ్ లేదా థైరాయిడ్ సమస్యలు ఇతర కారణాలు కావచ్చు. ఇవి ఉదాహరణలు మాత్రమే; కారణాన్ని ఆరోగ్య నిపుణుడు అంచనా వేస్తారు.",
}

I18N = {
    "en": {
        "home": "Home", "understand": "Understand symptoms", "learn": "Learn about PCOS", "tagline": "Understand your symptoms. Take your next step.",
        "language": "Preferred language", "start": "Understand My Symptoms", "learn_button": "Learn About PCOS", "describe": "Describe your symptoms in your own words", "voice_note": "Voice support depends on your browser and available language voices. Typed input always works.",
        "voice_prompt": "Would you like to add anything else?", "confirm_summary": "I reviewed this limited keyword summary. It may miss meaning, especially with mixed language, slang, or speech recognition errors.",
        "menstrual": "How would you describe your periods?", "duration": "How long have you noticed these symptoms?", "urgent_q": "Are any of these happening now: severe or worsening lower-belly/pelvic pain, fainting or dizziness, heavy vaginal bleeding, trouble breathing, or sudden confusion?", "skin_q": "Have you noticed acne or oily skin?", "hair_q": "Have you noticed unusual facial/body hair or scalp hair thinning?",
        "yes": "Yes", "no": "No", "unsure": "Not sure", "step_a": "1 · Describe", "step_b": "2 · Follow-up", "step_c": "3 · Confirm", "step_d": "4 · Guidance",
        "empty_summary": "No supported symptom phrases were recognized. You can still continue, but the written description may not have been understood by this limited prototype.",
        "no_match": "No phrases from this prototype's small symptom vocabulary were found. That does not mean you have no symptoms. Please check the original text and continue only if the summary is accurate enough for you.",
        "results_heading": "Your next-step guide", "summary_heading": "What you reported", "urgent_heading": "Please get urgent medical help now", "urgent_body": "Your answers include a possible warning sign. This tool cannot assess an emergency. Contact your local emergency number or go to the nearest emergency department now. Ask someone to stay with you; do not drive yourself if you feel faint or severely unwell.",
        "uncertain_heading": "Please clarify this with a health professional promptly", "uncertain_body": "You are unsure whether a warning sign is present. If severe or worsening pain, faintness, heavy bleeding, breathing difficulty, or sudden confusion may be happening, contact local urgent or emergency medical care now.",
        "possible_heading": "A possible association, not a diagnosis", "possible_body": "Irregular periods together with acne, oily skin, unusual facial/body hair, or scalp hair thinning can be seen with PCOS (now also called PMOS). These features can also have other causes. A questionnaire cannot establish or rule out PCOS/PMOS.",
        "limited_heading": "What this checker can say", "limited_body": "This short description does not establish a specific association. Many symptoms have several possible causes, and this keyword-based prototype may miss context or symptoms.",
        "next_heading": "Suggested next steps", "appointment": "If symptoms persist, affect your daily life, or concern you, arrange a non-urgent appointment with a primary care clinician or gynaecology professional. Bring your own notes about cycle changes, symptom timing, and questions. They can decide whether an examination or tests are appropriate.",
        "unclear": "Some answers are missing or marked ‘not sure’. A clinician can help clarify them; the summary below keeps that uncertainty visible.", "not_diagnosis": "NariCare AI provides educational information. It does not diagnose, rule out a condition, or replace professional medical care.",
        "text": "Type or edit your description", "examples": "Quick add", "continue": "Continue", "back": "Back", "clear": "Clear", "confirm": "Confirm and view guidance", "start_again": "Start again", "try_again": "Try again", "not_sure": "Not sure / prefer not to answer", "duration_options": ["Less than a month", "1–3 months", "More than 3 months", "It varies", "Not sure"], "period_options": ["Regular", "Irregular / often late", "No periods for 3+ months", "It varies", "Not sure / prefer not to answer"],
        "check_sources": "Sources", "pcos_name_note": "Many people still recognize the term PCOS. NHS and Monash now use PMOS (polyendocrine metabolic ovarian syndrome); some guidance and research pages still use PCOS.",
        "demo_note": "All scenarios below are fictional and use the same review and guidance flow. The Kannada example is typed; it does not pretend to be a voice transcript.",
    },
    "kn": {
        "home": "ಮುಖಪುಟ", "understand": "ಲಕ್ಷಣಗಳನ್ನು ಅರ್ಥಮಾಡಿಕೊಳ್ಳಿ", "learn": "PCOS ಬಗ್ಗೆ ತಿಳಿಯಿರಿ", "tagline": "ನಿಮ್ಮ ಲಕ್ಷಣಗಳನ್ನು ಅರ್ಥಮಾಡಿಕೊಳ್ಳಿ. ಮುಂದಿನ ಹೆಜ್ಜೆ ಇಡಿ.", "language": "ಆದ್ಯತೆಯ ಭಾಷೆ", "start": "ನನ್ನ ಲಕ್ಷಣಗಳನ್ನು ಅರ್ಥಮಾಡಿಕೊಳ್ಳಿ", "learn_button": "PCOS ಬಗ್ಗೆ ತಿಳಿಯಿರಿ", "describe": "ನಿಮ್ಮ ಮಾತಿನಲ್ಲಿ ಲಕ್ಷಣಗಳನ್ನು ವಿವರಿಸಿ", "voice_note": "ಧ್ವನಿ ಸೌಲಭ್ಯವು ನಿಮ್ಮ ಬ್ರೌಸರ್ ಮತ್ತು ಲಭ್ಯವಿರುವ ಭಾಷಾ ಧ್ವನಿಗಳ ಮೇಲೆ ಅವಲಂಬಿತವಾಗಿದೆ. ಟೈಪ್ ಮಾಡುವುದು ಯಾವಾಗಲೂ ಲಭ್ಯ.", "voice_prompt": "ಇನ್ನೇನಾದರೂ ಸೇರಿಸಲು ಬಯಸುವಿರಾ?", "confirm_summary": "ಈ ಸೀಮಿತ ಪದ-ಹೊಂದಾಣಿಕೆಯ ಸಾರಾಂಶವನ್ನು ಪರಿಶೀಲಿಸಿದ್ದೇನೆ. ಬೇರೆ ಭಾಷೆಗಳ ಮಿಶ್ರಣ, ಸ್ಥಳೀಯ ಪದಗಳು ಅಥವಾ ಧ್ವನಿ ಗುರುತಿಸುವಿಕೆಯ ತಪ್ಪುಗಳಿಂದ ಅರ್ಥ ತಪ್ಪಿರಬಹುದು.",
        "menstrual": "ನಿಮ್ಮ ಮಾಸಿಕವನ್ನು ಹೇಗೆ ವಿವರಿಸುತ್ತೀರಿ?", "duration": "ಈ ಲಕ್ಷಣಗಳನ್ನು ಎಷ್ಟು ಸಮಯದಿಂದ ಗಮನಿಸಿದ್ದೀರಿ?", "urgent_q": "ಈಗ ಇವುಗಳಲ್ಲಿ ಯಾವುದಾದರೂ ಇದೆಯೇ: ತೀವ್ರ ಅಥವಾ ಹೆಚ್ಚಾಗುತ್ತಿರುವ ಕೆಳ ಹೊಟ್ಟೆ/ಶ್ರೋಣಿ ನೋವು, ಮೂರ್ಛೆ ಅಥವಾ ತಲೆಸುತ್ತು, ಹೆಚ್ಚು ಯೋನಿ ರಕ್ತಸ್ರಾವ, ಉಸಿರಾಟದ ತೊಂದರೆ ಅಥವಾ ಹಠಾತ್ ಗೊಂದಲ?", "skin_q": "ಮೊಡವೆ ಅಥವಾ ಎಣ್ಣೆಯ ಚರ್ಮ ಗಮನಿಸಿದ್ದೀರಾ?", "hair_q": "ಮುಖ/ದೇಹದ ಅಸಾಮಾನ್ಯ ಕೂದಲು ಅಥವಾ ತಲೆಯ ಕೂದಲು ತೆಳುವಾಗುವುದನ್ನು ಗಮನಿಸಿದ್ದೀರಾ?", "yes": "ಹೌದು", "no": "ಇಲ್ಲ", "unsure": "ಖಚಿತವಿಲ್ಲ", "step_a": "1 · ವಿವರಿಸಿ", "step_b": "2 · ಪ್ರಶ್ನೆಗಳು", "step_c": "3 · ದೃಢೀಕರಿಸಿ", "step_d": "4 · ಮಾರ್ಗದರ್ಶನ", "empty_summary": "ಈ ಸೀಮಿತ ವ್ಯವಸ್ಥೆಗೆ ಹೊಂದುವ ಲಕ್ಷಣ ಪದಗಳು ಪತ್ತೆಯಾಗಿಲ್ಲ. ಮುಂದುವರಿಯಬಹುದು, ಆದರೆ ವಿವರಣೆ ಸರಿಯಾಗಿ ಅರ್ಥವಾಗಿರದೆ ಇರಬಹುದು.", "no_match": "ಈ ಸಣ್ಣ ಪದಪಟ್ಟಿಯಲ್ಲಿ ಹೊಂದುವ ಪದಗಳು ಕಂಡುಬಂದಿಲ್ಲ. ಅದರಿಂದ ನಿಮಗೆ ಲಕ್ಷಣಗಳಿಲ್ಲ ಎಂದರ್ಥವಲ್ಲ.", "results_heading": "ಮುಂದಿನ ಹೆಜ್ಜೆಯ ಮಾರ್ಗದರ್ಶನ", "summary_heading": "ನೀವು ತಿಳಿಸಿದವು", "urgent_heading": "ದಯವಿಟ್ಟು ಈಗಲೇ ತುರ್ತು ವೈದ್ಯಕೀಯ ಸಹಾಯ ಪಡೆಯಿರಿ", "urgent_body": "ನಿಮ್ಮ ಉತ್ತರಗಳಲ್ಲಿ ಸಾಧ್ಯವಾದ ಎಚ್ಚರಿಕೆಯ ಲಕ್ಷಣವಿದೆ. ಸ್ಥಳೀಯ ತುರ್ತು ಸಂಖ್ಯೆಗೆ ಕರೆ ಮಾಡಿ ಅಥವಾ ಹತ್ತಿರದ ತುರ್ತು ಚಿಕಿತ್ಸಾ ವಿಭಾಗಕ್ಕೆ ಈಗಲೇ ಹೋಗಿ. ತಲೆಸುತ್ತು ಅಥವಾ ತೀವ್ರ ಅಸ್ವಸ್ಥತೆ ಇದ್ದರೆ ನೀವೇ ವಾಹನ ಚಲಾಯಿಸಬೇಡಿ.", "uncertain_heading": "ದಯವಿಟ್ಟು ಶೀಘ್ರವೇ ಆರೋಗ್ಯ ವೃತ್ತಿಪರರಿಂದ ಸ್ಪಷ್ಟಪಡಿಸಿಕೊಳ್ಳಿ", "uncertain_body": "ಎಚ್ಚರಿಕೆಯ ಲಕ್ಷಣ ಇದೆಯೇ ಎಂಬುದು ಖಚಿತವಿಲ್ಲ. ತೀವ್ರ/ಹೆಚ್ಚಾಗುವ ನೋವು, ಮೂರ್ಛೆ, ಹೆಚ್ಚು ರಕ್ತಸ್ರಾವ, ಉಸಿರಾಟದ ತೊಂದರೆ ಅಥವಾ ಹಠಾತ್ ಗೊಂದಲ ಇರಬಹುದೆಂದರೆ ತಕ್ಷಣ ಸ್ಥಳೀಯ ತುರ್ತು ವೈದ್ಯಕೀಯ ಸಹಾಯ ಪಡೆಯಿರಿ.", "possible_heading": "ಸಂಭವಿಸಬಹುದಾದ ಸಂಬಂಧ — ರೋಗನಿರ್ಣಯವಲ್ಲ", "possible_body": "ಅನಿಯಮಿತ ಮಾಸಿಕದ ಜೊತೆಗೆ ಮೊಡವೆ, ಎಣ್ಣೆಯ ಚರ್ಮ, ಮುಖ/ದೇಹದ ಅಸಾಮಾನ್ಯ ಕೂದಲು ಅಥವಾ ತಲೆಯ ಕೂದಲು ತೆಳುವಾಗುವುದು PCOS (ಈಗ PMOS ಎಂದೂ ಕರೆಯುತ್ತಾರೆ) ನಲ್ಲಿ ಕಾಣಬಹುದು. ಬೇರೆ ಕಾರಣಗಳೂ ಇರಬಹುದು. ಪ್ರಶ್ನಾವಳಿ ರೋಗನಿರ್ಣಯ ಮಾಡುವುದಿಲ್ಲ.", "limited_heading": "ಈ ಪರಿಶೀಲಕ ಏನು ಹೇಳಬಲ್ಲದು", "limited_body": "ಈ ಚಿಕ್ಕ ವಿವರಣೆಯಿಂದ ನಿರ್ದಿಷ್ಟ ಸಂಬಂಧವನ್ನು ನಿರ್ಧರಿಸಲಾಗುವುದಿಲ್ಲ. ಹಲವು ಲಕ್ಷಣಗಳಿಗೆ ಹಲವು ಕಾರಣಗಳಿರಬಹುದು; ಈ ಪದ-ಆಧಾರಿತ ಮಾದರಿ ಸಂದರ್ಭವನ್ನು ತಪ್ಪಿಸಬಹುದು.", "next_heading": "ಮುಂದಿನ ಹಂತಗಳು", "appointment": "ಲಕ್ಷಣಗಳು ಮುಂದುವರಿದರೆ, ದಿನನಿತ್ಯದ ಜೀವನಕ್ಕೆ ಅಡ್ಡಿಯಾದರೆ ಅಥವಾ ಚಿಂತೆಯಿದ್ದರೆ, ಪ್ರಾಥಮಿಕ ವೈದ್ಯರು ಅಥವಾ ಸ್ತ್ರೀರೋಗ ತಜ್ಞರೊಂದಿಗೆ ಸಾಮಾನ್ಯ ಭೇಟಿಯನ್ನು ಏರ್ಪಡಿಸಿ. ಮಾಸಿಕ ಬದಲಾವಣೆ, ಲಕ್ಷಣಗಳ ಅವಧಿ ಮತ್ತು ನಿಮ್ಮ ಪ್ರಶ್ನೆಗಳ ಬಗ್ಗೆ ನಿಮ್ಮದೇ ಟಿಪ್ಪಣಿಗಳನ್ನು ಕೊಂಡೊಯ್ಯಿರಿ.", "unclear": "ಕೆಲವು ಉತ್ತರಗಳು ಖಾಲಿ ಅಥವಾ ‘ಖಚಿತವಿಲ್ಲ’ ಎಂದು ಗುರುತಿಸಲಾಗಿದೆ. ಕೆಳಗಿನ ಸಾರಾಂಶದಲ್ಲಿ ಆ ಅನಿಶ್ಚಿತತೆ ಉಳಿಸಲಾಗಿದೆ.", "not_diagnosis": "NariCare AI ಶಿಕ್ಷಣದ ಮಾಹಿತಿಯನ್ನು ಮಾತ್ರ ನೀಡುತ್ತದೆ. ಇದು ರೋಗನಿರ್ಣಯ ಮಾಡುವುದಿಲ್ಲ ಅಥವಾ ವೈದ್ಯಕೀಯ ಆರೈಕೆಗೆ ಪರ್ಯಾಯವಲ್ಲ.", "text": "ನಿಮ್ಮ ವಿವರಣೆಯನ್ನು ಟೈಪ್ ಮಾಡಿ ಅಥವಾ ತಿದ್ದುಪಡಿ ಮಾಡಿ", "examples": "ತ್ವರಿತವಾಗಿ ಸೇರಿಸಿ", "continue": "ಮುಂದುವರಿಸಿ", "back": "ಹಿಂದೆ", "clear": "ಅಳಿಸಿ", "confirm": "ದೃಢೀಕರಿಸಿ ಮತ್ತು ಮಾರ್ಗದರ್ಶನ ನೋಡಿ", "start_again": "ಮತ್ತೆ ಪ್ರಾರಂಭಿಸಿ", "try_again": "ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ", "not_sure": "ಖಚಿತವಿಲ್ಲ / ಉತ್ತರಿಸಲು ಇಷ್ಟವಿಲ್ಲ", "duration_options": ["ಒಂದು ತಿಂಗಳಿಗಿಂತ ಕಡಿಮೆ", "1–3 ತಿಂಗಳು", "3 ತಿಂಗಳಿಗಿಂತ ಹೆಚ್ಚು", "ಬದಲಾಗುತ್ತದೆ", "ಖಚಿತವಿಲ್ಲ"], "period_options": ["ನಿಯಮಿತ", "ಅನಿಯಮಿತ / ತಡವಾಗುತ್ತದೆ", "3+ ತಿಂಗಳು ಮಾಸಿಕ ಇಲ್ಲ", "ಬದಲಾಗುತ್ತದೆ", "ಖಚಿತವಿಲ್ಲ / ಉತ್ತರಿಸಲು ಇಷ್ಟವಿಲ್ಲ"], "check_sources": "ಮೂಲಗಳು", "pcos_name_note": "PCOS ಪದವನ್ನು ಇನ್ನೂ ಹಲವರು ಬಳಸುತ್ತಾರೆ. NHS ಮತ್ತು Monash ಈಗ PMOS ಪದವನ್ನು ಬಳಸುತ್ತವೆ; ಕೆಲವು ಮಾರ್ಗಸೂಚಿಗಳು ಇನ್ನೂ PCOS ಎಂದು ಕರೆಯುತ್ತವೆ.", "demo_note": "ಕೆಳಗಿನ ಎಲ್ಲಾ ಉದಾಹರಣೆಗಳು ಕಲ್ಪಿತವಾಗಿವೆ ಮತ್ತು ಇದೇ ಪರಿಶೀಲನೆ-ಮಾರ್ಗದರ್ಶನ ಹಂತಗಳನ್ನು ಬಳಸುತ್ತವೆ. ಕನ್ನಡ ಉದಾಹರಣೆ ಟೈಪ್ ಮಾಡಿದ್ದು; ನಕಲಿ ಧ್ವನಿ ಲಿಪ್ಯಂತರವಲ್ಲ.",
    },
    "hi": {
        "home": "होम", "understand": "लक्षण समझें", "learn": "PCOS के बारे में", "tagline": "अपने लक्षण समझें। अगला कदम जानें।", "language": "पसंदीदा भाषा", "start": "मेरे लक्षण समझें", "learn_button": "PCOS के बारे में जानें", "describe": "अपने शब्दों में लक्षण बताएं", "voice_note": "आवाज़ की सुविधा आपके ब्राउज़र और उपलब्ध भाषा-आवाज़ पर निर्भर करती है। टाइप करने का विकल्प हमेशा उपलब्ध है।", "voice_prompt": "क्या आप कुछ और जोड़ना चाहेंगे?", "confirm_summary": "मैंने इस सीमित शब्द-मिलान सारांश को जाँचा है। मिली-जुली भाषा, स्थानीय शब्द या आवाज़ पहचान की गलती से अर्थ छूट सकता है।", "menstrual": "आप अपने पीरियड्स को कैसे बताएंगे?", "duration": "आपने ये लक्षण कितने समय से देखे हैं?", "urgent_q": "क्या अभी इनमें से कुछ हो रहा है: तेज़ या बढ़ता हुआ निचले पेट/श्रोणि का दर्द, बेहोशी या चक्कर, बहुत अधिक योनि से खून, सांस लेने में दिक्कत या अचानक भ्रम?", "skin_q": "क्या आपने मुंहासे या तैलीय त्वचा देखी है?", "hair_q": "क्या चेहरे/शरीर पर असामान्य बाल या सिर के बाल पतले होना देखा है?", "yes": "हाँ", "no": "नहीं", "unsure": "पक्का नहीं", "step_a": "1 · बताएं", "step_b": "2 · सवाल", "step_c": "3 · जाँचें", "step_d": "4 · मार्गदर्शन", "empty_summary": "इस सीमित प्रणाली को पहचाने जाने वाले लक्षण शब्द नहीं मिले। आप आगे बढ़ सकते हैं, लेकिन विवरण सही तरह समझा न गया हो सकता है।", "no_match": "इस छोटे शब्द-संग्रह से कोई मेल नहीं मिला। इसका मतलब यह नहीं कि आपको लक्षण नहीं हैं।", "results_heading": "आपके अगले कदम", "summary_heading": "आपने जो बताया", "urgent_heading": "कृपया अभी तत्काल चिकित्सा सहायता लें", "urgent_body": "आपके उत्तरों में एक संभावित चेतावनी संकेत है। स्थानीय आपातकालीन नंबर पर संपर्क करें या निकटतम आपातकालीन विभाग जाएँ। चक्कर या गंभीर अस्वस्थता हो तो खुद गाड़ी न चलाएँ।", "uncertain_heading": "कृपया जल्द स्वास्थ्य पेशेवर से स्पष्ट करें", "uncertain_body": "आपको पक्का नहीं कि चेतावनी संकेत मौजूद है। यदि तेज़/बढ़ता दर्द, बेहोशी, अधिक रक्तस्राव, सांस की दिक्कत या अचानक भ्रम हो सकता है, तो अभी स्थानीय तत्काल चिकित्सा सहायता लें।", "possible_heading": "संभावित संबंध, निदान नहीं", "possible_body": "अनियमित पीरियड्स के साथ मुंहासे, तैलीय त्वचा, चेहरे/शरीर पर असामान्य बाल या सिर के बाल पतले होना PCOS (जिसे अब PMOS भी कहा जाता है) में दिख सकता है। अन्य कारण भी हो सकते हैं। प्रश्नावली निदान नहीं कर सकती।", "limited_heading": "यह जाँच क्या बता सकती है", "limited_body": "इस छोटे विवरण से कोई खास संबंध तय नहीं होता। कई लक्षणों के कई कारण हो सकते हैं और यह शब्द-आधारित नमूना संदर्भ चूक सकता है।", "next_heading": "सुझाए गए अगले कदम", "appointment": "यदि लक्षण बने रहें, रोज़मर्रा के जीवन को प्रभावित करें या चिंता हो, तो प्राथमिक देखभाल चिकित्सक या स्त्रीरोग विशेषज्ञ से सामान्य समय लें। पीरियड में बदलाव, लक्षण कब होते हैं और सवालों के बारे में अपने नोट्स साथ ले जाएँ।", "unclear": "कुछ उत्तर खाली हैं या ‘पक्का नहीं’ चुना गया है। नीचे के सारांश में यह अनिश्चितता बनी रहेगी।", "not_diagnosis": "NariCare AI केवल शैक्षिक जानकारी देता है। यह निदान नहीं करता और पेशेवर चिकित्सा देखभाल का विकल्प नहीं है।", "text": "अपना विवरण लिखें या संपादित करें", "examples": "जल्दी जोड़ें", "continue": "आगे बढ़ें", "back": "पीछे", "clear": "मिटाएँ", "confirm": "पुष्टि करें और मार्गदर्शन देखें", "start_again": "फिर से शुरू करें", "try_again": "फिर कोशिश करें", "not_sure": "पक्का नहीं / जवाब नहीं देना", "duration_options": ["एक महीने से कम", "1–3 महीने", "3 महीने से अधिक", "बदलता रहता है", "पक्का नहीं"], "period_options": ["नियमित", "अनियमित / अक्सर देर से", "3+ महीने से पीरियड नहीं", "बदलता रहता है", "पक्का नहीं / जवाब नहीं देना"], "check_sources": "स्रोत", "pcos_name_note": "कई लोग PCOS नाम से परिचित हैं। NHS और Monash अब PMOS नाम इस्तेमाल करते हैं; कुछ मार्गदर्शिकाएँ अभी PCOS कहती हैं।", "demo_note": "नीचे के सभी उदाहरण काल्पनिक हैं और इसी समीक्षा व मार्गदर्शन प्रक्रिया का उपयोग करते हैं। कन्नड़ उदाहरण टाइप किया गया है, आवाज़ का नकली प्रतिलेख नहीं।",
    },
    "ta": {
        "home": "முகப்பு", "understand": "அறிகுறிகளைப் புரிந்துகொள்ளுங்கள்", "learn": "PCOS பற்றி", "tagline": "உங்கள் அறிகுறிகளைப் புரிந்து அடுத்த படியை அறியுங்கள்.", "language": "விருப்ப மொழி", "start": "என் அறிகுறிகளைப் புரிந்துகொள்ளுங்கள்", "learn_button": "PCOS பற்றி அறிக", "describe": "உங்கள் சொற்களில் அறிகுறிகளை விவரிக்கவும்", "voice_note": "குரல் வசதி உங்கள் உலாவி மற்றும் கிடைக்கும் மொழிக் குரலைப் பொறுத்தது. தட்டச்சு எப்போதும் கிடைக்கும்.", "voice_prompt": "வேறு ஏதாவது சேர்க்க விரும்புகிறீர்களா?", "confirm_summary": "இந்த வரையறுக்கப்பட்ட சொல்-பொருத்தச் சுருக்கத்தைச் சரிபார்த்தேன். மொழிக்கலப்பு, வழக்குச் சொற்கள் அல்லது குரல் பிழைகள் அர்த்தத்தைத் தவறவிடலாம்.", "menstrual": "உங்கள் மாதவிடாயை எப்படிச் சொல்வீர்கள்?", "duration": "இந்த அறிகுறிகளை எவ்வளவு காலமாகக் கவனிக்கிறீர்கள்?", "urgent_q": "இப்போது இவற்றில் ஏதேனும் உள்ளதா: கடுமையான அல்லது அதிகரிக்கும் அடிவயிறு/இடுப்பு வலி, மயக்கம், அதிக யோனி இரத்தப்போக்கு, மூச்சுத்திணறல் அல்லது திடீர் குழப்பம்?", "skin_q": "முகப்பரு அல்லது எண்ணெய் பசை சருமம் உள்ளதா?", "hair_q": "முகம்/உடலில் வழக்கத்திற்கு மாறான முடி அல்லது தலையில் முடி மெலிதல் உள்ளதா?", "yes": "ஆம்", "no": "இல்லை", "unsure": "தெரியவில்லை", "step_a": "1 · விவரிக்கவும்", "step_b": "2 · கேள்விகள்", "step_c": "3 · உறுதிப்படுத்தவும்", "step_d": "4 · வழிகாட்டல்", "empty_summary": "இந்த வரையறுக்கப்பட்ட அமைப்பிற்கு பொருந்தும் அறிகுறிச் சொற்கள் கிடைக்கவில்லை. தொடரலாம்; ஆனால் விவரம் சரியாகப் புரியாமல் இருக்கலாம்.", "no_match": "இந்தச் சிறிய சொல் பட்டியலில் பொருத்தம் கிடைக்கவில்லை. அதனால் அறிகுறிகள் இல்லை என்று அர்த்தமல்ல.", "results_heading": "அடுத்த படி வழிகாட்டி", "summary_heading": "நீங்கள் தெரிவித்தவை", "urgent_heading": "தயவுசெய்து இப்போது அவசர மருத்துவ உதவி பெறுங்கள்", "urgent_body": "உங்கள் பதில்களில் ஒரு எச்சரிக்கை அறிகுறி இருக்கலாம். உள்ளூர் அவசர எண்ணைத் தொடர்புகொள்ளவும் அல்லது அருகிலுள்ள அவசர சிகிச்சைப் பிரிவுக்குச் செல்லவும். மயக்கம் அல்லது கடுமையான உடல்நலக்குறைவு இருந்தால் நீங்களே வாகனம் ஓட்ட வேண்டாம்.", "uncertain_heading": "சுகாதார நிபுணரிடம் விரைவில் தெளிவுபடுத்துங்கள்", "uncertain_body": "எச்சரிக்கை அறிகுறி உள்ளதா என்பது உறுதியாகத் தெரியவில்லை. கடுமையான/அதிகரிக்கும் வலி, மயக்கம், அதிக இரத்தப்போக்கு, மூச்சுத்திணறல் அல்லது திடீர் குழப்பம் இருக்கலாம் என்றால் உடனடி உள்ளூர் மருத்துவ உதவி பெறுங்கள்.", "possible_heading": "சாத்தியமான தொடர்பு; நோயறிதல் அல்ல", "possible_body": "ஒழுங்கற்ற மாதவிடாயுடன் முகப்பரு, எண்ணெய் பசை சருமம், முகம்/உடலில் வழக்கத்திற்கு மாறான முடி அல்லது தலையில் முடி மெலிதல் PCOS (இப்போது PMOS என்றும் அழைக்கப்படுகிறது) நிலையில் காணப்படலாம். வேறு காரணங்களும் இருக்கலாம். கேள்வித்தாள் நோயறிதல் செய்யாது.", "limited_heading": "இந்தச் சரிபார்ப்பு என்ன சொல்ல முடியும்", "limited_body": "இந்தச் சிறிய விளக்கம் ஒரு குறிப்பிட்ட தொடர்பை உறுதிப்படுத்தாது. அறிகுறிகளுக்குப் பல காரணங்கள் இருக்கலாம்; இந்தச் சொல்-அடிப்படை முன்மாதிரி சூழலைத் தவறவிடலாம்.", "next_heading": "பரிந்துரைக்கப்படும் அடுத்த படிகள்", "appointment": "அறிகுறிகள் தொடர்ந்தால், அன்றாட வாழ்க்கையைப் பாதித்தால் அல்லது கவலை இருந்தால், முதன்மை மருத்துவர் அல்லது மகப்பேறு நிபுணரிடம் வழக்கமான சந்திப்பை ஏற்பாடு செய்யுங்கள். மாதவிடாய் மாற்றங்கள், அறிகுறிகளின் காலம் மற்றும் கேள்விகள் பற்றிய உங்கள் குறிப்புகளை எடுத்துச் செல்லுங்கள்.", "unclear": "சில பதில்கள் விடுபட்டுள்ளன அல்லது ‘தெரியவில்லை’ என்று குறிக்கப்பட்டுள்ளன. கீழே உள்ள சுருக்கம் அந்த நிச்சயமின்மையை வைத்திருக்கிறது.", "not_diagnosis": "NariCare AI கல்வித் தகவலை மட்டுமே வழங்குகிறது. இது நோயறிதல் செய்யாது; மருத்துவப் பராமரிப்புக்கு மாற்றாகாது.", "text": "உங்கள் விளக்கத்தைத் தட்டச்சு செய்யவும் அல்லது திருத்தவும்", "examples": "விரைவாகச் சேர்க்க", "continue": "தொடரவும்", "back": "பின்னால்", "clear": "அழிக்க", "confirm": "உறுதிப்படுத்தி வழிகாட்டலைப் பார்க்கவும்", "start_again": "மீண்டும் தொடங்கவும்", "try_again": "மீண்டும் முயற்சிக்கவும்", "not_sure": "தெரியவில்லை / பதிலளிக்க விருப்பமில்லை", "duration_options": ["ஒரு மாதத்திற்கும் குறைவு", "1–3 மாதங்கள்", "3 மாதங்களுக்கு மேல்", "மாறுபடும்", "தெரியவில்லை"], "period_options": ["சீரானது", "ஒழுங்கற்றது / அடிக்கடி தாமதம்", "3+ மாதங்களாக மாதவிடாய் இல்லை", "மாறுபடும்", "தெரியவில்லை / பதிலளிக்க விருப்பமில்லை"], "check_sources": "ஆதாரங்கள்", "pcos_name_note": "பலர் PCOS என்ற பெயரை அறிந்திருக்கிறார்கள். NHS மற்றும் Monash இப்போது PMOS எனப் பயன்படுத்துகின்றன; சில வழிகாட்டிகள் இன்னும் PCOS எனக் குறிப்பிடுகின்றன.", "demo_note": "கீழே உள்ள எடுத்துக்காட்டுகள் அனைத்தும் கற்பனையானவை; இதே சரிபார்ப்பு மற்றும் வழிகாட்டல் படிகளைப் பயன்படுத்துகின்றன. கன்னட எடுத்துக்காட்டு தட்டச்சு செய்யப்பட்டது, போலியான குரல் உரைமாற்றம் அல்ல.",
    },
    "te": {
        "home": "హోమ్", "understand": "లక్షణాలను అర్థం చేసుకోండి", "learn": "PCOS గురించి", "tagline": "మీ లక్షణాలను అర్థం చేసుకుని తదుపరి అడుగు తెలుసుకోండి.", "language": "ప్రాధాన్య భాష", "start": "నా లక్షణాలను అర్థం చేసుకోండి", "learn_button": "PCOS గురించి తెలుసుకోండి", "describe": "మీ మాటల్లో లక్షణాలను వివరించండి", "voice_note": "వాయిస్ సౌకర్యం మీ బ్రౌజర్ మరియు అందుబాటులో ఉన్న భాషా వాయిస్‌పై ఆధారపడి ఉంటుంది. టైప్ చేసే ఎంపిక ఎప్పుడూ ఉంటుంది.", "voice_prompt": "ఇంకేమైనా జోడించాలనుకుంటున్నారా?", "confirm_summary": "ఈ పరిమిత పద-సరిపోలిక సారాంశాన్ని పరిశీలించాను. భాషల కలయిక, స్థానిక పదాలు లేదా వాయిస్ గుర్తింపు పొరపాట్ల వల్ల అర్థం తప్పవచ్చు.", "menstrual": "మీ పీరియడ్స్ గురించి ఎలా చెబుతారు?", "duration": "ఈ లక్షణాలను ఎంతకాలంగా గమనిస్తున్నారు?", "urgent_q": "ఇప్పుడు వీటిలో ఏమైనా ఉన్నాయా: తీవ్రమైన లేదా పెరుగుతున్న దిగువ కడుపు/పొత్తికడుపు నొప్పి, మూర్ఛ లేదా తలతిరగడం, అధిక యోని రక్తస్రావం, శ్వాస ఇబ్బంది లేదా అకస్మాత్తు గందరగోళం?", "skin_q": "మొటిమలు లేదా జిడ్డు చర్మం గమనించారా?", "hair_q": "ముఖం/శరీరంపై అసాధారణ వెంట్రుకలు లేదా తలపై జుట్టు పలుచబడటం గమనించారా?", "yes": "అవును", "no": "కాదు", "unsure": "నిశ్చయంగా తెలియదు", "step_a": "1 · వివరించండి", "step_b": "2 · ప్రశ్నలు", "step_c": "3 · నిర్ధారించండి", "step_d": "4 · మార్గదర్శకం", "empty_summary": "ఈ పరిమిత వ్యవస్థకు సరిపడే లక్షణ పదాలు గుర్తించబడలేదు. కొనసాగవచ్చు, కానీ వివరణ సరిగ్గా అర్థం కాకపోయి ఉండవచ్చు.", "no_match": "ఈ చిన్న పదజాబితాలో సరిపోలిక దొరకలేదు. దాని అర్థం మీకు లక్షణాలు లేవని కాదు.", "results_heading": "మీ తదుపరి అడుగు మార్గదర్శకం", "summary_heading": "మీరు తెలిపినవి", "urgent_heading": "దయచేసి ఇప్పుడే అత్యవసర వైద్య సహాయం పొందండి", "urgent_body": "మీ సమాధానాల్లో ఒక హెచ్చరిక సంకేతం ఉండవచ్చు. స్థానిక అత్యవసర నంబర్‌ను సంప్రదించండి లేదా సమీప అత్యవసర విభాగానికి వెళ్లండి. తలతిరగడం లేదా తీవ్రమైన అస్వస్థత ఉంటే మీరే వాహనం నడపకండి.", "uncertain_heading": "ఆరోగ్య నిపుణుడితో త్వరగా స్పష్టత పొందండి", "uncertain_body": "హెచ్చరిక సంకేతం ఉందో లేదో మీకు నిశ్చయంగా తెలియదు. తీవ్రమైన/పెరుగుతున్న నొప్పి, మూర్ఛ, అధిక రక్తస్రావం, శ్వాస ఇబ్బంది లేదా అకస్మాత్తు గందరగోళం ఉండవచ్చని అనిపిస్తే ఇప్పుడే స్థానిక అత్యవసర వైద్య సహాయం పొందండి.", "possible_heading": "సాధ్యమైన సంబంధం; నిర్ధారణ కాదు", "possible_body": "క్రమం తప్పిన పీరియడ్స్‌తో పాటు మొటిమలు, జిడ్డు చర్మం, ముఖం/శరీరంపై అసాధారణ వెంట్రుకలు లేదా తలపై జుట్టు పలుచబడటం PCOS (ఇప్పుడు PMOS అని కూడా పిలుస్తారు)లో కనిపించవచ్చు. ఇతర కారణాలూ ఉండవచ్చు. ప్రశ్నావళి నిర్ధారణ చేయలేదు.", "limited_heading": "ఈ పరిశీలన ఏమి చెప్పగలదు", "limited_body": "ఈ చిన్న వివరణతో నిర్దిష్ట సంబంధాన్ని నిర్ణయించలేం. అనేక లక్షణాలకు అనేక కారణాలు ఉండవచ్చు; ఈ పద-ఆధారిత నమూనా సందర్భాన్ని మిస్ కావచ్చు.", "next_heading": "సూచించిన తదుపరి చర్యలు", "appointment": "లక్షణాలు కొనసాగితే, రోజువారీ జీవితాన్ని ప్రభావితం చేస్తే లేదా ఆందోళన కలిగిస్తే, ప్రాథమిక వైద్యుడు లేదా స్త్రీరోగ నిపుణుడితో సాధారణ అపాయింట్‌మెంట్ తీసుకోండి. పీరియడ్స్ మార్పులు, లక్షణాల సమయం, మీ ప్రశ్నల గురించి మీరే రాసుకున్న నోట్స్ తీసుకెళ్లండి.", "unclear": "కొన్ని సమాధానాలు లేవు లేదా ‘నిశ్చయంగా తెలియదు’ అని గుర్తించబడ్డాయి. దిగువ సారాంశంలో ఆ అనిశ్చితి ఉంచబడింది.", "not_diagnosis": "NariCare AI విద్యాపరమైన సమాచారాన్ని మాత్రమే అందిస్తుంది. ఇది నిర్ధారణ చేయదు; వైద్య సంరక్షణకు ప్రత్యామ్నాయం కాదు.", "text": "మీ వివరణను టైప్ చేయండి లేదా సవరించండి", "examples": "త్వరగా జోడించండి", "continue": "కొనసాగించండి", "back": "వెనుకకు", "clear": "తొలగించండి", "confirm": "నిర్ధారించి మార్గదర్శకం చూడండి", "start_again": "మళ్లీ ప్రారంభించండి", "try_again": "మళ్లీ ప్రయత్నించండి", "not_sure": "నిశ్చయంగా తెలియదు / సమాధానం ఇవ్వకూడదనుకుంటున్నాను", "duration_options": ["ఒక నెలలోపు", "1–3 నెలలు", "3 నెలలకు మించి", "మారుతూ ఉంటుంది", "నిశ్చయంగా తెలియదు"], "period_options": ["క్రమంగా వస్తాయి", "క్రమం తప్పుతాయి / ఆలస్యం", "3+ నెలలుగా పీరియడ్స్ లేవు", "మారుతూ ఉంటుంది", "నిశ్చయంగా తెలియదు / సమాధానం ఇవ్వకూడదు"], "check_sources": "మూలాలు", "pcos_name_note": "చాలామందికి PCOS అనే పేరు తెలుసు. NHS మరియు Monash ఇప్పుడు PMOS అని ఉపయోగిస్తున్నాయి; కొన్ని మార్గదర్శకాలు ఇంకా PCOS అని వాడుతున్నాయి.", "demo_note": "క్రింది నమూనాలన్నీ కల్పితమైనవి; ఇదే సమీక్ష మరియు మార్గదర్శక ప్రక్రియను ఉపయోగిస్తాయి. కన్నడ నమూనా టైప్ చేసింది; ఇది నకిలీ వాయిస్ ట్రాన్స్‌క్రిప్ట్ కాదు.",
    },
}


def tx(key: str) -> Any:
    return I18N[st.session_state.lang].get(key, I18N["en"].get(key, key))


def choice_data(key: str) -> tuple[list[str], list[str]]:
    """Return stable internal values and labels in the selected language."""
    lang = st.session_state.lang
    choose_labels = {"en": "Choose an answer…", "kn": "ಒಂದು ಉತ್ತರ ಆಯ್ಕೆಮಾಡಿ…", "hi": "एक उत्तर चुनें…", "ta": "ஒரு பதிலைத் தேர்ந்தெடுக்கவும்…", "te": "ఒక సమాధానాన్ని ఎంచుకోండి…"}
    choose = choose_labels[lang]
    if key == "menstrual":
        return ["choose", "regular", "irregular", "absent", "varies", "unsure"], [choose] + tx("period_options")
    if key == "duration":
        return ["choose", "under_month", "one_to_three", "over_three", "varies", "unsure"], [choose] + tx("duration_options")
    yes_no_unsure = ["choose", "no", "yes", "unsure"]
    return yes_no_unsure, [choose, tx("no"), tx("yes"), tx("unsure")]


def answer_label(key: str, value: str | None) -> str:
    if not value or value == "choose":
        return "—"
    values, labels = choice_data(key)
    return labels[values.index(value)] if value in values else str(value)


def phrase_is_present(text: str, phrase: str, lang: str) -> bool:
    """Match a known phrase and ignore a nearby, common negation when clear."""
    content, phrase = text.casefold(), phrase.casefold()
    start = 0
    while True:
        position = content.find(phrase, start)
        if position < 0:
            return False
        prefix = content[max(0, position - 70):position]
        clause = re.split(r"[.!?;،。！？]+", prefix)[-1]
        negated = False
        for marker in NEGATIONS[lang]:
            matches = list(re.finditer(r"(?<!\w)" + re.escape(marker) + r"(?!\w)", clause))
            if matches:
                marker_position = matches[-1].start()
                after_marker = clause[marker_position + len(marker):]
                intervening_words = re.findall(r"[^\W_]+", after_marker, flags=re.UNICODE)
                if len(intervening_words) <= 3:
                    negated = True
                    break
        if not negated:
            return True
        start = position + len(phrase)


def set_page(page: str) -> None:
    st.session_state.page = page


def detect_symptoms(text: str, lang: str) -> set[str]:
    return {
        category
        for category, phrases in LEXICON[lang].items()
        if category in SYMPTOM_LABELS[lang] and any(phrase_is_present(text, phrase, lang) for phrase in phrases)
    }


def urgent_from_text(text: str, lang: str) -> bool:
    vocab = LEXICON[lang]
    has_pain = any(phrase_is_present(text, phrase, lang) for phrase in vocab["pelvic_pain"])
    has_severe = any(phrase_is_present(text, phrase, lang) for phrase in vocab["severe"])
    has_faintness = any(phrase_is_present(text, phrase, lang) for phrase in vocab["faintness"])
    other_red_flags = any(
        phrase_is_present(text, phrase, lang)
        for key in ("heavy_bleeding", "breathing_difficulty", "confusion")
        for phrase in vocab[key]
    )
    return (has_pain and (has_severe or has_faintness)) or other_red_flags


def localized_demo_scenarios() -> list[dict[str, str]]:
    return [
        {"title": "1 · Irregular periods + acne", "lang": "en", "text": "My periods are irregular and I have acne."},
        {"title": "2 · ಕನ್ನಡ typed example", "lang": "kn", "text": "ನನ್ನ ಮಾಸಿಕ ಅನಿಯಮಿತವಾಗಿದೆ ಮತ್ತು ಮುಖದಲ್ಲಿ ಮೊಡವೆ ಇದೆ."},
        {"title": "3 · Severe pain + fainting", "lang": "en", "text": "I have severe pelvic pain and I feel faint."},
    ]


def new_symptom_entry(text: str) -> None:
    st.session_state.symptom_widget_counter = st.session_state.get("symptom_widget_counter", 0) + 1
    widget_key = f"symptom_entry_{st.session_state.symptom_widget_counter}"
    st.session_state.symptom_widget_key = widget_key
    st.session_state[widget_key] = text
    st.session_state.symptom_text = text


def start_demo(scenario: dict[str, str]) -> None:
    st.session_state.lang = scenario["lang"]
    st.session_state.pending_language_label = next(name for name, item in LANGUAGES.items() if item["key"] == scenario["lang"])
    new_symptom_entry(scenario["text"])
    st.session_state.menstrual = "choose"
    st.session_state.duration = "choose"
    st.session_state.urgent_answer = "choose"
    st.session_state.acne_answer = "choose"
    st.session_state.oily_skin_answer = "choose"
    st.session_state.facial_hair_answer = "choose"
    st.session_state.hair_thinning_answer = "choose"
    st.session_state.summary_confirmed = False
    st.session_state.demo_mode = True
    st.session_state.page = "journey"
    st.session_state.step = 1


def reset_journey() -> None:
    new_symptom_entry("")
    st.session_state.menstrual = "choose"
    st.session_state.duration = "choose"
    st.session_state.urgent_answer = "choose"
    st.session_state.acne_answer = "choose"
    st.session_state.oily_skin_answer = "choose"
    st.session_state.facial_hair_answer = "choose"
    st.session_state.hair_thinning_answer = "choose"
    st.session_state.summary_confirmed = False
    st.session_state.demo_mode = False
    st.session_state.step = 1
    st.session_state.page = "journey"


for key, initial in {
    "page": "home", "step": 1, "lang": "en", "language_label": "English",
    "symptom_text": "", "symptom_widget_counter": 0, "symptom_widget_key": "symptom_entry_0", "menstrual": "choose", "duration": "choose", "urgent_answer": "choose",
    "acne_answer": "choose", "oily_skin_answer": "choose", "facial_hair_answer": "choose", "hair_thinning_answer": "choose", "summary_confirmed": False,
    "demo_mode": False, "voice_transcript": "", "voice_event_id": "",
}.items():
    st.session_state.setdefault(key, initial)

if st.session_state.get("pending_language_label"):
    # Apply demo selection before the language widget is created on this run.
    st.session_state.language_label = st.session_state.pop("pending_language_label")

# Normalize answers from an earlier app version or interrupted session.
for answer_key in ("menstrual", "duration", "urgent_answer", "acne_answer", "oily_skin_answer", "facial_hair_answer", "hair_thinning_answer"):
    if st.session_state.get(answer_key) is None:
        st.session_state[answer_key] = "choose"
if st.session_state.symptom_widget_key not in st.session_state:
    st.session_state[st.session_state.symptom_widget_key] = st.session_state.symptom_text

# If the user changes the language selector, use that for matching and all
# localized copy. The user always chooses; there is no automatic language claim.
if st.session_state.lang not in LANG_BY_KEY:
    st.session_state.lang = "en"

st.markdown(
    """
    <style>
    :root { --nc-bg:#F8F7FC; --nc-primary:#6750A4; --nc-secondary:#DDF3EC; --nc-text:#243047; --nc-muted:#566277; --nc-urgent:#B42318; }
    html, body, [data-testid="stAppViewContainer"] { background:var(--nc-bg); color:var(--nc-text); }
    [data-testid="stHeader"] { background:rgba(248,247,252,.93); }
    [data-testid="stAppViewContainer"] { overflow-x:hidden; }
    .block-container { max-width:1150px; padding-top:1.5rem; padding-bottom:3.5rem; }
    h1,h2,h3 { color:var(--nc-text); letter-spacing:-.02em; }
    h1 { font-size:clamp(2rem,4.5vw,3.65rem)!important; line-height:1.08!important; }
    p, li { color:var(--nc-text); line-height:1.65; }
    [data-testid="stBaseButton-secondary"] { min-height:48px; border-radius:14px; border-color:#d8d4e7; color:var(--nc-text); font-weight:650; }
    [data-testid="stBaseButton-primary"] { min-height:50px; border-radius:14px; background:var(--nc-primary); border-color:var(--nc-primary); color:#fff!important; font-weight:700; }
    [data-testid="stBaseButton-primary"] p { color:#fff!important; }
    button:focus-visible, a:focus-visible, input:focus-visible, textarea:focus-visible, [tabindex]:focus-visible { outline:3px solid #B8A8F0!important; outline-offset:3px!important; }
    textarea, input, [data-baseweb="select"] { border-radius:12px!important; }
    [data-testid="stAlert"] { border-radius:14px; }
    .brand { color:var(--nc-primary); font-size:1rem; font-weight:800; letter-spacing:.015em; padding:.15rem 0 .7rem; }
    .hero { background:linear-gradient(120deg,#EEEAF8 0%,#E6F5EF 100%); border:1px solid #e6e0f0; border-radius:28px; padding:clamp(1.3rem,4vw,3.2rem); margin:.4rem 0 1rem; }
    .eyebrow { color:var(--nc-primary); font-size:.82rem; font-weight:800; text-transform:uppercase; letter-spacing:.09em; }
    .lead { max-width:680px; font-size:1.12rem; color:#435066; }
    .soft-card { background:#fff; border:1px solid #e9e6f0; border-radius:20px; padding:1.25rem 1.35rem; height:100%; box-shadow:0 5px 20px rgba(36,48,71,.035); }
    .notice { background:#fff; border-left:4px solid var(--nc-primary); padding:1rem 1.1rem; border-radius:8px 14px 14px 8px; margin:.7rem 0; }
    .muted { color:var(--nc-muted); font-size:.93rem; }
    .step-pill { display:inline-block; border:1px solid #ded9ec; background:#fff; color:#525c72; border-radius:999px; padding:.42rem .8rem; margin:0 .3rem .55rem 0; font-size:.88rem; }
    .step-active { border-color:var(--nc-primary); color:var(--nc-primary); font-weight:750; background:#f1edfb; }
    .urgent-card { background:#fff3f1; border:1px solid #f0c9c3; border-left:5px solid var(--nc-urgent); border-radius:14px; padding:1rem 1.2rem; }
    .footer-note { margin-top:2rem; border-top:1px solid #e3dfec; padding-top:1rem; color:var(--nc-muted); font-size:.88rem; }
    @media(max-width:700px) { .block-container { padding-left:1rem; padding-right:1rem; } .hero { border-radius:21px; } }
    </style>
    """,
    unsafe_allow_html=True,
)


voice_component = components.declare_component(
    "naricare_voice", path=str(__import__("pathlib").Path(__file__).parent / "voice_component")
)


def render_voice_controls(voice_text: str = "", show_recorder: bool = False) -> Any:
    language = LANG_BY_KEY[st.session_state.lang]
    return voice_component(
        lang=language["locale"],
        language_name=language["short"],
        voice_text=voice_text,
        show_recorder=show_recorder,
        reset_token=st.session_state.voice_event_id,
        key="voice_controls",
        default=None,
    )


def render_nav() -> None:
    brand_col, nav_col = st.columns([1.1, 2.9], vertical_alignment="center")
    with brand_col:
        st.markdown('<div class="brand">🌿 NariCare AI</div>', unsafe_allow_html=True)
    with nav_col:
        navs = st.columns(3)
        for col, target, label in zip(navs, ("home", "journey", "education"), (tx("home"), tx("understand"), tx("learn"))):
            with col:
                if st.button(label, key=f"nav_{target}", use_container_width=True, type="secondary"):
                    set_page(target)


def render_language_selector() -> None:
    label_to_lang = list(LANGUAGES.keys())
    selected = st.selectbox(
        tx("language"),
        label_to_lang,
        key="language_label",
    )
    selected_key = LANGUAGES[selected]["key"]
    if selected_key != st.session_state.lang:
        st.session_state.lang = selected_key
        st.session_state.summary_confirmed = False
        st.rerun()


def render_footer() -> None:
    st.markdown(
        '<div class="footer-note">🔒 Privacy: this prototype keeps answers in the current app session and does not write them to a database. Avoid entering names or contact details. A public deployment host may process technical data. &nbsp; · &nbsp; Educational information only; not a diagnosis or replacement for professional care.</div>',
        unsafe_allow_html=True,
    )


def render_home() -> None:
    left, right = st.columns([1.65, 1], vertical_alignment="center")
    with left:
        st.markdown(
            f'<section class="hero"><div class="eyebrow">Women’s health, one step at a time</div><h1>NariCare AI</h1><p class="lead">{tx("tagline")}</p><p>Share what you’re experiencing, review a simple symptom summary, and see a safe next step. Your answers are not used to diagnose a condition.</p></section>',
            unsafe_allow_html=True,
        )
        buttons = st.columns([1.2, 1])
        with buttons[0]:
            if st.button(tx("start"), type="primary", use_container_width=True, key="home_start"):
                st.session_state.page = "journey"
                st.session_state.step = 1
        with buttons[1]:
            if st.button(tx("learn_button"), use_container_width=True, key="home_learn"):
                st.session_state.page = "education"
    with right:
        st.markdown('<div class="soft-card"><h3>🪷 A calmer way to get oriented</h3><p>Tell us what you have noticed, answer a few optional follow-up questions, then check the summary before viewing educational guidance.</p><p><strong>Private by design</strong><br><span class="muted">No account, database, or long-term health tracking.</span></p><p><strong>Medical safety first</strong><br><span class="muted">Possible urgent warning signs are checked before routine symptom information.</span></p></div>', unsafe_allow_html=True)
    st.markdown("### Choose your language")
    render_language_selector()
    st.markdown('<div class="notice"><strong>Privacy</strong> · Do not enter names, phone numbers, or other identifying details. Answers stay in this app session and are not written to a database.</div>', unsafe_allow_html=True)
    st.warning(tx("not_diagnosis"), icon="⚕️")

    st.markdown("## Try a fictional demonstration")
    st.caption(tx("demo_note"))
    scenario_cols = st.columns(3)
    scenarios = localized_demo_scenarios()
    subtitles = ["English typed description", "ಕನ್ನಡ typed description · voice is not faked", "Immediate warning-sign example"]
    for index, (column, scenario, subtitle) in enumerate(zip(scenario_cols, scenarios, subtitles)):
        with column:
            st.markdown(f'<div class="soft-card"><strong>{scenario["title"]}</strong><p class="muted">{subtitle}</p><span class="muted">Fictional scenario</span></div>', unsafe_allow_html=True)
            if st.button("Use this fictional scenario", key=f"demo_{index}", use_container_width=True):
                start_demo(scenario)


def render_progress() -> None:
    steps = [tx("step_a"), tx("step_b"), tx("step_c"), tx("step_d")]
    active = st.session_state.step
    st.markdown("".join(f'<span class="step-pill {"step-active" if i == active else ""}">{label}</span>' for i, label in enumerate(steps, start=1)), unsafe_allow_html=True)
    st.progress(active / 4)


def append_symptom(category: str) -> None:
    lang = st.session_state.lang
    examples = {
        "en": {"irregular_periods": "My periods are irregular.", "acne": "I have acne.", "facial_body_hair": "I have unusual facial or body hair.", "hair_thinning": "I have noticed scalp hair thinning."},
        "kn": {"irregular_periods": "ನನ್ನ ಮಾಸಿಕ ಅನಿಯಮಿತವಾಗಿದೆ.", "acne": "ನನಗೆ ಮೊಡವೆ ಇದೆ.", "facial_body_hair": "ಮುಖದಲ್ಲಿ ಅಸಾಮಾನ್ಯ ಕೂದಲು ಇದೆ.", "hair_thinning": "ತಲೆಯ ಕೂದಲು ಉದುರುತ್ತಿದೆ."},
        "hi": {"irregular_periods": "मेरे पीरियड्स अनियमित हैं।", "acne": "मुझे मुंहासे हैं।", "facial_body_hair": "चेहरे पर असामान्य बाल हैं।", "hair_thinning": "सिर के बाल झड़ रहे हैं।"},
        "ta": {"irregular_periods": "எனக்கு ஒழுங்கற்ற மாதவிடாய் உள்ளது.", "acne": "எனக்கு முகப்பரு உள்ளது.", "facial_body_hair": "முகத்தில் வழக்கத்திற்கு மாறான முடி உள்ளது.", "hair_thinning": "தலையில் முடி உதிர்கிறது."},
        "te": {"irregular_periods": "నాకు క్రమం తప్పిన పీరియడ్స్ ఉన్నాయి.", "acne": "నాకు మొటిమలు ఉన్నాయి.", "facial_body_hair": "ముఖంపై అసాధారణ వెంట్రుకలు ఉన్నాయి.", "hair_thinning": "తలపై జుట్టు రాలుతోంది."},
    }
    phrase = examples[lang][category]
    current = st.session_state.get(st.session_state.symptom_widget_key, "").strip()
    value = f"{current} {phrase}".strip()
    st.session_state[st.session_state.symptom_widget_key] = value
    st.session_state.symptom_text = value
    st.session_state.summary_confirmed = False


def sync_symptom_entry() -> None:
    st.session_state.symptom_text = st.session_state.get(st.session_state.symptom_widget_key, "")


def clear_symptom_text() -> None:
    st.session_state.symptom_text = ""
    st.session_state[st.session_state.symptom_widget_key] = ""
    st.session_state.summary_confirmed = False


def render_symptoms_step() -> None:
    st.header(tx("describe"))
    st.caption("Your language choice is manual. This prototype matches a small, visible vocabulary; it does not translate arbitrary text or detect language automatically.")
    st.info(tx("voice_note"), icon="🎙️")
    voice_privacy = {
        "en": "Your browser's speech service may send audio to its provider over the internet. Choose typed input if you prefer not to share audio.",
        "kn": "ನಿಮ್ಮ ಬ್ರೌಸರ್‌ನ ಧ್ವನಿ ಸೇವೆಯು ಆಡಿಯೊವನ್ನು ಇಂಟರ್ನೆಟ್ ಮೂಲಕ ತನ್ನ ಪೂರೈಕೆದಾರರಿಗೆ ಕಳುಹಿಸಬಹುದು. ಆಡಿಯೊ ಹಂಚಲು ಇಷ್ಟವಿಲ್ಲದಿದ್ದರೆ ಟೈಪ್ ಮಾಡಿ.",
        "hi": "आपके ब्राउज़र की वाक् सेवा ऑडियो को इंटरनेट पर अपने प्रदाता तक भेज सकती है। ऑडियो साझा नहीं करना चाहते तो टाइप करें।",
        "ta": "உங்கள் உலாவியின் குரல் சேவை ஒலியை இணையம் வழியாக அதன் வழங்குநருக்கு அனுப்பலாம். ஒலியைப் பகிர விரும்பவில்லை என்றால் தட்டச்சு செய்யுங்கள்.",
        "te": "మీ బ్రౌజర్ వాయిస్ సేవ ఆడియోను ఇంటర్నెట్ ద్వారా దాని ప్రొవైడర్‌కు పంపవచ్చు. ఆడియో పంచుకోవడం ఇష్టం లేకపోతే టైప్ చేయండి.",
    }
    st.caption(voice_privacy[st.session_state.lang])
    component_value = render_voice_controls(show_recorder=True)
    if isinstance(component_value, dict) and component_value.get("type") == "transcript":
        transcript = str(component_value.get("text", ""))
        event_id = str(component_value.get("eventId", ""))
        if transcript.strip() and event_id != st.session_state.voice_event_id:
            previous = st.session_state.get(st.session_state.symptom_widget_key, "").strip()
            value = f"{previous} {transcript}".strip()
            st.session_state[st.session_state.symptom_widget_key] = value
            st.session_state.symptom_text = value
            st.session_state.voice_transcript = transcript
            st.session_state.voice_event_id = event_id
            st.session_state.summary_confirmed = False
            st.rerun()
    st.markdown(f"**{tx('examples')}**")
    chips = st.columns(4)
    for col, category, label in zip(chips, ("irregular_periods", "acne", "facial_body_hair", "hair_thinning"), ("Irregular periods", "Acne", "Facial/body hair", "Scalp hair thinning")):
        with col:
            if st.button(label, key=f"chip_{category}", use_container_width=True):
                append_symptom(category)
                st.rerun()
    st.text_area(tx("text"), key=st.session_state.symptom_widget_key, on_change=sync_symptom_entry, height=165, max_chars=1500, placeholder="Example: My periods are often late and I have acne.")
    actions = st.columns([1, 1, 2])
    with actions[0]:
        st.button(tx("clear"), key="clear_text", use_container_width=True, on_click=clear_symptom_text)
    with actions[2]:
        if st.button(tx("continue"), type="primary", key="to_questions", use_container_width=True):
            st.session_state.symptom_text = st.session_state.get(st.session_state.symptom_widget_key, "")
            if not st.session_state.symptom_text.strip():
                st.error("Please add a description or use a symptom example before continuing.")
            else:
                st.session_state.step = 2
                st.rerun()


def render_followup_step() -> None:
    st.header(tx("step_b").split("·")[-1].strip())
    st.caption(f"Choose ‘{tx('unsure')}’ if you do not know. You can change answers before guidance.")
    period_values, period_labels = choice_data("menstrual")
    duration_values, duration_labels = choice_data("duration")
    yes_no_values, yes_no_labels = choice_data("urgent_answer")
    def restore(key: str, choices: list[str]) -> int:
        val = st.session_state.get(key)
        return choices.index(val) if val in choices else 0
    st.selectbox(tx("menstrual"), period_values, format_func=lambda value: period_labels[period_values.index(value)], index=restore("menstrual", period_values), key="menstrual")
    st.selectbox(tx("duration"), duration_values, format_func=lambda value: duration_labels[duration_values.index(value)], index=restore("duration", duration_values), key="duration")
    st.radio(tx("urgent_q"), yes_no_values, format_func=lambda value: yes_no_labels[yes_no_values.index(value)], index=restore("urgent_answer", yes_no_values), key="urgent_answer", horizontal=True)
    questions = [
        ("acne_answer", "acne"), ("oily_skin_answer", "oily_skin"),
        ("facial_hair_answer", "facial_body_hair"), ("hair_thinning_answer", "hair_thinning"),
    ]
    for row in (questions[:2], questions[2:]):
        left, right = st.columns(2)
        for column, (state_key, label_key) in zip((left, right), row):
            with column:
                st.radio(FOLLOWUP_LABELS[st.session_state.lang][label_key], yes_no_values, format_func=lambda value: yes_no_labels[yes_no_values.index(value)], index=restore(state_key, yes_no_values), key=state_key, horizontal=True)
    left, right = st.columns([1, 2])
    with left:
        if st.button(tx("back"), key="questions_back", use_container_width=True):
            st.session_state.step = 1
            st.rerun()
    with right:
        if st.button(tx("continue"), type="primary", key="questions_continue", use_container_width=True):
            st.session_state.step = 3
            st.session_state.summary_confirmed = False
            st.rerun()


def build_summary() -> tuple[list[str], bool, bool, list[str]]:
    lang = st.session_state.lang
    reported = detect_symptoms(st.session_state.symptom_text, lang)
    if st.session_state.get("menstrual") in ("irregular", "absent"):
        reported.add("irregular_periods")
    if st.session_state.get("acne_answer") == "yes":
        reported.add("acne")
    if st.session_state.get("oily_skin_answer") == "yes":
        reported.add("oily_skin")
    if st.session_state.get("facial_hair_answer") == "yes":
        reported.add("facial_body_hair")
    if st.session_state.get("hair_thinning_answer") == "yes":
        reported.add("hair_thinning")
    categories = ["irregular_periods", "acne", "oily_skin", "facial_body_hair", "hair_thinning", "pelvic_pain"]
    summary = [SYMPTOM_LABELS[lang][key] for key in categories if key in reported]
    answer_keys = ("menstrual", "duration", "urgent_answer", "acne_answer", "oily_skin_answer", "facial_hair_answer", "hair_thinning_answer")
    answers_incomplete = any(st.session_state.get(key) == "choose" for key in answer_keys)
    urgent_answer = st.session_state.get("urgent_answer")
    urgent_yes = urgent_answer == "yes"
    urgent_unsure = urgent_answer == "unsure"
    urgent = urgent_yes or urgent_from_text(st.session_state.symptom_text, lang)
    return summary, urgent, urgent_unsure, [tx("unclear")] if answers_incomplete else []


def render_confirm_step() -> None:
    st.header("Review before guidance")
    st.markdown("**Your original description**")
    st.code(st.session_state.symptom_text, language=None)
    summary, _, _, _ = build_summary()
    st.markdown(f"**{tx('summary_heading')} · limited keyword matches**")
    if summary:
        st.write(" · ".join(summary))
    else:
        st.warning(tx("empty_summary"))
    if not detect_symptoms(st.session_state.symptom_text, st.session_state.lang):
        st.caption(tx("no_match"))
    with st.expander("Follow-up answers", expanded=True):
        st.write(f"{tx('menstrual')} {answer_label('menstrual', st.session_state.get('menstrual'))}")
        st.write(f"{tx('duration')} {answer_label('duration', st.session_state.get('duration'))}")
        for state_key, label_key in (("acne_answer", "acne"), ("oily_skin_answer", "oily_skin"), ("facial_hair_answer", "facial_body_hair"), ("hair_thinning_answer", "hair_thinning")):
            st.write(f"{FOLLOWUP_LABELS[st.session_state.lang][label_key]} {answer_label(state_key, st.session_state.get(state_key))}")
        st.write(f"{tx('urgent_q')} {answer_label('urgent_answer', st.session_state.get('urgent_answer'))}")
    st.checkbox(tx("confirm_summary"), key="summary_confirmed")
    left, right = st.columns([1, 2])
    with left:
        if st.button(tx("back"), key="confirm_back", use_container_width=True):
            st.session_state.step = 2
            st.rerun()
    with right:
        if st.button(tx("confirm"), key="analyze", type="primary", use_container_width=True):
            if not st.session_state.summary_confirmed:
                st.error("Please review and confirm the summary or go back to edit your answers.")
            else:
                st.session_state.step = 4
                st.rerun()


def render_reference_links() -> None:
    st.markdown("#### " + tx("check_sources"))
    st.markdown(
        "- [NHS: PMOS (formerly PCOS)](https://www.nhs.uk/conditions/polyendocrine-metabolic-ovarian-syndrome-pmos/)\n"
        "- [NHS: missed or late periods and possible causes](https://www.nhs.uk/symptoms/missed-or-late-periods/)\n"
        "- [Monash University: international PMOS / PCOS guideline and resources](https://www.monash.edu/medicine/mchri/pcos/guideline)\n"
        "- [NHS: pelvic pain and urgent warning signs](https://www.nhs.uk/symptoms/pelvic-pain/)"
    )



def render_results() -> None:
    lang = st.session_state.lang

    st.header(tx("results_heading"))

    # Send symptom information to the Flask backend
    try:
        response = requests.post(
            "http://127.0.0.1:5000/api/analyze",
            json={
                "symptoms": st.session_state.symptom_text,
                "language": lang,
                "answers": {
                    "menstrual": st.session_state.get("menstrual", "choose"),
                    "urgent_answer": st.session_state.get(
                        "urgent_answer", "choose"
                    ),
                    "acne_answer": st.session_state.get(
                        "acne_answer", "choose"
                    ),
                    "oily_skin_answer": st.session_state.get(
                        "oily_skin_answer", "choose"
                    ),
                    "facial_hair_answer": st.session_state.get(
                        "facial_hair_answer", "choose"
                    ),
                    "hair_thinning_answer": st.session_state.get(
                        "hair_thinning_answer", "choose"
                    ),
                },
            },
            timeout=10,
        )

        response.raise_for_status()
        result = response.json()

    except requests.exceptions.Timeout:
        st.error(
            "The backend took too long to respond. "
            "Please try again."
        )
        return

    except requests.exceptions.ConnectionError:
        st.error(
            "Cannot connect to the backend. "
            "Make sure server.py is running on port 5000."
        )
        return

    except requests.exceptions.RequestException as error:
        st.error(f"Backend request failed: {error}")
        return

    except ValueError:
        st.error("The backend returned an invalid JSON response.")
        return

    # Display the backend response
    st.subheader("Your symptom summary")

    summary = result.get("summary", [])
    if isinstance(summary, list):
        if summary:
            for item in summary:
                st.markdown(f"- {item}")
        else:
            st.info("No matching symptoms were identified.")
    elif summary:
        st.write(summary)
    else:
        st.info("No matching symptoms were identified.")

    # Display urgency information
    urgent_warning = result.get("urgent_warning")

    if urgent_warning:
        st.warning(
            f"Urgent care guidance: {urgent_warning}",
            icon="⚠️",
        )

    # Display care level
    care_level = result.get("care_level")
    if care_level:
        st.subheader("Recommended level of care")
        st.write(care_level)

    # Display educational information
    pcos_information = result.get("pcos_information")
    if pcos_information:
        st.subheader("PCOS information")
        st.write(pcos_information)

    # Display next steps
    next_steps = result.get("next_steps")
    if next_steps:
        st.subheader("Suggested next steps")

        if isinstance(next_steps, list):
            for step in next_steps:
                st.markdown(f"- {step}")
        else:
            st.write(next_steps)

    # Display the non-diagnostic disclaimer
    disclaimer = result.get("disclaimer")
    if disclaimer:
        st.warning(disclaimer, icon="⚕️")
    else:
        st.warning(
            "This tool does not diagnose PCOS or any other condition. "
            "Consult a qualified healthcare professional for assessment.",
            icon="⚕️",
        )

    # Reference links already defined in your app.py
    render_reference_links()

    # Navigation buttons
    left, right = st.columns(2)

    with left:
        if st.button(
            tx("back"),
            key="results_edit",
            use_container_width=True,
        ):
            st.session_state.step = 3
            st.rerun()

    with right:
        if st.button(
            tx("start_again"),
            key="results_restart",
            type="primary",
            use_container_width=True,
        ):
            reset_journey()
            st.rerun()


def localized_spoken_response(urgent: bool, uncertain: bool, summary: list[str]) -> str:
    if urgent:
        return f"{tx('urgent_heading')}. {tx('urgent_body')}"
    if uncertain:
        return f"{tx('uncertain_heading')}. {tx('uncertain_body')}"
    if summary:
        summary_phrase = ", ".join(summary)
        if st.session_state.lang == "en":
            return f"{tx('summary_heading')}: {summary_phrase}. {tx('limited_body')} {tx('appointment')}"
    return f"{tx('results_heading')}. {tx('limited_body')} {tx('appointment')}"


def render_journey() -> None:
    render_language_selector()
    render_progress()
    if st.session_state.step == 1:
        render_symptoms_step()
    elif st.session_state.step == 2:
        render_followup_step()
    elif st.session_state.step == 3:
        render_confirm_step()
    else:
        render_results()


def render_education() -> None:
    st.header("PCOS / PMOS: an overview")
    st.caption(tx("pcos_name_note"))
    st.markdown("### What is it?")
    st.write("PCOS—now called polyendocrine metabolic ovarian syndrome (PMOS) by the NHS and Monash—is a hormone-related condition that can affect menstrual cycles, hair growth, skin, fertility, and wellbeing. It can look different from person to person.")
    st.markdown("### Common symptoms and associated features")
    st.write("People may notice irregular or absent periods, acne or oily skin, increased facial or body hair, scalp hair thinning, or difficulty getting pregnant. Some people have few obvious symptoms. These features can also occur for reasons other than PCOS/PMOS.")
    st.markdown("### What contributes to it?")
    st.write("The exact cause is not known. NHS information notes that hormones such as insulin and testosterone may be involved, and family history can be relevant. This is not the same as saying a particular factor caused one person's symptoms.")
    st.markdown("### Do ovarian cysts have to be present?")
    st.write("No. The name can be misleading: ovarian appearance is only one possible part of a professional assessment, and it is not required in every case. A scan by itself also cannot establish the full clinical picture.")
    st.markdown("### How do health professionals evaluate it?")
    st.write("A clinician considers symptom and menstrual history, examines the overall picture, and may use blood tests or imaging when appropriate. They may also consider other explanations for similar symptoms. The right assessment depends on age and individual circumstances.")
    st.markdown("### When to seek care")
    st.write("Consider a routine appointment if you think you may have PCOS/PMOS, symptoms continue, or they affect everyday life. Seek urgent help for severe or worsening pelvic pain, faintness, heavy bleeding, difficulty breathing, or sudden confusion.")
    st.warning(tx("not_diagnosis"), icon="⚕️")
    render_reference_links()
    if st.button(tx("start"), type="primary", key="education_start"):
        st.session_state.page = "journey"
        st.session_state.step = 1


render_nav()
if st.session_state.page == "home":
    render_home()
elif st.session_state.page == "education":
    render_education()
else:
    render_journey()
render_footer()

