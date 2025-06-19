import os, requests
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from dotenv import load_dotenv
import requests
from datetime import datetime, timedelta, timezone
import secrets

# Sæt tidspunkt, hvor kampe skal starte efter
cutoff = datetime.now(timezone.utc).replace(hour=1, minute=0, second=0, microsecond=0) + timedelta(days=0)

load_dotenv()

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

API_KEY = os.getenv("ODDS_API_KEY")

# Function to set region
def get_bookmakers_for_region(region):
    if region == "us":
        return "draftkings,fanduel,betmgm,williamhill_us,pointsbetus,wynnbet"
    elif region == "eu":
        return "sport888,betanysports,betfair_ex_eu,matchbook,betsson,everygame,mybookieag,nordicbet,unibet_eu,williamhill"
    else:
        return ""

# Function to fetch odds
def fetch_odds_h2h(sport="baseball_mlb", region="eu"):

    print(f"Fetching H2H odds for sport: {sport}, region: {region}")
    
    url = f"https://api.the-odds-api.com/v4/sports/{sport}/odds/"
    # Andre URLs kan indsættes her for at finde arbs på andre sportsgrene. Eksempelvis "tennis", "basketball", "baseball", "americanfootball".

    params = {
        "apiKey": API_KEY,
        "regions": region,         # EU bookmakers
        "markets": "h2h",        # Vælg mellem "h2h", "totals", "spreads", "draw_no_bet"
        "oddsFormat": "decimal",
        "bookmakers": get_bookmakers_for_region(region)
    }

    response = requests.get(url, params=params)
    if response.status_code != 200:
        return {"error": "API call failed", "details": response.json()}

    return response.json()

def fetch_odds_totals(sport="baseball_mlb", region="eu"):
    target_total = "2.5"  # <- Define it inside the function

    print(f"Fetching totals odds for sport: {sport}, region: {region}")

    url = f"https://api.the-odds-api.com/v4/sports/{sport}/odds/"
    
    params = {
        "apiKey": API_KEY,
        "regions": region,         # EU bookmakers
        "markets": "h2h",        # Vælg mellem "h2h", "totals", "spreads", "draw_no_bet"
        "oddsFormat": "decimal",
        "bookmakers": get_bookmakers_for_region(region)
    }

    response = requests.get(url, params=params)
    if response.status_code != 200:
        return {"error": "API call failed", "details": response.json()}

    all_events = response.json()

    # Filter markets to only include totals with "target_total" goals
    for event in all_events:
        filtered_bookmakers = []
        for bookmaker in event.get("bookmakers", []):
            filtered_markets = []
            for market in bookmaker.get("markets", []):
                if market["key"] == "totals":
                    outcomes = market.get("outcomes", [])
                    if all(str(outcome.get("point")) == target_total for outcome in outcomes if "point" in outcome):
                        filtered_markets.append(market)
            if filtered_markets:
                bookmaker["markets"] = filtered_markets
                filtered_bookmakers.append(bookmaker)
        event["bookmakers"] = filtered_bookmakers

    return all_events

def check_arbitrage(event):
    
    # Only include games starting after 12:00 tomorrow (UTC)
    cutoff = datetime.now(timezone.utc).replace(hour=15, minute=30, second=0, microsecond=0) + timedelta(days=0)
    event_time = datetime.fromisoformat(event['commence_time'].replace("Z", "+00:00"))
    if event_time < cutoff:
        return []    
    
    outcomes = {}

    # Extract odds for each bookmaker
    for bookmaker in event['bookmakers']:
        name = bookmaker['title']
        try:
            odds = bookmaker['markets'][0]['outcomes']
            if len(odds) == 2:  # Ensure there are exactly two outcomes (home vs away)
                outcomes[name] = {
                    odds[0]['name']: odds[0]['price'],
                    odds[1]['name']: odds[1]['price']
                }
        except KeyError:
            continue  # Skip events with missing data

    # Check for arbitrage opportunities between different bookmakers
    bookies = list(outcomes.keys())
    arbitrage_opportunities = []
    
    for i in range(len(bookies)):
        for j in range(len(bookies)):
            if i != j:  # Avoid comparing the same bookmaker to itself
                b1 = bookies[i]
                b2 = bookies[j]

                for o1, odds1 in outcomes[b1].items():
                    for o2, odds2 in outcomes[b2].items():
                        if o1 != o2:  # Opposite outcomes (home vs away)
                            inv_prob = 1 / odds1 + 1 / odds2
                            if inv_prob < 1:  # Arbitrage found
                                profit_margin = (1 - inv_prob) * 100
                                
                                # Filter: Only include bets with a profit margin of X% or more. Adjust filter if needed.
                                if profit_margin <= 5:
                                    arbitrage_opportunities.append({
                                        "event": f"{event['home_team']} vs {event['away_team']}",
                                        "sport": event.get("sport_key", "N/A"),
                                        "time": event.get("commence_time", "N/A"),                                        
                                        "outcome_1": f"{o1} at {b1}: {odds1}",
                                        "outcome_2": f"{o2} at {b2}: {odds2}",
                                        "profit_margin": profit_margin
                                })
    
    return arbitrage_opportunities



### Functions for functionality on the index page ###

@app.route('/set-sport', methods=['POST'])
def set_sport():
    data = request.get_json()
    session['sport'] = data.get('sport', 'baseball_mlb')
    return jsonify({"message": "Sport updated"}), 200

@app.route('/set-region', methods=['POST'])
def set_region():
    data = request.get_json()
    session['region'] = data.get('region', 'eu')
    return jsonify({"message": "Region updated"}), 200


@app.route("/get-arbitrage-count", methods=["GET"])
def get_arbitrage_count():
    sport = request.args.get("sport", "baseball_mlb")
    region = request.args.get("region", "eu")

    # Fetch H2H arbitrage bets
    h2h_odds = fetch_odds_h2h(sport, region)
    h2h_arbs = []
    if isinstance(h2h_odds, list):
        for event in h2h_odds:
            h2h_arbs.extend(check_arbitrage(event))

    # Fetch Totals arbitrage bets
    totals_odds = fetch_odds_totals(sport, region)
    totals_arbs = []
    if isinstance(totals_odds, list):
        for event in totals_odds:
            totals_arbs.extend(check_arbitrage(event))

    return jsonify({
        "h2h_count": len(h2h_arbs),
        "totals_count": len(totals_arbs),
        "total_count": len(h2h_arbs) + len(totals_arbs)
    })



### Routes to pages on the app ###

# Main route
@app.route("/", methods=["GET"])
def index():
    # Get the selected sport from the GET request (default to "baseball_mlb")
    sport = session.get("sport", "baseball_mlb")
    region = session.get("region", "eu")

    # Fetch odds for the selected sport
    odds_data = fetch_odds_h2h(sport=sport, region=region)
    
    # Handle errors if fetching odds fails
    if isinstance(odds_data, dict) and odds_data.get("error"):
        return render_template("index.html", error=odds_data["error"])

    # Render the landing page with odds data
    return render_template("index.html", odds=odds_data, sport=sport, region=region)



# Route to arbitrage H2H bets, using the fetch_odds_heh function. 
@app.route("/h2h-arb")
def h2h_page():
    sport = session.get("sport", "baseball_mlb")  # Use sport from session
    region = session.get("region", "eu") 

    odds_data = fetch_odds_h2h(sport, region)
    arbitrage_bets = []

    if isinstance(odds_data, list):
        for event in odds_data:
            arbitrage_bets.extend(check_arbitrage(event))
    else:
        return render_template("h2h_arb.html", odds=None, arbitrage=None, error=odds_data.get("error", "Unknown error"))

    return render_template("h2h_arb.html", odds=odds_data, arbitrage=arbitrage_bets, sport=sport, region=region)




# Route to arbitrage total bets, using the "fetch_odds_totals" function. 
@app.route("/totals-arb")
def totals_page():
    sport = session.get("sport", "baseball_mlb")
    region = session.get("region", "eu") 

    odds_data = fetch_odds_totals(sport, region)
    arbitrage_bets = []

    if isinstance(odds_data, list):
        for event in odds_data:
            arbitrage_bets.extend(check_arbitrage(event))
    else:
        return render_template("totals_arb.html", odds=None, arbitrage=None, error=odds_data.get("error", "Unknown error"))

    return render_template("totals_arb.html", odds=odds_data, arbitrage=arbitrage_bets, region=region)



# Route to test if the API key is working for H2H bets
@app.route("/api-test-h2h")
def api_test():
    sport = session.get("sport", "baseball_mlb")  # Read sport from session
    region = session.get("region", "eu") 

    odds_data = fetch_odds_h2h(sport, region)

    if isinstance(odds_data, dict) and odds_data.get("error"):
        return render_template("api_test_h2h.html", error=odds_data["error"], odds=None)

    return render_template("api_test_h2h.html", odds=odds_data, sport=sport, region=region)



# Route to test if the API key is working for Totals bets
@app.route("/api-test-totals")
def api_test_totals():
    sport = session.get("sport", "baseball_mlb")  # Read sport from session
    region = session.get("region", "eu") 

    odds_data = fetch_odds_totals(sport, region)

    if isinstance(odds_data, dict) and odds_data.get("error"):
        return render_template("api_test_totals.html", error=odds_data["error"], odds=None)

    return render_template("api_test_totals.html", odds=odds_data, sport=sport, region=region)


if __name__ == "__main__":
    app.run(debug=True)


