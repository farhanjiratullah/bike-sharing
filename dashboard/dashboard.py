import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set(style='dark')

def create_daily_rents_df(df):
    daily_rents_df = df.resample(rule='D', on='dteday').agg({
        "casual": "sum",
        "registered": "sum",
        "cnt": "sum"
    })
    daily_rents_df = daily_rents_df.reset_index()
    
    return daily_rents_df

def create_byseason_df(df):
	byseason_df = df.groupby(by='season').agg({
        "cnt": "mean"
    })
	byseason_df = byseason_df.reset_index()

	season_labels = {1: "Spring", 2: "Summer", 3: "Fall", 4: "Winter"}
	byseason_df["season"] = byseason_df["season"].map(season_labels)
    
	return byseason_df

def create_byweather_df(df):
	byweather_df = df.groupby(by='weathersit').agg({
		"cnt": "mean"
	})
	byweather_df = byweather_df.reset_index()
	weather_labels = {
		1: "Clear/Few Clouds",
		2: "Mist/Cloudy",
		3: "Light Snow/Rain",
		4: "Heavy Rain/Snow"
	}
	byweather_df["weathersit"] = byweather_df["weathersit"].map(weather_labels)
    
	return byweather_df

def create_sum_rent_perdays_df(df):
	sum_rent_perdays_df = df.groupby(by='hr').agg({
		"cnt": "mean"
	})
	sum_rent_perdays_df = sum_rent_perdays_df.reset_index()
    
	return sum_rent_perdays_df

hour_df = pd.read_csv("main_data.csv")

datetime_columns = ["dteday"]
hour_df.sort_values(by="dteday", inplace=True)
hour_df.reset_index(inplace=True)
 
for column in datetime_columns:
    hour_df[column] = pd.to_datetime(hour_df[column])

min_date = hour_df["dteday"].min()
max_date = hour_df["dteday"].max()
 
with st.sidebar:    
    # Input tanggal
    start_date, end_date = st.date_input(
        label='Rentang Waktu',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

main_df = hour_df[(hour_df["dteday"] >= str(start_date)) & 
                (hour_df["dteday"] <= str(end_date))]

daily_rents_df = create_daily_rents_df(main_df)
byseason_df = create_byseason_df(main_df)
byweather_df = create_byweather_df(main_df)
sum_rent_perdays_df = create_sum_rent_perdays_df(main_df)

st.header('Bike Sharing 🚲')

st.subheader('Daily Rents')
 
col1, col2, col3 = st.columns(3)
 
with col1:
    total_casual_rents = daily_rents_df.casual.sum()
    st.metric("Total casual rents", value=f"{total_casual_rents:,}".replace(",", "."))
 
with col2:
    total_registered_rents = daily_rents_df.registered.sum()
    st.metric("Total registered rents", value=f"{total_registered_rents:,}".replace(",", "."))

with col3:
    total_cnt_rents = daily_rents_df.cnt.sum()
    st.metric("Total cnt rents", value=f"{total_cnt_rents:,}".replace(",", "."))

fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    daily_rents_df["dteday"],
    daily_rents_df["cnt"],
    marker='o', 
    linewidth=2,
    color="#90CAF9"
)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)
 
st.pyplot(fig)

st.subheader("Average Bike Rentals by Season & Weather")
 
fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(35, 15))
 
max_value = byseason_df["cnt"].max()
colors = ["#90CAF9" if cnt == max_value else "#D3D3D3" for cnt in byseason_df["cnt"]]
 
sns.barplot(x="season", y="cnt", data=byseason_df, palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].set_title("Average Bike Rentals by Season", loc="center", fontsize=50)
ax[0].tick_params(axis='y', labelsize=35)
ax[0].tick_params(axis='x', labelsize=30)

colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
 
sns.barplot(x="weathersit", y="cnt", data=byweather_df, palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].set_title("Average Bike Rentals by Weather", loc="center", fontsize=50)
ax[1].tick_params(axis='y', labelsize=35)
ax[1].tick_params(axis='x', labelsize=25)
 
st.pyplot(fig)

st.subheader("Average Bike Rentals per Hour of the Day")

fig, ax = plt.subplots(figsize=(10, 5))

# Membuat lineplot
sns.lineplot(data=sum_rent_perdays_df, x="hr", y="cnt", marker="o", linestyle="-", color="royalblue", ax=ax)

# Menemukan titik maksimum dan minimum
max_hour = sum_rent_perdays_df.loc[sum_rent_perdays_df["cnt"].idxmax()]
min_hour = sum_rent_perdays_df.loc[sum_rent_perdays_df["cnt"].idxmin()]

# Menambahkan titik puncak dan terendah
ax.scatter(max_hour["hr"], max_hour["cnt"], color="green", s=100, label=f"Puncak: {int(max_hour['hr'])}:00")
ax.scatter(min_hour["hr"], min_hour["cnt"], color="red", s=100, label=f"Terendah: {int(min_hour['hr'])}:00")

# Konfigurasi plot
ax.set_xlabel(None)
ax.set_ylabel(None)
ax.set_xticks(range(0, 24))
ax.legend()
ax.grid(axis="y", linestyle="--", alpha=0.7)

# Menampilkan plot di Streamlit
st.pyplot(fig)

st.caption('Copyright (c) Farhan Jiratullah 2025')