import os, requests
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from dotenv import load_dotenv
import requests
from datetime import datetime, timedelta, timezone

# Sæt tidspunkt, hvor kampe skal starte efter
cutoff = datetime.now(timezone.utc).replace(hour=1, minute=0, second=0, microsecond=0) + timedelta(days=0)

load_dotenv()

app = Flask(__name__)

API_KEY = os.getenv("ODDS_API_KEY")

leagues = [
    # NCAA sports
    "americanfootball_ncaaf", 
    "baseball_ncaa", 
    "lacrosse_ncaa" ,

    # American football
    "americanfootball_ncaaf", 
    "americanfootball_nfl_preseason", 
    "americanfootball_ufl", 
    "aussierules_afl", 

    # Baseball
    "baseball_ncaa", 
    "baseball_mlb",

    # Basketball
    "basketball_euroleague", 
    "basketball_nba", 
    "basketball_ncaab", 

    # Icehockey
    "icehockey_ahl" ,
    "icehockey_liiga" ,
    "icehockey_sweden_hockey_league" ,

    # MMA/Boxing
    "mma_mixed_martial_arts" ,
    "boxing_boxing",


    # Soccer
    "soccer_africa_cup_of_nations" ,
    "soccer_argentina_primera_division" ,
    "soccer_australia_aleague" ,
    "soccer_austria_bundesliga" ,
    "soccer_belgium_first_div" ,
    "soccer_brazil_serie_b" ,
    "soccer_chile_campeonato" ,
    "soccer_china_superleague" ,
    "soccer_england_league2" ,
    "soccer_england_league1" ,
    "soccer_fa_cup" ,
    "soccer_fa_cup" ,
    "soccer_germany_bundesliga2" ,
    "soccer_germany_liga3" ,
    "soccer_greece_super_league" ,
    "soccer_italy_serie_b" ,
    "soccer_japan_j_league" ,
    "soccer_norway_eliteserien" ,
    "soccer_sweden_superettan" ,
    "soccer_turkey_super_league" ,
    "soccer_usa_mls" ,

    # Tennis
    "" ,
    "" ,
    "" ,
    "" ,
    "" ,
    "" ,
    "" ,
    "" ,
    "" ,
    "" ,
    "" ,
    ]

# Function to fetch odds for H2H markets
def fetch_odds_h2h():

    url = "https://api.the-odds-api.com/v4/sports/soccer_spain_la_liga/odds/"
    # Andre URLs kan indsættes her for at finde arbs på andre sportsgrene. Eksempelvis "tennis", "basketball", "baseball", "americanfootball".

    params = {
        "apiKey": API_KEY,
        "regions": "eu",         # EU bookmakers
        "markets": "h2h",        # Vælg mellem "h2h", "totals", "spreads", "draw_no_bet"
        "oddsFormat": "decimal",
        "bookmakers": "sport888,betanysports,betfair_ex_eu,matchbook,betonlineag,betsson,everygame,mybookieag,nordicbet,unibet_eu,williamhill,"
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        print("Status code:", response.status_code)
        print("Response content:", response.text)
        return {"error": "API call failed", "details": response.json()}

    return response.json()

# Function to fetch odds for Totals markets
def fetch_odds_totals():
    target_total = "7.5"  # <- Define it inside the function
    url = "https://api.the-odds-api.com/v4/sports/soccer_spain_la_liga/odds/"
    
    params = {
        "apiKey": API_KEY,
        "regions": "eu",
        "markets": "totals",
        "oddsFormat": "decimal",
        "bookmakers": "sport888,betanysports,betfair_ex_eu,matchbook,betonlineag,betsson,everygame,mybookieag,nordicbet,unibet_eu,williamhill"
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

### Routes to pages on the app ###

# Main route
@app.route("/")
def index():
    return render_template("index_backup.html")


# Route to arbitrage H2H bets, using the "fetch_odds_h2h" function. 
@app.route("/h2h-arb")
def h2h_page():
    odds_data = fetch_odds_h2h()
    arbitrage_bets = []

    # Check for errors in odds_data (assuming it's a list)
    if isinstance(odds_data, list):
        for event in odds_data:
            arbitrage_bets.extend(check_arbitrage(event))
    else:
        # Handle the case where odds_data might be an error message
        return render_template("h2h_arb_backup.html", odds=None, arbitrage=None, error=odds_data.get("error", "Unknown error"))

    return render_template("h2h_arb_backup.html", odds=odds_data, arbitrage=arbitrage_bets)

# Route to arbitrage total bets, using the "fetch_odds_totals" function. 
@app.route("/totals-arb")
def totals_page():
    odds_data = fetch_odds_totals()
    arbitrage_bets = []

    # Check for errors in odds_data (assuming it's a list)
    if isinstance(odds_data, list):
        for event in odds_data:
            arbitrage_bets.extend(check_arbitrage(event))
    else:
        # Handle the case where odds_data might be an error message
        return render_template("totals_arb_backup.html", odds=None, arbitrage=None, error=odds_data.get("error", "Unknown error"))

    return render_template("totals_arb_backup.html", odds=odds_data, arbitrage=arbitrage_bets)

# Route to test if the API key is working
@app.route("/api-test-h2h")
def h2h_api_test():
    odds_data = fetch_odds_h2h()

    if isinstance(odds_data, dict) and odds_data.get("error"):
        return render_template("api_test_h2h_backup.html", error=odds_data["error"], details=odds_data.get("details"), odds=None)

    return render_template("api_test_h2h_backup.html", odds=odds_data)

# Route to test if the API key is working
@app.route("/api-test-totals")
def totals_api_test():
    # Use the same fetch_odds function you already have
    odds_data = fetch_odds_totals()

    if isinstance(odds_data, dict) and odds_data.get("error"):
        return render_template("api_test_totals_backup.html", error=odds_data["error"], odds=None)

    return render_template("api_test_totals_backup.html", odds=odds_data)

if __name__ == "__main__":
    app.run(debug=True)


