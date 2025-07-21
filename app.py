from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from dotenv import load_dotenv
from openai import OpenAI
import os
import base64



load_dotenv()
app = Flask(__name__)
CORS(app)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/apps/ai-gen", methods=["GET"])
def generate_image():
    prompt = request.args.get("prompt", "AI T-shirt design")
    try:
        print(f"🔍 Generating image for prompt: {prompt}")
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            n=1,
            size="1024x1024",
            response_format="b64_json"
        )
        image_data = response.data[0].b64_json
        filename = f"static/ai_{os.urandom(4).hex()}.png"

        # Ensure static directory exists
        static_dir = os.path.join(app.root_path, "static")
        os.makedirs(static_dir, exist_ok=True)

        full_path = os.path.join(app.root_path, filename)
        with open(full_path, "wb") as f:
            f.write(base64.b64decode(image_data))

        print(f"✅ Image saved at {full_path}")
        return jsonify({ "images": ["/" + filename] })
    except Exception as e:
        print("❌ ERROR:", e)
        return jsonify({ "error": str(e) }), 500
    
from werkzeug.utils import secure_filename

@app.route("/upload-image", methods=["POST"])
def upload_image():
    if "image" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["image"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    filename = secure_filename(file.filename)
    unique_name = f"static/user_{os.urandom(4).hex()}_{filename}"
    file_path = os.path.join(app.root_path, unique_name)
    file.save(file_path)

    print(f"📸 User image uploaded: {file_path}")
    return jsonify({ "image_url": "/" + unique_name })


if __name__ == "__main__":
    app.run(debug=True)
