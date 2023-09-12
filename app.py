from flask import Flask, request, send_file, jsonify
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import json
import pandas as pd
import io
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Load data from JSON file
try:
    with open('transformed_data_nha_tot.json', 'r') as f:
        data = json.load(f)
except Exception as e:
    logging.error(f"Failed to load JSON file: {e}")
    data = []

df = pd.DataFrame(data)
df['time'] = pd.to_datetime(df['time'], format='%m/%Y')
@app.route('/get_chart', methods=['GET'])
def get_chart():
    try:
        district = request.args.get('district')
        city = request.args.get('city')
        time = request.args.get('time')
        type_house_str = request.args.get('type_house')  # Changed to string to allow multiple values

        if "-" in time:
            start_time, end_time = time.split("-")
            is_range = True
        else:
            start_time, end_time = time, time
            is_range = False

        start_time = pd.to_datetime(start_time, format='%m/%Y')
        end_time = pd.to_datetime(end_time, format='%m/%Y')

        mask = (df['time'] >= start_time) & (df['time'] <= end_time)

        if district:
            filtered_df = df[mask & (df['district'] == district)]
        elif city:
            filtered_df = df[mask & (df['city'] == city)]
            filtered_df = filtered_df.groupby(['type_house', 'time'])['mean'].mean().reset_index()

        if filtered_df.empty:
            return "No data available for the given district or city and time period.", 400

        # If a specific type of house is selected, filter by it
        if type_house_str:
            type_house_list = type_house_str.split(",")  # Convert string to list
            filtered_df = filtered_df[filtered_df['type_house'].isin(type_house_list)]  # Filter using isin()

        plt.figure(figsize=(12, 6))
        location = district if district else city
        
        if is_range:
            markers = ['o', '^', 's', 'p', '*', 'x']  # Define a list of markers
            for i, type_house in enumerate(filtered_df['type_house'].unique()):
                sub_df = filtered_df[filtered_df['type_house'] == type_house]
                plt.plot(sub_df['time'], sub_df['mean'], label=type_house, marker=markers[i % len(markers)])
                
            plt.xlabel('Time')
            plt.ylabel('Mean Price')
            plt.legend()
            plt.title(f'Mean Price of Different Types of Houses in {location} from {start_time} to {end_time}')
        else:
            plt.bar(filtered_df['type_house'], filtered_df['mean'], color='#00FF00')
            plt.xlabel('Type of House')
            plt.ylabel('Mean Price')
            plt.title(f'Mean Price of Different Types of Houses in {location} for {time}')

        plt.xticks(rotation=45)
        plt.xticks(fontsize=10)
        plt.yticks(fontsize=10)
        plt.tight_layout()

        img = io.BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)

        return send_file(img, mimetype='image/png')
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return jsonify({"error": "An error occurred while generating the chart."}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
