import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuração de Layout e Tema Adaptativo
st.set_page_config(page_title="Painel Logístico - Monitoramento de SLA", layout="wide", initial_sidebar_state="expanded")

# CSS Inteligente: Se adapta ao Modo Claro e Escuro automaticamente
st.markdown("""
    <style>
    /* Cards de KPI adaptativos */
    div[data-testid="stMetricValue"] {
        font-size: 34px !important;
        font-weight: 700 !important;
        color: #00B4D8 !important; /* Azul destacado */
    }
    div[data-testid="stMetricLabel"] {
        color: var(--text-color) !important;
    }
    div[data-testid="stMetricBackground"] {
        background-color: var(--background-color) !important;
        padding: 20px !important;
        border-radius: 8px !important;
        border: 1px solid #3A506B !important;
        box-shadow: 0px 2px 4px rgba(0, 0, 0, 0.1);
    }
    /* Ajuste fino na tabela */
    div[data-testid="stDataFrame"] {
        padding: 5px !important;
        border-radius: 8px !important;
    }
    </style>
""", unsafe_allow_html=True)

# Título Principal Limpo
st.title("Painel de Controle Logístico")
st.markdown("Análise de performance operacional e conformidade de prazos.")
st.write("---")

# 2. Base de dados real extraída da imagem do desafio
dados = {
    'id_entrega': [301, 302, 303, 304, 305, 306, 307, 308, 309, 310],
    'transportadora': ['RotaMax', 'ViaCargo', 'FlashLog', 'RotaMax', 'ViaCargo', 'FlashLog', 'RotaMax', 'ViaCargo', 'FlashLog', 'ViaCargo'],
    'regiao': ['Sudeste', 'Sul', 'Nordeste', 'Norte', 'Centro-Oeste', 'Sul', 'Sul', 'Sudeste', 'Norte', 'Nordeste'],
    'prazo_dias': [3, 5, 4, 6, 2, 5, 6, 3, 5, 4],
    'dias_reais': [7, 5, 9, 4, 6, 12, 9, 4, 5, 8]
}

df = pd.DataFrame(dados)

# 3. Engenharia de Dados (Bolinhas de status)
df['Atrasado'] = df['dias_reais'] > df['prazo_dias']
df['Dias de Atraso'] = (df['dias_reais'] - df['prazo_dias']).clip(lower=0)
df['Status'] = df['Atrasado'].map({True: '🔴 Atrasado', False: '🟢 No Prazo'})

# 4. Barra Lateral de Filtros
st.sidebar.header("Filtros de Pesquisa")

regiao_selecionada = st.sidebar.multiselect(
    "Filtrar por Região:", 
    options=sorted(df['regiao'].unique()), 
    default=df['regiao'].unique()
)

transportadora_selecionada = st.sidebar.multiselect(
    "Filtrar por Transportadora:", 
    options=sorted(df['transportadora'].unique()), 
    default=df['transportadora'].unique()
)

df_filtrado = df[df['regiao'].isin(regiao_selecionada) & df['transportadora'].isin(transportadora_selecionada)]

# 5. Indicadores de Performance (Cards de KPI)
total_entregas = len(df_filtrado)
total_atrasos = df_filtrado['Atrasado'].sum()
taxa_atraso = (total_atrasos / total_entregas * 100) if total_entregas > 0 else 0

kpi1, kpi2, kpi3 = st.columns(3)
with kpi1:
    st.metric("Total de Entregas", f"{total_entregas}")
with kpi2:
    st.metric("Entregas em Atraso", f"{total_atrasos}")
with kpi3:
    st.metric("Taxa de Atraso Geral", f"{taxa_atraso:.1f}%")

st.write("---")

# 6. Configuração de Gráficos Adaptativos
col_graf1, col_graf2 = st.columns(2)
paleta_viva = px.colors.qualitative.G10 

layout_adaptativo = {
    'paper_bgcolor': 'rgba(0,0,0,0)',
    'plot_bgcolor': 'rgba(0,0,0,0)',
    'margin': dict(l=10, r=10, t=30, b=10)
}

with col_graf1:
    st.subheader("Dias Acumulados de Atraso por Transportadora")
    df_transp = df_filtrado.groupby('transportadora')['Dias de Atraso'].sum().reset_index()
    fig_bar = px.bar(
        df_transp, x='transportadora', y='Dias de Atraso', 
        labels={'transportadora': 'Transportadora', 'Dias de Atraso': 'Acumulado de Dias'},
        color='transportadora', color_discrete_sequence=paleta_viva
    )
    fig_bar.update_layout(showlegend=False, **layout_adaptativo)
    st.plotly_chart(fig_bar, use_container_width=True)

with col_graf2:
    st.subheader("Distribuição de Atrasos por Região")
    df_regiao = df_filtrado.groupby('regiao')['Dias de Atraso'].sum().reset_index()
    fig_pie = px.pie(
        df_regiao, names='regiao', values='Dias de Atraso', 
        hole=0.4, color_discrete_sequence=paleta_viva
    )
    fig_pie.update_layout(**layout_adaptativo)
    st.plotly_chart(fig_pie, use_container_width=True)

st.write("---")

# 7. Tabela de Priorização com Destaque de Fundo nos Atrasados
st.subheader("Lista Operacional de Prioridade Crítica")
st.markdown("Pedidos ordenados de forma decrescente pelo volume de desvio do prazo.")

df_ordenado = df_filtrado.sort_values(by='Dias de Atraso', ascending=False)

# Função para aplicar o fundo vermelho claro nas linhas que estão atrasadas
def destacar_atrasos(row):
    # Usando um vermelho bem suave (rgba) que não esconde o texto em nenhum dos modos
    return ['background-color: rgba(230, 57, 70, 0.20);' if row['Atrasado'] else '' for _ in row]

df_estilizado = df_ordenado.style.apply(destacar_atrasos, axis=1)

# Renderização com aplicação de estilo para o fundo vermelho
st.dataframe(
    df_estilizado, 
    use_container_width=True,
    column_config={
        "id_entrega": "ID da Entrega",
        "transportadora": "Transportadora",
        "regiao": "Região",
        "prazo_dias": "Prazo Contratual (Dias)",
        "dias_reais": "Tempo Real Utilizado",
        "Dias de Atraso": "Total de Dias Excedidos",
        "Status": "Classificação",
        "Atrasado": None, # Esconde a coluna booleana pra ficar limpo
    }
)
