# Importación de librerías
import streamlit as st
import sparql_dataframe
import plotly.express as px

# Interfaz
st.title('Datos de calles')
st.markdown('***')

# Obtener datos con SPARQL de GraphDB
endPoint = "http://192.168.1.2:7200/repositories/Bikeways"

# Obtener Calles con SPARQL
streetQuery = """
PREFIX bikeways: <https://bikeways.org/>
PREFIX schema: <http://schema.org/>
SELECT ?Calle ?ID ?Nombre ?Material ?Longitud ?Estado ?Tipo ?Señalizacion ?Coordenadas
WHERE {
?Calle a bikeways:Street .
?Calle schema:identifier ?ID .
OPTIONAL { ?Calle schema:name ?Nombre . }
OPTIONAL { ?Calle schema:material ?Material . }
OPTIONAL { ?Calle schema:size ?Longitud . }
OPTIONAL { ?Calle bikeways:streetStatus ?Estado . }
OPTIONAL { ?Calle bikeways:streetType ?Tipo . }
OPTIONAL { ?Calle bikeways:streetSignaling ?Señalizacion . }
OPTIONAL { ?Calle bikeways:startPosition ?Ubicacion . }
OPTIONAL { ?Ubicacion schema:geo ?Coordenadas . }
} ORDER BY ?ID
"""

# Obtener resultados de la consulta
streets = sparql_dataframe.get(endPoint, streetQuery)
# st.dataframe(streets)

# Sidebar para filtros
st.sidebar.header('Filtra los datos aquí 👇🏻')

# Filtrar calles por material
material = st.sidebar.multiselect('Material',
                                  options=streets['Material'].unique(),
                                  default=streets['Material'].unique())
# Filtrar calles por status
status = st.sidebar.multiselect('Estado',
                                options=streets['Estado'].unique(),
                                default=streets['Estado'].unique())

# Filtrar calles por tipo
type = st.sidebar.multiselect('Tipo',
                              options=streets['Tipo'].unique(),
                              default=streets['Tipo'].unique())

# Filtrar calles por señalización
signaling = st.sidebar.multiselect('Señalización',
                                   options=streets['Señalizacion'].unique(),
                                   default=streets['Señalizacion'].unique())

# Aplicación de filtros al DataFrame
mask = (streets['Material'].isin(material)) & (streets['Estado'].isin(status)) & (streets['Tipo'].isin(type)) & (
    streets['Señalizacion'].isin(signaling))
st.dataframe(streets[mask])

# Gráficas
st.markdown('***')
st.header('Visualización gráfica de los datos de las calles')
st.markdown('***')

# Gráfico de barras
st.subheader('🚧 Longitud de las calles')
st.bar_chart(data=streets[mask], x='Nombre', y='Longitud')

# Gráficos de pastel
st.markdown('***')
st.subheader('🛑 Estado de las calles')

streetStatusPie = streets.groupby(['Estado']).count()[['Calle']]
streetStatusPie.rename(columns={'Calle': 'Cantidad'}, inplace=True)
streetStatusPie = streetStatusPie.reset_index()

statusPieChart = px.pie(streetStatusPie,
                        title='Porcentaje de los estados de las calles',
                        values='Cantidad',
                        names='Estado')
st.plotly_chart(statusPieChart)

st.markdown('***')
st.subheader('⚠️ Señalización de las calles')

streetSignalingPie = streets.groupby(['Señalizacion']).count()[['Calle']]
streetSignalingPie.rename(columns={'Calle': 'Cantidad'}, inplace=True)
streetSignalingPie = streetSignalingPie.reset_index()

signalingPieChart = px.pie(streetSignalingPie,
                           title='Porcentaje de la señalización de las calles',
                           values='Cantidad',
                           names='Señalizacion')
st.plotly_chart(signalingPieChart)

# Gráfico de mapa
st.markdown('***')
st.subheader('📍 Ubicación de las calles')

streetCoordinates = streets[['Coordenadas']]
streetCoordinates = streetCoordinates['Coordenadas'].str.split(',', expand=True)
streetCoordinates.rename(columns={0: 'latitude', 1: 'longitude'}, inplace=True)

streetMap = streetCoordinates
streetMap['latitude'] = streetMap['latitude'].astype(float)
streetMap['longitude'] = streetMap['longitude'].astype(float)

st.map(data=streetMap, zoom=13)
