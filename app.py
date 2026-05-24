import plotly.express as px
import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Uber Analytics", layout="wide",page_icon="🏎️")

df = pd.read_csv("Uber_data.csv")

# sidebar
with st.sidebar:
    selected = option_menu("Main Menu",["Dataset", "Overview", "Ride Analytics","Data Assistant"],
                           icons=["table", "bar-chart", "graph-up"],menu_icon="car-front",
                           default_index=1)

# dataset
if selected == "Dataset":
    st.title("Data Exploration")

    col1, col2, col3 = st.columns(3)
    col1.metric(label="Total Rows", value=df.shape[0])
    col2.metric(label="Total Columns", value=df.shape[1])
    col3.metric(label="Missing Values", value=df.isnull().sum().sum())

    st.divider()

    # column selection
    st.subheader("Select Columns")
    selected_columns = st.multiselect(
        label="Choose Columns",
        options=df.columns,
        default=df.columns
    )

    filtered_df = df[selected_columns]

    st.divider()

    # search dataset
    st.subheader("Search in Dataset")
    search = st.text_input("Search Data From Here")

    if search:
        filtered_df = filtered_df[
            filtered_df.astype(str).apply(
                lambda row: row.str.contains(search, case=False).any(),axis=1
            )]
    st.divider()

    # column filter - column name | value
    st.subheader("Column Filter")
    col1, col2 = st.columns(2)

    with col1:
        filter_column = st.selectbox("Select Column", filtered_df.columns)

    with col2:
        filter_value = st.selectbox("Select Value",filtered_df[filter_column].dropna().unique())

    if st.button("Apply Filter"):
        filtered_df = filtered_df[filtered_df[filter_column] == filter_value]

    st.divider()
    st.dataframe(filtered_df)
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button("Download Data",data=csv,file_name="Uber_filtered_data.csv",mime="text/csv")


    st.divider()
    # slider for show row data
    st.subheader("Row slider")
    row_num = st.slider("Select Row Index", min_value=1, max_value=df.shape[0])

    st.subheader("Row Preview")
    st.dataframe(filtered_df.iloc[row_num - 1])

if selected=="Overview":
    st.title("Dashboard Overview")
    col1,col2 = st.columns(2)
    col1.metric("Total Rides",len(df))
    col2.metric("Revenue",df["Booking Value"].sum())
    st.divider()
    total_rides=len(df)
    total_revenue = df["Booking Value"].sum()

    # business unit performance
    st.subheader("Business Unit Performance")
    bu_metrix=df.groupby("Vehicle Type").agg(
        Total_Booking=("Booking ID","count"),
        Revenue_Generated=("Booking Value","sum"),
        Avg_Distance=("Ride Distance","mean"),
        Av_Rating=("Customer Rating","mean")
    )

    bu_metrix["Revenue Share%"]=(bu_metrix["Revenue_Generated"]/total_revenue*100
                                 if total_revenue > 0 else 0)
    st.dataframe(bu_metrix.style.format({
        "Total_Booking":"${:,.2f}",
        "Avg_Distance":"{:,.2f}km",
        "Av_Rating":"{:,.1f}",
        "Revenue Share%":"{:,.2f}%"
    }).background_gradient(subset="Revenue_Generated",cmap="YlOrRd"))

    # operational efficiency
    col_eff,col_can=st.columns(2)
    with col_eff:
        st.subheader("Operational efficiency")
        eef_df=df.groupby("Vehicle Type")[["Avg VTAT","Avg CTAT"]].mean()
        st.write("Average TurnAround Time (in Minutes)")
        st.dataframe(eef_df.style.highlight_max(axis=0,color="#d81416").highlight_min(axis=0,color="#e6ed6f"),
                     use_container_width=True)

    with col_can:
        st.subheader("Cancellation Audit")
        status_count=df["Booking Status"].value_counts().to_frame(name="Count")
        status_count["Share %"]=(status_count["Count"]/total_rides*100)
        st.dataframe(status_count,use_container_width=True)

    # FINANCIAL DEEP DIVE
    st.header("Financial Deep Dive")
    pay_col, reason_col = st.columns([4, 6])

    # payment analysis
    completed_ride = (df["Booking Status"] == "Completed").sum()

    with pay_col:
        st.markdown("** Payment Method Overview")
        pay_summary = (df["Payment Method"].value_counts(normalize=True) * 100)
        st.dataframe(pay_summary.rename("% Usage"), use_container_width=True)

    with reason_col:
        st.markdown("**Primary Cancellation Trigger")

        cust_reason = (df["Reason for cancelling by Customer"]
                       .dropna()
                       .value_counts()
                       .head(3))

        drv_reason = (df["Driver Cancellation Reason"]
                      .dropna()
                      .value_counts()
                      .head(3))

        cust_reason.index = "Customer:" + cust_reason.index
        drv_reason.index = "Driver:" + drv_reason.index

        reason_df = pd.concat([cust_reason, drv_reason]).to_frame()
        reason_df.columns = ["Incident Found"]

        st.dataframe(reason_df)

    # data quality
    with st.expander("Data Quality & Audit Logs"):
        audit1, audit2 = st.columns(2)
        audit1.write(f"Duplicate Records: {df.duplicated().sum()}")
        audit2.write(f"Missing Values: {df['Booking Value'].isna().sum()}")
        st.info("Missing Booking Values are Expected for Cancelled ride or no-driver found")
        st.success("Executive Overview Generated from Operational Dataset")

    st.title("Uber Operation")
    st.markdown("---")

    # strategic kpi layer
    completed_ride = df[df["Booking Status"] == "Completed"]
    total_revenue = completed_ride["Booking Value"].sum()
    avg_distance = completed_ride["Ride Distance"].mean()
    success_rate = (len(completed_ride) / total_rides * 100 if total_rides > 0 else 0)
    avg_rating = completed_ride["Customer Rating"].dropna().mean()

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric(label="Gross Total Revenue", value=f"{total_revenue:,.0f}", delta="Target:₹1.2M")
    kpi2.metric(label="Fulfilment Rate", value=f"{success_rate:.1f}",
                delta="-2.4% vs Last Month", delta_color="red")
    kpi3.metric(label="Avg Distance", value=f"{avg_distance:.2f}km")
    kpi4.metric(label="Avg Rating", value=f"{avg_rating:.1f}")

    # show full dataset
    if st.checkbox("Show Full Dataset"):
        st.dataframe(completed_ride, use_container_width=True)

    # column statistics
    st.subheader("Column Statistics")
    numeric_cols = df.select_dtypes(include=["int64", "float64"]).columns

    if len(numeric_cols) > 0:
        selected_col = st.selectbox(label="Select Numeric Value", options=numeric_cols)
        st.write(df[selected_col].describe())

    st.divider()

if selected == "Ride Analytics":
    st.title("Revenue Ride Intelligence Dashboard")
    st.divider()

    completed = df[df["Booking Status"] == "Completed"]

    # SUNBURST CHART
    st.subheader("Revenue Hierarchy")
    fig1 = px.sunburst(
        completed,
        path=["Vehicle Type", "Payment Method"],
        values="Booking Value",
        color="Booking Value",
        color_continuous_scale="Viridis"
    )
    fig1.update_layout(height=500)
    st.plotly_chart(fig1)

    # TREEMAP
    st.subheader("Revenue Distribution")
    fig2 = px.treemap(
        completed,
        path=["Vehicle Type", "Payment Method"],
        values="Booking Value",
        color="Booking Value",
        color_continuous_scale="Blues"
    )
    fig2.update_layout(margin=dict(t=50, l=25, r=25, b=25))
    fig2.update_traces(textinfo="label+value")
    st.plotly_chart(fig2, use_container_width=True)

    # CUSTOMER RATING BAR
    st.subheader("Customer Rating Scores")
    fig3 = px.bar(
        completed,
        x="Driver Ratings",
        y="Customer Rating",
        color="Vehicle Type"
    )
    fig3.update_layout(barmode="group", height=400)
    st.plotly_chart(fig3)

    # SANKEY CHART
    st.subheader("Customer Flow Analysis")

    flow = df.groupby(["Vehicle Type", "Booking Status"]).size().reset_index(name="Count")

    source_labels = flow["Vehicle Type"].unique().tolist()
    target_labels = flow["Booking Status"].unique().tolist()

    source = flow["Vehicle Type"].apply(lambda x: source_labels.index(x)).tolist()
    target = flow["Booking Status"].apply(lambda x: target_labels.index(x)).tolist()
    value = flow["Count"].tolist()

    labels = source_labels + target_labels

    source = flow["Vehicle Type"].apply(
        lambda x: labels.index(x)
    ).tolist()

    target = flow["Booking Status"].apply(
        lambda x: labels.index(x)
    ).tolist()

    import plotly.graph_objects as go

    fig4 = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=labels
        ),
        link=dict(
            source=source,
            target=target,
            value=value
        )
    )])

    fig4.update_layout(height=500)
    st.plotly_chart(fig4)

if selected == "Data Assistant":
    st.title("Data Assistant")
    st.divider()

    st.write("Ask Questions about the dataset and get visual analytics")
    user_question = st.text_input("Ask your question")

    if user_question:
        q = user_question.lower()

        completed = df[df["Booking Status"] == "Completed"]

    if user_question:
        q = user_question.lower()

        completed = df[df["Booking Status"] == "Completed"]

        # total rides
        if "total rides" in q:
            total = len(df)
            st.success(f"Total Rides in Dataset : {total}")

            status = df["Booking Status"].value_counts()

            fig = px.bar(
                x=status.index,
                y=status.values,
                labels={"x": "Booking Status", "y": "Ride Count"},
                title="Ride Distribution by Status"
            )
            st.plotly_chart(fig, use_container_width=True)

        # revenue analysis
        elif "revenue" in q:
            revenue = completed.groupby("Vehicle Type")["Booking Value"].sum()
            st.success(f"Total Revenue : {revenue.sum():,.2f}")

            fig = px.bar(
                revenue,
                title="Revenue by Vehicle Type",
                labels={"value": "Revenue", "Vehicle Type": "Booking Value"}
            )
            st.plotly_chart(fig, use_container_width=True)

        # vehicle distribution
        elif "vehicle" in q:
            vehicle = df["Vehicle Type"].value_counts()
            st.success(f"Most Used Vehicle : {vehicle.idxmax()}")

            fig = px.pie(
                names=vehicle.index,
                values=vehicle.values,
                title="Vehicle Usage Distribution"
            )
            st.plotly_chart(fig)

        # payment analysis
        elif "payment" in q:
            payment = df["Payment Method"].value_counts()
            fig = px.pie(names=payment.index,
                         values=payment.values,
                         title="Payment Method")
            st.plotly_chart(fig)

        # cancellation
        elif "cancel" in q:
            cancel = df["Booking Status"].value_counts()
            fig = px.bar(x=cancel.index, y=cancel.values,
                         title="Ride Status",
                         labels={"x": "Booking Status", "y": "Ride Count"})
            st.plotly_chart(fig)


        # rating analysis
        elif "rating" in q:
            fig = px.histogram(completed, x="Customer Rating", nbins=10, title="Customer Rating")
            st.plotly_chart(fig)
            st.success(f"Average Rating: {completed['Customer Rating'].mean():.1f}")

        # distance analysis
        elif "distance" in q:
            fig = px.scatter(completed, x="Ride Distance", y="Booking Value",
                             title="Ride Distance vs Booking Value",
                             color="Vehicle Type")
            st.plotly_chart(fig)
            st.success(f"Average Distance: {completed['Ride Distance'].mean():.2f} km")

        else:
            st.warning("Question not recognized please ask question from cancellation, vehicle, revenue etc")