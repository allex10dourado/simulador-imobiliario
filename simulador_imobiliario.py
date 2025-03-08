import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from numpy_financial import irr, npv, pmt

# Função para calcular os indicadores financeiros
def calcular_indicadores(valor_imovel, entrada, taxa_juros, aluguel, prazo, vacancia, valorizacao, desconto):
    entrada_valor = entrada / 100 * valor_imovel
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
st.title("Simulador de Investimento Imobiliário")

# Entrada de Dados
st.sidebar.header("Parâmetros do Investimento")
valor_imovel = st.sidebar.number_input("Valor do imóvel (R$)", min_value=50000, value=300000)
entrada = st.sidebar.slider("Entrada (%)", 0, 100, 20)
taxa_juros = st.sidebar.slider("Taxa de juros (%)", 0.0, 20.0, 8.0, 0.1)
aluguel = st.sidebar.number_input("Valor do aluguel (R$)", min_value=500, value=1500)
prazo = st.sidebar.slider("Prazo do financiamento (anos)", 1, 30, 20)
vacancia = st.sidebar.slider("Taxa de vacância (%)", 0.0, 50.0, 5.0, 0.1)
valorizacao = st.sidebar.slider("Taxa de valorização (%)", 0.0, 20.0, 5.0, 0.1)
desconto = st.sidebar.slider("Taxa de desconto (%)", 0.0, 20.0, 10.0, 0.1)

# Cálculo dos Indicadores
indicadores, fluxo_caixa = calcular_indicadores(valor_imovel, entrada, taxa_juros, aluguel, prazo, vacancia, valorizacao, desconto)

# Exibição dos Resultados
st.header("Resultados")
st.write(pd.DataFrame(indicadores, index=["Imóvel"]).T)

# Gráfico do Fluxo de Caixa
st.header("Fluxo de Caixa ao Longo dos Anos")
plt.figure(figsize=(8, 4))
plt.plot(range(1, prazo + 1), fluxo_caixa, marker='o', linestyle='-', label="Fluxo de Caixa")
plt.axhline(0, color='red', linestyle='--')
plt.xlabel("Ano")
plt.ylabel("Fluxo de Caixa (R$)")
plt.title("Evolução do Fluxo de Caixa")
plt.legend()
st.pyplot(plt)
