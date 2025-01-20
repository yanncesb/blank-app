import pandas as pd
import streamlit as st
import plotly.express as px

# Configuração inicial da página Streamlit
st.set_page_config(page_title="Análise Poço - Unidade Timon",
                   layout="wide",
                   initial_sidebar_state="expanded")

# ========================================
# Funções Úteis
# ========================================

# Função para carregar os dados do arquivo Excel
@st.cache_data
def carregar_dados(uploaded_file):
    try:
        # Lê o arquivo Excel enviado
        df = pd.read_excel(uploaded_file)
        return df
    except Exception as e:
        st.error(f"Erro ao carregar o arquivo: {e}")
        st.stop()

# Função para converter o DataFrame para formato CSV
@st.cache_data
def convert_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')

# Função para contar a quantidade de poços por situação
def contar_pocos(df, coluna, valor):
    return df[df[coluna] == valor].shape[0]

# Função para contar a quantidade de poços por situação e processo de outorga
def contar_pocos_outorga(df, situacao, outorga):
    return df[(df["Situação"] == situacao) & (df["Processo Outorga"] == outorga)].shape[0]

# ========================================
# Interface da aplicação
# ========================================

def main():
    st.title("Análise de Poços - Unidade Timon")

    # Configuração para exibir todas as colunas sem truncamento, incluindo "Observações"
    pd.set_option("display.max_colwidth", None)

    # Upload do arquivo pelo usuário
    st.sidebar.header("Carregue seu arquivo Excel")
    uploaded_file = st.sidebar.file_uploader("Faça upload do arquivo Excel", type=["xlsx"])

    if uploaded_file:
        # Se o arquivo for enviado, carregue os dados
        df_POÇOS = carregar_dados(uploaded_file)
    else:
        st.warning("Por favor, faça upload de um arquivo Excel.")
        st.stop()  # Interrompe a execução do restante do app se não há arquivo.

    # ========================================
    # Filtros
    # ========================================

    # Elementos na barra lateral
    st.sidebar.header("Filtros")
    situacao = st.sidebar.selectbox("Situação do Poço", ["Todos", "ATIVO", "INATIVO", "TAMPONADO"])
    processo_outorga = st.sidebar.selectbox("Processo de Outorga", ["Todos", "Sim", "Não", "Solicitado"])
    termo_cessao = st.sidebar.selectbox("Termo de Cessão", ["Todos", "Sim", "Não"])
    outorga_tramitacao = st.sidebar.selectbox("Outorga em Tramitação", ["Todos", "Não", "Em tramitação/análise"])

    # Aplicação de filtros no DataFrame
    df_filtrado = df_POÇOS.copy()

    if situacao != "Todos":
        df_filtrado = df_filtrado[df_filtrado["Situação"] == situacao]

    if processo_outorga != "Todos":
        df_filtrado = df_filtrado[df_filtrado["Processo Outorga"] == processo_outorga]

    if termo_cessao != "Todos":
        df_filtrado = df_filtrado[df_filtrado["Termo de Cessão"] == termo_cessao]

    if outorga_tramitacao != "Todos":
        df_filtrado = df_filtrado[df_filtrado["Outorga em Tramitação"] == outorga_tramitacao]

    # ========================================
    # Contagens e Estatísticas
    # ========================================

    # Contagem de poços por situação após aplicação dos filtros
    ativos = contar_pocos(df_filtrado, "Situação", "ATIVO")
    inativos = contar_pocos(df_filtrado, "Situação", "INATIVO")
    tamponados = contar_pocos(df_filtrado, "Situação", "TAMPONADO")

    # Contagem de poços por situação e processo de outorga
    ativos_sim = contar_pocos_outorga(df_filtrado, "ATIVO", "Sim")
    ativos_nao = contar_pocos_outorga(df_filtrado, "ATIVO", "Não")
    ativos_solicitado = contar_pocos_outorga(df_filtrado, "ATIVO", "Solicitado")

    inativos_sim = contar_pocos_outorga(df_filtrado, "INATIVO", "Sim")
    inativos_nao = contar_pocos_outorga(df_filtrado, "INATIVO", "Não")
    inativos_solicitado = contar_pocos_outorga(df_filtrado, "INATIVO", "Solicitado")

    tamponados_sim = contar_pocos_outorga(df_filtrado, "TAMPONADO", "Sim")
    tamponados_nao = contar_pocos_outorga(df_filtrado, "TAMPONADO", "Não")
    tamponados_solicitado = contar_pocos_outorga(df_filtrado, "TAMPONADO", "Solicitado")

    # ========================================
    # Gráficos e Exibição
    # ========================================

    # Gráfico de distribuição de poços
    fig = px.pie(values=[ativos, inativos, tamponados],
                 names=["Ativos", "Inativos", "Tamponados"],
                 title="Quantitativo de Poços")

    # Exibição das informações
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Quantitativos")
        st.write(f"**Poços Ativos:** {ativos}")
        st.write(f"- Com processo de outorga: {ativos_sim}")
        st.write(f"- Sem processo de outorga: {ativos_nao}")
        st.write(f"- Processo de outorga solicitado: {ativos_solicitado}")

        st.write(f"**Poços Inativos:** {inativos}")
        st.write(f"- Com processo de outorga: {inativos_sim}")
        st.write(f"- Sem processo de outorga: {inativos_nao}")
        st.write(f"- Processo de outorga solicitado: {inativos_solicitado}")

        st.write(f"**Poços Tamponados:** {tamponados}")
        st.write(f"- Com processo de outorga: {tamponados_sim}")
        st.write(f"- Sem processo de outorga: {tamponados_nao}")
        st.write(f"- Processo de outorga solicitado: {tamponados_solicitado}")

    with col2:
        st.subheader("Gráfico de Quantitativo de Poços")
        st.plotly_chart(fig)

    # ========================================
    # Informações Detalhadas de um Poço Específico
    # ========================================

    st.subheader("Detalhes de um Poço Específico")
    lista_pocos = df_filtrado["Numeração"].unique()
    poço_escolhido = st.selectbox("Escolha o Poço", options=["Selecione"] + list(lista_pocos), key="selecionar_poco")

    if poço_escolhido != "Selecione":
        info_poco = df_filtrado[df_filtrado["Numeração"] == poço_escolhido]

        st.write(f"**Detalhes do Poço {poço_escolhido}:**")
        st.write(f"- **Locin:** {info_poco.iloc[0]['Locin']}")
        st.write(f"- **Bairro:** {info_poco.iloc[0]['Bairro']}")
        st.write(f"- **Situação:** {info_poco.iloc[0]['Situação']}")
        st.write(f"- **Sistema:** {info_poco.iloc[0]['Sistema']}")
        st.write(f"- **Endereço:** {info_poco.iloc[0]['Endereço']}")
        st.write(f"- **Observações:** {info_poco.iloc[0]['Observações']}")

    # Exibição da tabela completa com todas as colunas visíveis
    st.subheader("Tabela Completa")
    st.dataframe(df_filtrado)

    # Download da tabela filtrada
    csv = convert_to_csv(df_filtrado)

    st.download_button(
        label="Download da Tabela Completa",
        data=csv,
        file_name='analise_pocos_unidade_timon.csv',
        mime='text/csv',
    )

# ========================================
# Ponto de entrada para execução
# ========================================
if __name__ == "__main__":
    main()

