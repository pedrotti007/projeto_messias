
from flask import Flask, request, jsonify, render_template, redirect, url_for
import google.generativeai as genai
import os
from dotenv import load_dotenv


load_dotenv()

app = Flask(__name__)


GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
gemini_model = None

# Verificar se o Gemini está funcionando

if not GEMINI_API_KEY:
    print("ERRO CRÍTICO: A variável de ambiente GEMINI_API_KEY não está configurada.")
else:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        generation_config = {
            "temperature": 0.7,
            "top_p": 1,
            "top_k": 1,
            "max_output_tokens": 2048,
        }
        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        ]
        gemini_model = genai.GenerativeModel(
            model_name="gemini-1.5-flash-latest",
            generation_config=generation_config,
            safety_settings=safety_settings
        )
        print("Modelo Gemini inicializado com sucesso.")
    except Exception as e:
        print(f"Erro ao inicializar o modelo Gemini: {e}")


#aqui vamos definir a parte dos templates

@app.route('/')
def index():
    return render_template('index.html')

#template onde está o gemini, informando se esta fora do ar, ou se está funcionando, ela também relata o erro que aconteceu.

@app.route('/tirar_duvidas', methods=['GET', 'POST'])
def tirar_duvidas_route():
    if request.method == 'POST':
        if not gemini_model:
            return jsonify({
                               "error": "O serviço de IA não está disponível no momento. Verifique a configuração da API Key e os logs do servidor."}), 503

#definindo a mesma, aqui é caso esteja tudo certo, pronta para funcionar. Iremos dizer a sequencia que precisa ser seguida.

        try:
            data = request.get_json()
            if not data or 'pergunta' not in data:
                return jsonify({"error": "Nenhuma pergunta fornecida."}), 400

            pergunta_usuario = data['pergunta'].strip()
            if not pergunta_usuario:
                return jsonify({"error": "A pergunta não pode estar vazia."}), 400

            prompt_parts = [
                "Contexto: Você é um assistente virtual do site 'APF - Aprenda Python Facilmente'. Responda perguntas sobre Python, programação e tópicos relacionados de forma clara e útil para iniciantes.",
                f"Pergunta do usuário: {pergunta_usuario}",
                "Resposta:"
            ]

#aqui nos vamos dar sentido e dizer pra ela oque fazer quando nao conseguir responder. Ou problemas de response.

            response = gemini_model.generate_content(prompt_parts)

            resposta_texto = ""
            if response.parts:
                for part in response.parts:
                    resposta_texto += part.text
            elif hasattr(response, 'text') and response.text:
                resposta_texto = response.text
            else:
                if response.prompt_feedback and response.prompt_feedback.block_reason:
                    resposta_texto = f"Não foi possível gerar uma resposta devido a: {response.prompt_feedback.block_reason_message or response.prompt_feedback.block_reason}"
                else:
                    resposta_texto = "Não foi possível obter uma resposta do modelo Gemini (resposta vazia ou bloqueada sem motivo claro)."
                print(f"Resposta completa do Gemini (ou feedback): {response}")

            return jsonify({"resposta": resposta_texto})

        except Exception as e:
            print(f"Erro ao processar pergunta com Gemini: {e}")
            return jsonify({"error": "Ocorreu um erro interno ao processar sua pergunta."}), 500


    return render_template('tirar_duvidas.html')


# as @app.route('/....') sao para poder integrar a navegacao entre as paginas. Quando for executada "..._page" ele retorne o arquivo.
# Ex: def equipe_page():
#         return render_template('equipe.html')

@app.route('/equipe')
def equipe_page():
    return render_template('equipe.html')

@app.route('/python_fundamentos')
def python_fundamentos_page():
    return render_template('python_fundamentos.html')

termos_dicionario = [
    {"termo": "Variável", "definicao": "Um espaço na memória do computador destinado a um dado que pode ser modificado durante a execução de um programa."},
    {"termo": "Função", "definicao": "Um bloco de código que realiza uma tarefa específica e pode ser chamado várias vezes."},
    {"termo": "Loop (Laço)", "definicao": "Uma estrutura de controle que repete um bloco de código várias vezes enquanto uma condição for verdadeira ou por um número definido de vezes."}
]

#outra funcionalidade é a integracao da página e também aparecer com algo escrito que quisermos puxando de uma variável.

@app.route('/dicionario')
def dicionario_page():
    return render_template('dicionario.html', termos=termos_dicionario)

@app.route('/dicionario_formulario', methods=['GET', 'POST'])
def dicionario_formulario_page():
    if request.method == 'POST':
        novo_termo = request.form.get('termo')
        nova_definicao = request.form.get('definicao')

        if novo_termo and nova_definicao:
            termos_dicionario.append({'termo': novo_termo, 'definicao': nova_definicao})
            return redirect(url_for('dicionario_page'))
        else:
            return render_template('dicionario_formulario.html', error="Ambos os campos são obrigatórios.")

    return render_template('dicionario_formulario.html')

@app.route('/editar_termo/<int:index>', methods=['GET', 'POST'])
def editar_termo_page(index):
    if not (0 <= index < len(termos_dicionario)):
        return redirect(url_for('dicionario_page'))

    termo_para_editar = termos_dicionario[index]

    if request.method == 'POST':
        termo_atualizado = request.form.get('termo')
        definicao_atualizada = request.form.get('definicao')

        if termo_atualizado and definicao_atualizada:
            termos_dicionario[index]['termo'] = termo_atualizado
            termos_dicionario[index]['definicao'] = definicao_atualizada
            return redirect(url_for('dicionario_page'))
        else:
            return render_template('editar_termo.html', termo_para_editar=termo_para_editar, index=index, error="Ambos os campos são obrigatórios.")

    return render_template('editar_termo.html', termo_para_editar=termo_para_editar, index=index)


@app.route('/excluir_termo/<int:index>')
def excluir_termo_page(index):

    if 0 <= index < len(termos_dicionario):

        termos_dicionario.pop(index)

    return redirect(url_for('dicionario_page'))

if __name__ == '__main__':
    app.run(debug=True)
