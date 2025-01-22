import pandas as pd
import streamlit as st
import plotly.express as px

# Função para carregar os dados enviados (upload do usuário)
@st.cache_data
def carregar_dados(uploaded_file):
    try:
        # Lê o arquivo Excel enviado pelo usuário
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
    :param df: DataFrame
    :param colunas: Lista de colunas a serem formatadas
    """
    for coluna in colunas:
        if coluna in df.columns:
            df[coluna] = df[coluna].apply(
                lambda x: f"{x:.0f}" if isinstance(x, float) and x.is_integer() else x
            )
    return df

# Função Principal do Streamlit
def main():
    # Configuração do layout para expandir
    st.set_page_config(page_title="Dashboard de OS's", layout="wide")
    st.title("📊 Dashboard Interativo de OS's")

    # Barra Lateral para Upload
    st.sidebar.title("Envie seu Arquivo")
    uploaded_file = st.sidebar.file_uploader("Carregar arquivo Excel", type=["xlsx"])

    if uploaded_file is not None:
        # Carregar os dados
        dados = carregar_dados(uploaded_file)
        dados.columns = dados.columns.str.strip().str.lower()  # Padronizar nomes de colunas

        # Verificar se o DataFrame está vazio
        if dados.empty:
            st.error("O arquivo carregado está vazio. Por favor, envie um arquivo válido.")
            st.stop()

        # Validar as colunas essenciais
        if "dias em atraso" not in dados.columns:
            st.error("A coluna 'Dias em Atraso' não foi encontrada no arquivo carregado.")
            st.stop()

        # BARRA LATERAL: FILTROS
        with st.sidebar:
            st.header("Filtros para Análise")

            # Filtro de Dias em Atraso (slider)
            dias_min, dias_max = int(dados["dias em atraso"].min()), int(dados["dias em atraso"].max())
            dias_em_atraso = st.slider("Dias em Atraso", dias_min, dias_max, (dias_min, dias_max))

            # Filtro de Serviço (multiselect com multi-filtramento)
            if "serviço" in dados.columns:
                servicos_disponiveis = ["Todos"] + dados["serviço"].dropna().unique().tolist()
                servicos_selecionados = st.multiselect("Serviço (Pesquisável)", servicos_disponiveis, default="Todos")
                
                # Se "Todos" for selecionado ou nenhum serviço for selecionado, consideramos todos os serviços
                if "Todos" in servicos_selecionados or not servicos_selecionados:
                    servicos_selecionados = dados["serviço"].dropna().unique().tolist()
            else:
                servicos_selecionados = []  # Caso não exista a coluna "serviço"

            # Filtro de Situação (selectbox)
            if "situação" in dados.columns:
                situacoes_disponiveis = ["Todas"] + dados["situação"].dropna().unique().tolist()
                situacao_selecionada = st.selectbox("Situação", situacoes_disponiveis)
            else:
                situacao_selecionada = "Todas"

            # Filtro de Bairro (selectbox)
            if "bairro" in dados.columns:
                bairros_disponiveis = ["Todos"] + dados["bairro"].dropna().unique().tolist()
                bairro_selecionado = st.selectbox("Bairro", bairros_disponiveis)
            else:
                bairro_selecionado = "Todos"

        # APLICAR FILTROS AO DATAFRAME
        # Filtrar por "Dias em Atraso"
        dados_filtrados = dados[
            (dados["dias em atraso"] >= dias_em_atraso[0]) &
            (dados["dias em atraso"] <= dias_em_atraso[1])
        ]
        
        # Filtrar por "Serviço"
        if servicos_selecionados:
            dados_filtrados = dados_filtrados[dados_filtrados["serviço"].isin(servicos_selecionados)]
        
        # Filtrar por "Situação"
        if situacao_selecionada != "Todas":
            dados_filtrados = dados_filtrados[dados_filtrados["situação"] == situacao_selecionada]
        
        # Filtrar por "Bairro"
        if bairro_selecionado != "Todos":
            dados_filtrados = dados_filtrados[dados_filtrados["bairro"] == bairro_selecionado]

        # Remover zeros desnecessários nas colunas "número da os" e "matrícula"
        colunas_para_ajuste = ["número da os", "matrícula"]
        dados_filtrados = formatar_coluna_sem_zeros(dados_filtrados, colunas_para_ajuste)

        # SEÇÃO PRINCIPAL DE RESULTADOS
        if dados_filtrados.empty:
            st.warning("Nenhum dado encontrado com os filtros aplicados.")
        else:
            # Divisão das Informações Gerais no Topo
            col1, col2 = st.columns([2, 1])  # Largura ajustada: col1 maior para gráficos, col2 menor para informações

            with col2:
                st.subheader("📋 Informações Gerais")
                st.metric("Total de OS's Atrasadas", len(dados_filtrados))  # Total de linhas filtradas

                if "bairro" in dados.columns:
                    st.write("**Top 5 Bairros com mais OS's**")
                    top_bairros = dados_filtrados["bairro"].value_counts().head(5).reset_index()
                    top_bairros.columns = ["Bairro", "Quantidade"]
                    st.dataframe(top_bairros, use_container_width=True)

            with col1:
                # GRÁFICO: Quantitativo de Serviços
                st.subheader("Gráfico: Top 10 Serviços com mais OS's")
                servicos_quantitativo = dados_filtrados["serviço"].value_counts().head(10).reset_index()
                servicos_quantitativo.columns = ["Serviço", "Quantidade"]
                fig_servico = px.bar(
                    servicos_quantitativo,
                    x="Serviço",
                    y="Quantidade",
                    title="Top 10 Serviços com mais OS's",
                    text="Quantidade",
                    color="Serviço"
                )
                st.plotly_chart(fig_servico, use_container_width=True)

            # OUTRAS SEÇÕES: Tabelas e Detalhes
            st.divider()  # Linha divisória para organizar o layout
            col3, col4 = st.columns(2)

            with col3:
                st.subheader("Top 6 OS's com mais Tempo em Atraso")

                # Obter 6 maiores atrasos
                top_oss = dados_filtrados.nlargest(
                    6, "dias em atraso"
                )[["número da os", "matrícula", "serviço", "dias em atraso", "endereço"]]

                st.table(top_oss)

            with col4:
                st.subheader("Tabela Geral de OS's Filtradas")
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
