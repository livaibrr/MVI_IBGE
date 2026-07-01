import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import urllib.request
import json

# ==============================================================================
# 1. CONFIGURAÇÕES E CARREGAMENTO DE DADOS (Cérebro Leve e Limpo)
# ==============================================================================
st.set_page_config(page_title="Painel IBGE", layout="wide")

@st.cache_data 
def carregar_dados():
    # O site agora APENAS LÊ o banco de dados. Sem cálculos pesados aqui!
    conexao = sqlite3.connect('banco_seguranca_publica.db')
    tabela = pd.read_sql('SELECT * FROM tb_indicadores_estaduais', conexao)
    conexao.close()
    return tabela

@st.cache_data
def carregar_mapa():
    url = "https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson"
    resposta = urllib.request.urlopen(url)
    return json.load(resposta)

dados_ibge = carregar_dados()
mapa_brasil = carregar_mapa()

# ==============================================================================
# 2. BARRA LATERAL (Menu de Filtros)
# ==============================================================================
st.sidebar.title("⚙️ Filtros do Painel")

lista_indicadores = ['Taxa de MVI', 'Renda', 'Gini', 'Desemprego Médio 2024']
indicador_selecionado = st.sidebar.radio("1. Pinte o mapa pelo indicador:", lista_indicadores)

# Usando o nome correto com underline, igual salvamos no ETL
lista_perfis = ["Todos"] + list(dados_ibge['Perfil Socioeconomico'].unique())
perfil_selecionado = st.sidebar.selectbox("2. Filtre por Perfil:", lista_perfis)

if perfil_selecionado != "Todos":
    dados_ibge = dados_ibge[dados_ibge['Perfil Socioeconomico'] == perfil_selecionado]

# ==============================================================================
# 3. INTERFACE PRINCIPAL
# ==============================================================================
st.title("🗺️ Dashboard de Indicadores Socioeconômicos")
st.markdown("---")

aba_mapa, aba_novas_ideias = st.tabs(["🌐 Visão Geográfica", "🚀 Próximas Implementações"])

# ==============================================================================
# BLOCO A: MAPA E CARDS
# ==============================================================================
with aba_mapa:
    coluna_esquerda, coluna_direita = st.columns([2, 1]) 

    with coluna_esquerda:
        st.subheader(f"Distribuição: {indicador_selecionado}")
        
        # Desenha o mapa
        fig_mapa = px.choropleth(
            dados_ibge, geojson=mapa_brasil, locations='Estado',
            featureidkey='properties.name', color=indicador_selecionado,
            color_continuous_scale="Reds", hover_name='Estado'
        )
        fig_mapa.update_geos(fitbounds="locations", visible=False)
        fig_mapa.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        evento_mapa = st.plotly_chart(fig_mapa, use_container_width=True, on_select="rerun")

    with coluna_direita:
        st.subheader("🔍 Raio-X do Estado")
        
        estado_clicado = None
        if isinstance(evento_mapa, dict) and "selection" in evento_mapa:
            pontos_clicados = evento_mapa["selection"].get("points", [])
            if len(pontos_clicados) > 0:
                estado_clicado = pontos_clicados[0].get("location")
                
        lista_estados_filtrada = list(dados_ibge['Estado'].unique())
        
        # Trava de segurança: Se o filtro deixar o mapa vazio, não dá erro
        if len(lista_estados_filtrada) > 0:
            index_estado = lista_estados_filtrada.index(estado_clicado) if estado_clicado in lista_estados_filtrada else 0
            estado_selecionado = st.selectbox("Estado atual:", lista_estados_filtrada, index=index_estado)
            
            # Puxa os dados do estado selecionado
            dados_estado = dados_ibge[dados_ibge['Estado'] == estado_selecionado].iloc[0]
            
            # Os Cards Exibidos na tela
            st.metric(label="🏷️ Perfil Socioeconômico", value=dados_estado['Perfil Socioeconomico'])
            st.metric(label="🏆 Score de Desenvolvimento (0 a 1)", value=f"{dados_estado['Score Desenvolvimento']:.3f}")
            st.metric(label="💰 Renda (Normalizada)", value=f"{dados_estado['Renda']:.3f}")
            st.metric(label="📉 Desemprego Médio", value=f"{dados_estado['Desemprego Médio 2024']:.3f}")
            st.metric(label="⚖️ Índice Gini", value=f"{dados_estado['Gini']:.3f}")
            st.metric(label="🚨 Taxa de MVI", value=f"{dados_estado['Taxa de MVI']:.3f}")
        else:
            st.warning("Nenhum estado atende a este filtro atualmente.")

# ==============================================================================
# BLOCO B: ESPAÇO RESERVADO PARA NOVAS ATUALIZAÇÕES
# ==============================================================================
with aba_novas_ideias:
    st.subheader("🚧 Próximas Implementações")
    st.info("Este espaço está limpo e isolado. Aqui colocaremos a próxima parte que você escolher, sem mexer no mapa.")