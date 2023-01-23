# Importación de librerías
import pandas as pd
import streamlit as st
import sparql_dataframe
import plotly.express as px

# Interfaz
st.title('Datos de incidentes')
st.markdown('***')

# Obtener datos con SPARQL de GraphDB
endPoint = "http://192.168.1.2:7200/repositories/Bikeways"

# Obtener Calles con SPARQL
incidentQuery = """
PREFIX bikeways: <https://bikeways.org/>
PREFIX schema: <http://schema.org/>
SELECT ?ID ?Nombre ?Categoria ?Descripcion ?Imagen ?Fecha ?Estado ?Ubicacion ?Ruta
WHERE {
    ?publicacion a bikeways:Publication .
    ?publicacion schema:identifier ?ID .
    OPTIONAL { ?publicacion schema:name ?Nombre . }
    OPTIONAL { ?publicacion schema:category ?Categoria . }
    OPTIONAL { ?publicacion schema:description ?Descripcion . }
    OPTIONAL { ?publicacion schema:image ?Imagen . }
    OPTIONAL { ?publicacion schema:startDate ?Fecha . }
    OPTIONAL { ?publicacion schema:eventStatus ?Estado . }
    OPTIONAL { ?publicacion schema:location ?Ubicacion . }
    ?publicacion bikeways:isRegisteredIn ?route .
    OPTIONAL { ?route schema:identifier ?Ruta . }
} ORDER BY ?Categoria
"""

# Obtener resultados de la consulta
incidents = sparql_dataframe.get(endPoint, incidentQuery)

# Eliminación de valores nulos
# incidents = pd.to_datetime(incidents['Fecha'])
incidents = incidents.fillna('No definido')

# Sidebar para filtros
st.sidebar.header('Filtra los datos aquí 👇🏻')

# Filtrar calles por material
category = st.sidebar.multiselect('Categoría',
                                  options=incidents['Categoria'].unique(),
                                  default=incidents['Categoria'].unique())
# Filtrar calles por status
status = st.sidebar.multiselect('Estado',
                                options=incidents['Estado'].unique(),
                                default=incidents['Estado'].unique())

# Aplicación de filtros al DataFrame
filter = incidents.query(
    'Categoria == @category & Estado == @status')

st.dataframe(filter)

# Gráficas
st.markdown('***')
st.header('Visualización gráfica de los datos de las rutas')
st.markdown('***')

# Gráficos de pastel
st.subheader('🚫 Categorías de incidentes')

incidentCategoryPie = incidents.groupby(['Categoria']).count()[['Estado']]
incidentCategoryPie.rename(columns={'Estado': 'Cantidad'}, inplace=True)
incidentCategoryPie = incidentCategoryPie.reset_index()

incidentCategoryPieChart = px.pie(incidentCategoryPie,
                                  title='Porcentaje de los categorías de los incidentes',
                                  values='Cantidad',
                                  names='Categoria')
st.plotly_chart(incidentCategoryPieChart)

# Gráficos de barras
st.markdown('***')
st.subheader('📊 Incidentes organizados por categorías')

incidentCategoryNumber = incidents.groupby(['Categoria', 'Estado', 'Nombre']).count()[['Fecha']]
incidentCategoryNumber.rename(columns={'Fecha': 'Cantidad'}, inplace=True)
incidentCategoryNumber = incidentCategoryNumber.reset_index()

incidentCategoryNumberBar = px.bar(incidentCategoryNumber, x='Nombre', y="Cantidad", color="Categoria", barmode="group")
st.plotly_chart(incidentCategoryNumberBar)

# Gráfico de mapa
st.markdown('***')
st.subheader('📍 Ubicación de los principales incidentes')

incidentCoordinates = incidents['Ubicacion'].str.split(',', expand=True)
incidentCoordinates.rename(columns={0: 'longitude', 1: 'latitude'}, inplace=True)

incidentMap = incidentCoordinates
incidentMap['latitude'] = incidentMap['latitude'].astype(float)
incidentMap['longitude'] = incidentMap['longitude'].astype(float)

st.map(data=incidentMap, zoom=13)
