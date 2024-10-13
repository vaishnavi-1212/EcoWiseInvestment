from flask import Flask, render_template, request, redirect, url_for, send_file
import allocate_capital
import get_rankings
import pandas as pd
import plotly
import json
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'hwedfbuyhedbfwe3484747erh')
app.debug = True

#Home page:
@app.route('/')
def home():
    return render_template('index1.html')

#Allocation page getting user input to create portfolio:
@app.route('/index', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

#Allocation page getting user input to create portfolio:
@app.route('/allocation', methods=['GET', 'POST'])
def allocation():
    if request.method == 'POST':
        return redirect(url_for("portfolio"))
    else:
        return render_template('allocation.html')

#Allocation page giving the portfolio from user input:
@app.route("/allocation/portfolio", methods=['GET', 'POST'])
def portfolio():
    #Get user input data from form:
    e_scr = request.form.get("E", '')                         #Environmental
    s_scr = request.form.get("S", '')                         #Social
    g_scr = request.form.get("G", '')                         #Governance
    risk = float(request.form.get("risk", 0))                #Risk-aversion
    del_sectors = request.form.getlist("sectors")     #Sectors to delete
    del_symbs = request.form.get("symb", '').split(',')   #Stocks to delete

    #Get portfolio charts and metrics with user inputs from the allocation algo:
    metrics, fig_stocks, fig_sectors = allocate_capital.get_portfolio(e_scr,
                                                                      s_scr,
                                                                      g_scr,
                                                                      risk,
                                                                      del_sectors,
                                                                      del_symbs)
    #Use JSON and Plotly to display charts on the webpage:
    port_stocks = json.dumps(fig_stocks, cls=plotly.utils.PlotlyJSONEncoder)
    port_sectors = json.dumps(fig_sectors, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template('portfolio.html', graph_stocks=port_stocks,
                                             graph_sectors=port_sectors,
                                             e_scr=metrics.get('E_scr', 0),
                                             s_scr=metrics.get('S_scr', 0),
                                             g_scr=metrics.get('G_scr', 0),
                                             esg_scr=metrics.get('ESG_scr', 0),
                                             ret=metrics.get('Ret', 0),
                                             vol=metrics.get('Vol', 0),
                                             beta=metrics.get('beta', 0))

#Route to allow downloading option of CSV file of allocations:
@app.route("/download")
def download_csv():
    f = os.path.join('static', 'data', 'portfolio.csv')
    return send_file(f, as_attachment=True)

#Ratings search page:
@app.route("/ratings", methods=['GET', 'POST'])
def ratings():
    #Read in stock symbols and their ESG data:
    data_path = os.path.join('static', 'data', 'stock_data.csv')
    data = pd.read_csv(data_path, index_col='ticker')

    #If user submits a stock symbol, show that new page with the ratings:
    if request.method == "POST":
        stock = request.form['symbol-rating']
        return redirect(url_for('stock_ratings', symbol=stock))

    #If user simply requests to see this page, show it instead:
    else:
        return render_template('ratings.html', data=data)

#Ratings page for each symbol searched above:
@app.route("/ratings/<symbol>")
def stock_ratings(symbol):
    #Get ESG rankings and stock info:
    symbol_info = get_rankings.get_company(symbol)

    return render_template('stock_ratings.html', symb_info=symbol_info, stock=symbol)

#Main methodologies page to see allocation and rating methods:
@app.route("/methodologies")
def methodologies():
    return render_template('methodologies.html')

#Methodology page for allocation model:
@app.route("/methodologies/allocation")
def allocation_methodology():
    return render_template('alloc_method.html')

#Methodology page for scoring firms on ESG criteria:
@app.route("/methodologies/esg-scores")
def scoring_methodology():
    return render_template('scoring_method.html')

#Methodology page for technology tools used:
@app.route("/methodologies/tech-used")
def tech_methodology():
    return render_template('tech_method.html')

#Contact me page:
@app.route("/contact")
def contact_me():
    return render_template('contact.html')

@app.route("/chat_now")
def chat_now():
    return redirect('http://localhost:8501') 

if __name__ == '__main__':
    app.run(debug=True, port=5000) 
