#created 25Jul2021 by dondemici

from _plotly_utils.colors import colorscale_to_colors
from matplotlib.pyplot import xlabel
import mysql.connector
import pandas as pd
import os  
import numpy as np 
import seaborn as sns
from seaborn.palettes import color_palette; sns.set_theme()

from datetime import datetime
import datetime as dt
import plotly.express as px
import plotly.graph_objects as go

import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output

#Connect to MySQL
mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="r!s3@b0V3",
  database="cooee_db"
)

#1 Revenue by Nation (METHOD - SQL Driven)
query = "SELECT nation.n_name AS Nation, sum(orders.o_totalprice) as Revenue \
    FROM orders \
    LEFT JOIN customers ON orders.o_custkey=customers.c_custkey \
    LEFT JOIN nation ON customers.c_nationkey=nation.n_nationkey \
    GROUP BY customers.c_nationkey \
    ORDER BY sum(orders.o_totalprice) DESC \
    LIMIT 5"
df = pd.read_sql(query, mydb)
df['Revenue'] = pd.to_numeric(df['Revenue'])

#Bar Chart 1
Revenue_by_Nation = px.bar(df,y = 'Revenue', x = 'Nation', 
             color = 'Nation', barmode='stack',
             height=500, text='Revenue',
             color_discrete_sequence=[px.colors.qualitative.Plotly[3], 
             px.colors.qualitative.Plotly[0], px.colors.qualitative.T10[2], px.colors.qualitative.Plotly[2]],
             title="Revenue of Top 5 Nations",
             template="simple_white"
             )
Revenue_by_Nation.update_traces(texttemplate='%{text:.2s}', textposition='outside')
Revenue_by_Nation.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')


#2 Shipping Mode by Nation (METHOD - SQL Driven)
query2 = "SELECT l_shipmode AS Ship_Mode, COUNT(*) AS Mode_Count FROM lineitem \
    LEFT JOIN supplier ON lineitem.l_ps_id=supplier.s_suppkey \
    LEFT JOIN nation ON supplier.s_nationkey=nation.n_nationkey \
    WHERE nation.n_name IN ('CANADA','EGYPT','IRAN','BRAZIL','ALGERIA') \
    GROUP BY lineitem.l_shipmode \
    ORDER BY COUNT(*) DESC"
df2 = pd.read_sql(query2, mydb)
df2['Mode_Count'] = pd.to_numeric(df2['Mode_Count'])


#Bar Chart 2
Shipping_Mode_by_Nation = px.bar(df2, x="Mode_Count", y="Ship_Mode", orientation='h',
    title="Shipping Mode of Top 5 Nations", color="Ship_Mode", height=500, template="simple_white")


#3 Top Selling Months (METHOD - Python Driven)
orders = "SELECT orders.o_orderdate AS Order_Date, orders.o_totalprice as Revenue FROM orders"
dfraw = pd.read_sql(orders, mydb)
df3 = pd.read_sql(orders, mydb)
df3['Revenue'] = pd.to_numeric(df3['Revenue'])

df3['Month No.'] = df3['Order_Date'].str[3:5]
df3['Month'] = pd.to_datetime(df3['Month No.'], format='%m').dt.month_name().str.slice(stop=3)
df3['Year'] = df3['Order_Date'].str[6:10]
df3['Day'] = df3['Order_Date'].str[0:2]
df3['Order_Date'] = df3['Day'] + "-" + df3['Month'] + "-" + df3['Year']
df3['Order_Date'] = pd.to_datetime(df3['Order_Date'])
df3['Year Order'] = df3['Order_Date'].dt.isocalendar().year
df3['Month Order'] = df3['Order_Date'].dt.to_period('m')

df3a = (df3.loc[:100000,["Year Order","Month","Revenue"]])
df3a = df3a.sort_values(['Revenue'], ascending=False)

#df3 = (df3.loc[:100000,["Year","Month No.","Month","Revenue"]])  
df4 = df3.pivot_table(  
    values=['Revenue'], 
    index=['Month No.','Month'],columns='Year', 
    aggfunc=np.sum 
).reset_index()


#Seaborn
df_m = df3.groupby(["Month No.", "Year"]).sum().unstack(level=0)
#sns.heatmap(df_m, cmap="Spectral")
#plt.show()

#Plotly
df3c = df3.groupby(["Year Order", "Month No."]).sum().unstack(level=0)
Top_Selling_Months = px.imshow(df3c, title="Top Selling Months",
    labels=dict(x="Year", y="Month"),
    x=['1992', '1993', '1994', '1995', '1996', '1997','1998'],
    y=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun','Jul','Aug','Sep','Oct','Nov','Dec'],
    color_continuous_scale=px.colors.sequential.Cividis_r)
#fig.show()


#4B Top Customers by Revenue
customersr = "SELECT customers.c_name AS Customer_Name, sum(orders.o_totalprice) as Revenue \
    FROM orders \
    LEFT JOIN customers ON orders.o_custkey=customers.c_custkey \
    GROUP BY customers.c_name \
    ORDER BY sum(orders.o_totalprice) DESC \
    LIMIT 10"
df6 = pd.read_sql(customersr, mydb)
df6['Revenue'] = pd.to_numeric(df6['Revenue'])

Top_Customers_by_Revenue = px.pie(df6, values='Revenue', names='Customer_Name', labels='Customer_Name',
    title='Top Customers by Revenue', hole=.3, color_discrete_sequence=px.colors.sequential.RdBu)
#Top_Customers_by_Revenue.show()


#4B Top Customers by Quantity
customersq = "SELECT customers.c_name AS Customer_Name, sum(lineitem.l_quantity) as Quantity \
    FROM lineitem \
    LEFT JOIN orders ON lineitem.l_orderkey=orders.o_orderkey \
    LEFT JOIN customers ON orders.o_custkey=customers.c_custkey \
    GROUP BY customers.c_name \
    ORDER BY sum(orders.o_totalprice) DESC \
    LIMIT 10"
df7 = pd.read_sql(customersq, mydb)
df7['Quantity'] = pd.to_numeric(df7['Quantity'])
Top_Customers_by_Quantity = px.pie(df7, values='Quantity', names='Customer_Name', 
    title='Top Customers by Quantity', hole=.3, color_discrete_sequence=px.colors.sequential.RdBu)
#Top_Customers_by_Quantity.show()


#4C Top Customers by Revenue and Quantity
#Orders data contains only 1 Order Key which inidicates total price. Line Item has multiple Order Keys. 



#5 Year on Year Change
orders = "SELECT orders.o_orderdate AS Order_Date, orders.o_totalprice as Revenue FROM orders"
df20 = pd.read_sql(orders, mydb)
df20['Revenue'] = pd.to_numeric(df20['Revenue'])

df20['Month No.'] = df20['Order_Date'].str[3:5]
df20['Month'] = pd.to_datetime(df20['Month No.'], format='%m').dt.month_name().str.slice(stop=3)
df20['Year'] = df20['Order_Date'].str[6:10]
df20['Day'] = df20['Order_Date'].str[0:2]
df20['Order_Date'] = df20['Day'] + "-" + df20['Month No.'] + "-" + df20['Year']
df20['Order_Date'] = pd.to_datetime(df20['Order_Date'])
df20['Year Order'] = df20['Order_Date'].dt.isocalendar().year
df20['Month Order'] = df20['Order_Date'].dt.to_period('m')

df21 = (df20.loc[:100000,["Month Order","Revenue"]])
df21['Month Order'] = df21['Month Order'].astype(str)
df21 = df21.groupby(by="Month Order").sum().reset_index()

df21['OTM'] = df21['Revenue'].pct_change()
df21['OYM'] = df21['Revenue'].pct_change(12)
#df22 = (df21.iloc[:100000,[1,4]])
#print(df22)
Period_Change = px.line(df21, x="Month Order", y="OYM", title='Sales Revenue Period Change')
#Period_Change.show()


#Generate Output 
dir_name=(r'C:\Users\Dundee Adriatico\Documents\2021\Business Engineering\Data Engineer Test\TBL Files')  
outputfile = ('Revenue by Month.xlsx')  
outfileloc = os.path.join(dir_name, outputfile)  
writer = pd.ExcelWriter(outfileloc)
dfraw.to_excel(writer, sheet_name = 'Raw')
df3a.to_excel(writer, sheet_name = 'Top Selling Months')    
df4.to_excel(writer, sheet_name = 'Pivot') 
df_m.to_excel(writer, sheet_name = 'Pivot II')
df21.to_excel(writer, sheet_name = 'OTM OYM')  
writer.save()


# REPORTING
# app = JupyterDash(__name__)
app = dash.Dash()
figs = ['Revenue_by_Nation','Shipping_Mode_by_Nation',
    'Top_Selling_Months','Top_Customers_by_Revenue','Top_Customers_by_Quantity','Period_Change']
app.layout = html.Div([
    html.Div([
        html.Div([
        html.H1("ETL Data Analysis"),
        dcc.Dropdown(
                id='variables',
                options=[{'label': i, 'value': i} for i in figs],
                value=figs[0]
            ),
        dcc.Graph(id='plot')

        ])
    ])
])
@app.callback(
    Output('plot', 'figure'),
    [Input('variables', 'value')])
def update_graph(fig_name):
    if fig_name == 'Revenue_by_Nation':
        return Revenue_by_Nation
    if fig_name == 'Shipping_Mode_by_Nation':
        return Shipping_Mode_by_Nation
    if fig_name == 'Top_Selling_Months':
        return Top_Selling_Months
    if fig_name == 'Top_Customers_by_Revenue':
        return Top_Customers_by_Revenue
    if fig_name == 'Top_Customers_by_Quantity':
        return Top_Customers_by_Quantity
    if fig_name == 'Period_Change':
        return Period_Change

# app.run_server(mode='external', debug=True)
app.run_server(debug=True,
           use_reloader=False # Turn off reloader if inside Jupyter
          ) 