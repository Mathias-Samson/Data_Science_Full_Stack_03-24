import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import requests

### Config
st.set_page_config(
    page_title="Getaround",
    page_icon="🚗",
    layout="wide"
)

### App
st.title("🚗 Getaround app")

st.markdown("""
    You will find in this dashboard below info about the "delay before rebooking"
""")

st.markdown("---")


# Use `st.cache_data` when loading data is extremely useful
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
data_load_state.text("") # change text from "Loading data..." to "" once the load_data function has run

# Calculate proportions
mobile_rentals = dataset[dataset["checkin_type"] == "mobile"]
prop_mobile = (dataset["checkin_type"] == "mobile").sum() / len(dataset) * 100
connect_rentals = dataset[dataset["checkin_type"] == "connect"]
prop_connect = (dataset["checkin_type"] == "connect").sum() / len(dataset) * 100

prop_two_rentals = (dataset["previous_ended_rental_id"] > 0).sum() / len(dataset) * 100
two_or_more_rentals = dataset[dataset["previous_ended_rental_id"] > 0]


# Display metrics
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total car reservations", dataset.shape[0])
col2.metric("Percentage of mobile checkin", f"{prop_mobile.round(1)}%")
col3.metric("Proportion of connect checkin", f"{prop_connect.round(1)}%")
col4.metric("Proportion of rebooked cars", f"{prop_two_rentals.round(1)}%")

st.markdown("---")

st.header("""
    Statistics about delay and time delta between two rentals 🕐
""")

# Create two columns
col1, col2 = st.columns([2,8])

with col1:
    prop_late_drivers = (dataset["delay_at_checkout_in_minutes"] > 0).sum() / len(dataset) * 100   
    prop_mobile_late = (mobile_rentals["delay_at_checkout_in_minutes"] > 0).sum() / len(mobile_rentals) * 100 
    prop_connect_late = (connect_rentals["delay_at_checkout_in_minutes"] > 0).sum() / len(connect_rentals) * 100 
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"""
        <div style="text-align: center;">
            <p>Percentage of late drivers</p>
            <h3> {prop_late_drivers.round(1)}%</h3>
        </div>
    """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"""
        <div style="text-align: center;">
            <p>Percentage of late mobile drivers</p>
            <h3> {prop_mobile_late.round(1)}%</h3>
        </div>
    """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"""
        <div style="text-align: center;">
            <p>Percentage of late connect drivers</p>
            <h3> {prop_connect_late.round(1)}%</h3>
        </div>
    """, unsafe_allow_html=True)

with col2:
    fig_hist = go.Figure()

    fig_hist.add_trace(go.Histogram(
        x=mobile_rentals["time_delta_with_previous_rental_in_minutes"],
        name='Mobile',
        marker_color='blue',
        opacity=0.75
    ))

    fig_hist.add_trace(go.Histogram(
        x=connect_rentals["time_delta_with_previous_rental_in_minutes"],
        name='Connect',
        marker_color='red',
        opacity=0.75
    ))

    fig_hist.update_layout(
        title={
            'text': 'Distribution of Time Delta vs next rental (scope)',
            'x': 0.5,
            'xanchor': 'center'
        },
        xaxis_title='Time Delta (minutes)',
        yaxis_title='Transaction qty',
        barmode='stack',
        height=500,
        legend=dict(
            x=1,
            y=0.5,
            xanchor='left',
            yanchor='middle',
            orientation='v'
        )
    )

    st.plotly_chart(fig_hist)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("""
    Almost 50% of rentals are brought back late.
    It is hard to know at what point the owner has knowledge and agrees with the delay.
            
    We can notice on another hand that the time delta between two rentals is often less than 2 hours,
    which is critical in case of delay from the previous renter.
""")

st.markdown("---")

st.header("""
    What is the impact of delay on rentals and cancellations?
""")

# Create two columns for delay impact
col1, col2 = st.columns([2,8])

with col1:
    # Delay impact on rentals
    delay_delay = (two_or_more_rentals["delay_at_checkout_in_minutes"] > two_or_more_rentals["time_delta_with_previous_rental_in_minutes"]).sum() / len(two_or_more_rentals) * 100
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"""
        <div style="text-align: center;">
            <p>Rentals brought after<br>next rental beggining</p>
            <h2>{delay_delay.round(1)}%</h2>
        </div>
    """, unsafe_allow_html=True)
    
    problematic_cases = (two_or_more_rentals["state"] == "canceled").sum() / len(two_or_more_rentals) * 100
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"""
        <div style="text-align: center;">
            <p>Percentage of canceled rentals<br>due to delay</p>
            <h2>{problematic_cases.round(1)}%</h2>
        </div>
    """, unsafe_allow_html=True)

with col2:
    # Plot cumulative frequency
    dataset_pb = two_or_more_rentals.loc[two_or_more_rentals["state"] == "canceled"]
    mobile_pb = dataset_pb[dataset_pb["checkin_type"] == "mobile"]
    connect_pb = dataset_pb[dataset_pb["checkin_type"] == "connect"]

    def plot_cumulative_frequency(data, label, color):
        sorted_data = np.sort(data)
        cumul_counts = np.arange(1, len(sorted_data) + 1)
        return go.Scatter(x=sorted_data, y=cumul_counts, mode='lines', name=label, line=dict(color=color))

    fig_cumulative = go.Figure()

    fig_cumulative.add_trace(plot_cumulative_frequency(two_or_more_rentals['time_delta_with_previous_rental_in_minutes'], 'Total', 'white'))
    fig_cumulative.add_trace(plot_cumulative_frequency(mobile_rentals['time_delta_with_previous_rental_in_minutes'], 'Mobile', 'blue'))
    fig_cumulative.add_trace(plot_cumulative_frequency(connect_rentals['time_delta_with_previous_rental_in_minutes'], 'Connect', 'green'))
    fig_cumulative.add_trace(plot_cumulative_frequency(mobile_pb['time_delta_with_previous_rental_in_minutes'], 'Mobile Cancelled', 'orange'))
    fig_cumulative.add_trace(plot_cumulative_frequency(connect_pb['time_delta_with_previous_rental_in_minutes'], 'Connect Cancelled', 'red'))

    fig_cumulative.update_layout(
        title={
            'text': 'Cumulative amount of transactions with a given Time Delta Between Rentals (300min max)',
            'x': 0.5,
            'xanchor': 'center'
        },
        xaxis_title='Time Delta (minutes)',
        yaxis_title='Cumulative transaction qty',
        xaxis=dict(range=[0, 300]),
        yaxis=dict(range=[0, 1000]),
        legend=dict(
            x=1,
            y=0.5,
            xanchor='left',
            yanchor='middle',
            orientation='v'
        )
    )

    st.plotly_chart(fig_cumulative)  

st.markdown("""
We can see that in the case where the owner have a second reservation for its car,
around 15% of the cars are deposited later than the time where next rental beggins.
When it happens, the next renter cancels its reservation very often.
There is not a big difference between the type of connection for this phenomenon.
""")

st.markdown("---")

st.header("""
    Analysis
""") 
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("""
    The issue seams serious, even if the proportion of rebooked cars is low, 
    when it is the case more than 10% of cancels due to delay is something to improve.
    

    The problem is that a almost a third of rebooked cars have less than 2hrs delta between the twor rentals.
    It is a risk to loose these transactions because of a potential gain that represent approx 10% of the transaction volume.       
            
    We cannot evaluate the financial impact for the owners with our dataset, but we could maybe try a different approach :  
    * Warning the next renter when he chooses a time to pick up the car too close from the return 
    * Penalising renters that allow low delta times between rentals
""")
