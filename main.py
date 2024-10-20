from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from . import db
from project.models import UserStock, Transaction
import random
import threading
import time

main = Blueprint('main', __name__)

# store current stock prices
current_stock_prices = {}

def get_random_stock_price():
    # Generate a random stock price between $50 and $150
    return round(random.uniform(50, 150), 2)

def update_stock_prices():
    while True:
        # Update the prices for stocks every hour 
        for stock in ["AAPL", "GOOGL", "AMZN", "MSFT"]:  # stocks to track
            current_stock_prices[stock] = get_random_stock_price()
        time.sleep(3600)  # Sleep for 1 hour

# Start the price updating thread when your app starts
threading.Thread(target=update_stock_prices, daemon=True).start()

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/buy-stocks', methods=['GET', 'POST'])
@login_required
def buy_stocks():
    if request.method == 'POST':
        stock_symbol = request.form.get('stock_symbol').upper()  
        num_shares = int(request.form.get('num_shares'))

        # Get a random price for the stock
        price_per_share = get_random_stock_price()

        # Validate the inputs
        if not stock_symbol or num_shares <= 0:
            error = "All fields must be valid."
            return render_template('buy_stocks.html', error=error)

        # Add to transactions table
        new_transaction = Transaction(
            user_id=current_user.id,
            stock_symbol=stock_symbol,
            num_shares=num_shares,
            price_per_share=price_per_share,  
            transaction_type='buy'
        )
        db.session.add(new_transaction)

        # user_stocks table
        user_stock = UserStock.query.filter_by(user_id=current_user.id, stock_symbol=stock_symbol).first()
        if user_stock:
            user_stock.num_shares += num_shares
            user_stock.purchase_price = price_per_share  
        else:
            # Add new stock and include the purchase price
            new_stock = UserStock(
                user_id=current_user.id,
                stock_symbol=stock_symbol,
                num_shares=num_shares,
                purchase_price=price_per_share  # Set purchase price here
            )
            db.session.add(new_stock)

        db.session.commit()

        flash(f'Successfully bought {num_shares} shares of {stock_symbol} at ${price_per_share}.')
        return redirect(url_for('main.transactions'))

    return render_template('buy_stocks.html', current_prices=current_stock_prices)

@main.route('/sell-stocks', methods=['GET', 'POST'])
@login_required
def sell_stocks():
    user_stocks = UserStock.query.filter_by(user_id=current_user.id).all()

    if request.method == 'POST':
        stock_symbol = request.form.get('stock_symbol').upper()
        num_shares_to_sell = int(request.form.get('num_shares'))

        # Retrieve the user's current stock for the selected symbol
        user_stock = UserStock.query.filter_by(user_id=current_user.id, stock_symbol=stock_symbol).first()

        # Check if the user has enough shares to sell
        if not user_stock or user_stock.num_shares < num_shares_to_sell:
            error = "You don't own enough shares to sell."
            return render_template('sell_stocks.html', user_stocks=user_stocks, current_prices=current_stock_prices, error=error)

        # Proceed with selling the stocks
        # Add a new transaction record
        new_transaction = Transaction(
            user_id=current_user.id,
            stock_symbol=stock_symbol,
            num_shares=num_shares_to_sell,  
            price_per_share=current_stock_prices.get(stock_symbol, 0),  # Use the current price
            transaction_type='sell'
        )
        db.session.add(new_transaction)

        # Update the user's stock quantity
        user_stock.num_shares -= num_shares_to_sell
        if user_stock.num_shares == 0:
            db.session.delete(user_stock)  # Remove the stock if all shares are sold

        
        db.session.commit()

        flash(f'Successfully sold {num_shares_to_sell} shares of {stock_symbol}.', 'success')
        return redirect(url_for('main.transactions'))

    
    return render_template('sell_stocks.html', user_stocks=user_stocks, current_prices=current_stock_prices)

@main.route('/transactions')
@login_required
def transactions():
    user_transactions = Transaction.query.filter_by(user_id=current_user.id).all()
    return render_template('transactions.html', transactions=user_transactions)

@main.route('/profile')
@login_required
def profile():
    user_stocks = UserStock.query.filter_by(user_id=current_user.id).all()
    return render_template('profile.html', user_stocks=user_stocks)
