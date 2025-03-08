import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from numpy_financial import irr, npv, pmt

# Função para calcular os indicadores financeiros
def calcular_indicadores(valor_imovel, entrada, taxa_juros, aluguel, prazo, vacancia, valorizacao, desconto):
    entrada_valor = (entrada / 100) * valor_imovel
    financiamento = valor_imovel - entrada_valor
    taxa_juros_mensal = (taxa_juros / 100) / 12
    num_meses = prazo * 12
    
    parcela_price = -pmt(taxa_juros_mensal, num_meses, financiamento)
    parcelas_sac = [(financiamento / num_meses) + (financiamento - (i * (financiamento / num_meses))) * taxa_juros_mensal for i in range(num_meses)]
    
    fluxo_caixa = []
    saldo_acumulado = -entrada_valor
    for ano in range(1, prazo + 1):
        receita_anual = aluguel * 12 * (1 - vacancia / 100) * (1 + valorizacao / 100) ** (ano - 1)
        despesa_anual = parcela_price * 12 if ano <= prazo else 0
        fluxo_anual = receita_anual - despesa_anual
        fluxo_caixa.append(fluxo_anual)
        saldo_acumulado += fluxo_anual
    
    tir = irr([-entrada_valor] + fluxo_caixa) * 100
    vpl = npv(desconto / 100, [-entrada_valor] + fluxo_caixa)
    payback = next((ano for ano, saldo in enumerate(np.cumsum([-entrada_valor] + fluxo_caixa)) if saldo > 0), prazo)
    cap_rate = (aluguel * 12 / valor_imovel) * 100
    
    return {
        "ROI (%)": (saldo_acumulado / entrada_valor) * 100,
        "TIR (%)": tir,
        "VPL (R$)": vpl,
        "Payback (anos)": payback,
        "Cap Rate (%)": cap_rate,
        "Parcela Price (R$)": parcela_price,
        "Parcela SAC Inicial (R$)": parcelas_sac[0],
        "Parcela SAC Final (R$)": parcelas_sac[-1]
    }, fluxo_caixa

# Configuração da Interface
st.set_page_config(page_title="Simulador de Investimento Imobiliário", layout="wide")
st.title("📊 Simulador de Investimento Imobiliário")

st.sidebar.header("🔹 Painel de Entrada de Dados")
st.sidebar.write("Preencha os dados abaixo para simular o investimento.")

# Entrada de Dados para Dois Imóveis
num_imoveis = 2
dados_imoveis = []
fluxo_caixa_imoveis = []

for i in range(1, num_imoveis + 1):
    st.sidebar.subheader(f"🏠 Imóvel {i}")
    valor_imovel = st.sidebar.number_input(f"💰 Valor do imóvel {i} (R$)", min_value=50000, value=300000)
    entrada = st.sidebar.slider(f"💵 Entrada (%) - Imóvel {i}", 0, 100, 20)
    taxa_juros = st.sidebar.slider(f"📉 Taxa de juros (%) - Imóvel {i}", 0.0, 20.0, 8.0, 0.1)
    aluguel = st.sidebar.number_input(f"🏠 Valor do aluguel (R$) - Imóvel {i}", min_value=500, value=1500)
    prazo = st.sidebar.slider(f"📆 Prazo do financiamento (anos) - Imóvel {i}", 1, 30, 20)
    vacancia = st.sidebar.slider(f"📊 Taxa de vacância (%) - Imóvel {i}", 0.0, 50.0, 5.0, 0.1)
    valorizacao = st.sidebar.slider(f"📈 Taxa de valorização (%) - Imóvel {i}", 0.0, 20.0, 5.0, 0.1)
    desconto = st.sidebar.slider(f"💲 Taxa de desconto (%) - Imóvel {i}", 0.0, 20.0, 10.0, 0.1)
    
    indicadores, fluxo_caixa = calcular_indicadores(valor_imovel, entrada, taxa_juros, aluguel, prazo, vacancia, valorizacao, desconto)
    dados_imoveis.append(indicadores)
    fluxo_caixa_imoveis.append(fluxo_caixa)

# Exibição dos Resultados
st.header("📌 Comparação dos Imóveis")
st.dataframe(pd.DataFrame(dados_imoveis, index=[f"Imóvel {i+1}" for i in range(num_imoveis)]).T)

# Gráfico do Fluxo de Caixa
st.header("📉 Fluxo de Caixa Comparativo")
fig, ax = plt.subplots()
colors = ['blue', 'green']

for i in range(num_imoveis):
    ax.plot(range(1, len(fluxo_caixa_imoveis[i]) + 1), fluxo_caixa_imoveis[i], marker='o', linestyle='-', label=f"Imóvel {i+1}", color=colors[i])

ax.axhline(0, color='red', linestyle='--')
ax.set_xlabel("Ano")
ax.set_ylabel("Fluxo de Caixa (R$)")
ax.set_title("Evolução do Fluxo de Caixa")
ax.legend()
st.pyplot(fig)
