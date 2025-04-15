import json
import os
import streamlit as st
import requests
from sympy import sympify
from dotenv import load_dotenv

load_dotenv()

LLM_URL = os.getenv("LLM_URL", "http://localhost:8000/v1/completions")
LLM_MODEL = os.getenv("LLM_MODEL", "mistral")

try:
    with open('data/dev-data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
except FileNotFoundError:
    st.error("Erro: Arquivo 'data/dev-data.json' não encontrado.")
    data = []
except json.JSONDecodeError:
    st.error("Erro: Formato inválido no arquivo JSON.")
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
        try:
            prompt = (
                f"Você é um professor paciente no Brasil. O aluno tentou resolver '{problem}' e respondeu '{user_answer}'. "
                f"A resposta correta é '{correct_answer}'. Explique o erro de forma curta e clara, em português brasileiro, "
                f"como se estivesse ensinando frações para um estudante."
            )
            payload = {
                "model": LLM_MODEL,
                "prompt": prompt,
                "max_tokens": 80,
                "temperature": 0.7
            }
            response = requests.post(LLM_URL, json=payload)
            response.raise_for_status()
            result = response.json()
            feedback = result.get("choices", [{}])[0].get("text", "").strip()
            return feedback if feedback else fallback
        except:
            return fallback

st.title("Tutor de Matemática Básica")

if not data:
    st.write("Nenhum dado disponível. Verifique o arquivo 'data/dev-data.json'.")
else:
    topics = [t["topic"] for t in data]
    topic = st.selectbox("Escolha o tópico:", topics)
    topic_data = next(t for t in data if t["topic"] == topic)

    st.write("**Explicação**:")
    st.write(topic_data["explanation"])
    st.write("**Exemplo**:")
    for ex in topic_data["example"]:
        st.write(ex)

    levels = ["easy", "medium", "difficult"]
    level = st.selectbox("Nível de dificuldade:", levels)
    questions = [q for q in topic_data["questions"] if q["level"] == level]

    if questions:
        question = questions[0]
        st.write("**Questão**:")
        st.write(question["problem"])

        user_answer = st.text_input("Sua resposta:", key=f"answer_{question['problem']}")

        if st.button("Verificar"):
            if user_answer:
                feedback = generate_feedback(user_answer, question["answer"], question["problem"])
                if "Correto" in feedback:
                    st.success(feedback)
                else:
                    st.error(feedback)
            else:
                st.warning("Por favor, insira uma resposta.")
