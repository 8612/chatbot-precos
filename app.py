from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

MERCADO_LIVRE_API = "https://api.mercadolibre.com/sites/MLB/search?q="

@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json()

    # Extrai o nome do produto da intent do Dialogflow
    produto = data["queryResult"]["parameters"].get("produto")

    if not produto:
        return jsonify({"fulfillmentText": "Por favor, informe um produto para buscar os preços."})

    # Faz a requisição para a API do Mercado Livre
    response = requests.get(MERCADO_LIVRE_API + produto)
    
    if response.status_code != 200:
        return jsonify({"fulfillmentText": "Não consegui buscar os preços agora. Tente novamente mais tarde."})

    # Pega os 3 primeiros resultados da busca
    resultados = response.json()["results"][:3]

    # Monta a resposta formatada
    resposta = f"Aqui estão os preços para '{produto}':\n\n"
    for item in resultados:
        resposta += f"💰 *{item['title']}* - R$ {item['price']}\n🔗 [Ver produto]({item['permalink']})\n\n"

    return jsonify({"fulfillmentText": resposta})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
