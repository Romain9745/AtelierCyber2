from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
import transformers
import uvicorn
import torch
import re
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
    device=0 if torch.cuda.is_available() else -1,
    top_k=1,
    batch_size=1
)

Phi_tokenizer = transformers.AutoTokenizer.from_pretrained("unsloth/Phi-4-mini-instruct-unsloth-bnb-4bit")
Phi_model = transformers.AutoModelForCausalLM.from_pretrained("unsloth/Phi-4-mini-instruct-unsloth-bnb-4bit", device_map="auto")
Phi_model.to(device)
Phi_model.eval()

API_KEY = "your-secure-api-key"
API_KEY_NAME = "X-API-KEY"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)

def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Unauthorized")
    return api_key
    
@app.post("/predict")
async def predict(email_content: str, api_key: str = Depends(verify_api_key)):
    try:
        # Prédiction du modèle
        result = classifier(email_content)
        label = result[0][0]['label']
        score = result[0][0]['score']
        explanation = generate_explanation(email_content, label, score)


        return {
            "label": label,
            "score": score,
            "explanation": explanation
        }
    except Exception as e:
        explanation = {
            "label": label,
            "score": score,
            "explanation": str(e)
        }
    return explanation
    
def generate_explanation(text: str,label: str, score: str) -> str:
    """Convert token importance into a human-readable sentence."""
    token_explanation = cls_explainer(text, internal_batch_size=1, n_steps=30)
    sorted_explanation = sorted(token_explanation, key=lambda x: x[1], reverse=True)[:5]
    print(token_explanation)
    
    prompt = f"""
    The AI classified this email as "{label}" with {score} confidence.

    **Why was this classified as "{label}"?**  
    Using the most important words: {sorted_explanation} and the text: {text}, write a **concise, user-friendly explanation in 1 sentence**.
    """
    
    inputs = Phi_tokenizer(prompt, return_tensors="pt").to(device)
    outputs = Phi_model.generate(**inputs, max_new_tokens=100)

    generated_text = Phi_tokenizer.decode(outputs[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)
    cleaned_text = re.search(r'([A-Za-z].*?\.)', generated_text)
    if cleaned_text:
        result = cleaned_text.group(1).strip().replace("\"", "")
    else:
        result = text

    return result


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7080)