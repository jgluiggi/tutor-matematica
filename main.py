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
            prompt = (f"'Você é um professor de matemática. Seu objetivo é explicar de forma curta, clara e didática o erro do estudante ao resolver um problema de frações. Siga rigorosamente as instruções abaixo para garantir clareza, formatação correta e controle de fluxo. INSTRUÇÕES (siga todas exatamente): 1. NÃO retorne seu próprio raciocínio ou pensamentos. Apenas explique o erro do estudante e conduza o próximo passo da resolução, sem revelar a resposta final. 2. Use LaTeX entre delimitadores $$ para qualquer número, fração, operação ou equação. Exemplo: Correto → $$\\frac{2}{3} + \\frac{1}{3} = 1$$ Errado → [2/3] + [1/3] = 1 3. Estruture a resposta em etapas discretas numeradas. Após cada etapa, pare e peça confirmação ou diga ao estudante para continuar. 4. Ao explicar o erro do aluno, cite diretamente os valores de entrada: “Você tentou resolver '{problem}' e respondeu '{user_answer}'” 5. Após apontar o erro, direcione o aluno ao caminho correto com uma orientação clara e simples, sem dar a resposta. 6. NÃO assuma nada além do enunciado. Seja específico, direto e didático. 7. Use SEMPRE o valor real de '{problem}', com LaTeX. NUNCA use exemplos genéricos em vez disso. 8. Se a resposta do aluno estiver totalmente correta, diga apenas \"Correto\". Não adicione nenhuma explicação, saudação ou comentário. Apenas escreva: Correto. EXEMPLO DE SAÍDA: Você tentou resolver '{problem}' e respondeu '{user_answer}'. 1. Vamos verificar sua resposta. Reescrevendo a equação corretamente com formatação: $${problem}$$ Qual operação deve ser feita primeiro? EXEMPLOS DE FORMATAÇÃO EM LaTeX (4 OPERAÇÕES BÁSICAS): Adição: $$2 + 3 = 5$$ Subtração: $$7 - 4 = 3$$ Multiplicação: $$6 \\times 2 = 12$$ Divisão: $$8 \\div 4 = 2$$ INSERÇÃO DE VARIÁVEIS: Substitua '{problem}' pelo enunciado completo do problema. Substitua '{user_answer}' pela resposta exata dada pelo aluno. OBJETIVO FINAL: Ajudar o aluno a compreender o erro sem dar a resposta final e incentivá-lo a resolver com orientação clara, passo a passo.'"),
            print(prompt)
            payload = {
                "model": LLM_MODEL,
                "prompt": prompt,
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
                feedback = generate_feedback(user_answer,"", equation)
                if "Correto" in feedback:
                    st.success("Acertou")
                else:
                    st.error("Tente novamente.")  # Mensagem curta em vermelho
                    st.write(feedback)  # Explicação detalhada em preto
            else:
                st.warning("Por favor, insira uma equação e uma resposta.")
