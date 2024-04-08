import telebot
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import os
import time


# List of stocks
stocks = ['NHPC.NS','SJVN.NS', 'YESBANK.NS','IREDA.NS','SUZLON.NS','HFCL.NS','RPOWER.NS','PAYTM.NS','IDEA.NS','MUTHOOTMF.NS','ATGL.NS','COALINDIA.NS','IOC.NS','ONGC.NS']

# Telegram Bot API key
API_KEY = '6541519098:AAH06wUBMwKdXXCX_iNZMBXl8677zG_5lMU'

# Initialize the bot
bot = telebot.TeleBot(API_KEY)

# Handler for /THANKS command
@bot.message_handler(commands=['THANKS'])
def thanks(message):
    bot.reply_to(message, "Glad I could help you!")

# Handler for /start command
@bot.message_handler(commands=['start'])
def hello(message):
    bot.send_message(message.chat.id, "Hello! I am Market Gyani aka Pp's bot.\nYou can use the following commands:\n1. /MTG = to know the top 3 most gainer stocks.\n2. /MTL = to know the top 3 most losers stocks.\n3. /MMV = to know the top 3 most popular stocks.\n4. /PRICE = to check the current price of any stock.\n5. /THANKS = if you want to appreciate the bot\n6. /BYE = to exit the chat")

# Handler for /BYE command
@bot.message_handler(commands=['BYE'])
def bye(message):
    bot.reply_to(message, "Bye. See you around later :)")

# Function to get top gainers
def top_gain(stocks, top_n=3):
    top_stocks = []
    for stock in stocks:
        data = yf.download(tickers=stock, period='10d', interval='1d')
        if not data.empty:
            closing_prices = data['Close']
            price_percentage_change = ((closing_prices[-1] - closing_prices[0]) / closing_prices[0]) * 100
            top_stocks.append((stock, price_percentage_change))
    top_stocks.sort(key=lambda x: x[1], reverse=True)
    return top_stocks[:top_n]

# Function to get top losers
def get_highest_price_percentage_loss(stocks, top_n=3):
    top_losers = []
    for stock in stocks:
        data = yf.download(tickers=stock, period='10d', interval='1d')
        if not data.empty:
            closing_prices = data['Close']
            price_percentage_change = ((closing_prices[-1] - closing_prices[0]) / closing_prices[0]) * 100
            top_losers.append((stock, price_percentage_change))
    top_losers.sort(key=lambda x: x[1])
    return top_losers[:top_n]

# Function to get top volume
def top_volume(stocks, top_n=3):
    top_stocks = []
    for stock in stocks:
        data = yf.download(tickers=stock, period='10d', interval='1d')
        if not data.empty:
            volumes = data['Volume']
            avg_volume = volumes.mean()
            top_stocks.append((stock, avg_volume))
    top_stocks.sort(key=lambda x: x[1], reverse=True)
    return top_stocks[:top_n]

# Function to generate graph
def generate_graph(stock_data, stock_name):
    plt.figure(figsize=(10, 6))
    plt.plot(stock_data.index, stock_data['Close'], label='Close Price', color='blue')
    plt.title(f'Stock Price for {stock_name.rsplit(".NS",1)[0]}')
    plt.xlabel('Date')
    plt.ylabel('Price (INR)')
    plt.legend()
    image_path = f"{stock_name}.png"
    plt.savefig(image_path)
    plt.close()  # Close the figure to free up resources
    return image_path

# Handler for /MTG command
@bot.message_handler(commands=['MTG'])
def handle_mtg(message):
    top_stocks = top_gain(stocks, top_n=3)
    if top_stocks:
        response = "Top 3 stocks with the highest percentage price change over the past 10 days:\n"
        for i, (stock, percentage_change) in enumerate(top_stocks, start=1):
            stock_name = stock.rsplit('.NS', 1)[0]
            response += f"{i}. {stock_name}: Percentage change of {percentage_change:.2f}%\n"
        bot.send_message(message.chat.id, response)

        # Get data for top 3 gainers
        top_gainer_data = {}
        for stock, _ in top_stocks:
            data = yf.download(tickers=stock, period='10d', interval='1d')
            if not data.empty:
                top_gainer_data[stock] = data

        # Calculate percentage change in prices
        combined_percentage_change = pd.DataFrame()
        for stock, data in top_gainer_data.items():
            percentage_change = ((data['Close'].iloc[-1] - data['Close'].iloc[0]) / data['Close'].iloc[0]) * 100
            combined_percentage_change[stock] = [percentage_change]

        # Plot combined percentage change
        plt.figure(figsize=(10, 6))
        for stock in combined_percentage_change.columns:
            plt.bar(stock.rsplit('.NS', 1)[0], combined_percentage_change[stock].values[0], label=stock.rsplit('.NS', 1)[0])
        plt.title('Comparison of Top 3 Gainers (Percentage Change)')
        plt.ylabel('Percentage Change (%)')
        plt.legend()
        image_path = "top_gainers_percentage_change.png"
        plt.savefig(image_path)
        plt.close()  # Close the figure to free up resources

        # Send the graph to the user
        bot.send_photo(message.chat.id, open(image_path, 'rb'))
        os.remove(image_path)  # Remove the image file after sending
    else:   
        bot.send_message(message.chat.id, "Failed to fetch data for stocks.")

# Handler for /MTL command
@bot.message_handler(commands=['MTL'])
def handle_mtl(message):
    top_losers = get_highest_price_percentage_loss(stocks, top_n=3)
    if top_losers:
        response = "Top 3 stocks with the lowest percentage price change over the past 10 days:\n"
        for i, (stock, percentage_change) in enumerate(top_losers, start=1):
            stock_name = stock.rsplit('.NS', 1)[0]
            response += f"{i}. {stock_name}: Percentage change of {percentage_change:.2f}%\n"
        bot.send_message(message.chat.id, response)

        # Get data for top 3 losers
        top_loser_data = {}
        for stock, _ in top_losers:
            data = yf.download(tickers=stock, period='10d', interval='1d')
            if not data.empty:
                top_loser_data[stock] = data

        # Calculate percentage change in prices
        combined_percentage_change = pd.DataFrame()
        for stock, data in top_loser_data.items():
            percentage_change = ((data['Close'].iloc[-1] - data['Close'].iloc[0]) / data['Close'].iloc[0]) * 100
            combined_percentage_change[stock] = [percentage_change]

        # Plot combined percentage change
        plt.figure(figsize=(10, 6))
        for stock in combined_percentage_change.columns:
            plt.bar(stock.rsplit('.NS', 1)[0], combined_percentage_change[stock].values[0], label=stock.rsplit('.NS', 1)[0])
        plt.title('Comparison of Top 3 Losers (Percentage Change)')
        plt.ylabel('Percentage Change (%)')
        plt.legend()
        image_path = "top_losers_percentage_change.png"
        plt.savefig(image_path)
        plt.close()  # Close the figure to free up resources

        # Send the graph to the user
        bot.send_photo(message.chat.id, open(image_path, 'rb'))
        os.remove(image_path)  # Remove the image file after sending
    else:
        bot.send_message(message.chat.id, "Failed to fetch data for stocks.")

# Handler for /MMV command
def process_stock_name(message):
    stock_name = message.text.strip().upper() + '.NS'
    if len(stock_name) < 2:
        bot.send_message(message.chat.id, "Invalid Stock")
    else:
        # Start sending periodic updates
        bot.send_message(message.chat.id, f"Starting price change updates for {stock_name}")
        send_price_updates(message.chat.id, stock_name)


# Function to periodically send price change updates
# Function to periodically send price change updates
def send_price_updates(chat_id, stock_name):
    prev_price = None
    while True:
        data = yf.download(tickers=stock_name, period='1d', interval='30m')
        if not data.empty:
            close_prices = data['Close']
            curr_price = close_prices.iloc[-1]
            if prev_price is not None:
                if curr_price < prev_price:
                    price_change_text = "-1"  # Indicates price decrease
                else:
                    price_change_text = "1"   # Indicates price increase or no change
                bot.send_message(chat_id, f"{data.index[-1]}    {curr_price} {price_change_text}")
            prev_price = curr_price
        else:
            bot.send_message(chat_id, "No data found for updates.")
        time.sleep(1800)  # Sleep for 30 minutes (30 minutes * 60 seconds)
    


# Handler for /PRICE command
@bot.message_handler(commands=['PRICE'])
def handle_price(message):
    bot.send_message(message.chat.id, "Enter the name of the Stock (e.g., NHPC):")
    bot.register_next_step_handler(message, process_stock_name)

# Handler to process stock name input
# Handler to process stock name input
def process_stock_name(message):
    stock_name = message.text.strip().upper() + '.NS'
    if len(stock_name) < 2:
        bot.send_message(message.chat.id, "Invalid Stock")
    else:
        data = yf.download(tickers=stock_name, period='1d', interval='1m')
        data1 = yf.download(tickers=stock_name, period='1d', interval='30m')
        if not data.empty:
            data = data.reset_index()
            data["format_date"] = data['Datetime'].dt.strftime('%d/%m%I:%M%p')
            data.set_index('format_date', inplace=True)
            # Compare the closing prices
            close_prices = data['Close']
            price_change = close_prices.iloc[-1] - close_prices.iloc[0]
            if price_change > 0:
                price_change_text = "+1"  # Indicates price increase
            elif price_change < 0:
                price_change_text = "-1"  # Indicates price decrease
            else:
                price_change_text = "0"   # Indicates no change
            image_path = generate_graph(data, stock_name)
            bot.send_message(message.chat.id, f"Price Change: {price_change_text}")
            bot.send_message(message.chat.id, data1['Close'].to_string(header=True))
            bot.send_photo(message.chat.id, open(image_path, 'rb'))
            os.remove(image_path)  # Remove the image file after sending
        else:
            bot.send_message(message.chat.id, "No data found.")

# Start polling for messages
bot.polling()