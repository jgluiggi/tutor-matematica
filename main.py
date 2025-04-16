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

def format_latex_feedback(feedback):
    # Adicionar "$" antes de \frac e após o segundo "}"
    formatted_feedback = feedback.replace("[", "").replace("]", "")  # Substitui colchetes por cifrões

    # Ajustar \frac para sempre estar no formato $ \frac{}{} $
    import re
    formatted_feedback = re.sub(r"\frac{(.*?)}{(.*?)}", r"$\frac{\1}{\2}$", formatted_feedback)

    return formatted_feedback

def generate_feedback(user_answer, correct_answer, problem):
    if check_answer(user_answer, correct_answer):
        return "Correto! Parabéns!"
    else:
        fallback = "Tente novamente. Dica: Para somar frações, encontre o denominador comum."
        try:
            student_message = f"Eu tentei resolver '{problem}' e respondi '{user_answer}', explique meu erro e tente me direcionar no caminho certo sem revelar a resposta."
            messages=[
              {"role": "system", "content": "Você é um professor de matemática. Explique o erro de forma curta e clara, em pt-BR, como se estivesse ensinando frações para um estudante. Não retorne seu fluxo de pensamento, apenas a resolução passo a passo. Use LaTeX para as equações/resolução coloque os valores dentro de $$ ao invés de []."},
              {"role": "user", "content": student_message}
            ],
            print(messages)
            payload = {
                "model": LLM_MODEL,
                "messages": messages,
                "max_tokens": 1000,
                "temperature": 0.6
            }
            response = requests.post(LLM_URL, json=payload)
            response.raise_for_status()
            result = response.json()
            feedback = result.get("choices", {})[0].get("text", "").strip().split('</think>')[-1].strip()
            feedback = format_latex_feedback(feedback)  # Formatar o feedback para renderização LaTeX
            return feedback if feedback else fallback
        except:
            return fallback

st.title("Tutor de Matemática Básica")
if not data:
    st.write("Nenhum dado disponível. Verifique o arquivo 'data/dev-data.json'.")
else:
    options = ["Usar sistema implementado", "Fornecer equação"]
    option = st.selectbox("Escolha a opção:", options)

    if option == "Usar sistema implementado":
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
            question_index = st.selectbox("Escolha a questão:", [q['problem'] for q in questions], format_func=lambda x: x, index=0, key="question_selector")
            question = questions[questions.index(next(q for q in questions if q['problem'] == question_index))]

            st.write("**Questão**:")
            st.write(question["problem"])

            user_answer = st.text_input("Sua resposta:", key=f"answer_{question['problem']}")

            if st.button("Verificar"):
                if user_answer:
                    feedback = generate_feedback(user_answer, question["answer"], question["problem"])
                    if "Correto" in feedback:
                        st.success("Acertou")
                    else:
                        st.error("Tente novamente.")  # Mensagem curta em vermelho
                        st.write(feedback)  # Explicação detalhada em preto
                else:
                    st.warning("Por favor, insira uma resposta.")
    elif option == "Fornecer equação":
        equation = st.text_input("Insira a equação:")
        user_answer = st.text_input("Sua resposta:")

        if st.button("Verificar"):
            if user_answer and equation:
                feedback = generate_feedback(user_answer, equation, "Equação fornecida pelo usuário")
                if "Correto" in feedback:
                    st.success("Acertou")
                else:
                    st.error("Tente novamente.")  # Mensagem curta em vermelho
                    st.write(feedback)  # Explicação detalhada em preto
            else:
                st.warning("Por favor, insira uma equação e uma resposta.")
