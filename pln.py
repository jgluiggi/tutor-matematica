from transformers import pipeline

generator = pipeline('text-generation', model='pierreguillou/gpt2-small-portuguese')
prompt = "Explique como somar frações em português do Brasil, de forma curta e clara."
response = generator(prompt, max_length=50, truncation=True)[0]['generated_text']
print(response)
