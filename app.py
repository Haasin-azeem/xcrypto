from flask import Flask, render_template, request , session, redirect
from flask_session import Session
from helpers import apology, login_required
from cs50 import SQL
from werkzeug.security import check_password_hash, generate_password_hash
import random , time



app = Flask(__name__)
app.config['TESTING'] = True
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
db = SQL("sqlite:///flask.db")



@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    else:
        session.clear()
        username = request.form.get("username")
        password = request.form.get("password")

        if not password:
            return apology("Enter a password", 400)
        if not username:
            return apology("Enter a username", 400)
        
    rows = db.execute("SELECT * FROM users WHERE username = ?", username)

    if len(rows) != 1 or not check_password_hash(rows[0]["hash"], password):
        return apology("invalid username and/or password", 400)
    
    session["user_id"] = rows[0]["id"]

    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    else:
        username = request.form.get("username")
        password = request.form.get("password")
        confirm = request.form.get("confirm")

        if not username:
            return apology("Enter username")
        if not password:
            return apology("enter a password")
        if password != confirm:
            return apology("passwords do not match")

        hash = generate_password_hash(password)
        try:
            user = db.execute("insert into users (username, hash) values (?, ?)", username, hash)
        except:
            return apology("username in use!")

        session["user_id"] = user

        return redirect("/")
@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/")
@login_required
def index():
    id =session["user_id"]
    username = db.execute("select username from users where id = ?", id)
    username = username[0]["username"]

    session["btc"]= random.randint(0,100000)
    session["eth"] = random.randint(0,100000)
    session["doge"] = random.randint(0,100000)
    session["ustd"] = random.randint(0,100000)
    session["ltc"] = random.randint(0,100000)

    btc = session["btc"]
    user_id = session["user_id"]
    eth = session["eth"]
    doge = session["doge"]
    ustd = session["ustd"]
    ltc = session["ltc"]
    cash = db.execute("select cash from users where id = ?", user_id)
    cash = cash[0]["cash"]

    return render_template("index.html", cash=cash ,username=username, btc=btc , eth = eth , doge = doge , ustd = ustd , ltc = ltc)

@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    if request.method == "GET":
        return render_template("buy.html")
    else:
        name = request.form.get("name")
        amount = int(request.form.get("amount"))
        btc = session["btc"]
        eth = session["eth"]
        doge = session["doge"]
        ustd = session["ustd"]
        ltc = session["ltc"]

        if not name:
            return apology("please enter name")
        if not amount:
            return apology("enter a valid amount")
        if amount < 0:
            return apology("enter a valid amount")

        user_id = session["user_id"]
        cash = db.execute("select cash from users where id = ?", user_id)
        cash = cash[0]["cash"]

        if name == "btc":
            total = btc * amount
            if total > cash:
                return apology("not enough cash")
            user_cash = cash - total
            db.execute("update users set cash = ? where id = ?", user_cash, user_id)
            db.execute("insert into transactions (user_id, symbol, shares, price) values(?, ?, ?, ?)", user_id, "btc", amount, btc)
            return redirect("/")
        elif name == "eth":
            total = eth * amount
            if total > cash:
                return apology("not enough cash")
            user_cash = cash - total
            db.execute("update users set cash = ? where id = ?", user_cash, user_id)
            db.execute("insert into transactions (user_id, symbol, shares, price) values(?, ?, ?, ?)", user_id, "eth", amount, eth)
            return redirect("/")
        elif name == "doge":
            total = doge * amount
            if total > cash:
                return apology("not enough cash")
            user_cash = cash - total
            db.execute("update users set cash = ? where id = ?", user_cash, user_id)
            db.execute("insert into transactions (user_id, symbol, shares, price) values(?, ?, ?, ?)", user_id, "doge", amount, doge)
            return redirect("/")
        elif name == "ustd":
            total = ustd * amount
            if total > cash:
                return apology("not enough cash")
            user_cash = cash - total
            db.execute("update users set cash = ? where id = ?", user_cash, user_id)
            db.execute("insert into transactions (user_id, symbol, shares, price) values(?, ?, ?, ?)", user_id, "ustd", amount, ustd)
            return redirect("/")
        elif name == "ltc":
            total = ltc * amount
            if total > cash:
                return apology("not enough cash")
            user_cash = cash - total
            db.execute("update users set cash = ? where id = ?", user_cash, user_id)
            db.execute("insert into transactions (user_id, symbol, shares, price) values(?, ?, ?, ?)", user_id, "ltc", amount, ltc)
            return redirect("/")
        else:
            return apology("Enter a valid name. ex: btc , eth , doge ...")
        

@app.route("/sell", methods=["POST", "GET"])
@login_required
def sell():
    if request.method == "GET":
        return render_template("sell.html")
    else:
        name = request.form.get("name")
        amount = int(request.form.get("amount"))
        btc = session["btc"]
        eth = session["eth"]
        doge = session["doge"]
        ustd = session["ustd"]
        ltc = session["ltc"]

        if not name:
            return apology("enter valid name")
        if not amount:
           amount = 1
        user_id = session["user_id"]
        cash = db.execute("select cash from users where id = ?", user_id)
        cash = cash[0]["cash"]
        shares_user = db.execute("SELECT SUM(shares) AS shares FROM transactions WHERE user_id=? AND symbol = ?", user_id, name)
        shares_user = shares_user[0]["shares"]

        if amount > shares_user:
            return apology("too poor for this")

        if name == 'btc':
            total = amount * btc
            cash = cash + total
            db.execute("update users set cash = ? where id = ?", cash, user_id)
            db.execute("insert into transactions (user_id, symbol, shares, price) values (?, ?, ?, ?)", user_id, "btc", (-1)*amount, btc)
            return redirect("/")
        elif name == 'eth':
            total = amount * eth
            cash = cash + total
            db.execute("update users set cash = ? where id = ?", cash, user_id)
            db.execute("insert into transactions (user_id, symbol, shares, price) values (?, ?, ?, ?)", user_id, "eth", (-1)*amount, eth)
            return redirect("/")
        elif name == 'doge':
            total = amount * doge
            cash = cash + total
            db.execute("update users set cash = ? where id = ?", cash, user_id)
            db.execute("insert into transactions (user_id, symbol, shares, price) values (?, ?, ?, ?)", user_id, "doge", (-1)*amount, doge)
            return redirect("/")
        elif name == 'ustd':
            total = amount * ustd
            cash = cash + total
            db.execute("update users set cash = ? where id = ?", cash, user_id)
            db.execute("insert into transactions (user_id, symbol, shares, price) values (?, ?, ?, ?)", user_id, "ustd", (-1)*amount, ustd)
            return redirect("/")
        elif name == 'ltc':
            total = amount * ltc
            cash = cash + total
            db.execute("update users set cash = ? where id = ?", cash, user_id)
            db.execute("insert into transactions (user_id, symbol, shares, price) values (?, ?, ?, ?)", user_id, "ltc", (-1)*amount, ltc)
            return redirect("/")
        else:
            return apology("enter a valid name")

@app.route("/account")
@login_required
def account():
    user_id = session["user_id"]

    stocks = db.execute("select symbol, price, sum(shares) as totalshares from transactions where user_id = ? group by symbol", user_id)
    cash = db.execute("select cash from users where id = ?", user_id)[0]["cash"]
    d_b = db.execute("select * from transactions where user_id = ?", user_id)
    

    return render_template("account.html", stocks = stocks , cash = cash , actions = d_b)   
@app.route("/transactions")
@login_required
def transactions():
    user_id = session["user_id"]
    cash = db.execute("select cash from users where id = ?", user_id)[0]["cash"]
    d_b = db.execute("select * from transactions where user_id = ?", user_id)
    
    return render_template("transactions.html", cash = cash , actions = d_b)   





