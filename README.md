# Brickview-Real-Estate-Analytics_Project
A Real Estate Listings Dashboard built with SQL and Streamlit to analyze property features, pricing trends, and sales performance. It helps buyers, sellers, and agents explore market dynamics, study relationships between key indicators, and gain actionable insights through interactive visualizations.

  Project_1 is the python notebook file. Use this file to load all json files and sales.csv files and preprocess the data.
  In Project_1 sqlalchemy is used to migrate the datasets to MYSQL and queries are written to retrieve some information.
  Streamlit_app.py is a file where the analytical dashboard creation codes are written using the all json and sales.csv file. 
  Detailed Description in Python:
  Libraries used in this project: pandas, matplotlib, sqlalchemy, json, streamlit, plotly.
  EDA: There is no duplicate observations found in any of the datasets.  'floor_number' variable under 'prop_attri.json' dataset in that 248 observations found as outlier (above the upper fence) and these values are replaced by the mean of the 'floor_number'.  Correlation heatmap is constructed to identify is there any linear relationship between the numeric variables of the dataset and concluded that no relationship existed between the variables.
  SQL: create_engine function under the 'sqlalchemy' library used to create a database in the SQL.  Analyze property listings, agent performance, and sales patterns to find the insights in the pricing trends, time on market, distribution of property type.
  Streamlit: Enable filtering by location, property type, price, and sales agent to display the interactive Bar, line, Map, Pie charts for better understanding. Showed the analytical table by connecting dashboard with MySQL using the sqlalchemy to get insights on the real estate market performance by city, property, agents, infrastruture.
