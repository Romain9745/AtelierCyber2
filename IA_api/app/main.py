from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
import transformers
import uvicorn
import shap
import numpy as np

app = FastAPI()

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

tokenizer = transformers.AutoTokenizer.from_pretrained("ealvaradob/bert-finetuned-phishing", use_fast=True)
model = transformers.AutoModelForSequenceClassification.from_pretrained("ealvaradob/bert-finetuned-phishing")

pred = transformers.pipeline(
    "text-classification",
    model=model,
    tokenizer=tokenizer,
    device=0,
    top_k=1,
)

explainer = shap.Explainer(pred)



@app.post("/predict")
async def predict(text: str):
    # Prédiction du modèle
    result = pred(text)
    print(result)
    label = result[0][0]['label']
    score = result[0][0]['score']
    try:
        # Générer l'explication SHAP
        print("Générer l'explication SHAP...")
        print("Texte:", text)
        shap_values = explainer([text], fixed_context=1, batch_size=2)  # SHAP peut gérer un seul texte directement
        print("SHAP values:", shap_values)


        # Créer une explication simple et compréhensible pour les utilisateurs lambda
        explanation_details = {
            "key_words": [],
            "simple_explanation": ""
        }


        predicted_class_idx = 0 if label == "phising" else 1  # Adaptez ceci selon vos classes

        # Extraction des mots les plus influents dans la décision
        feature_importance = []
        for i, val_row in enumerate(shap_values.values[0, :]):
            # Utiliser la valeur de la classe prédite
            val = val_row[predicted_class_idx]
            if val != 0:
                feature_importance.append((i, abs(val), val))

        feature_importance.sort(key=lambda x: x[1], reverse=True)

        # Récupérer les 5 mots les plus importants
        top_n = 5
        for idx, importance, original_value in feature_importance[:top_n]:
            if idx < len(shap_values.data[0]):
                word = shap_values.data[0][idx]
                influence = "favorable" if original_value > 0 else "défavorable"
        
                explanation_details["key_words"].append({
                    "word": word,
                    "influence": influence,
                    "importance": round(float(importance), 3)
                })

        # Créer une explication en langage courant
        positive_words = [f"« {f['word']} »" for f in explanation_details["key_words"] if f["influence"] == "favorable"]
        negative_words = [f"« {f['word']} »" for f in explanation_details["key_words"] if f["influence"] == "défavorable"]

        explanation_text = f"Votre texte a été classé comme « {label} » avec un niveau de confiance de {int(score*100)}%.\n\n"

        if positive_words:
            if len(positive_words) == 1:
                explanation_text += f"Le mot {positive_words[0]} a particulièrement orienté cette décision."
            else:
                explanation_text += f"Les mots {', '.join(positive_words[:-1])} et {positive_words[-1]} ont particulièrement orienté cette décision."
    
        if positive_words and negative_words:
            explanation_text += "\n\n"
    
        if negative_words:
            if len(negative_words) == 1:
                explanation_text += f"En revanche, le mot {negative_words[0]} a joué contre cette classification."
            else:
                explanation_text += f"En revanche, les mots {', '.join(negative_words[:-1])} et {negative_words[-1]} ont joué contre cette classification."

        explanation_details["simple_explanation"] = explanation_text

        explanation = {
            "label": label,
            "score": score,
            "explanation": explanation_details
        }
    except Exception as e:
        explanation = {
            "label": label,
            "score": score,
            "explanation": str(e)
        }
    return explanation