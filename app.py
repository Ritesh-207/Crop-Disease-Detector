from flask import Flask, request, jsonify, render_template
import tensorflow as tf
import numpy as np
from PIL import Image
import io
import os
import gdown

app = Flask(__name__)

# ─── Download Models from Google Drive ─────────────────
def download_models():
    os.makedirs("models", exist_ok=True)

    potato_id = "1mkZ-OWKmTrh1IS1Y9zN2FsS9lLsgYLJ9"
    tomato_id = "1fv8roQTDbrUB2XBY6QX49FA94Cwqurtf"

    if not os.path.exists("models/potato_model.h5"):
        print("Downloading potato model...")
        gdown.download(f"https://drive.google.com/uc?id={potato_id}",
                      "models/potato_model.h5", quiet=False)

    if not os.path.exists("models/tomato_model.h5"):
        print("Downloading tomato model...")
        gdown.download(f"https://drive.google.com/uc?id={tomato_id}",
                      "models/tomato_model.h5", quiet=False)

download_models()

# ─── Disease Info ──────────────────────────────────────
DISEASE_INFO = {
    "potato": {
        "Early_Blight": {
            "name": "Potato Early Blight",
            "treatment": "Apply fungicides containing Chlorothalonil or Mancozeb. Remove and destroy infected leaves immediately. Avoid overhead irrigation and water at the base of plants.",
            "prevention": "Use certified disease-free seed potatoes. Practice crop rotation every 2-3 years. Maintain proper plant spacing for good air circulation. Apply preventive fungicide sprays during humid conditions."
        },
        "Late_Blight": {
            "name": "Potato Late Blight",
            "treatment": "Apply fungicides containing Metalaxyl or Cymoxanil immediately. Remove and burn all infected plant parts. Do not compost infected material. Apply copper-based fungicides as a protective measure.",
            "prevention": "Plant resistant potato varieties. Avoid planting in poorly drained soils. Destroy volunteer potato plants. Monitor weather conditions and apply fungicides before infection during cool wet weather."
        },
        "Healthy": {
            "name": "Healthy Potato Plant",
            "treatment": "No treatment needed. Your potato plant appears healthy!",
            "prevention": "Continue regular monitoring. Maintain proper watering, fertilization, and crop rotation practices to keep plants healthy."
        }
    },
    "tomato": {
        "Bacterial_Spot": {
            "name": "Tomato Bacterial Spot",
            "treatment": "Apply copper-based bactericides such as Copper Hydroxide. Remove severely infected leaves. Avoid working with plants when wet to prevent spreading bacteria.",
            "prevention": "Use disease-free certified seeds. Avoid overhead irrigation. Practice crop rotation. Disinfect garden tools regularly. Plant resistant tomato varieties when available."
        },
        "Early_Blight": {
            "name": "Tomato Early Blight",
            "treatment": "Apply fungicides containing Chlorothalonil or Copper Octanoate. Remove infected lower leaves. Mulch around plants to prevent soil splash. Ensure adequate plant nutrition especially nitrogen.",
            "prevention": "Rotate crops annually. Stake plants for better air circulation. Avoid wetting foliage when watering. Remove plant debris at end of season."
        },
        "Late_Blight": {
            "name": "Tomato Late Blight",
            "treatment": "Apply fungicides with Metalaxyl or Mandipropamid immediately. Remove and destroy all infected plant parts. Do not compost infected material. Apply preventive copper sprays.",
            "prevention": "Plant resistant varieties. Avoid overhead watering. Ensure good drainage. Monitor plants closely during cool wet weather. Destroy infected plant debris promptly."
        },
        "Leaf_Mold": {
            "name": "Tomato Leaf Mold",
            "treatment": "Apply fungicides containing Chlorothalonil or Copper-based products. Improve greenhouse ventilation if growing indoors. Remove and destroy infected leaves.",
            "prevention": "Maintain low humidity below 85%. Ensure good air circulation between plants. Avoid overhead watering. Use resistant tomato varieties. Prune lower leaves to improve airflow."
        },
        "Mosaic_Virus": {
            "name": "Tomato Mosaic Virus",
            "treatment": "No cure exists for mosaic virus. Remove and destroy infected plants immediately to prevent spread. Wash hands and tools thoroughly after handling infected plants.",
            "prevention": "Control aphids and whiteflies which spread the virus. Use virus-free seeds and transplants. Avoid tobacco products near plants. Plant resistant varieties. Disinfect tools with bleach solution."
        },
        "Septoria_Leaf_Spot": {
            "name": "Tomato Septoria Leaf Spot",
            "treatment": "Apply fungicides containing Chlorothalonil, Mancozeb, or Copper-based products. Remove infected leaves immediately. Apply mulch to reduce soil splash onto lower leaves.",
            "prevention": "Rotate crops every 2-3 years. Stake plants for air circulation. Avoid overhead irrigation. Remove and destroy plant debris at season end. Use disease-resistant varieties."
        },
        "Spider_Mites": {
            "name": "Tomato Spider Mites",
            "treatment": "Apply miticides or insecticidal soap sprays. Use Neem oil as an organic treatment. Spray plants with strong water jets to dislodge mites. Introduce natural predators like ladybugs.",
            "prevention": "Maintain adequate soil moisture as mites thrive in dry conditions. Avoid excessive nitrogen fertilization. Monitor plants regularly especially during hot dry weather."
        },
        "Target_Spot": {
            "name": "Tomato Target Spot",
            "treatment": "Apply fungicides containing Chlorothalonil or Azoxystrobin. Remove infected plant material. Improve air circulation around plants. Avoid wetting foliage during watering.",
            "prevention": "Use crop rotation. Maintain proper plant spacing. Stake or cage plants for better airflow. Remove plant debris after harvest. Apply preventive fungicide during humid weather."
        },
        "Yellow_Leaf_Curl_Virus": {
            "name": "Tomato Yellow Leaf Curl Virus",
            "treatment": "No direct cure exists. Remove and destroy infected plants. Control whitefly populations using yellow sticky traps and insecticides. Apply Imidacloprid to control whitefly vectors.",
            "prevention": "Use virus-resistant tomato varieties. Install reflective mulches to repel whiteflies. Use insect-proof nets in early growth stages. Monitor and control whitefly populations regularly."
        },
        "Healthy": {
            "name": "Healthy Tomato Plant",
            "treatment": "No treatment needed. Your tomato plant appears healthy!",
            "prevention": "Continue regular monitoring. Maintain proper watering schedule, balanced fertilization, and good air circulation to keep plants healthy."
        }
    }
}

# ─── Weather Risk Info ─────────────────────────────────
WEATHER_RISK = {
    "potato": {
        "Early_Blight": {
            "temperature": "Thrives in warm temperatures between 24°C to 29°C. Risk increases significantly during hot days.",
            "humidity": "High humidity above 90% greatly increases spread. Wet leaves accelerate infection.",
            "rainfall": "Frequent rainfall and wet conditions promote rapid disease spread.",
            "dry_weather": "Disease slows down in dry conditions but does not stop completely.",
            "risk_tip": "Monitor plants closely during warm and humid weather. Apply fungicide before rainy periods."
        },
        "Late_Blight": {
            "temperature": "Favors cool temperatures between 10°C to 20°C. Most dangerous during cold nights.",
            "humidity": "Requires humidity above 90% to spread. Morning dew is enough to trigger infection.",
            "rainfall": "Rain spreads spores rapidly. A single rainy day can infect entire field.",
            "dry_weather": "Hot dry weather above 30°C stops disease spread temporarily.",
            "risk_tip": "Most dangerous in cool wet weather. Apply fungicide immediately before rain forecast."
        },
        "Healthy": {
            "temperature": "Current temperature conditions are suitable for healthy potato growth.",
            "humidity": "Maintain moderate humidity levels to keep plants healthy.",
            "rainfall": "Regular moderate rainfall is beneficial for healthy potato plants.",
            "dry_weather": "Ensure adequate irrigation during dry spells.",
            "risk_tip": "Continue regular monitoring to maintain plant health."
        }
    },
    "tomato": {
        "Bacterial_Spot": {
            "temperature": "Spreads rapidly in warm temperatures between 25°C to 30°C.",
            "humidity": "High humidity and wet foliage greatly increase bacterial spread.",
            "rainfall": "Rain and overhead irrigation splash bacteria from soil to leaves.",
            "dry_weather": "Dry conditions slow bacterial spread significantly.",
            "risk_tip": "Avoid overhead irrigation during warm humid weather."
        },
        "Early_Blight": {
            "temperature": "Favors warm temperatures between 24°C to 29°C with warm nights.",
            "humidity": "High humidity above 90% accelerates fungal growth on leaves.",
            "rainfall": "Wet weather promotes spore germination and rapid spread.",
            "dry_weather": "Dry weather reduces spread but existing infection continues.",
            "risk_tip": "Apply fungicide before expected rainfall during warm weather."
        },
        "Late_Blight": {
            "temperature": "Cool temperatures between 10°C to 20°C are most dangerous.",
            "humidity": "Needs high humidity above 90% to germinate and spread.",
            "rainfall": "Rain is the primary spreader of Late Blight spores.",
            "dry_weather": "Hot dry weather above 30°C stops new infections.",
            "risk_tip": "Spray fungicide immediately when cool wet weather is forecast."
        },
        "Leaf_Mold": {
            "temperature": "Grows best in moderate temperatures between 22°C to 25°C.",
            "humidity": "Thrives in very high humidity above 85%. Common in greenhouses.",
            "rainfall": "Wet conditions and poor ventilation promote rapid growth.",
            "dry_weather": "Good air circulation and dry conditions prevent spread.",
            "risk_tip": "Improve ventilation and reduce humidity to control Leaf Mold."
        },
        "Mosaic_Virus": {
            "temperature": "Virus spreads faster in warm temperatures as insects are more active.",
            "humidity": "Humidity does not directly affect virus but affects insect vectors.",
            "rainfall": "Rain can reduce insect activity temporarily slowing virus spread.",
            "dry_weather": "Dry hot weather increases aphid activity which spreads the virus.",
            "risk_tip": "Control aphid and whitefly populations especially during dry warm weather."
        },
        "Septoria_Leaf_Spot": {
            "temperature": "Favors moderate temperatures between 20°C to 25°C.",
            "humidity": "Wet humid conditions above 80% humidity accelerate spread.",
            "rainfall": "Rain splashes spores from soil and infected leaves to healthy ones.",
            "dry_weather": "Dry conditions significantly slow disease progression.",
            "risk_tip": "Mulch around plants to prevent soil splash during rainfall."
        },
        "Spider_Mites": {
            "temperature": "Thrives in hot dry temperatures above 27°C. Population explodes in heat.",
            "humidity": "Low humidity below 50% greatly favors mite reproduction.",
            "rainfall": "Rain naturally reduces mite populations by washing them off.",
            "dry_weather": "Dry hot weather is most dangerous for mite infestations.",
            "risk_tip": "Monitor plants closely during hot dry spells. Mist plants to increase humidity."
        },
        "Target_Spot": {
            "temperature": "Favors warm temperatures between 20°C to 30°C.",
            "humidity": "High humidity above 80% promotes fungal growth.",
            "rainfall": "Wet weather promotes spore spread between plants.",
            "dry_weather": "Dry conditions reduce new infections significantly.",
            "risk_tip": "Ensure good drainage and air circulation during wet seasons."
        },
        "Yellow_Leaf_Curl_Virus": {
            "temperature": "Whiteflies which spread virus are most active above 25°C.",
            "humidity": "Warm dry conditions increase whitefly populations.",
            "rainfall": "Heavy rain temporarily reduces whitefly activity.",
            "dry_weather": "Hot dry weather increases virus spread via whitefly vectors.",
            "risk_tip": "Use yellow sticky traps and monitor whitefly levels during hot weather."
        },
        "Healthy": {
            "temperature": "Current temperature is suitable for healthy tomato growth.",
            "humidity": "Maintain moderate humidity for optimal tomato health.",
            "rainfall": "Moderate regular rainfall supports healthy tomato growth.",
            "dry_weather": "Ensure consistent irrigation during dry periods.",
            "risk_tip": "Continue monitoring plants regularly to maintain health."
        }
    }
}

# ─── Class Labels ──────────────────────────────────────
POTATO_CLASSES = ['Early_Blight', 'Healthy', 'Late_Blight']

TOMATO_CLASSES = [
    'Bacterial_Spot', 'Early_Blight', 'Healthy',
    'Late_Blight', 'Leaf_Mold', 'Mosaic_Virus',
    'Septoria_Leaf_Spot', 'Spider_Mites',
    'Target_Spot', 'Yellow_Leaf_Curl_Virus'
]

# ─── Load Models ───────────────────────────────────────
potato_model = None
tomato_model = None

try:
    potato_model = tf.keras.models.load_model("models/potato_model.h5")
    print("Potato model loaded!")
except Exception as e:
    print(f"Potato model error: {e}")

try:
    tomato_model = tf.keras.models.load_model("models/tomato_model.h5")
    print("Tomato model loaded!")
except Exception as e:
    print(f"Tomato model error: {e}")

# ─── Helper ────────────────────────────────────────────
def preprocess_image(image_bytes):
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    img = img.resize((224, 224))
    img_array = np.array(img) / 255.0
    return np.expand_dims(img_array, axis=0)

# ─── Routes ────────────────────────────────────────────
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():
    try:
        crop = request.form.get("crop", "").lower()
        if crop not in ["potato", "tomato"]:
            return jsonify({"error": "Invalid crop. Choose potato or tomato."}), 400

        if "image" not in request.files:
            return jsonify({"error": "No image uploaded."}), 400

        img_array = preprocess_image(request.files["image"].read())

        if crop == "potato":
            if potato_model is None:
                return jsonify({"error": "Potato model not loaded."}), 500
            predictions = potato_model.predict(img_array)
            class_labels = POTATO_CLASSES
        else:
            if tomato_model is None:
                return jsonify({"error": "Tomato model not loaded."}), 500
            predictions = tomato_model.predict(img_array)
            class_labels = TOMATO_CLASSES

        predicted_class = class_labels[np.argmax(predictions[0])]
        info = DISEASE_INFO[crop][predicted_class]
        weather = WEATHER_RISK[crop][predicted_class]

        return jsonify({
            "disease":      info["name"],
            "treatment":    info["treatment"],
            "prevention":   info["prevention"],
            "weather": {
                "temperature": weather["temperature"],
                "humidity":    weather["humidity"],
                "rainfall":    weather["rainfall"],
                "dry_weather": weather["dry_weather"],
                "risk_tip":    weather["risk_tip"]
            }
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ─── Run ───────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
