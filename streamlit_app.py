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

# Função para contar a quantidade de poços por observação específica
def contar_pocos_observacao(df, observacao):
    return df[df["Observações"].str.contains(observacao, na=False, case=False)].shape[0]

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
    termo_cessao = st.sidebar.selectbox("Termo de Cessão", ["Todos", "Sim", "Não", "Documento de Uso e Ocupação do Solo"])
    outorga_tramitacao = st.sidebar.selectbox("Outorga em Tramitação", ["Todos", "Não", "Em tramitação/análise"])
    fluxo_devolucao = st.sidebar.selectbox("Criar fluxo de devolução?", ["Todos", "Sim", "Não"])

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

    if fluxo_devolucao != "Todos":
        df_filtrado = df_filtrado[df_filtrado["Criar fluxo de devolução?"] == fluxo_devolucao]

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
    # Exibição: Informações Resumidas
    # ========================================
    
    st.markdown("<h2 style='text-align: center;'>Informações Resumidas</h2>", unsafe_allow_html=True)

    st.markdown(
        f"""
        <div style='font-size:20px; line-height:1.8;'>
            <strong>Poços Ativos:</strong> {ativos}<br>
            &nbsp;&nbsp;&nbsp;&nbsp;- Com processo de outorga: {ativos_sim}<br>
            &nbsp;&nbsp;&nbsp;&nbsp;- Sem processo de outorga: {ativos_nao}<br>
            &nbsp;&nbsp;&nbsp;&nbsp;- Processo de outorga solicitado: {ativos_solicitado}<br><br>

            <strong>Poços Inativos:</strong> {inativos}<br>
            &nbsp;&nbsp;&nbsp;&nbsp;- Com processo de outorga: {inativos_sim}<br>
            &nbsp;&nbsp;&nbsp;&nbsp;- Sem processo de outorga: {inativos_nao}<br>
            &nbsp;&nbsp;&nbsp;&nbsp;- Processo de outorga solicitado: {inativos_solicitado}<br><br>

            <strong>Poços Tamponados:</strong> {tamponados}<br>
            &nbsp;&nbsp;&nbsp;&nbsp;- Com processo de outorga: {tamponados_sim}<br>
            &nbsp;&nbsp;&nbsp;&nbsp;- Sem processo de outorga: {tamponados_nao}<br>
            &nbsp;&nbsp;&nbsp;&nbsp;- Processo de outorga solicitado: {tamponados_solicitado}<br>
        </div>
        """,
        unsafe_allow_html=True
    )

    # ========================================
    # Gráficos e Exibição
    # ========================================

    # Gráfico de distribuição de poços
    fig = px.pie(
        values=[ativos, inativos, tamponados],
        names=["Ativos", "Inativos", "Tamponados"],
        title="Distribuição dos Poços"
    )

    # Exibição dos gráficos
    st.plotly_chart(fig, use_container_width=True)

# ========================================
# Ponto de entrada para execução
# ========================================
if __name__ == "__main__":
    main()


