import streamlit as st
import pandas as pd
import plotly.express as px 
import plotly.graph_objects as go
import numpy as np
import requests

### Config
st.set_page_config(
    page_title="Getaround analysis",
    page_icon="🚗 ",
    layout="wide"
)

### App
st.title("🚗 Getaround analysis")

st.markdown("""
    You'll find below elements to design the "delay before rebooking" getaround feature 👇
""")

st.markdown("---")


# Use `st.cache` when loading data is extremly useful
# because it will cache your data so that your app 
# won't have to reload it each time you refresh your app
@st.cache_data
def load_data():
    dataset = pd.read_excel('get_around_delay_analysis.xlsx')
    #
    #  Potential pre-processing here
    #
    return dataset

data_load_state = st.text('Loading data...')
dataset = load_data()
data_load_state.text("") # change text from "Loading data..." to "" once the the load_data function has run

df_no_canceled = dataset.loc[dataset['state'] != "canceled"]
df_no_canceled['late_by'] = df_no_canceled['delay_at_checkout_in_minutes'].apply(lambda x : max(x,0))

latencies = df_no_canceled['late_by'].value_counts().reset_index()
overtime = pd.DataFrame(columns=["nb_late","percent_late"])

df_no_canceled_short_delay = df_no_canceled.loc[df_no_canceled['time_delta_with_previous_rental_in_minutes'].notna()]
df_no_canceled_short_delay['late_by'].count(), df_no_canceled['late_by'].count()

df_no_canceled_short_delay['real_delta'] = df_no_canceled_short_delay['time_delta_with_previous_rental_in_minutes'] - df_no_canceled_short_delay['late_by']
real_latencies = df_no_canceled_short_delay['real_delta'].value_counts().reset_index()

#real_filtered_latencies = real_latencies.loc[(real_latencies["real_delta"] < 0) & (real_latencies["real_delta"] > -180)]

col1, col2, col3 = st.columns(3)
col1.metric("Total bookings", f"{dataset.shape[0]}")
col2.metric("Uncanceled rentals", f"{df_no_canceled.shape[0]}")
col3.metric("Next booking under 12h", f"{df_no_canceled_short_delay.shape[0]}")

st.markdown("---")

st.header("""
    What's the volume of rentals ending with delays ?
""")

#### Create two columns
col1, col2 = st.columns(2)

with col1:
    st.markdown("**1️⃣ Late vs booking**")

    for delay in range (6):
        filtered_latencies = latencies.loc[latencies["late_by"] > (60*delay)]
        overtime.loc[delay,"nb_late"] = filtered_latencies['count'].sum()
        overtime.loc[delay,"percent_late"] = round(100 * filtered_latencies['count'].sum() / df_no_canceled['late_by'].count(), 1)

    fig = px.area(overtime, y="nb_late")
    fig.update_layout(
        xaxis_title="hours late"
    )
    #fig.show()
    st.plotly_chart(fig, use_container_width=True)

    fig = px.area(overtime, y="percent_late")
    fig.update_layout(
        xaxis_title="hours late"
    )
    #fig.show()
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown("**1️⃣ Late vs next rental**")

    for delay in range (6):
        real_filtered_latencies = real_latencies.loc[(real_latencies["real_delta"] < 0) & (real_latencies["real_delta"] < (-60*delay))]
        overtime.loc[delay,"nb_real_late"] = real_filtered_latencies['count'].sum()
        overtime.loc[delay,"percent_real_late"] = round(100 * real_filtered_latencies['count'].sum() / df_no_canceled['late_by'].count(), 1)

    fig = px.area(overtime, y="nb_real_late")
    fig.update_layout(
        xaxis_title="hours late"
    )
    #fig.show()
    st.plotly_chart(fig, use_container_width=True)

    fig = px.area(overtime, y="percent_real_late")
    fig.update_layout(
        xaxis_title="hours late"
    )
    #fig.show()
    st.plotly_chart(fig, use_container_width=True)

st.markdown("""
    More than 50% of rentals are brought back late.
    Given the dataset, we can't know whether these late drop off have been discussed with the car owner or not.
            
    We should look at the "real late" drop off, meaning the drop off made after the start time for the next rental.
            
    We can see more than 15% of rental are deposited later than the next rental. The issue raised by Getaround looks serious.
""")

st.markdown("---")

st.header("""
    What's the volume of bookings impacted by a "Delay before next rental" feature ?
""")

df_no_canceled_hours_delay = df_no_canceled_short_delay.loc[df_no_canceled_short_delay['time_delta_with_previous_rental_in_minutes'] < 300]
df_no_canceled_mins_delay = df_no_canceled_short_delay.loc[df_no_canceled_short_delay['time_delta_with_previous_rental_in_minutes'] < 90]

col1, col2, col3 = st.columns(3)

col1.metric("Next booking under 6h", 
          f"{df_no_canceled_hours_delay.shape[0]}", 
          f"({round(100* df_no_canceled_hours_delay['real_delta'].count() / df_no_canceled['late_by'].count(), 2)} %)")
col2.metric("Next booking under 90min", 
          f"{df_no_canceled_mins_delay.shape[0]}", 
          f"({round(100* df_no_canceled_mins_delay['real_delta'].count() / df_no_canceled['late_by'].count(), 2)} %)")
col3.metric("90min / 6h delays", 
          f"{round(100*df_no_canceled_mins_delay.shape[0]/df_no_canceled_hours_delay.shape[0],1)} %",)

fig = px.histogram(df_no_canceled_hours_delay, y='time_delta_with_previous_rental_in_minutes', nbins=6)
#fig.show()
st.plotly_chart(fig, use_container_width=True)

st.markdown("""
    We can see 5.6% of uncanceled rentals start less than 6h after the previous rental's drop off time.
    Decreasing the threshold to rentals starting less than 90min after the previous rental's drop off time, we get 3% of all uncanceled rentals
    (it's still more than 50% of the 6h threshold)
""")

st.subheader("3% of rentals start less than 90min after the previous rental")

st.markdown("""
    Given "real late" dropoff less than 60min for the next rental reprents 0.8% of rentals (50% of all real late dropoffs)
    Setting a 90min delay between two bookings would make sure these 0.8% rentals happen smoothly.
    On the other side, 3% of all rentals would be affected.
            
    While this could mean a delay is a bad idea : gain 0.8% to loose 3%, avoiding these specific 3% bookings does NOT mean
    a loss of 3% of bookings. It just means "not showing these booking options", leading users to others booking options.
            
    While it's not possible with the given data to evaluate the impact of such a feature, we could design a smarter feature 
    which would :  
    - Remove the risk of loosing bookings 
    - Reduce the risk of "real late" dropoffs
    - Reduce the client insatisfaction on the rare case it still happens
    - Provide new data to deepen the analysis
            
    The feature would be:
    - Short delay with the previous rental are flagged
    - A warning is displayed to the user about the short delay risk 
    - Short delay booking options are penalized in the search engine
""")