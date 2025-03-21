from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
import transformers
import uvicorn
import shap
import numpy as np
import re
import json
import google.generativeai as genai
from pydantic import BaseModel
from config import google_api_key

class PredictionResponse(BaseModel):
    class_: str
    explanation: str

def model_to_json(model_instance):
    """
    Converts a Pydantic model instance to a JSON string.
    Args:
        model_instance (YourModel): An instance of your Pydantic model.
    Returns:
        str: A JSON string representation of the model.
    """
    return model_instance.model_dump_json()

def extract_json_from_string(text_with_markers: str) -> PredictionResponse:
    """
    Extracts JSON from a string that may contain ```json markers.
    """
    # 1. Remove ```json blocks and surrounding whitespace:

    json_string = re.sub(r"^\s*```json\s*", "", text_with_markers)  # Remove at beginning
    json_string = re.sub(r"\s*```\s*$", "", json_string)  # Remove at the end
    json_string = json_string.strip()  # Remove leading/trailing whitespace

    # 2. Basic validation: ensure curly braces are present

    if not (json_string.startswith("{") and json_string.endswith("}")):
        print(f"Error: String does not appear to be JSON. String: {json_string}")  # Log issue
        return PredictionResponse(class_="error", explanation="Could not find JSON")

    # 3. Attempt to load the JSON:
    try:
        data = json.loads(json_string)
        return PredictionResponse(**data)  # Create object and return
    except json.JSONDecodeError as e:
        print(f"JSONDecodeError: {e}.  String: {json_string}")
        return PredictionResponse(
            class_="error",
            explanation=f"Failed to decode JSON. Error: {e}",
        )  # Error response


app = FastAPI()

API_KEY = "your-secure-api-key"
API_KEY_NAME = "X-API-KEY"
api_key_header = APIKeyHeader(name=google_api_key, auto_error=True)

def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Unauthorized")
    return api_key

@app.get("/protected-route")
def protected_route(api_key: str = Depends(verify_api_key)):
    return {"message": "You have access!"}

genai.configure(api_key=GOOGLE_API_KEY)
tokenizer = transformers.AutoTokenizer.from_pretrained("ealvaradob/bert-finetuned-phishing", use_fast=True)
modele = transformers.AutoModelForSequenceClassification.from_pretrained("ealvaradob/bert-finetuned-phishing")
model = genai.GenerativeModel('gemini-2.0-flash')

classifier = transformers.pipeline(
    "text-classification",
    tokenizer=tokenizer,
    model=modele,
    top_k=1,
)

pmodel = shap.models.TransformersPipeline(classifier, rescale_to_logits=True)


explainer2 = shap.Explainer(pmodel, classifier.tokenizer)
explainer = shap.Explainer(classifier)

@app.post("/predictwithgemini", response_model=PredictionResponse)
async def predict(text: str) -> PredictionResponse:
    json_model = model_to_json(PredictionResponse(class_="phishing", explanation="This is a phishing attempt."))
    prompt = f"""
    Tu es un expert en sécurité informatique spécialisé dans la détection de phishing. Ton rôle est d'analyser des emails et de déterminer s'il s'agit de tentatives de phishing ou non.

    Pour chaque email analysé, tu dois fournir une réponse sous la forme : {json_model}

    La réponse doit contenir les deux clés suivantes :

    *   `"class"` : Une chaîne de caractères qui peut prendre deux valeurs : `"phishing"` ou `"no_phishing"`.
    *   `"explanation"` : Une chaîne de caractères expliquant clairement et de manière concise, pour un utilisateur non technique, pourquoi l'email a été classifié de cette manière. Cette explication doit mettre en évidence les indices spécifiques présents dans l'email qui ont mené à cette classification (erreurs d'orthographe, demandes urgentes, liens suspects, etc.). Si class est `"phishing"`, ajoute une recommandation simple à l'utilisateur (ex: "Ne cliquez sur aucun lien").

    **Voici l'email à analyser :**

    {text}

    
    """
    response = model.generate_content(prompt)
    
    response_text = response.text  # Extract the generated text (JSON string)
    if not response_text:
        print("Gemini returned an empty response.")
        return PredictionResponse(class_="error", explanation="Gemini returned an empty response.")

    try:
        data = extract_json_from_string(response_text)  # Parse the JSON string into a dictionary
        return data  # Return the PredictionResponse Object

    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}, Response Text: {response_text}")  # Log the problematic response
        return PredictionResponse(class_="error", explanation=f"Failed to parse Gemini's JSON response: {e}, Raw response text: '{response_text}'")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return PredictionResponse(class_="error", explanation="An unexpected error occurred while processing the response.")
    
@app.post("/predict")
async def predict(text: str):
    # Prédiction du modèle
    result = classifier(text)
    print(result)
    label = result[0][0]['label']
    score = result[0][0]['score']
    try:
        # Générer l'explication SHAP
        print("Générer l'explication SHAP...")
        print("Texte:", text)

        # Générer l'explication SHAP
        shap_values = explainer2([text])
        #shap_values = explainer(tokenizer(text, return_tensors="pt")["input_ids"])
        #input_ids = tokenizer(text, return_tensors="pt")["input_ids"]
        #shap_values = explainer(input_ids)
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