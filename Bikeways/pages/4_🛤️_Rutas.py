# Importación de librerías
import pandas as pd
import streamlit as st
import sparql_dataframe
import plotly.express as px

# Interfaz
st.title('Datos de rutas')
st.markdown('***')

# Obtener datos con SPARQL de GraphDB
endPoint = "http://192.168.1.2:7200/repositories/Bikeways"

# Obtener Calles con SPARQL
routeQuery = """
PREFIX bikeways: <https://bikeways.org/>
PREFIX schema: <http://schema.org/>
SELECT ?ID ?Nombre ?Descripcion ?FechaInicio ?FechaFin ?Distancia ?Duracion ?Velocidad ?Calorias
?PosicionInicio ?PosicionFin ?NombreCiclista
WHERE {
    ?route a bikeways:Route .
    ?route schema:identifier ?ID .
    OPTIONAL { ?route schema:name ?Nombre . }
    OPTIONAL { ?route schema:description ?Descripcion . }
    OPTIONAL { ?route schema:startDate ?FechaInicio . }
    OPTIONAL { ?route schema:endDate ?FechaFin . }
    OPTIONAL { ?route schema:distance ?Distancia . }
    OPTIONAL { ?route schema:duration ?Duracion . }
    OPTIONAL { ?route bikeways:averageSpeed ?Velocidad . }
    OPTIONAL { ?route bikeways:burnoutCalories ?Calorias . }
    OPTIONAL { ?route bikeways:startPosition ?PosicionInicio . }
    OPTIONAL { ?route bikeways:endPosition ?PosicionFin . }
    ?route bikeways:isMadeBy ?user .
    OPTIONAL { ?user schema:name ?NombreCiclista . }
} ORDER BY ?ID
"""

# Obtener resultados de la consulta
routes = sparql_dataframe.get(endPoint, routeQuery)

# Reemplazar valores nulos
routes = routes.fillna('No definido')

# Modificación de tipos de datos
routes['Distancia'] = routes['Distancia'].astype(int)
routes['Duracion'] = routes['Duracion'].astype(int)
routes['Velocidad'] = routes['Velocidad'].astype(int)
routes['Calorias'] = routes['Calorias'].astype(int)

# Sidebar para filtros
st.sidebar.header('Filtra los datos aquí 👇🏻')

# Filtrar ciclistas por distancia
distance = routes['Distancia'].unique().tolist()
distance = st.sidebar.slider('Distancia',
                             min_value=min(distance),
                             max_value=max(distance),
                             value=(min(distance), max(distance)))

# Filtrar ciclistas por duración
duration = routes['Duracion'].unique().tolist()
duration = st.sidebar.slider('Duracion',
                             min_value=min(duration),
                             max_value=max(duration),
                             value=(min(duration), max(duration)))

# Filtrar ciclistas por velocidad
velocity = routes['Velocidad'].unique().tolist()
velocity = st.sidebar.slider('Velocidad',
                             min_value=min(velocity),
                             max_value=max(velocity),
                             value=(min(velocity), max(velocity)))

# Filtrar rutas por calorías quemadas
calories = routes['Calorias'].unique().tolist()
calories = st.sidebar.slider('Calorias',
                             min_value=min(calories),
                             max_value=max(calories),
                             value=(min(calories), max(calories)))

# Aplicación de filtros al DataFrame
mask = (routes['Distancia'].between(*distance)) & (routes['Duracion'].between(*duration)) & (
    routes['Velocidad'].between(*velocity)) & (routes['Calorias'].between(*calories))

st.dataframe(routes[mask])

# Gráficas
st.markdown('***')
st.header('Visualización gráfica de los datos de las rutas')
st.markdown('***')

# Gráfico de barras
st.subheader('🔢 Cantidad de rutas realizadas por los ciclistas')

routesNumber = routes.groupby(['NombreCiclista']).count()[['Duracion']]
routesNumber.rename(columns={'Duracion': 'Rutas realizadas'}, inplace=True)
routesNumber = routesNumber.reset_index()

st.bar_chart(data=routesNumber, x='NombreCiclista', y='Rutas realizadas')

# Gráfico de líneas
st.markdown('***')
st.subheader('⏱️ Distancias de las rutas realizadas en distintas fechas')

routesDatesDistance = routes.groupby(['FechaInicio', 'Distancia']).count()
routesDatesDistance = routesDatesDistance.reset_index()

routesDatesDistanceLine = px.line(routesDatesDistance, x='FechaInicio', y='Distancia')

st.plotly_chart(routesDatesDistanceLine)

# Gráfico de burbujas
st.markdown('***')
st.subheader('🔥 Calorías que han quemado los ciclistas en las rutas')
routesCalories = px.scatter(routes[mask], x='Distancia', y='Duracion', size='Calorias', color='Calorias',
                            hover_name='NombreCiclista',
                            size_max=15)

st.plotly_chart(routesCalories)
