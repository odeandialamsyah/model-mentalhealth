from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import joblib

from database.db import SessionLocal, engine
from database.models import PredictionHistory, Base
from utils.preprocessing import preprocess_text

# ===============================
# INIT
# ===============================
app = Flask(__name__)
CORS(app)

Base.metadata.create_all(bind=engine)

# ===============================
# LOAD MODEL
# ===============================
model = joblib.load("ml/model.joblib")
vectorizer = joblib.load("ml/tfidf_vectorizer.joblib")
label_encoder = joblib.load("ml/label_encoder.joblib")

# ===============================
# ROUTES
# ===============================
# @app.route("/")
# def index():
#     return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():
    data = request.json
    text = data.get("text", "")
    user_id = data.get("user_id")  # dari JWT / frontend

    cleaned = preprocess_text(text)
    X_vec = vectorizer.transform([cleaned])

    pred_id = int(model.predict(X_vec)[0])
    pred_label = label_encoder.inverse_transform([pred_id])[0]

    probabilities = {}
    if hasattr(model, "predict_proba"):
        probs = model.predict_proba(X_vec)[0]
        probabilities = {
            label: float(probs[i])
            for i, label in enumerate(label_encoder.classes_)
        }

    db = SessionLocal()
    record = PredictionHistory(
        user_id=user_id,
        input_text=text,
        predicted_label=pred_label,
        predicted_id=pred_id,
        probability_json=probabilities
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    db.close()

    return jsonify({
        "record_id": record.id,
        "predicted_label": pred_label,
        "predicted_id": pred_id,
        "probabilities": probabilities
    })


@app.route("/history", methods=["GET"])
def history():
    db = SessionLocal()

    user_id = request.args.get("user_id", type=int)
    if not user_id:
        return jsonify({"error": "user_id is required"}), 400

    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 10))
    offset = (page - 1) * limit

    query = (
        db.query(PredictionHistory)
        .filter(PredictionHistory.user_id == user_id)
    )

    total = query.count()

    rows = (
        query
        .order_by(PredictionHistory.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    db.close()

    return jsonify({
        "user_id": user_id,
        "page": page,
        "limit": limit,
        "total": total,
        "items": [
            {
                "id": r.id,
                "input_text": r.input_text,
                "predicted_label": r.predicted_label,
                "predicted_id": r.predicted_id,
                "probabilities": r.probability_json,
                "created_at": r.created_at.isoformat()
            }
            for r in rows
        ]
    })


# ===============================
if __name__ == "__main__":
    app.run(debug=True)
