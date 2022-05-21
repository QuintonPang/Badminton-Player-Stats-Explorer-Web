#imports
import pandas as pd
import base64
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import streamlit as st

# title
st.title('Badminton Player Stats Explorer Web')

# description
# * means bullet
# ** means bold
st.markdown("""
This app performs webscraping of stats of badminton players from all around the world.
* **Python libraries used:** base64, pandas, streamlit
* **Data source:** https://badmintonstatistics.net
""")

### sidebar for filtering ###

# sidebar header
st.sidebar.header("User Filter Options")

# select year from 1989 to 2022
selected_year = st.sidebar.selectbox('Year',list(reversed(range(1989,2023))))

### web scraping ###

# function to load data based on year

# @st.cache decorator speeds up the app,
# it provides a caching mechanism that allows your app to 
# stay performant even when loading data from the web, 
# manipulating large datasets, 
# or performing expensive computations. 
@st.cache
def load_data(year):
    # url for web scraping (consists of a table)
    url = "https://badmintonstatistics.net/Reports?reportname=PlayerWinsAndLosses&category=%&year="+str(year)+"&level=all&country=%"
    # read the table in the html file
    html = pd.read_html(url,header=0)
    # make it into a dataframe
    df = html[0]

    # change index to start from 1
    df.index = np.arange(1, len(df) + 1)
    
    # drop certain data based on criteria
    # raw = df.drop(df[df.Category=="WS"].index)
    # fill NaN values
    # raw = raw.fillna(0)
    # drop certain column
    # axis 0 is index, axis 1 is column
    
    # remove data with index 2
    # playerStats = raw.drop(2,axis=0)

    # remove column 'Players'
    # playerStats = raw.drop(['Players'],axis=0)
    return df

# call the function
playerStats = load_data(selected_year)

### sidebar - Country selection ###
# get available countries
sorted_unique_country = sorted(playerStats.Country.unique())
# multiselect countries
# second argument is the possible value, third argument is default value (which is all are selected in this case)
selected_country = st.sidebar.multiselect("Country",sorted_unique_country,sorted_unique_country)

### sidebar - Category selection ###
# choice for category
unique_category = ['MS','WS','MD','WD','XD']
# multiselect category
selected_category =  st.sidebar.multiselect("Category",unique_category,unique_category)

# Filtering data
df_filtered = playerStats[(playerStats.Country.isin(selected_country))&(playerStats.Category.isin(selected_category))]

### Display data ###
# Header
st.header('Display Player Stats')
# shape returns tuple, index 0 is no. of rows, index 1 is no. of columns
st.write('Data Dimension: '+str(df_filtered.shape[0]) + ' rows and' +str(df_filtered.shape[1]) + ' columns')
st.dataframe(df_filtered)

# Download badminton player stats data
# Credit: https://discuss.streamlit.io/t/how-to-download-file-in-streamlit/1806/2
def fileDownload(df):
    """Generates a link allowing the data in a given panda dataframe to be downloaded
    in:  dataframe
    out: href string
    """
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode() # strings <-> bytes conversions
    href = f'<a href="data:file/csv;base64,{b64}">Download csv file</a>'
    return href

# Generates link for downloading the dataframe as csv file
# By default, any HTML tags found in the body will be escaped 
# and therefore treated as pure text. 
# This behavior may be turned off by setting unsafe_allow_html argument to True.
st.markdown(fileDownload(df_filtered),unsafe_allow_html=True)

### Heatmap ###
# check if button is pressed
if st.button('Intercorrelation heatmap'):
    # Header
    st.header('Intercorrelation Matrix Heatmap')
    # convert it into csv file and export it in local directory
    df_filtered.to_csv('output.csv',index=False)
    # read the file
    df = pd.read_csv('output.csv')

    # logic of plotting heatmap
    corr = df.corr()
    mask = np.zeros_like(corr)
    mask[np.triu_indices_from(mask)] = True
    #  style must be one of white, dark, whitegrid, darkgrid, ticks
    with sns.axes_style("white"):
        f,ax = plt.subplots(figsize=(7,5))
        ax = sns.heatmap(corr,mask=mask,vmax=1,square=True)
    st.pyplot(f)
