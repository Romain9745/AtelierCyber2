from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
import transformers
import uvicorn
import shap
import numpy as np
import torch
import json
from pydantic import BaseModel
from transformers_interpret import SequenceClassificationExplainer

app = FastAPI()

    
model = transformers.AutoModelForSequenceClassification.from_pretrained("ealvaradob/bert-finetuned-phishing")
tokenizer = transformers.AutoTokenizer.from_pretrained("ealvaradob/bert-finetuned-phishing")

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)
model.eval()

    # Initialize the SequenceClassificationExplainer
cls_explainer = SequenceClassificationExplainer(model, tokenizer)

    # Create the text classification pipeline
classifier = transformers.pipeline(
    "text-classification",
    model=model,
    tokenizer=tokenizer,
    device=0 if torch.cuda.is_available() else -1,  # Use GPU if available
  #if torch.cuda.is_available() else -1,  # Use GPU if available
    top_k=1,
    batch_size=1  # Reduce prediction overhead
)

    # Initialize SHAP explainer
pmodel = shap.models.TransformersPipeline(classifier)
explainer2 = shap.Explainer(pmodel, classifier.tokenizer)


# Initialize the FastAPI app



class PredictionResponse(BaseModel):
    class_: str
    explanation: str


API_KEY = "your-secure-api-key"
API_KEY_NAME = "X-API-KEY"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)

def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Unauthorized")
    return api_key

@app.get("/protected-route")
def protected_route(api_key: str = Depends(verify_api_key)):
    return {"message": "You have access!"}

    
@app.post("/predict")
async def predict(text: str):
    try:
        # Prédiction du modèle
        result = classifier(text)
        print(result)
        label = result[0][0]['label']
        score = result[0][0]['score']
        explainer = cls_explainer(text, internal_batch_size=1, n_steps=30)
        print(explainer)

        


        explanation = {
            "label": label,
            "score": score,
        }
    except Exception as e:
        explanation = {
            "label": label,
            "score": score,
            "explanation": str(e)
        }
    return explanation



@app.post("/predict-shap")
async def predict_with_shap(text: str):
    try:
        # Prédiction rapide
        result = classifier(text)[0][0]
        label, score = result["label"], result["score"]

        # Génération de l'explication SHAP accélérée (réduction des samples)
        shap_values = explainer2([text])

        # Extraction des mots influents
        predicted_class_idx = 0 if label == "phishing" else 1
        feature_importance = [
            (i, abs(val_row[predicted_class_idx]), val_row[predicted_class_idx])
            for i, val_row in enumerate(shap_values.values[0, :])
            if val_row[predicted_class_idx] != 0
        ]
        feature_importance.sort(key=lambda x: x[1], reverse=True)

        # Récupérer les 5 mots les plus influents
        top_n = 5
        explanation_details = {
            "key_words": [
                {
                    "word": shap_values.data[0][idx],
                    "influence": "favorable" if original_value > 0 else "défavorable",
                    "importance": round(float(importance), 3)
                }
                for idx, importance, original_value in feature_importance[:top_n]
            ]
        }

        # Génération d'une explication en langage naturel
        positive_words = [f"« {f['word']} »" for f in explanation_details["key_words"] if f["influence"] == "favorable"]
        negative_words = [f"« {f['word']} »" for f in explanation_details["key_words"] if f["influence"] == "défavorable"]

        explanation_text = f"Votre texte a été classé comme « {label} » avec un niveau de confiance de {int(score * 100)}%."

        if positive_words:
            explanation_text += f" Les mots {', '.join(positive_words)} ont influencé cette décision."

        if negative_words:
            explanation_text += f" En revanche, les mots {', '.join(negative_words)} ont joué contre cette classification."

        explanation_details["simple_explanation"] = explanation_text

        return {"label": label, "score": round(score, 3), "explanation": explanation_details}

    except Exception as e:
        return {"error": str(e)}

# 📌 Lancement du serveur optimisé
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)