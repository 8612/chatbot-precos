import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

SERP_API_KEY = os.getenv("SERP_API_KEY")  # Pegando a API Key do ambiente
SERP_API_URL = "https://serpapi.com/search"

@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json()
    
    produto = data["queryResult"]["parameters"].get("produto")

    if not produto:
        return jsonify({"fulfillmentText": "Por favor, informe um produto para buscar os preços."})

    # Parâmetros da busca na SerpAPI filtrando para Brasil
    params = {
        "engine": "google_shopping",
        "q": produto,
        "api_key": SERP_API_KEY,
        "hl": "pt-BR",  # Define o idioma
        "gl": "BR",  # Define a localização como Brasil
        "currency": "BRL"  # Tenta forçar preços em reais
    }

    response = requests.get(SERP_API_URL, params=params)

    if response.status_code != 200:
        return jsonify({"fulfillmentText": "Houve um erro ao buscar os preços. Tente novamente mais tarde."})

    results = response.json().get("shopping_results", [])[:3]  # Pegando os 3 primeiros resultados

    if not results:
        return jsonify({"fulfillmentText": "Não encontrei resultados para esse produto no Brasil."})

    # Monta a resposta formatada
    resposta = f"Aqui estão os preços para '{produto}':\n\n"
    for item in results:
        nome = item.get("title", "Produto sem nome")
        preco = item.get("price", "Preço não disponível")
        link = item.get("link", "#")  # Se não tiver link, deixa como "#"
        resposta += f"💰 *{nome}* - {preco}\n🔗 [Ver produto]({link})\n\n"

    return jsonify({"fulfillmentText": resposta})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
