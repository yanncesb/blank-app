import pandas as pd
import streamlit as st
import plotly.express as px

# Função para carregar os dados carregados pelo usuário
@st.cache_data
def carregar_dados(uploaded_file):
    try:
        df = pd.read_excel(uploaded_file, engine="openpyxl")
        return df
    except Exception as e:
        st.error(f"Erro ao carregar o arquivo: {e}")
        st.stop()

# Função para converter DataFrame para CSV (quando aplicável)
@st.cache_data
def convert_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')

# Função para limpar zeros desnecessários nas colunas numéricas
def formatar_coluna_sem_zeros(df, colunas):
    """
    Remove zeros desnecessários após a vírgula nas colunas fornecidas.
    """
    for coluna in colunas:
        if coluna in df.columns:
            df[coluna] = df[coluna].apply(
                lambda x: f"{x:.0f}" if isinstance(x, float) and x.is_integer() else x
            )
    return df

# Função Principal do Streamlit
def main():
    st.set_page_config(page_title="Dashboard de OS's", layout="wide")
    st.title("📊 Dashboard Interativo de OS's")

    # Barra Lateral para Upload do Arquivo
    st.sidebar.title("📂 Envie seu Arquivo")
    uploaded_file = st.sidebar.file_uploader("Carregar arquivo Excel", type=["xlsx"])

    if uploaded_file is not None:
        # Carregar os dados
        dados = carregar_dados(uploaded_file)
        dados.columns = dados.columns.str.strip().str.lower()  # Padronizar nomes de colunas

        if dados.empty:
            st.error("O arquivo carregado está vazio. Por favor, envie um arquivo válido.")
            st.stop()

        # Validar as colunas essenciais
        colunas_necessarias = ["dias em atraso", "número da os", "matrícula", "serviço", "endereço", "bairro", "obs comercial"]
        for coluna in colunas_necessarias:
            if coluna not in dados.columns:
                st.error(f"A coluna '{coluna}' não foi encontrada no arquivo carregado.")
                st.stop()

        # BARRA LATERAL: FILTROS
        with st.sidebar:
            st.header("🛠️ Filtros para Análise")

            # Filtro de "Dias em Atraso" (slider)
            dias_min, dias_max = int(dados["dias em atraso"].min()), int(dados["dias em atraso"].max())
            dias_em_atraso = st.slider("Dias em Atraso", dias_min, dias_max, (dias_min, dias_max))

            # Filtro de Serviço
            servicos_disponiveis = ["Todos"] + dados["serviço"].dropna().unique().tolist()
            servicos_selecionados = st.multiselect("Serviço (Pesquisável)", servicos_disponiveis, default="Todos")
            if "Todos" in servicos_selecionados or not servicos_selecionados:
                servicos_selecionados = dados["serviço"].dropna().unique().tolist()

            # Filtro de Situação
            situacoes_disponiveis = ["Todas"] + dados.get("situação", pd.Series()).dropna().unique().tolist()
            situacao_selecionada = st.selectbox("Situação", situacoes_disponiveis)

            # Filtro de Bairro
            bairros_disponiveis = ["Todos"] + dados["bairro"].dropna().unique().tolist()
            bairro_selecionado = st.selectbox("Bairro", bairros_disponiveis)

        # APLICAR FILTROS
        dados_filtrados = dados[
            (dados["dias em atraso"] >= dias_em_atraso[0]) & 
            (dados["dias em atraso"] <= dias_em_atraso[1])
        ]
        if servicos_selecionados:
            dados_filtrados = dados_filtrados[dados_filtrados["serviço"].isin(servicos_selecionados)]
        if situacao_selecionada != "Todas":
            dados_filtrados = dados_filtrados[dados_filtrados["situação"] == situacao_selecionada]
        if bairro_selecionado != "Todos":
            dados_filtrados = dados_filtrados[dados_filtrados["bairro"] == bairro_selecionado]

        # Remover zeros desnecessários nas colunas "número da os" e "matrícula"
        colunas_para_ajuste = ["número da os", "matrícula"]
        dados_filtrados = formatar_coluna_sem_zeros(dados_filtrados, colunas_para_ajuste)

        # Verificação de dados
        if dados_filtrados.empty:
            st.warning("Nenhum dado encontrado com os filtros aplicados.")
            return

        # SEÇÃO PRINCIPAL: DASHBOARD
        col1, col2 = st.columns([2, 1])
        with col2:
            st.subheader("📋 Informações Gerais")
            st.metric("Total de OS's - Unidade", len(dados_filtrados))

            if "bairro" in dados_filtrados.columns:
                st.write("**🏠 Top 5 Bairros com mais OS's**")
                top_bairros = dados_filtrados["bairro"].value_counts().head(5).reset_index()
                top_bairros.columns = ["Bairro", "Quantidade"]
                st.dataframe(top_bairros, use_container_width=True)
        
        with col1:
            st.subheader("📊 Top 10 Serviços com mais OS's")
            servicos_quantitativo = dados_filtrados["serviço"].value_counts().head(10).reset_index()
            servicos_quantitativo.columns = ["Serviço", "Quantidade"]
            fig_servico = px.bar(
                servicos_quantitativo,
                x="Serviço",
                y="Quantidade",
                title="Top 10 Serviços",
                text="Quantidade",
                color="Serviço"
            )
            st.plotly_chart(fig_servico, use_container_width=True)

        # SEÇÃO: TOP 6 OS's com Mais Tempo em Atraso
        st.divider()
        st.subheader("⏳ Top 6 OS's com mais Tempo em Atraso")
        
        # Selecionando as 6 OSs com maior tempo de atraso, adicionando "Bairro" e "Obs Comercial"
        colunas_top6 = ["número da os", "matrícula", "serviço", "dias em atraso", "endereço", "bairro", "obs comercial"]
        top_oss = dados_filtrados.nlargest(6, "dias em atraso")[colunas_top6]

        st.table(top_oss)

        # SEÇÃO: Tabela Geral das OS's Filtradas (Movida para baixo)
        st.divider()
        st.subheader("📑 Tabela Geral de OS's Filtradas")
        st.dataframe(dados_filtrados, use_container_width=True)

        # DOWNLOAD DOS DADOS FILTRADOS
        st.divider()
        st.subheader("📥 Exportar Dados Filtrados")
        csv_dados_filtrados = convert_to_csv(dados_filtrados)
        st.download_button(
            label="Baixar Dados Filtrados (CSV)",
            data=csv_dados_filtrados,
            file_name="dados_filtrados.csv",
            mime="text/csv",
        )
    else:
        st.warning("Nenhum arquivo carregado. Por favor, envie um arquivo Excel para iniciar!")

if __name__ == "__main__":
    main()
