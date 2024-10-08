import streamlit as st
import plotly.express as px
import pandas as pd
import os
import matplotlib.pyplot as plt
from streamlit_option_menu import option_menu
import time
from streamlit_extras.metric_cards import style_metric_cards

import warnings
warnings.filterwarnings('ignore')

st.set_page_config(page_title="Dashboard", page_icon=":chart_with_upwards_trend:", layout="wide")
st.title(":chart_with_upwards_trend: Payment Dashboard")


# load Style css
st.markdown(
    """
    <style>
    body {
        background-color: #ffffff;  /* Light gray background */
    }
    [data-testid=metric-container] {
        box-shadow: 0 0 4px #686664;
        padding: 10px;
    }

    .plot-container>div {
        box-shadow: 0 0 2px #070505;
        padding: 5px;
        border-color: #000000;
    }

    div[data-testid="stExpander"] div[role="button"] p {
        font-size: 1.2rem;
        color: rgb(0, 0, 0);
        border-color: #000000;
        color-scheme: #000000;
    }

    .sidebar-content {
        color: white;
    }

    [data-testid=stSidebar] {
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True
)

def style_metric_cards(background_color="#333333", border_left_color="#444444", border_color="#555555", box_shadow="#000000"):
    st.markdown(
        f"""
        <style>
        div[data-testid="metric-container"] {{
            background-color: {background_color};
            border-left: 5px solid {border_left_color};
            border: 1px solid {border_color};
            box-shadow: 0 0 4px {box_shadow};
            padding: 10px;
            border-radius: 5px;
            color: #FFFFFF;  /* Text color for dark theme */
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

df = pd.read_csv("Untitled_report.csv")


st.sidebar.header("Please Filter Here: ")

# Convert created_date to datetime
df["created"] = pd.to_datetime(df["created"])

start_date = st.sidebar.date_input("Start date", df["created"].min())
end_date = st.sidebar.date_input("End date", df["created"].max())

# Ensure start_date and end_date are in datetime format
start_date = pd.to_datetime(start_date)
end_date = pd.to_datetime(end_date)

subscription = st.sidebar.multiselect(
    "Select the subscription: ",
    options=df["subscription"].unique(),
    default=df["subscription"].unique()
)



df_selection=df.query(
    "subscription == @subscription and created >= @start_date and created <= @end_date")

def Home():
    with st.expander("VIEW DATA"):
        showData=st.multiselect('Filter: ',df_selection.columns,default=['created','customer_id','email','phone','name', 'address_line1', 'address_line2', 'address_city', 'address_state', 'address_country', 'address_postal_code','subscription','automatic_tax_enabled','invoice_number','description','quantity','currency','line_item_amount','total_invoice_amount','discount','fee','tax','net_amount'])
        st.dataframe(df_selection[showData],use_container_width=True)

    #Total Transaction 
    total_transactions = df_selection["total_invoice_amount"].count()
    # Total net Amount 
    total_net_amount = df_selection["net_amount"].sum()
    # Total fee amount 
    total_fee_amount = df_selection["fee"].sum()
    # Total subscriptions sold (monthly, yearly) 
    total_sub = df_selection.dropna(subset=["subscription"])
    total_subscriptions_sold = total_sub["subscription"].count()

    total_tax =df_selection["tax"].sum()

    # unique customers
    unique_costomers = df["customer_id"].nunique()

    # Debugging: Display calculated values
    # st.write(f"Total Transactions: {total_transaction}")
    # st.write(f"Total Net Amount: {total_net_amount}")
    # st.write(f"Total Fee Amount: {total_fee_amount}")
    # st.write(f"Total Subscriptions Sold: {total_subscriptions_sold}")

    total1, total2, total3 = st.columns(3, gap='small')
    with total1:
        st.info('Total Tax Amount', icon="💰")
        st.metric(label="Total Tax", value=f"$ {total_tax:,.0f}")

    with total2:
        st.info('Total Net Amount', icon="💰")
        st.metric(label="Total Net Amount", value=f"$ {total_net_amount:,.0f}")

    with total3:
        st.info('Total Fee Amount', icon="💰")
        st.metric(label="Total Fee Amount", value=f"$ {total_fee_amount:,.0f}")
    
    total1, total2, total3 = st.columns(3, gap='small')

    with total1:
        st.info('Total Transactions')
        st.metric(label="Total Transactions", value=f" {total_transactions:,.0f}")

    with total2:
        st.info('Total Subscriptions Sold')
        st.metric(label="Total Subscriptions Sold", value=f"{total_subscriptions_sold:,.0f}")
    
    with total3:
        st.info('Total customers')
        st.metric(label="Total customers", value=f"{unique_costomers:,.0f}")


    style_metric_cards(background_color="#333333", border_left_color="#444444", border_color="#555555", box_shadow="#000000")
    #style_metric_cards(background_color="#FFFFFF",border_left_color="#686664",border_color="#000000",box_shadow="#F71938")
    # with st.expander("DISTRIBUTIONS BY FREQUENCY"):
    #    fig,ax = plt.subplots(figsize=(16,8))
    #    df_selection.hist(ax=ax, color='#898784', zorder=2, rwidth=0.9, legend=['Investment'])
    #    st.pyplot(fig)



def graphs():
    # Assuming 'df' is your DataFrame
    top5_subscriptions = df_selection.groupby("subscription")["net_amount"].sum().nlargest(5)
    # Convert the Series to a DataFrame for better display
    top5_subscriptions_df = top5_subscriptions.reset_index()

    # Create the pie chart
    fig1 = px.pie(top5_subscriptions_df, values=top5_subscriptions.values, names=top5_subscriptions.index, title="Top 5 Subscriptions by Net Amount")

    # Count the occurrences of each subscription type
    subscription_counts = df_selection["subscription"].value_counts()

    # Group by subscription and line item, then sum the charges
    grouped_df = df_selection.groupby(["subscription", "line_item_amount"])["line_item_amount"].count().reset_index(name="count")

    # Display the results
    fig2 = px.pie(grouped_df, values='count', names='subscription', title='Subscription and Line Item Amount Distribution')

    # Calculate total fees for each subscription
    total_fees = grouped_df.groupby("subscription")["line_item_amount"].sum()

    fig3 = px.line(
        total_fees,
        x=total_fees.index,
        y=total_fees.values,
        title='Total Fees by Subscription',
        labels={'x': 'Subscription Type', 'y': 'Total Fees'},
        markers=True
    )

    fig3.update_layout(
        xaxis_title='Subscription Type',
        yaxis_title='Total Fees',
        template='plotly_white'
    )


    # Ensure 'created' column is in datetime format
    df_selection['created'] = pd.to_datetime(df_selection['created'])

    # Group the data by month and sum the total invoice amounts
    df_selection['month'] = df_selection['created'].dt.to_period('M')
    df_monthly = df_selection.groupby('month')['total_invoice_amount'].sum().reset_index()

    # Convert the 'month' column back to datetime for plotting
    df_monthly['month'] = df_monthly['month'].dt.to_timestamp()

    # Group the data by month and sum the total invoice amounts
    df_selection['month'] = df_selection['created'].dt.to_period('M')
    df_monthly = df_selection.groupby('month')['total_invoice_amount'].sum().reset_index()

    st.markdown("---") 
    col1,col2 = st.columns(2)
    with col1:
        st.write("### Top 5 Subscriptions")
        st.plotly_chart(fig1)
    
    with col2:
        st.write("### Subscription counts")
        st.bar_chart(subscription_counts)

    st.markdown("---") 
    
    col1,col2 = st.columns(2)
    with col1:
        st.write("### Subscription and Line Item")
        st.plotly_chart(fig2)
    with col2:
        st.write("### Subscription Fees")
        st.plotly_chart(fig3)


def table2(df_selection):
    df2 = pd.read_csv("both_success_fail.csv")

    # Ensure 'created_date' column is present and in datetime format
    if 'created_date' in df2.columns:
        df2["created_date"] = pd.to_datetime(df2["created_date"])

        # Filter df2 based on the date range selected in the sidebar
        df2_filtered = df2[(df2["created_date"] >= start_date) & (df2["created_date"] <= end_date)]
    else:
        st.error("The 'created_date' column is missing from the dataset.")
        return  # Exit the function if the column is missing

    with st.expander("VIEW DATA"):
        showData=st.multiselect('Filter: ',df2_filtered.columns,default=['id', 'amount', 'amount_refunded', 'application_fee_id','balance_transaction_id', 'calculated_statement_descriptor', 'captured','created_date', 'currency', 'customer_id', 'description',
        'destination_id', 'dispute_id', 'failure_code', 'failure_message',
        'invoice_id', 'order_id', 'paid', 'captured_at', 'payment_intent',
        'receipt_email', 'receipt_number', 'refunded', 'statement_descriptor',
        'statement_descriptor_suffix', 'status', 'source_transfer_id',
        'transfer_id', 'transfer_group', 'application_id', 'source_id',
        'card_customer_id', 'card_recipient_id', 'card_tokenization_method',
        'outcome_network_status', 'outcome_reason', 'outcome_rule_id',
        'outcome_type', 'outcome_seller_message', 'outcome_risk_level',
        'outcome_risk_score'])
        st.dataframe(df2_filtered[showData],use_container_width=True)


    total_transactions = df2_filtered.shape[0]
    successful_transactions = df2_filtered[df2_filtered["status"] == "succeeded"].shape[0]
    failed_transactions = df2_filtered[df2_filtered["status"] == "failed"].shape[0]
    
    total1, total2, total3 = st.columns(3, gap='small')
    with total1:
        st.info('Total Transactions')
        st.metric(label="Total Transactions", value=f" {total_transactions:,.0f}")

    with total2:
        st.info('Number of successful transactions')
        st.metric(label="Number of successful transactions:", value=f"{successful_transactions:,.0f}")
    
    with total3:
        st.info('Number of failed transactions')
        st.metric(label="Number of failed transactions:", value=f"{failed_transactions:,.0f}")
    

    # Top 5 failure reasons as a bar chart
    failure_reasons = (df2_filtered["failure_code"].value_counts(normalize=True).head() * 100).round(2)

    # Create a DataFrame for Plotly
    failure_reasons_df = failure_reasons.reset_index()
    failure_reasons_df.columns = ['Failure Reason', 'Percentage']

    # Create the bar chart using Plotly
    fig = px.bar(failure_reasons_df, x='Failure Reason', y='Percentage', 
                title="Top 5 Failure Reasons", 
                labels={'Failure Reason': 'Failure Reason', 'Percentage': 'Percentage (%)'},
                text='Percentage')

    # Update layout for better visibility
    fig.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
    fig.update_layout(xaxis_title='Failure Reason', yaxis_title='Percentage (%)', xaxis_tickangle=340)  # Rotate x-axis labels

    # Display the Plotly chart
    st.plotly_chart(fig)

    # Most frequent refunded amounts
    refunded_amounts = df2_filtered[df2_filtered["amount_refunded"] > 0]["amount_refunded"].value_counts().head()
    st.subheader("Most Frequent Refunded Amounts")
    st.bar_chart(refunded_amounts)

    # Top 2 refunded line items
    refunded_line_items = df2_filtered[df2_filtered["refunded"] == True]["description"].value_counts()
    top_2 = refunded_line_items.head(2)
    other = refunded_line_items[2:].sum() if len(refunded_line_items) > 2 else 0
    top_2_with_other = pd.concat([top_2, pd.Series({'Other': other})])

    fig = px.pie(values=top_2_with_other, names=top_2_with_other.index, title="Top 2 Refunded Line Items and Others", 
                labels={'index': 'Refunded Items', 'values': 'Count'}, hole=0.3)

    st.plotly_chart(fig)

    
    


#menu bar
def sideBar():
    with st.sidebar:
        selected = option_menu(menu_title="Main Menu", options=["Home", "Table2"], icons=["house", "eye"], default_index=0)
    if selected == "Home":
        st.subheader(f"Page: {selected}")
        Home()
        graphs()
    if selected == "Table2":
        st.subheader(f"Page: {selected}")
        table2(df_selection)
    
sideBar()