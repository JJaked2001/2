import matplotlib
matplotlib.use('Agg')  
from flask import Flask, render_template, request, jsonify
import requests
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from datetime import datetime

app = Flask(__name__)


def get_stock_data(symbol, api_key, function='TIME_SERIES_DAILY'):
    url = f"https://www.alphavantage.co/query?function={function}&symbol={symbol}&apikey={api_key}&outputsize=full&datatype=json"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        if 'Time Series (Daily)' in data:
            return data
        else:
            return None
    return None


def filter_by_date(data, start_date, end_date):
    time_series = data['Time Series (Daily)']
    filtered_data = {date: time_series[date] for date in time_series if start_date <= date <= end_date}
    return filtered_data


def plot_stock_data(data, chart_type='line'):
    dates = list(data.keys())
    close_prices = [float(data[date]['4. close']) for date in dates]
    
    plt.figure(figsize=(10, 5))
    
    if chart_type == 'line':
        plt.plot(dates, close_prices, label='Close Price')
    elif chart_type == 'bar':
        plt.bar(dates, close_prices, label='Close Price')
    else:
        return None
    
    plt.xlabel('Date')
    plt.ylabel('Close Price (USD)')
    plt.title('Stock Price Over Time')
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()

    
    img = BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    return img


def validate_dates(start_date, end_date):
    try:
        datetime.strptime(start_date, "%Y-%m-%d")
        datetime.strptime(end_date, "%Y-%m-%d")
        if end_date < start_date:
            raise ValueError("End date cannot be before start date.")
    except ValueError as e:
        return str(e)
    return None

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route('/generate_graph', methods=['POST'])
def generate_graph():
  
    stock_symbol = request.form['symbol']
    start_date = request.form['start_date']
    end_date = request.form['end_date']
    chart_type = request.form['chart_type']
    
    
    date_error = validate_dates(start_date, end_date)
    if date_error:
        return jsonify({'error': date_error}), 400  
    
    
    api_key = '1J6GKQDV19YZ249T'  
    stock_data = get_stock_data(stock_symbol, api_key)
    if not stock_data:
        return jsonify({'error': 'Error fetching stock data or symbol not found.'}), 400  
    
    
    filtered_data = filter_by_date(stock_data, start_date, end_date)
    if not filtered_data:
        return jsonify({'error': 'No data found for the given date range.'}), 400  
    
    
    img = plot_stock_data(filtered_data, chart_type)
    if not img:
        return jsonify({'error': 'Error generating the plot.'}), 400  
    
   
    img_base64 = base64.b64encode(img.getvalue()).decode('utf-8')
    
    
    return jsonify({'image_data': img_base64})

if __name__ == '__main__':
    app.run(host="0.0.0.0")
