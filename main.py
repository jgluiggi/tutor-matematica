import json
from sympy import sympify

# Carregar dataset
with open("data/dev-data.json") as f:
    data = json.load(f)

def show_topic(topic):
    for t in data:
        if t["topic"] == topic:
            print("Explicação:", t["explanation"])
            print("Exemplo:", t["example"])
            return t["questions"]
    return []

def check_answer(user_answer, correct_answer):
    try:
        user = sympify(user_answer)
        correct = sympify(correct_answer)
        return user == correct
    except:
        return False

# Fluxo básico
topic = "soma_frações"
questions = show_topic(topic)
current_level = "easy"
for q in questions:
    if q["level"] == current_level:
        print("Questão:", q["problem"])
        user_answer = input("Sua resposta: ")
        if check_answer(user_answer, q["answer"]):
            print("Correto!")
            current_level = "medium" if current_level == "easy" else "hard"
        else:
            print("Tente novamente. Dica: Verifique o denominador.")
