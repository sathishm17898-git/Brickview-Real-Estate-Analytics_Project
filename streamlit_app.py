#Importing necessary libraries
import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
from sqlalchemy import text

#Setting the page layout
st.set_page_config(layout='wide')

#Setting up the interface of the app
st.title("Real Estate Listing Dashboard")

#Importing the required datasets
#For this dashboard creation it require listing(Listing_ID,Agent_ID), agents(Agent_ID), sales(Listing_ID)
listing = pd.read_json("D:/Sathish/AIML/BrickView Real Estate Analytics Platform/listings_final_expanded.json")
prop_attri = pd.read_json("D:/Sathish/AIML/BrickView Real Estate Analytics Platform/property_attributes_final_expanded.json")
agents = pd.read_json("D:/Sathish/AIML/BrickView Real Estate Analytics Platform/agents_cleaned.json")
sales = pd.read_csv("D:/Sathish/AIML/BrickView Real Estate Analytics Platform/sales_cleaned.csv")
buyers = pd.read_json("D:/Sathish/AIML/BrickView Real Estate Analytics Platform/buyers_cleaned.json")

#Renaming a column name
prop_attri = prop_attri.rename(columns={'listing_id':'Listing_ID'})

#Creating a Month variable in Listing data
listing['Month'] = pd.to_datetime(listing['Date_Listed']).dt.strftime('%b')
sales['SMonth']=pd.to_datetime(sales['Date_Sold']).dt.strftime("%b")

#Merging all the dataframe
list_prop=pd.merge(listing,prop_attri,how='inner',on='Listing_ID')
list_prop_ag = pd.merge(list_prop,agents,how='inner',on='Agent_ID')
df=pd.merge(list_prop_ag,sales, how='left',on='Listing_ID')
df['Date_Listed']=pd.DatetimeIndex(df['Date_Listed'])
df['Date_Sold']=pd.DatetimeIndex(df['Date_Sold'])


#All SQL queries are stored in a dictionary with Question as the key and the code as the query
queries = {
    "Average listing price by city":"select City,avg(price) as Average_Price from listing group by city order by Average_Price",
    "Average price per square foot by property type?":"select Property_Type, avg(Price/Sqft) as Average_Price_persqft from listing group by Property_type order by Average_Price_persqft",
    "How Furnishing status impact property prices?":"select furnishing_status, avg(Price) as Price from listing inner join prop_attri on listing.Listing_ID=prop_attri.listing_id group by furnishing_status order by Price desc;",
    "Do property closer to metro stations command higher prices?":
    "select metro_distance_km as Metro_Distance,avg(price) as Average_Price from listing inner join prop_attri on listing.Listing_ID=prop_attri.listing_id group by metro_distance_km order by metro_distance_km, Average_Price desc;",
    "Rented properties price differently from non-rented ones":"select is_rented as Rented, avg(Price) as Average_Price from listing inner join prop_attri on listing.Listing_ID=prop_attri.listing_id group by Rented order by Average_Price desc;",
    "How do bed rooms and bath rooms affect price?":
    "select bedrooms as Bedroom, bathrooms as Bathroom, avg(Price) as Average_Price from listing inner join prop_attri on listing.Listing_ID=prop_attri.listing_id group by Bedroom, Bathroom order by Bedroom, Average_Price asc",
    "Do properties with parking and powerbackup selling at higher costs?":
    "select parking_available as Parking, power_backup as Power_backup, avg(price) as Avg_Price from listing inner join prop_attri on listing.Listing_ID=prop_attri.listing_id group by Parking, Power_backup order by Parking, Avg_Price asc",
    "Do built year influence listing price?":
    "select year_built as Year, avg(Price) as Avg_Price from listing inner join prop_attri on listing.Listing_ID=prop_attri.listing_id group by Year order by Year asc",
    "Which Cities has the highest median property prices?":
    "with med as (select City, Price,row_number() over(partition by City order by Price) as Rownum,count(*) over(partition by City) as total_count from listing) select City, avg(Price) as Median_Value \
    from med where Rownum in (floor((total_count+1)/2),ceil((total_count+1)/2)) group by City order by avg(Price) asc",
    "Average days on market by city":"select City, avg(Days_on_Market) as Avg_days from listing inner join sales on listing.Listing_ID=sales.Listing_ID group by City order by Avg_days",
    "Which Property types sell the fast?":
    "with pr_fa as (select s.Date_Sold, l.Date_Listed, l.Property_Type from sales s inner join listing l on l.Listing_ID=s.Listing_ID) select Property_Type, Date_Listed, Date_Sold, \
    datediff(Date_Sold, Date_Listed) as days from pr_fa order by days desc;",
    "What is the sale to list price ratio by city?":
    "with pr_fa as (select s.Sale_Price, l.Price, l.City from sales s inner join listing l on l.Listing_ID=s.Listing_ID) select City, avg(Sale_Price/Price) as Ratio \
    from pr_fa group by City order by Ratio",
    "Which listing took more than 90 days to sell":
    "with pr_fa as (select s.Date_Sold, l.Date_Listed, l.City, l.Listing_ID from sales s inner join listing l on l.Listing_ID=s.Listing_ID) select Listing_ID, City, \
    datediff(Date_Sold, Date_Listed) as days from pr_fa where datediff(Date_Sold, Date_Listed)>90;",
    "What is the monthly sales trend?":
    "select DATE_FORMAT(Date_Sold, '%%m') as month, count(*) as Total_Sales from sales group by DATE_FORMAT(Date_Sold, '%%m') order by month",
    "How does metro distance affect time on market?":
    "with m_d as (select p.listing_id, p.metro_distance_km, s.Sale_Price from prop_attri p inner join sales s on p.listing_id=s.Listing_ID) select listing_id, metro_distance_km, Sale_Price \
    from m_d order by metro_distance_km, Sale_Price",
    "Which properties are currently unsold?":
    "with pr_un as (select l.Listing_ID, l.Property_Type, l.Date_Listed, s.Date_Sold from Listing l left join sales s on l.Listing_ID=s.Listing_ID) select Property_Type, count(*) as Total_unsold \
    from pr_un where Date_Sold is NULL group by Property_Type order by Total_unsold",
    "Which agents have closed the most sales":
    "select ag.Agent_ID, ag.Name, ag.Email as Email, ag.deals_closed as Deal from agents ag order by Deal desc limit 5",
    "Top agents by total sales revenue":
    "with revenue as (select ag.Agent_ID, ag.Name, ag.Email, l.Listing_ID from agents as ag inner join listing as l on l.Agent_ID = ag.Agent_ID) select r.Agent_ID, r.Name, r.Email, s.Sale_Price \
    from revenue as r inner join sales as s on s.Listing_ID=r.Listing_ID order by s.Sale_Price desc limit 10;",
    "Which agents close deals fast?":
    "select ag.Agent_ID, ag.Name, ag.Email, ag.avg_closing_days from agents ag order by ag.avg_closing_days asc limit 5;",
    "Does experience correlated with deals closed?":
    "select experience_years as Exp, avg(deals_closed) as Avg_Deals_closed from agents group by Exp order by Exp asc",
    "Do agents with high rating close deal faster?":
    "select rating, avg(deals_closed) as Avg_Deals_closed from agents group by rating order by rating",
    "What is the average commission earned by each agent":
    "select ag.Agent_ID, ag.Name, avg(ag.commission_rate) as Commission_rate from agents as ag group by ag.Agent_ID,ag.Name order by Commission_rate",
    "Which agents have the most active listing?":
    "select Agent_ID, count(*) as total_listing from listing group by Agent_ID order by total_listing limit 1",
    "Average loan amount by buyer type?":
    "select buyer_type as Buyer_type,avg(loan_amount) as Avg_Loan_amt from buyers group by buyer_type order by Buyer_type",
    "Which payment mode is commonly used?":
    "select payment_mode as Payment_mode,count(*) as Frequency from buyers group by Payment_mode order by Frequency"
    }

#Adding the select all and deselect button
if "city_selected" not in st.session_state:
    st.session_state.city_selected = ['New York']

if "prop_selected" not in st.session_state:
    st.session_state.prop_selected = ['Apartment']

if "agent_selected" not in st.session_state:
    st.session_state.agent_selected = ['Agent A0003']

#Setting the Navigation page
st.sidebar.title("Page Navigation")
pages = st.sidebar.radio(
        "Go to",
        ['Home','Dashboard','Datasets/Queries']
    )

#Adding the sidebar filters
if pages == "Home":
     st.subheader("Introduction to the Project")
     st.write("Real estate is a market where prices of the property and demand varies dynamically. Buyers, sellers and agents lack accessible tools to monitor it shifts and trends in prices.")
     st.markdown("""
        - This project aims to build a Real Estate Listings Dashboard that uses SQL and Streamlit to:
        - Analyze property listings, agent performance, and sales patterns
        - Provide insights into pricing, time on market, and property types
        - Enable filtering by location, property type, price, and sales agent
        - Display interactive visuals like maps and bar charts for better understanding
        - There are 5 datasets are provided from the client.  A standard data exploration done before analyzing the dataset to identify the data discrepancies.
        - All the queries raised by the client are addressed through SQL.
     Tools: Python, SQL, Streamlit"
""")
     

elif pages == 'Dashboard':
    with st.sidebar:
        st.markdown("**Filters**")
        city_filter = st.multiselect(
            "**Select City:**",
            options = sorted(df['City'].unique()),
            default = st.session_state.city_selected)
        if st.sidebar.button("Select all City"):
            st.session_state.city_selected = list(df['City'].unique())
        if st.sidebar.button("Deselect all City"):
            st.session_state.city_selected = []
        st.markdown("---")
        prop_type = st.multiselect(
            "**Select the Property type:**",
            options = sorted(df['Property_Type'].unique()),
            default = st.session_state.prop_selected)
        if st.sidebar.button("Select all Property type"):
            st.session_state.prop_selected = list(df['Property_Type'].unique())
        if st.sidebar.button("Deselect all Property type"):
            st.session_state.prop_selected = []
        st.markdown("---")
        price_range = st.slider(
            "**Select the Price range:**",
            min_value = int(df['Price'].min()),
            max_value = int(df['Price'].max()),
            value = (int(df['Price'].min()),int(df['Price'].max())))
        st.markdown("---")
        agent_name = st.multiselect(
            "**Select the Agent Name:**",
            options = sorted(df['Name'].unique()),
            default = st.session_state.agent_selected)
        if st.sidebar.button("Select All agent"):
            st.session_state.agent_selected = list(df['Name'].unique())
        if st.sidebar.button("Deselect All agent"):
            st.session_state.agent_selected = []
        st.markdown("---")
        start_date,end_date=st.date_input(
            "**Select the Date:**",
            [df['Date_Listed'].min().date(),df['Date_Listed'].max().date()])
        
    filter_df = df[(df['City'].isin(city_filter)) & (df['Property_Type'].isin(prop_type)) & (df['Price'].between(price_range[0],price_range[1])) \
    & (df['Name'].isin(agent_name)) & (df['Date_Listed'].dt.date>=start_date) & (df['Date_Listed'].dt.date<=end_date)]

    #Main dashboard layout
    with st.container():
        col1, col2 = st.columns(2)

    with col1:
        #--Bar Chart--#
        st.markdown("**Average Prices by City**")
        fig1 = px.bar(filter_df,x="City",y="Price", color = "City",color_discrete_sequence=["#FF5733", "#33C1FF"])
        fig1.update_layout(height = 400)
        st.plotly_chart(fig1,use_container_width=True)
        
        #Map
        filter_df = filter_df.rename(columns={'Latitude':"lat","Longitude":"lon"})
        st.markdown("**Property Map**")
        st.map(filter_df)

    with col2:
        #Line chart
        l_per_month = listing.groupby('Month').size().reset_index(name='list_count')
        s_per_month = sales.groupby("SMonth").size().reset_index(name="sale_count")
        monthly = pd.merge(l_per_month,s_per_month,left_on = 'Month',right_on='SMonth',how='outer')
        monthly['month']=monthly['Month'].combine_first(monthly['SMonth'])
        monthly = monthly[['month','list_count','sale_count']]
        month_order = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
        monthly['month']=pd.Categorical(monthly['month'],categories = month_order,ordered=True)
        monthly=monthly.sort_values('month')
        st.markdown("**Montly listing and Sales trend**")
        fig3 = px.line(monthly, x = 'month',y=['list_count','sale_count'], markers=True)
        st.plotly_chart(fig3,use_container_width=True)

        #Pie Chart
        st.markdown("**Distribution of Property type**")
        prop_dist = filter_df['Property_Type'].value_counts().reset_index()
        prop_dist.columns=['Property_Type','Frequency']
        fig2 = px.pie(
            prop_dist,
            names = "Property_Type",
            values = "Frequency")
        st.plotly_chart(fig2,use_container_width=True)


else:
    st.write("This page shows the dataset")
    engine = create_engine("mysql+pymysql://root:123456789o@localhost/real_estate")
    sort_col = st.selectbox("Sorting column",df.columns)
    sort_order = st.radio("Order",['Ascending','Descending'])
    df_sorted = df.sort_values(by = sort_col,ascending=(sort_order=="Ascending"))
    #Pagination setup
    page_size = st.selectbox("Rows per page",[10,20,30,40,50,80],index=0) #define how many rows to be appear in a single page
    total_pages = (len(df_sorted)-1)//page_size+1 #total number of pages required according to the page_size
    page = st.number_input("Page",min_value=1,max_value=total_pages,step=1)
    start = (page-1)*page_size
    end = start+page_size
    df_page = df_sorted.iloc[start:end]
    st.dataframe(df_page, use_container_width=True)
    selected_query = st.selectbox("Select the query",list(queries.keys()))
    sql = queries[selected_query]
    x = pd.read_sql(sql,con=engine)
    st.dataframe(x, use_container_width=True)

##########################################################################################################################################################################