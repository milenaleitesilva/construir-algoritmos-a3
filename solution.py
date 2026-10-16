import os
import requests
from dotenv import load_dotenv
from folium import Map, Marker, Icon

# autenticação
load_dotenv(".env")
s = requests.Session()
token = os.getenv("SPTRANS_TOKEN")
res_auth = s.post(f"http://api.olhovivo.sptrans.com.br/v2.1/Login/Autenticar?token={token}")

# 2 Busca por linha ("Pinheiros")
termo_busca = "Pinheiros"
res_linhas = s.get(f"http://api.olhovivo.sptrans.com.br/v2.1/Linha/Buscar?termosBusca={termo_busca}")
linhas = res_linhas.json()
codigo_linha = linhas[0]['cl']

# 3 Busca de Paradas e Veículos em tempo real
res_paradas = s.get(f"http://api.olhovivo.sptrans.com.br/v2.1/Parada/BuscarParadasPorLinha?codigoLinha={codigo_linha}")
paradas = res_paradas.json()

if not paradas:
    res_paradas = s.get("http://api.olhovivo.sptrans.com.br/v2.1/Parada/Buscar?termosBusca=Paulista")
    paradas = res_paradas.json()

res_posicao = s.get(f"http://api.olhovivo.sptrans.com.br/v2.1/Posicao/Linha?codigoLinha={codigo_linha}")
veiculos = res_posicao.json().get('vs', [])

# 4 define o centro do mapa
if paradas:
    centro_mapa = [paradas[0]["py"], paradas[0]["px"]]
elif veiculos:
    centro_mapa = [veiculos[0]["py"], veiculos[0]["px"]]
else:
    centro_mapa = [-23.550520, -46.633308]

# 5 Cria o mapa usando o servidor de imagens da Esri (que não bloqueia)
m = Map(
    location=centro_mapa, 
    zoom_start=13,
    tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}",
    attr="Esri"
)

# Pins das Paradas (Azul)
for p in paradas:
    Marker(
        location=[p["py"], p["px"]],
        popup=p["np"],
        icon=Icon(color="blue", icon="info-sign")
    ).add_to(m)

# Pins dos Ônibus em Tempo Real (Vermelho)
for v in veiculos:
    Marker(
        location=[v["py"], v["px"]],
        popup=f"Ônibus: {v['p']}",
        icon=Icon(color="red", icon="bus", prefix="fa")
    ).add_to(m)

# Salva/Sobrescreve o mapa.html automaticamente
m.save("mapa.html")
print("✅ Mapa gerado e salvo em mapa.html com sucesso!")
