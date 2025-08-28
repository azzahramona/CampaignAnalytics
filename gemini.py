import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

# --- Sample mock data generation ---
@st.cache_data
def load_mock_data():
    daily_data = pd.DataFrame({
        "month": np.random.choice(['Jan', 'Feb', 'Mar', 'Apr'], 100),
        "spend": np.random.randint(1000, 10000, 100),
        "views": np.random.randint(10000, 100000, 100),
        "campaign": np.random.choice(['Campaign A', 'Campaign B', 'Campaign C'], 100),
        "brand": np.random.choice(['Brand X', 'Brand Y'], 100),
        "category": np.random.choice(['Electronics', 'Fashion'], 100),
        "objective": np.random.choice(['Awareness', 'Engagement', 'Conversion'], 100),
        "platform": np.random.choice(['YouTube', 'Facebook', 'Instagram'], 100),
        "impression": np.random.randint(5000, 100000, 100),
        "clicks": np.random.randint(100, 10000, 100),
    })

    weekly_data = pd.DataFrame({
        "analysis_week_start": pd.date_range(start="2023-01-01", periods=10, freq='W'),
        "month": np.random.choice(['Jan', 'Feb', 'Mar', 'Apr'], 10),
        "campaign": np.random.choice(['Campaign A', 'Campaign B'], 10),
        "brand": np.random.choice(['Brand X', 'Brand Y'], 10),
        "category": np.random.choice(['Electronics', 'Fashion'], 10),
        "objective": np.random.choice(['Awareness', 'Engagement'], 10),
        "platform": np.random.choice(['YouTube', 'Instagram'], 10),
        "going_well": np.random.choice(['High CTR', 'Strong Impressions'], 10),
        "need_improvement": np.random.choice(['Low Conversion', 'High CPC'], 10),
        "continue_monitoring": np.random.choice(['Avg Reach', 'Moderate Engagement'], 10),
        "last_week_comparison": np.random.choice(['+10%', '-5%', '0%'], 10),
        "benchmark_comparison": np.random.choice(['Above', 'Below'], 10),
        "actionable_insights_based_on_last_week": np.random.choice(
            ['Optimize copy', 'Increase budget', 'Test new creatives'], 10)
    })

    return daily_data, weekly_data

daily_df, weekly_df = load_mock_data()
base_data=weekly_df.copy()

# --- Sidebar Navigation ---
st.sidebar.title("📊 Welcome to Campaign Analytics")
view = st.sidebar.radio("Select a view:", ["Daily Campaign", "Weekly Update","Pacing Monitoring"])

# --- DAILY CAMPAIGN VIEW ---
if view == "Daily Campaign":
    st.title("📅 Daily Campaign View")

    # Filters
    st.subheader("🔍 Filters")
    cols = ["campaign", "objective", "platform", "impression", "month", "brand", "category"]
    filtered_df = daily_df.copy()
    for col in cols:
        selected = st.sidebar.multiselect(f"Filter by {col}:", sorted(daily_df[col].unique()))
        if selected:
            filtered_df = filtered_df[filtered_df[col].isin(selected)]

    # Show filtered table
    st.subheader("📋 Filtered Daily Data")
    st.dataframe(filtered_df)

    selected_platform_or_campaign = st.sidebar.radio("Group bubbles by:", ["campaign", "platform"])

    st.subheader("🔵 Spend vs Views Bubble Chart")

    if not filtered_df.empty:
        bubble_data = (
            filtered_df
            .groupby(selected_platform_or_campaign)
            .agg({
                "spend": "sum",
                "views": "sum",
                "impression": "sum",  # You can change to 'clicks' if preferred
            })
            .reset_index()
            .rename(columns={
                selected_platform_or_campaign: "group",
                "impression": "impressions"
            })
        )

        bubble_chart = alt.Chart(bubble_data).mark_circle(opacity=0.7).encode(
            x=alt.X('spend:Q', title='Total Spend'),
            y=alt.Y('views:Q', title='Total Views'),
            size=alt.Size('impressions:Q', title='Impressions', scale=alt.Scale(range=[50, 1000])),
            color='group:N',
            tooltip=['group', 'spend', 'views', 'impressions']
        ).properties(
            width=700,
            height=400
        )

        st.altair_chart(bubble_chart, use_container_width=True)
    else:
        st.info("No data available for the current filters.")

# --- WEEKLY UPDATE VIEW ---


elif view == "Weekly Update":
    
    # --- Step 2: Create long format data for metrics and week types ---

    metrics = ['CPM', 'CPC', 'CPV', 'VTR', 'CompletionRate', 'CPCV']
    week_types = ['this_week', 'last_week', 'benchmark']

    rows = []
    for _, row in base_data.iterrows():
        for metric in metrics:
            for week_type in week_types:
                # Simulate metric values (benchmarks more stable)
                if week_type == 'benchmark':
                    val = np.random.uniform(0.5, 2.0) * 100
                elif week_type == 'this_week':
                    val = np.random.uniform(0.8, 1.2) * 100
                else:  # last_week
                    val = np.random.uniform(0.7, 1.3) * 100
                rows.append({
                    **row.to_dict(),
                    "metric": metric,
                    "week_type": week_type,
                    "value": val
                })

    weekly_long_df = pd.DataFrame(rows)

    # --- Step 3: Pivot to wide format ---

    weekly_df = weekly_long_df.pivot_table(
        index=["analysis_week_start", "month", "campaign", "brand", "category", "objective", "platform",
            "going_well", "need_improvement", "continue_monitoring"],
        columns=["metric", "week_type"],
        values="value"
    ).reset_index()
    
    

    # Flatten multiindex columns
    weekly_df.columns = ['_'.join(col).strip() if isinstance(col, tuple) else col for col in weekly_df.columns.values]

    # --- Step 4: Define summary functions ---
    
    def generate_last_week_comparison(row):
        return (f"CPM: {row['CPM_this_week']:.2f}, CPC: {row['CPC_this_week']:.2f}, CPV: {row['CPV_this_week']:.2f} "
                f"vs {row['CPM_last_week']:.2f}, {row['CPC_last_week']:.2f}, {row['CPV_last_week']:.2f} last week")

    def generate_actionable_insight(row):
        cpm_change = (row['CPM_this_week'] - row['CPM_last_week']) / row['CPM_last_week'] * 100
        cpc_change = (row['CPC_this_week'] - row['CPC_last_week']) / row['CPC_last_week'] * 100
        cpv_change = (row['CPV_this_week'] - row['CPV_last_week']) / row['CPV_last_week'] * 100

        if abs(cpm_change) >30 or abs(cpc_change) > 30:
            return "This campaign needs optimization. Investigate ad creatives, targeting, and bidding strategy to reduce costs."
        else:
            return "Campaign performance is stable. Continue monitoring and optimizing ad strategies."

    def generate_benchmark_comparison(row):
        return (f"CPM: {row['CPM_this_week']:.2f} vs {row['CPM_benchmark']:.2f}, "
                f"VTR: {row['VTR_this_week']:.2f} vs {row['VTR_benchmark']:.2f}, "
                f"CompletionRate: {row['CompletionRate_this_week']:.2f} vs {row['CompletionRate_benchmark']:.2f}, "
                f"CPCV: {row['CPCV_this_week']:.2f} vs {row['CPCV_benchmark']:.2f}")

    # Apply these columns to dataframe
    weekly_df['last_week_comparison'] = weekly_df.apply(generate_last_week_comparison, axis=1)
    weekly_df['actionable_insights_based_on_last_week'] = weekly_df.apply(generate_actionable_insight, axis=1)
    weekly_df['benchmark_comparison'] = weekly_df.apply(generate_benchmark_comparison, axis=1)

    # --- Step 5: Streamlit UI ---

    st.title("📆 Weekly Update View")

    # Sidebar filters
    st.sidebar.subheader("🔍 Filters")
    weekly_df.rename(columns={ "going_well_":"going_well", "need_improvement_":"need_improvement", "continue_monitoring_":"continue_monitoring",'category_':'category','platform_':'platform','brand_':'brand','objective_':'objective',"analysis_week_start_": "analysis_week_start",'campaign_':'campaign'}, inplace=True)
    filter_cols = ["analysis_week_start", "campaign", "brand", "category", "objective", "platform"]
    filtered_weekly_df = weekly_df.copy()

    for col in filter_cols:
        options = sorted(filtered_weekly_df[col].dropna().unique())
        selected = st.sidebar.multiselect(f"Filter by {col}:", options, default=options)
        if selected:
            filtered_weekly_df = filtered_weekly_df[filtered_weekly_df[col].isin(selected)]

    # Styling function to color status columns
    def style_row(row):
        styles = [''] * len(row)
        for i, col in enumerate(row.index):
            if col == "going_well" and row[col]:
                styles[i] = 'background-color: lightgreen'
            elif col == "need_improvement" and row[col]:
                styles[i] = 'background-color: lightcoral'
            elif col == "continue_monitoring" and row[col]:
                styles[i] = 'background-color: khaki'
        return styles

    # Columns to display
    base_cols = [
        "analysis_week_start", "month", "campaign", "brand", "category", "objective", "platform",
        "going_well", "need_improvement", "continue_monitoring"
    ]
    last_three_cols = [
        "last_week_comparison",
        "actionable_insights_based_on_last_week"
    ]
    display_cols = base_cols + last_three_cols
    display_cols = [col for col in display_cols if col in filtered_weekly_df.columns]

    st.subheader("📋 Weekly Performance Summary")
    
    if filtered_weekly_df.empty:
        st.info("No data available for the selected filters.")
    else:
        df_to_display = filtered_weekly_df[display_cols]
        styled_df = df_to_display.style.apply(style_row, axis=1)
        st.dataframe(styled_df, use_container_width=True)
elif view == "Pacing Monitoring":
    st.title("📊 Pacing Monitoring View")
    import pandas as pd

    pacing_data = pd.DataFrame({
        "Start Date": pd.to_datetime([
            "2025-07-19", "2025-07-06", "2025-07-10", "2025-07-15", "2025-07-20", 
            "2025-07-25", "2025-08-01", "2025-08-05", "2025-08-10", "2025-08-15",
            "2025-08-20", "2025-08-25"
        ]),
        "End Date": pd.to_datetime([
            "2025-08-31", "2025-09-30", "2025-09-15", "2025-09-20", "2025-09-25",
            "2025-09-30", "2025-10-05", "2025-10-10", "2025-10-15", "2025-10-20",
            "2025-10-25", "2025-10-30"
        ]),
        "month": [
            "Jul", "Jul", "Jul", "Jul", "Jul", 
            "Jul", "Aug", "Aug", "Aug", "Aug", 
            "Aug", "Aug"
        ],
        "campaign": [
            "Campaign A", "Campaign B", "Campaign C", "Campaign D", "Campaign E",
            "Campaign F", "Campaign G", "Campaign H", "Campaign I", "Campaign J",
            "Campaign K", "Campaign L"
        ],
        "brand": [
            "Brand X", "Brand Y", "Brand Z", "Brand X", "Brand Y",
            "Brand Z", "Brand X", "Brand Y", "Brand Z", "Brand X",
            "Brand Y", "Brand Z"
        ],
        "category": [
            "Electronics", "Fashion", "Automotive", "Beauty", "Food",
            "Electronics", "Fashion", "Automotive", "Beauty", "Food",
            "Electronics", "Fashion"
        ],
        "objective": [
            "Awareness", "Engagement", "Conversions", "Awareness", "Engagement",
            "Conversions", "Awareness", "Engagement", "Conversions", "Awareness",
            "Engagement", "Conversions"
        ],
        "platform": [
            "YouTube", "Instagram", "Facebook", "TikTok", "YouTube",
            "Instagram", "Facebook", "TikTok", "YouTube", "Instagram",
            "Facebook", "TikTok"
        ],
        "Day Left": [4, 34, 20, 15, 25, 10, 18, 12, 8, 22, 30, 14],
        "Plan Budget": [
            1_332_929, 700_097_080, 5_000_000, 3_500_000, 4_000_000,
            2_500_000, 7_000_000, 6_000_000, 8_000_000, 9_000_000,
            5_500_000, 4_500_000
        ],
        "Current Spend": [
            0, 36_664_910, 1_200_000, 2_000_000, 1_800_000,
            500_000, 3_500_000, 2_000_000, 4_000_000, 5_000_000,
            2_750_000, 1_500_000
        ],
    })

    # Calculate total campaign days
    pacing_data['Total Days'] = (pacing_data['End Date'] - pacing_data['Start Date']).dt.days + 1

    # Calculate days passed
    pacing_data['Days Passed'] = pacing_data['Total Days'] - pacing_data['Day Left']

    # Avoid division by zero or negative days passed
    pacing_data['Days Passed'] = pacing_data['Days Passed'].clip(lower=1)

    # Calculate expected spend up to today
    pacing_data['Expected Spend'] = pacing_data['Plan Budget'] * (pacing_data['Days Passed'] / pacing_data['Total Days'])

    # Calculate pacing as percentage
    pacing_data['Pacing'] = (pacing_data['Current Spend'] / pacing_data['Expected Spend']) * 100

    # Clip pacing at 100%
    pacing_data['Pacing'] = pacing_data['Pacing'].clip(upper=100)

    # Format pacing as percentage string
    pacing_data['Pacing'] = pacing_data['Pacing'].round(0).astype(int).astype(str) + '%'
    pacing_data['Remaining Budget'] = (pacing_data['Plan Budget'] - pacing_data["Current Spend"]).round(0).astype(int)
    pacing_data['Expected Spend'] = pacing_data['Expected Spend'].round(0).astype(int)
    pacing_data['Expected Spend/day'] = (pacing_data['Remaining Budget']/ pacing_data['Day Left']).round(0).astype(int)

    # Show full data (you can select any columns you want)
    print(pacing_data[[
        "month", "campaign", "brand", "category", "objective", "platform",
        "Day Left", "Plan Budget", "Current Spend", "Pacing"
    ]])

    import streamlit as st
    import pandas as pd

    # Your existing DataFrame code here (pacing_data)...

    st.write("If today is 28-08-2025, and data is available up to 27-08-2025")

    # Then show the DataFrame or any other outputs
    st.dataframe(pacing_data[[
        "month", 'Start Date','End Date',"campaign", "brand", "category", "objective", "platform",
        "Day Left", "Plan Budget","Remaining Budget", "Current Spend","Expected Spend",'Expected Spend/day', "Pacing"
    ]])

