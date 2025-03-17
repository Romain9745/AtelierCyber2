import shap
import numpy as np
import torch
import transformers
import scipy as sp

# Load tokenizer and model for phishing detection
tokenizer = transformers.AutoTokenizer.from_pretrained("ealvaradob/bert-finetuned-phishing", use_fast=True)
model = transformers.AutoModelForSequenceClassification.from_pretrained("ealvaradob/bert-finetuned-phishing")

pred = transformers.pipeline(
    "text-classification",
    model=model,
    tokenizer=tokenizer,
    device=0,
    return_all_scores=True,
)

explainer = shap.Explainer(pred)


# Example input: a single sentence
text = "This is a phishing attempt"

# Apply SHAP explainer to the single sentence
shap_values = explainer([text], fixed_context=1, batch_size=1)

# Output the SHAP values
print(shap_values)
