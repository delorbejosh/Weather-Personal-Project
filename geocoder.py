import requests



#Location Section
target_url = "https://geocoding-api.open-meteo.com/v1/search"

while True:
    city = input("Enter your destination: ")


    
    params = {
    "name" : city 
    ,
    "format" : "json"
    ,
    "count" : 5
    }

    data = requests.get(target_url,params).json()

    #Check for results 
    if 'results' in data: 
        print("Loading Results: ")
        for index, result in enumerate(data['results']):
            print(index + 1, ":", data['results'][index].get('name'), "," , data['results'][index].get('country'),",", data['results'][index].get('timezone'))
        city_index = input("Please select your desired location: ")
        final_city = data["results"][int(city_index) - 1]
        break
    else:
        print("No matching city found. Please try again.\n")


print("\nSuccessfully selected: " , final_city.get('name'), "," ,final_city.get('country'), "," ,final_city.get('latitude'), ",", final_city.get('longitude'))




#Weather Section
weather_url = "https://archive-api.open-meteo.com/v1/archive"

weather_params = {

"latitude" : final_city["latitude"],
"longitude" : final_city["longitude"],
"start_date" :"2025-01-01" ,
"end_date" : "2025-12-31",
"daily" : "apparent_temperature_max,precipitation_sum,sunshine_duration",
"timezone" : final_city["timezone"]

}

weather_data = requests.get(weather_url,weather_params).json()

daily_data = weather_data["daily"]

dates = daily_data["time"]
max_temps = daily_data["apparent_temperature_max"]
precipitation = daily_data["precipitation_sum"]
sunshine = daily_data["sunshine_duration"]


weather_list = list(zip(dates, max_temps, precipitation, sunshine))

monthly_summary = {}


for date, temp, precip, sun in weather_list:
    month = date[5:7]  # Extracts "01", "02", etc.

    # If this is our first time seeing this month, create its container
    if month not in monthly_summary:
        monthly_summary[month] = {
            "temps": [],
            "precip": [],
            "sunshine" : []
        }

    # Append the daily values directly into the correct month's lists
    monthly_summary[month]["temps"].append(temp)
    monthly_summary[month]["precip"].append(precip)
    monthly_summary[month]["sunshine"].append(sun)


print(monthly_summary)


ranked_months = []

#monthly summary is dictionary. I want to add the temps/month(need to figure out data type) and divide by days.
for month in monthly_summary:

    avg_temp = (sum(monthly_summary[month]["temps"]))/(len(monthly_summary[month]["temps"])) 
    total_precip = sum(monthly_summary[month]["precip"])
    avg_sunshine = (sum(monthly_summary[month]["sunshine"]))/(len(monthly_summary[month]["sunshine"])) 

    ranked_months.append({
        "month": month,
        "avg_temp": round(avg_temp, 1),
        "total_precip": round(total_precip, 1),
        "avg_sunshine" : round(avg_sunshine, 1)
    })



print(ranked_months)


#Scaling the temperatures
min_temp = min(x["avg_temp"] for x in ranked_months)
max_temp = max(x["avg_temp"] for x in ranked_months)
temp_range = max_temp - min_temp

min_sun = min(x["avg_sunshine"] for x in ranked_months)
max_sun = max(x["avg_sunshine"] for x in ranked_months)
sun_range = max_sun - min_sun

min_precip = min(x["total_precip"] for x in ranked_months)
max_precip = max(x["total_precip"] for x in ranked_months)
precip_range = max_precip - min_precip

WEIGHT_TEMP = 0.2
WEIGHT_SUN = 0.4
WEIGHT_PRECIP = 0.4



for month in ranked_months:

   
    if temp_range == 0:
        norm_temp = 1.0
    else:
        norm_temp = (month["avg_temp"] - min_temp) / temp_range

    
    sun_range = max_sun - min_sun
    if sun_range == 0:
        norm_sun = 1.0
    else:
        norm_sun = (month["avg_sunshine"] - min_sun) / sun_range

   
    
    if precip_range == 0:
        norm_precip = 0.0  
    else:
      
        norm_precip = (month["total_precip"] - min_precip) / precip_range
    
    inverted_precip = 1.0 - norm_precip

   
    weather_score = (
        (norm_temp * WEIGHT_TEMP) + 
        (norm_sun * WEIGHT_SUN) + 
        (inverted_precip * WEIGHT_PRECIP)
    ) * 100

    
    month["weather_score"] = round(weather_score, 1)

for m in ranked_months:
    print(f"Month {m['month']}: Weather Score = {m['weather_score']}")
