import json
from sympy import sympify
from transformers import pipeline, set_seed

set_seed(42)
try:
    generator = pipeline('text-generation', model='distilgpt2')
except Exception as e:
    print(f"Erro ao carregar o modelo: {e}")
    generator = None

try:
    with open('data/dev-data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
except FileNotFoundError:
    print("Erro: Arquivo 'data/dev-data.json' não encontrado.")
    data = []
except json.JSONDecodeError:
    print("Erro: Formato inválido no arquivo JSON.")
    data = []

def check_answer(user_answer, correct_answer):
    try:
        user = sympify(user_answer).simplify()
        correct = sympify(correct_answer).simplify()
        return user == correct
    except:
        return False

def generate_feedback(user_answer, correct_answer, problem):
    if check_answer(user_answer, correct_answer):
        return "Correto! Parabéns!"
    else:
        fallback = "Tente novamente. Dica: Para somar frações, encontre o denominador comum."
        if generator:
            try:
                prompt = (
                    f"Você é um professor paciente no Brasil. O aluno tentou resolver '{problem}' e respondeu '{user_answer}'. "
                    f"A resposta correta é '{correct_answer}'. Explique o erro de forma curta e clara, em português brasileiro, "
                    f"como se estivesse ensinando frações para um estudante."
                )
                response = generator(prompt, max_length=80, num_return_sequences=1, truncation=True)[0]['generated_text']
                response = response.replace(prompt, "").strip()
                if response:
                    return response
            except:
                pass
        else:
            return "wtf"
        return fallback

def show_topic(topic):
    for t in data:
        if t["topic"] == topic:
            print("Explicação:", t["explanation"])
            print("Exemplo:", t["example"])
            return t["questions"]
    print(f"Tópico '{topic}' não encontrado.")
    return []

print("Bem-vindo ao Tutor de Matemática Básica!")
if not data:
    print("Nenhum dado disponível. Verifique o arquivo 'data/dev-data.json'.")
else:
    topic = "soma_frações"
    questions = show_topic(topic)
    current_level = "easy"

    for q in questions:
        if q["level"] == current_level:
            print("\nQuestão:", q["problem"])
            user_answer = input("Sua resposta: ")
            feedback = generate_feedback(user_answer, q["answer"], q["problem"])
            print(feedback)
            if "Correto" in feedback:
                current_level = "medium"
