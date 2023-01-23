# Importación de librerías
import streamlit as st
import sparql_dataframe
import plotly.express as px
import altair as alt

# Interfaz
st.title('Datos de ciclistas')
st.markdown('***')

# Obtener datos con SPARQL de GraphDB
endPoint = "http://192.168.1.2:7200/repositories/Bikeways"

# Obtener Calles con SPARQL
cyclistQuery = """
PREFIX bikeways: <https://bikeways.org/>
PREFIX schema: <http://schema.org/>
SELECT ?ID ?Nombre ?Genero ?Correo ?Telefono ?Imagen ?Peso ?Altura ?Nacionalidad ?Edad
WHERE {
    ?cyclist a bikeways:Cyclist .
    ?cyclist schema:identifier ?ID .
    ?cyclist schema:name ?Nombre .
    OPTIONAL { ?cyclist schema:gender ?Genero . }
    OPTIONAL { ?cyclist schema:email ?Correo . }
    OPTIONAL { ?cyclist schema:telephone ?Telefono . }
    OPTIONAL { ?cyclist schema:image ?Imagen . }
    OPTIONAL { ?cyclist schema:weight ?Peso . }
    OPTIONAL { ?cyclist schema:height ?Altura .}
    OPTIONAL { ?cyclist schema:nationality ?Nacionalidad . }
    OPTIONAL { ?cyclist bikeways:cyclistAge ?Edad . }
} ORDER BY ?name
"""

# Obtener resultados de la consulta
cyclists = sparql_dataframe.get(endPoint, cyclistQuery)

# Modificar tipos de datos y eliminación de valores nulos
cyclists['Telefono'] = cyclists['Telefono'].fillna(0)
cyclists['Telefono'] = cyclists['Telefono'].astype(int)
cyclists['Peso'] = cyclists['Peso'].astype(int)
cyclists['Altura'] = cyclists['Altura'].fillna(0)
cyclists['Edad'] = cyclists['Edad'].fillna(0)
cyclists = cyclists.fillna('No definido')

# Sidebar para filtros
st.sidebar.header('Filtra los datos aquí 👇🏻')

# Filtrar ciclistas por género
gender = st.sidebar.multiselect('Género',
                                options=cyclists['Genero'].unique(),
                                default=cyclists['Genero'].unique())

# Filtrar ciclistas por peso
weights = cyclists['Peso'].unique().tolist()
weight = st.sidebar.slider('Peso',
                           min_value=min(weights),
                           max_value=max(weights),
                           value=(min(weights), max(weights)))

# Filtrar ciclistas por altura
heights = cyclists['Altura'].unique().tolist()
height = st.sidebar.slider('Altura',
                           min_value=min(heights),
                           max_value=max(heights),
                           value=(min(heights), max(heights)))

# Filtrar ciclistas por edad
ages = cyclists['Edad'].unique().tolist()
age = st.sidebar.slider('Edad',
                        min_value=min(ages),
                        max_value=max(ages),
                        value=(min(ages), max(ages)))

# Filtrar ciclistas por nacionalidad
nationality = st.sidebar.multiselect('Nacionalidad',
                                     options=cyclists['Nacionalidad'].unique(),
                                     default=cyclists['Nacionalidad'].unique())

# Aplicación de filtros al DataFrame
mask = (cyclists['Genero'].isin(gender)) & (cyclists['Peso'].between(*weight)) & (
    cyclists['Altura'].between(*height)) & (cyclists['Nacionalidad'].isin(nationality)) & (
           cyclists['Edad'].between(*age))

st.dataframe(cyclists[mask])

# Gráficas
st.markdown('***')
st.header('Visualización gráfica de los datos de los ciclistas')
st.markdown('***')

# Gráficos de pastel
st.subheader(' 🙎🏻‍♀️🙎🏻‍♂️Cantidad de ciclistas agrupados por género')

cyclistGenderPie = cyclists.groupby(['Genero']).count()[['Nombre']]
cyclistGenderPie.rename(columns={'Nombre': 'Cantidad'}, inplace=True)
cyclistGenderPie = cyclistGenderPie.reset_index()

genderPieChart = px.pie(cyclistGenderPie,
                        title='Porcentaje de ciclistas',
                        values='Cantidad',
                        names='Genero')
st.plotly_chart(genderPieChart)

# Gráfico de burbujas
st.markdown('***')
st.subheader('🤝 Ciclistas que poseen características similares')
cyclistsFeatures = px.scatter(cyclists[mask], x='Edad', y='Peso', size='Edad', color='Edad', hover_name='Nombre',
                              size_max=15)
st.plotly_chart(cyclistsFeatures)
