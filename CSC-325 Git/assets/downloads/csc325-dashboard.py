#https://plotly.com/python/v3/graph-data-from-mysql-database-in-python/
import mysql.connector
import plotly.express as px
import pandas as pd


#CHANGE THS INSTANCE NAME AND PASSWORD TO YOUR INSTANCE INFO
#CHANGE THE PATH TO THE .JSON PYTHON KEY TO A PATH ON YOUR COMPUTER
import json
import os
# name db = movies-on-streaming-platforms
# user_name = root
# password: admin8877


os.environ["GOOGLE_APPLICATION_CREDENTIALS"]= "csc-ser325-fbdd6f481a43.json"
# make the connection to the db
def make_connection():
    return mysql.connector.connect(user='root', password='karaDB2021',
                                  host='127.0.0.1',
                                  database='csc325')

conn = make_connection();
#execute query using pandas and read the data
#df = pd.read_sql('select dataSource, yearStart from dataSource', conn);
df = pd.read_sql('''
    SELECT locationDescription, ROUND(AVG(dataValue),0) AS estMortalityRate
    FROM DataUnit
    JOIN location ON location.locationID = dataUnit.locationID
    WHERE questionID in (
	   SELECT questionId FROM question
	      WHERE question LIKE '%mortality from heart failure%'
    ) AND locationDescription != 'United States'
    GROUP BY dataUnit.locationID
    ORDER BY estMortalityRate ASC
    ''', conn);

df2 = pd.read_sql('''
    SELECT locationAbbr AS state, ROUND(AVG(dataValue), 2) AS avgVaccinationRate from dataUnit
    JOIN location ON dataUnit.locationId = location.locationId
    WHERE questionId IN (
    	SELECT questionId FROM question
    	WHERE question LIKE "%influenza%"
    	AND topicId = "IMM"
    )
    GROUP BY dataUnit.locationId
    ''', conn);

df3 = pd.read_sql('''
    SELECT AVG(dataValue) as AgeAdjustedAnnualRate, question, topicId FROM dataUnit
    JOIN question ON question.questionId = dataUnit.questionId
    Join location ON location.locationId = dataUnit.locationId
    WHERE question.questionId IN (
    	SELECT question.questionId FROM question
    WHERE question LIKE "%mortality%")
    AND locationAbbr != "US"
    AND topicId != "OVC"
    GROUP BY dataUnit.questionId
    ORDER BY AgeAdjustedAnnualRate DESC
    ''', conn);

df4 = pd.read_sql('''
    SELECT locationDescription AS state, ROUND(AVG(dataValue), 2) AS avgAlcoholUse
    FROM dataUnit
    JOIN location ON location.locationID = dataUnit.locationID
    WHERE questionID = 'ALC1_1'
    AND locationDescription != 'United States'
    GROUP BY dataUnit.locationID
    ORDER BY avgAlcoholUse DESC
    LIMIT 20
    ''', conn);

df5 = pd.read_sql('''
    SELECT locationDescription AS state, ROUND(AVG(d1.dataValue),0) AS percentObesity, ROUND(AVG(d2.dataValue),0) AS tvViewing
    FROM DataUnit d1, DataUnit d2, location l
    WHERE d1.locationId = l.locationID AND d2.locationId = l.locationID AND d1.questionID in (
        SELECT questionId FROM question
        WHERE question LIKE '%obesity among high school students%'
    ) AND d2.questionID in (
        SELECT questionId FROM question
        WHERE question LIKE '%television viewing among high school students%'
    )

    GROUP BY d1.locationID

    ''', conn);

#figure 1
fig = px.bar(df, x="estMortalityRate", y="locationDescription", orientation='h',
    title='Mortality from Heart Failure in the US By State');
fig.update_traces(marker_color='#42c5f5');
fig.update_layout(
    font_family="Poppins",
    font_color="gray",
    title_font_family="Poppins",
    title_font_color="#42c5f5",
)
#fig.show();
fig.write_html("final-dashboard/assets/plot.html")


#figure 2
fig2 = px.choropleth(df2, locations="state", locationmode="USA-states", color="avgVaccinationRate", scope="usa",
title='Average Influenza Vaccination Rate in the US By State (2010-2015)', color_continuous_scale=["#cbf7cf","#89faf2", "#180de0"])
fig2.update_layout(
    font_family="Poppins",
    title_font_family="Poppins",
    title_font_color="#42c5f5",
)
#fig2.show();
fig2.write_html("final-dashboard/assets/plot2.html")

#figure 3
fig3 = px.funnel(df3, x='AgeAdjustedAnnualRate', y='question', title='Leading Causes of Death in the US By State (2010-2015)')
fig3.update_layout(
    font_family="Poppins",
    title_font_family="Poppins",
    title_font_color="#42c5f5"
)
fig3.update_traces(marker_color='#42c5f5');
#fig3.show();
fig3.write_html("final-dashboard/assets/plot3.html")

#figure 4

fig4 =  px.pie(df4, values='avgAlcoholUse', names='state', title='Top 20 States For Alcohol Consumption (2010-2015)')

fig4.update_layout(
    font_family="Poppins",
    title_font_family="Poppins",
    title_font_color="#42c5f5"
)

#fig4.show();
fig4.write_html("final-dashboard/assets/plot4.html")

#figure 5

fig5 =  px.scatter(df5, x="tvViewing", y="percentObesity",
	         size="percentObesity", color="state",
                 hover_name="state", log_x=True, size_max=36, title='Adolescent Television Use and Obesity in the US By State (2010-2015)', trendline="ols")

fig5.update_layout(
    font_family="Poppins",
    title_font_family="Poppins",
    title_font_color="#42c5f5"
)

#fig5.show();
fig5.write_html("final-dashboard/assets/plot5.html")

conn.close();
