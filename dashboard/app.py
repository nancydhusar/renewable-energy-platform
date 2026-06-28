import streamlit as st
import duckdb
import pandas as pd
import plotly.express as px

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(page_title="Renewable Energy Dashboard", layout="wide")

GOLD_PATH = "lakehouse/gold/weather/weather_gold.parquet"

# -----------------------------
# LOAD DATA
# -----------------------------
@st.cache_data
def load_data():
    df = duckdb.query(f"""
        SELECT *
        FROM read_parquet('{GOLD_PATH}')
    """).df()
    return df

df = load_data()

# -----------------------------
# CLEAN SAFE DATA (IMPORTANT FIX)
# -----------------------------
df = df.dropna(subset=["city", "energy_potential"])
df[["lat", "lon"]] = df[["lat", "lon"]].fillna(0)

st.title("🌍 Germany Renewable Energy Intelligence Dashboard")

st.markdown("Kafka + Lakehouse + DuckDB Analytics Layer")

# -----------------------------
# SIDEBAR FILTER
# -----------------------------
cities = sorted(df["city"].unique())
selected_city = st.sidebar.multiselect(
    "Select City",
    cities,
    default=cities
)

filtered_df = df[df["city"].isin(selected_city)]

# -----------------------------
# TOP INSIGHTS (NEW IMPROVEMENT)
# -----------------------------
st.subheader("🔥 Key Insights")

top_city = (
    filtered_df.groupby("city")["energy_potential"]
    .mean()
    .sort_values(ascending=False)
    .head(1)
)

best_city = top_city.index[0] if len(top_city) > 0 else "N/A"

col1, col2, col3 = st.columns(3)

col1.metric("🏆 Best City", best_city)
col2.metric("⚡ Avg Solar Score", round(filtered_df["solar_score"].mean(), 2))
col3.metric("🌬 Avg Wind Energy", round(filtered_df["wind_energy_index"].mean(), 2))

st.divider()

# -----------------------------
# MAP VIEW (SAFE VERSION FIXED)
# -----------------------------
st.subheader("🗺️ Germany Renewable Energy Map")

map_df = filtered_df.groupby(
    ["city", "lat", "lon"]
)[["energy_potential", "solar_score", "wind_energy_index"]].mean().reset_index()

map_df = map_df[(map_df["lat"] != 0) & (map_df["lon"] != 0)]

fig = px.scatter_geo(
    map_df,
    lat="lat",
    lon="lon",
    size="energy_potential",
    color="solar_score",
    hover_name="city",
    projection="natural earth",
    title="Germany Energy Potential Map"
)

fig.update_geos(
    scope="europe",
    center={"lat": 51, "lon": 10},
    showland=True,
    landcolor="lightgray"
)

st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# CITY COMPARISON (SORTED FIX)
# -----------------------------
st.subheader("🌍 City-wise Energy Potential")

city_df = filtered_df.groupby("city")["energy_potential"].mean().reset_index()
city_df = city_df.sort_values("energy_potential", ascending=False)

fig1 = px.bar(city_df, x="city", y="energy_potential", color="energy_potential")
st.plotly_chart(fig1, use_container_width=True)

# -----------------------------
# SOLAR VS WIND (SORTED FIX)
# -----------------------------
st.subheader("🌞 Solar vs 🌬 Wind Energy Comparison")

solar_wind = filtered_df.groupby("city")[["solar_score", "wind_energy_index"]].mean().reset_index()
solar_wind = solar_wind.sort_values("solar_score", ascending=False)

fig2 = px.line(
    solar_wind,
    x="city",
    y=["solar_score", "wind_energy_index"],
    markers=True
)

st.plotly_chart(fig2, use_container_width=True)

# -----------------------------
# HOURLY ENERGY PATTERN
# -----------------------------
st.subheader("⏰ Hourly Energy Pattern")

hourly = filtered_df.groupby("hour")["energy_potential"].mean().reset_index()

fig3 = px.line(hourly, x="hour", y="energy_potential", markers=True)

st.plotly_chart(fig3, use_container_width=True)

# -----------------------------
# SEASONAL ANALYSIS
# -----------------------------
st.subheader("🍂 Seasonal Energy Trends")

season = filtered_df.groupby("season")["energy_potential"].mean().reset_index()
season = season.sort_values("energy_potential", ascending=False)

fig4 = px.bar(season, x="season", y="energy_potential", color="season")

st.plotly_chart(fig4, use_container_width=True)