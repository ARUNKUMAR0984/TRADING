from flask import Flask, render_template
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.ensemble import RandomForestRegressor
import yfinance as yf
import pandas as pd
import numpy as np

app = Flask(__name__)

# Function Definitions (same as your original code)
# Fetch stock data
def fetch_stock_data(ticker, period="1mo", interval="1d"):
    return yf.download(ticker, period=period, interval=interval)

# Calculate Moving Averages
def calculate_moving_averages(data, short_window=10, long_window=30):
    data['SMA10'] = data['Close'].rolling(window=short_window).mean()
    data['SMA30'] = data['Close'].rolling(window=long_window).mean()
    return data

# Identify Buy/Sell Signals
def identify_signals(data):
    data['Signal'] = 0
    data.loc[data['SMA10'] > data['SMA30'], 'Signal'] = 1  # Buy Signal
    data.loc[data['SMA10'] <= data['SMA30'], 'Signal'] = -1  # Sell Signal
    return data

# Calculate Daily Returns
def calculate_returns(data):
    data['Daily Return'] = data['Close'].pct_change() * 100  # Daily returns in percentage
    data['Cumulative Return'] = (1 + data['Daily Return'] / 100).cumprod() - 1  # Cumulative return
    return data

# Suggest Intraday or Delivery
def suggest_trade(data):
    daily_std = data['Daily Return'].std()
    return daily_std

# Analyze stocks by price range and suggest top 5 stocks
def analyze_stocks_by_price_range(results_df):
    price_data = {}
    for ticker in results_df['Ticker']:
        stock = yf.Ticker(ticker)
        try:
            price_data[ticker] = stock.info.get('currentPrice', np.nan)
        except Exception:
            price_data[ticker] = np.nan
    
    results_df['Current Price'] = results_df['Ticker'].map(price_data)
    
    price_ranges = [
        (0, 500),
        (500, 1000),
        (1000, 1500),
        (1500, 2000),
        (2000, float('inf'))
    ]
    
    recommendations = {
        'Intraday': {},
        'Delivery': {}
    }
    
    for i, (min_price, max_price) in enumerate(price_ranges, 1):
        range_stocks = results_df[
            (results_df['Current Price'] >= min_price) & 
            (results_df['Current Price'] < max_price)
        ]
        
        positive_profit_stocks = range_stocks[range_stocks['Cumulative Return'] > 0]
        intraday_stocks = positive_profit_stocks.nlargest(10, 'Volatility')
        
        delivery_stocks = range_stocks.loc[
            (range_stocks['Cumulative Return'] > 0)
        ].nsmallest(10, 'Volatility')
        
        recommendations['Intraday'][f'Price Range {min_price}-{max_price}'] = intraday_stocks[['Ticker', 'Current Price', 'Volatility', 'Mean Daily Return']]
        
        recommendations['Delivery'][f'Price Range {min_price}-{max_price}'] = delivery_stocks[['Ticker', 'Current Price', 'Cumulative Return', 'Mean Daily Return']]
    
    return recommendations

# Main Workflow for Nifty 50 Analysis
@app.route('/')
def main():
    nifty_50_tickers = [
        
 "360ONE.NS", "3MINDIA.NS", "ABB.NS", "ACC.NS", "AIAENG.NS", "APLAPOLLO.NS", "AUBANK.NS", "AADHARHFC.NS", 
    "AARTIIND.NS", "AAVAS.NS", "ABBOTINDIA.NS", "ACE.NS", "ADANIENSOL.NS", "ADANIENT.NS", "ADANIGREEN.NS", 
    "ADANIPORTS.NS", "ADANIPOWER.NS", "ATGL.NS", "AWL.NS", "ABCAPITAL.NS", "ABFRL.NS", "ABREL.NS", "ABSLAMC.NS", 
    "AEGISLOG.NS", "AFFLE.NS", "AJANTPHARM.NS", "AKUMS.NS", "APLLTD.NS", "ALKEM.NS", "ALKYLAMINE.NS", "ALOKINDS.NS", 
    "ARE&M.NS", "AMBER.NS", "AMBUJACEM.NS", "ANANDRATHI.NS", "ANANTRAJ.NS", "ANGELONE.NS", "APARINDS.NS", 
    "APOLLOHOSP.NS", "APOLLOTYRE.NS", "APTUS.NS", "ACI.NS", "ASAHIINDIA.NS", "ASHOKLEY.NS", "ASIANPAINT.NS", 
    "ASTERDM.NS", "ASTRAZEN.NS", "ASTRAL.NS", "ATUL.NS", "AUROPHARMA.NS", "AVANTIFEED.NS", "DMART.NS", 
    "AXISBANK.NS", "BASF.NS", "BEML.NS", "BLS.NS", "BSE.NS", "BAJAJ-AUTO.NS", "BAJFINANCE.NS", "BAJAJFINSV.NS", 
    "BAJAJHLDNG.NS", "BALAMINES.NS", "BALKRISIND.NS", "BALRAMCHIN.NS", "BANDHANBNK.NS", "BANKBARODA.NS", 
    "BANKINDIA.NS", "MAHABANK.NS", "BATAINDIA.NS", "BAYERCROP.NS", "BERGEPAINT.NS", "BDL.NS", "BEL.NS", 
    "BHARATFORG.NS", "BHEL.NS", "BPCL.NS", "BHARTIARTL.NS", "BHARTIHEXA.NS", "BIKAJI.NS", "BIOCON.NS", 
    "BIRLACORPN.NS", "BSOFT.NS", "BLUEDART.NS", "BLUESTARCO.NS", "BBTC.NS", "BOSCHLTD.NS", "BRIGADE.NS", 
    "BRITANNIA.NS", "MAPMYINDIA.NS", "CCL.NS", "CESC.NS", "CGPOWER.NS", "CIEINDIA.NS", "CRISIL.NS", "CAMPUS.NS", 
    "CANFINHOME.NS", "CANBK.NS", "CAPLIPOINT.NS", "CGCL.NS", "CARBORUNIV.NS", "CASTROLIND.NS", "CEATLTD.NS", 
    "CELLO.NS", "CENTRALBK.NS", "CDSL.NS", "CENTURYPLY.NS", "CERA.NS", "CHALET.NS", "CHAMBLFERT.NS", 
    "CHEMPLASTS.NS", "CHENNPETRO.NS", "CHOLAHLDNG.NS", "CHOLAFIN.NS", "CIPLA.NS", "CUB.NS", "CLEAN.NS", 
    "COALINDIA.NS", "COCHINSHIP.NS", "COFORGE.NS", "COLPAL.NS", "CAMS.NS", "CONCORDBIO.NS", "CONCOR.NS", 
    "COROMANDEL.NS", "CRAFTSMAN.NS", "CREDITACC.NS", "CROMPTON.NS", "CUMMINSIND.NS", "CYIENT.NS", "DLF.NS", 
    "DOMS.NS", "DABUR.NS", "DALBHARAT.NS", "DATAPATTNS.NS", "DEEPAKFERT.NS", "DEEPAKNTR.NS", "DELHIVERY.NS", 
    "DEVYANI.NS", "DIVISLAB.NS", "DIXON.NS", "LALPATHLAB.NS", "DRREDDY.NS", "EIDPARRY.NS", "EIHOTEL.NS", 
    "EASEMYTRIP.NS", "EICHERMOT.NS", "ELECON.NS", "ELGIEQUIP.NS", "EMAMILTD.NS", "EMCURE.NS", "ENDURANCE.NS", 
    "ENGINERSIN.NS", "EQUITASBNK.NS", "ERIS.NS", "ESCORTS.NS", "EXIDEIND.NS", "NYKAA.NS", "FEDERALBNK.NS", 
    "FACT.NS", "FINEORG.NS", "FINCABLES.NS", "FINPIPE.NS", "FSL.NS", "FIVESTAR.NS", "FORTIS.NS", "GRINFRA.NS", 
    "GAIL.NS", "GVT&D.NS", "GMRINFRA.NS", "GRSE.NS", "GICRE.NS", "GILLETTE.NS", "GLAND.NS", "GLAXO.NS", 
    "GLENMARK.NS", "MEDANTA.NS", "GODIGIT.NS", "GPIL.NS", "GODFRYPHLP.NS", "GODREJAGRO.NS", "GODREJCP.NS", 
    "GODREJIND.NS", "GODREJPROP.NS", "GRANULES.NS", "GRAPHITE.NS", "GRASIM.NS", "GESHIP.NS", "GRINDWELL.NS", 
    "GAEL.NS", "FLUOROCHEM.NS", "GUJGASLTD.NS", "GMDCLTD.NS", "GNFC.NS", "GPPL.NS", "GSFC.NS", "GSPL.NS", 
    "HEG.NS", "HBLPOWER.NS", "HCLTECH.NS", "HDFCAMC.NS", "HDFCBANK.NS", "HDFCLIFE.NS", "HFCL.NS", "HAPPSTMNDS.NS", 
    "HAVELLS.NS", "HEROMOTOCO.NS", "HSCL.NS", "HINDALCO.NS", "HAL.NS", "HINDCOPPER.NS", "HINDPETRO.NS", 
    "HINDUNILVR.NS", "HINDZINC.NS", "POWERINDIA.NS", "HOMEFIRST.NS", "HONASA.NS", "HONAUT.NS", "HUDCO.NS", 
    "ICICIBANK.NS", "ICICIGI.NS", "ICICIPRULI.NS", "ISEC.NS", "IDBI.NS", "IDFCFIRSTB.NS", "IFCI.NS", "IIFL.NS", 
    "INOXINDIA.NS", "IRB.NS", "IRCON.NS", "ITC.NS", "ITI.NS", "INDGN.NS", "INDIACEM.NS", "INDIAMART.NS", 
    "INDIANB.NS", "IEX.NS", "INDHOTEL.NS", "IOC.NS", "IOB.NS", "IRCTC.NS", "IRFC.NS", "IREDA.NS", "IGL.NS", 
    "INDUSTOWER.NS", "INDUSINDBK.NS", "NAUKRI.NS", "INFY.NS", "INOXWIND.NS", "INTELLECT.NS", "INDIGO.NS", 
    "IPCALAB.NS", "JBCHEPHARM.NS", "JKCEMENT.NS", "JBMA.NS", "JKLAKSHMI.NS", "JKTYRE.NS", "JMFINANCIL.NS", 
    "JSWENERGY.NS", "JSWINFRA.NS", "JSWSTEEL.NS", "JPPOWER.NS", "J&KBANK.NS", "JINDALSAW.NS", "JSL.NS", 
    "JINDALSTEL.NS", "JIOFIN.NS", "JUBLFOOD.NS", "JUBLINGREA.NS", "JUBLPHARMA.NS", "JUSTDIAL.NS", "JYOTHYLAB.NS", 
    "KPRMILL.NS", "KALPATPOWR.NS", "KALYANKJIL.NS", "KARURVYSYA.NS", "KEI.NS", "KIRLOSBROS.NS", "KITEX.NS", 
    "KNINFRATEC.NS", "KNRCON.NS", "KOLTEPATIL.NS", "KOTAKBANK.NS", "KPITTECH.NS", "KRBL.NS", "KSB.NS", "LTI.NS", 
    "LTTS.NS", "LICHSGFIN.NS", "LICI.NS", "LAXMIMACH.NS", "L&TFH.NS", "LTIM.NS", "LTI.NS", "LTTS.NS", "LUPIN.NS","LUXIND.NS", "MRF.NS", "M&M.NS", "M&MFIN.NS", "MAHINDCIE.NS", "MAHLIFE.NS", "MANAPPURAM.NS", 
    "MARICO.NS", "MARUTI.NS", "MASFIN.NS", "MASTEK.NS", "MFSL.NS", "MAXHEALTH.NS", "MAZDOCK.NS", 
    "MCX.NS", "MEDPLUS.NS", "MEGH.NS", "METROPOLIS.NS", "MIDHANI.NS", "MINDAIND.NS", "MINDTREE.NS", 
    "MIRZAINT.NS", "MOL.NS", "MOIL.NS", "MOTHERSUMI.NS", "MOTILALOFS.NS", "MRPL.NS", "MSUMI.NS", 
    "MTARTECH.NS", "MUTHOOTFIN.NS", "NATCOPHARM.NS", "NBCC.NS", "NESCO.NS", "NFL.NS", "NH.NS", 
    "NILKAMAL.NS", "NIPPOBATRY.NS", "NMDC.NS", "NOCIL.NS", "NTPC.NS", "NAVINFLUOR.NS", "NAVNETEDUL.NS", 
    "NAZARA.NS", "NCC.NS", "NELCAST.NS", "NESTLEIND.NS", "NITINSPIN.NS", "NIACL.NS", "NIITLTD.NS", 
    "NIITTECH.NS", "NLCINDIA.NS", "NSIL.NS", "OBEROIRLTY.NS", "OFSS.NS", "ONGC.NS", "OLECTRA.NS", 
    "ORIENTELEC.NS", "ORIENTCEM.NS", "ORIENTPPR.NS", "PAGEIND.NS", "PANAMAPET.NS", "PATANJALI.NS", 
    "PERSISTENT.NS", "PETRONET.NS", "PFIZER.NS", "PIIND.NS", "PNB.NS", "PNBGILTS.NS", "POLYCAB.NS", 
    "POLYMED.NS", "POWERGRID.NS", "PPL.NS", "PRAJIND.NS", "PRINCEPIPE.NS", "PRSMJOHNSN.NS", "PSB.NS", 
    "PSPPROJECT.NS", "PTC.NS", "PVRINOX.NS", "PNCINFRA.NS", "QUESS.NS", "RBLBANK.NS", "RCF.NS", 
    "RECLTD.NS", "REDEXPO.NS", "RELAXO.NS", "RELIANCE.NS", "RENUKA.NS", "RHIM.NS", "ROHLTD.NS", 
    "ROSSARI.NS", "ROUTE.NS", "SBICARD.NS", "SBILIFE.NS", "SBIN.NS", "SIS.NS", "SKFINDIA.NS", "SRF.NS", 
    "SJVN.NS", "STLTECH.NS", "SUDARSCHEM.NS", "SUMICHEM.NS", "SUNPHARMA.NS", "SUNTV.NS", "SWSOLAR.NS", 
    "SYMPHONY.NS", "TATACOMM.NS", "TATACONSUM.NS", "TATAELXSI.NS", "TATAMOTORS.NS", "TATAPOWER.NS", 
    "TATASTEEL.NS", "TCI.NS", "TCPLPACK.NS", "TECHM.NS", "THERMAX.NS", "THYROCARE.NS", "TIMKEN.NS", 
    "TITAN.NS", "TORNTPOWER.NS", "TORNTPHARM.NS", "TRENT.NS", "TRIDENT.NS", "TRIVENI.NS", "TTKPRESTIG.NS", 
    "TV18BRDCST.NS", "TVSMOTOR.NS", "UBL.NS", "UCOBANK.NS", "UFLEX.NS", "UPL.NS", "UTIAMC.NS", 
    "VBL.NS", "VEDL.NS", "VENKEYS.NS", "VINATIORGA.NS", "VIPIND.NS", "VMART.NS", "VOLTAS.NS", "WABCOINDIA.NS", 
    "WELCORP.NS", "WELSPUNIND.NS", "WESTLIFE.NS", "WHIRLPOOL.NS", "WIPRO.NS", "WOCKPHARMA.NS", 
    "YESBANK.NS", "ZEEL.NS", "ZYDUSLIFE.NS" 
        # Add more tickers as needed
    ]

    results = []
    for ticker in nifty_50_tickers:
        stock_data = fetch_stock_data(ticker, period="1mo", interval="1d")

        if stock_data.empty:
            continue

        stock_data = calculate_moving_averages(stock_data)
        stock_data = identify_signals(stock_data)
        stock_data = calculate_returns(stock_data)

        volatility = suggest_trade(stock_data)

        results.append({
            "Ticker": ticker,
            "Volatility": volatility,
            "Mean Daily Return": stock_data['Daily Return'].mean(),
            "Cumulative Return": stock_data['Cumulative Return'].iloc[-1] * 100,
        })

    results_df = pd.DataFrame(results)
    recommendations = analyze_stocks_by_price_range(results_df)

    return render_template('index.html', recommendations=recommendations)

if __name__ == "__main__":
    app.run(debug=True)