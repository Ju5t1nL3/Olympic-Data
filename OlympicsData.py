"""
The program allows the user to see formatted olympic data. They can see rankings of countries by bronze, 
silver, gold, or total medals. They can also look at all the events for a certain day, and filter it by country,
discipline, or both.
"""

import requests
import time
from datetime import date
from pprint import PrettyPrinter
import sys
from deep_translator import GoogleTranslator

BASE_URL = "https://apis.codante.io"
ALL_JSON = "/olympic-games"
COUNTRIES_JSON = BASE_URL + ALL_JSON + "/countries"
DISCIPLINES_JSON = BASE_URL + ALL_JSON + "/disciplines"
EVENTS_JSON = BASE_URL + ALL_JSON + "/events"

CLEAR = "\033[K"
RETURN = "\033[1A"
RETURN_AND_CLEAR = RETURN + CLEAR

CLEAR_ALL = "\033[2J"
RETURN_HOME = "\033[H"
WIPE_EVERYTHING = CLEAR_ALL + RETURN_HOME

printer = PrettyPrinter()

'''
def create_country_list():
    """
    Grabs all 3-letter codes from countries endpoint of the api and stores them in a text file called Countries.txt.
    """
    country_list = []
    for page in range(5):
        data = requests.get(f"{COUNTRIES_JSON}?page={str(page+1)}").json()["data"]
        for country in data:
            name = GoogleTranslator(source = "pt", target = "en").translate(country["name"])
            id = country["id"]
            country_list.append({
                "name": name,
                "id": id,
            })
    country_list.sort(key = lambda x: x["name"])

    with open("Countries.txt","w") as f:
        for country in country_list:
            f.write(f"{country["name"]} - {country["id"]}\n")

def create_discipline_list():
    """
    Grabs all 3-letter codes from disciplines endpoint of the api and stores them in a text file called Disciplines.txt.
    """
    data = requests.get(DISCIPLINES_JSON).json()["data"]

    with open("Disciplines.txt","w") as f:
        for discipline in data:
            name = discipline["name"]
            id = discipline["id"]
            f.write(f"{name} - {id}\n")
'''


def format_rank(rank, format="b"):
    """
    Returns a formatted version of the rank based on if format a or b is needed.
    """
    if rank == "b":
        rank = "bronze medals"
    elif rank == "s":
        rank = "silver medals"
    elif rank == "g":
        rank = "gold medals"
    else:
        rank = "medals"

    if format == "a":
        if rank == "medals":
            rank = "total_medals"
        else:
            rank = rank.replace(" ", "_")

    return rank


def filtered_country_list(rank):
    """
    Rank represents what to rank the countries by (e.g., gold medals). This method
    returns an enumerated list of all the countries that have at least one of the medals and orders
    them from greatest to least.
    """

    rank = format_rank(rank, "a")
    country_list = []
    for page in range(5):
        data = requests.get(f"{COUNTRIES_JSON}?page={\
                            str(page+1)}").json()["data"]
        for country in data:
            name = country["name"]
            medals = country[rank]
            country_list.append({
                "name": name,
                "medals": medals,
                "ranking": 0
            })

    country_list = list(filter(lambda x: x["medals"] != 0, country_list))
    country_list.sort(key=lambda x: int(x["medals"]), reverse=True)
    enumerated_country_list = list(enumerate(country_list))

    return enumerated_country_list


def get_rankings(rank):
    """
    Takes in how countries should be ranked. Then, stores them all in a list and displays 10 at a time.
    """
    country_list = filtered_country_list(rank)
    rank = format_rank(rank)

    more_rankings = "y"
    start = -10
    stop = 0

    while more_rankings == "y":
        start += 10
        stop += 10

        if start >= len(country_list):
            print(f"Those are all the countries that have {rank}!")
            more_rankings == "stop everything"
            break
        else:
            for index, country in country_list[start:stop]:
                if index >= len(country_list):
                    print("Those are all the countries that have gold medals!")
                    more_rankings == "stop everything"
                    break
                if country["medals"] == country_list[index - 1][1]["medals"]:
                    country["ranking"] = country_list[index - 1][1]["ranking"]
                else:
                    country["ranking"] = index + 1

                print(f"{str(country["ranking"])}. {GoogleTranslator(
                    source="pt", target="en").translate(country["name"])}: {country["medals"]} {rank}")

            while True:
                more_rankings = input(
                    "Do you want to see more countries? (Y/N): ").lower().strip()
                if more_rankings != "y" and more_rankings != "n":
                    print("That is not an accepted answer")
                    time.sleep(1)
                    print(f"{RETURN_AND_CLEAR}{RETURN_AND_CLEAR}{RETURN}")
                else:
                    print(f"{RETURN_AND_CLEAR}{RETURN}")
                    break


def choose_rankings():
    """
    Asks the user how they want to rank the countries, and prints the rankings.
    """
    print("B - bronze medals\nS - silver medals\nG - gold medals\nT - total medals\nX - exit\n")
    while True:
        answer = input(
            "What would you like to see rankings of? (B/S/G/T/X): ").lower().strip()
        if answer == "x":
            sys.exit()
        elif answer not in ("b", "s", "g", "t"):
            print("That is not an accepted answer")
            time.sleep(1)
            print(f"{RETURN_AND_CLEAR}{RETURN_AND_CLEAR}{RETURN}")
        else:
            break

    print(WIPE_EVERYTHING)
    get_rankings(answer)


def check_versus(event):
    """
    Checks if it is a head to head event. Returns True if it is and False if it is not.
    """
    if (event["competitors"][0]["result_winnerLoserTie"] != "" and event["competitors"][0]["country_id"] != "") \
            or (event["competitors"][1]["result_winnerLoserTie"] != "" and event["competitors"][1]["country_id"] != ""):
        return True
    return False


def check_competitor_name(competitor, country_name):
    """
    Returns the competitor name if it exists and None if it doesn't.
    """
    if competitor["competitor_name"] != country_name and competitor["competitor_name"] != competitor["country_id"]:
        return competitor["competitor_name"]
    return None


def check_competitor_present(country, format):
    """
    Returns True if the competitor name if it exists and False if it doesn't.
    """
    if format == "one":
        if country["comp_name"] != None:
            return True
        return False
    elif format == "two":
        if country["competitor_name"] != GoogleTranslator(source="pt", target="en").translate(country["country_id"]) and country["competitor_name"] != country["country_id"]:
            return True
        return False


def country_exists(country):
    """
    Returns True if the country exists and False if it doesn't.
    """
    if country["country_id"] != "":
        return True
    return False


def display_results(format, comp_name_present, competitors=[], competitor={}):
    """
    Prints all the events that fit the filter based on the format.
    """
    print("")
    if format == "versus":
        if not comp_name_present:
            print(f"{competitors[0]["name"]} ({competitors[0]["result"]}) vs. {\
                  competitors[1]["name"]} ({competitors[1]["result"]})")
            print(f"{competitors[0]["score"]} - {competitors[1]["score"]}")
        else:
            print(f"{competitors[0]["name"]}: {competitors[0]["comp_name"]} ({competitors[0]["result"]}) vs. {\
                  competitors[1]["name"]}: {competitors[1]["comp_name"]} ({competitors[1]["result"]})")
            print(f"{competitors[0]["score"]} - {competitors[1]["score"]}")
    elif format == "list":
        print(competitor["name"])
        if comp_name_present:
            print(competitor["comp_name"])
        print(f"Position: {str(competitor["position"])}")
    elif format == "no results":
        name = GoogleTranslator(source="pt", target="en").translate(
            competitor["country_id"])
        print(name)
        if comp_name_present:
            print(competitor["competitor_name"])


def create_competitor_dict(competitor, format):
    """
    Creates the dictionary of info for the competitor and returns it based on the format of the event.
    """
    country_name = GoogleTranslator(
        source="pt", target="en").translate(competitor["country_id"])
    comp_name = check_competitor_name(competitor, country_name)
    if format == "versus":
        score = competitor["result_mark"]
        result = competitor["result_winnerLoserTie"]
        competitor_info = {
            "name": country_name,
            "score": score,
            "result": result,
            "comp_name": comp_name
        }
    elif format == "list":
        position = competitor["position"] + 1
        competitor_info = {
            "name": country_name,
            "position": position,
            "comp_name": comp_name
        }
    return competitor_info


def filter_json(json_link, filter, txt):
    """
    Returns the new json link if a new filter is added and the same json link if no new filter is added.
    """
    while True:
        answer = input(f"Would you like to filter by {\
                       filter}? (Y/N): ").strip().lower()
        if answer == "y":
            code = input(
                f"Enter the 3-letter code of the {filter} (located in {txt}): ").strip().upper()
            json_link += f"&{filter}={code}"
            break
        elif answer == "n":
            break
        else:
            print("That is not an accepted answer")
            time.sleep(1)
            print(f"{RETURN_AND_CLEAR}{RETURN_AND_CLEAR}{RETURN}")

    print(WIPE_EVERYTHING)
    return json_link


def filter_events():
    """
    Returns a json link with all the combined chosen filters (date, discipline, country)
    """
    json_link = f"{EVENTS_JSON}?date="
    print("T - today\nO - other\nX - exit\n")
    while True:
        answer = input(
            "Would you like to look at today's events or another day's? (T/O/X): ").lower().strip()
        if answer == "x":
            sys.exit()
        elif answer not in ("t", "o"):
            print("That is not an accepted answer")
            time.sleep(1)
            print(f"{RETURN_AND_CLEAR}{RETURN_AND_CLEAR}{RETURN}")
        else:
            break

    if answer == "t":
        date_filter = str(date.today())
    else:
        date_filter = input(
            "Which date would you like to look at? (YYYY-MM-DD): ").strip()

    print(WIPE_EVERYTHING)
    json_link += date_filter

    json_link = filter_json(json_link, "discipline", "Disciplines.txt")
    json_link = filter_json(json_link, "country", "Countries.txt")

    return json_link


def events_list():
    """
    Creates the entire list of events based on the filters
    """

    json_link = filter_events()
    total_pages = requests.get(json_link).json()["meta"]["last_page"]

    print(WIPE_EVERYTHING)
    for page in range(total_pages):

        data = requests.get(f"{json_link}&page={\
                            page + 1}").json()["data"]
        for event in data:
            if len(event["competitors"]) < 2:
                continue
            print(
                "--------------------------------------------------------------------------")
            print(event["discipline_name"].upper())
            print(event["detailed_event_name"])
            status = event["status"]
            print(f"Status: {status}")

            if status == "Finished":
                competitors = []
                if check_versus(event):
                    event_format = "versus"
                    for competitor in event["competitors"]:
                        if not country_exists(competitor):
                            continue
                        else:
                            competitor_info = create_competitor_dict(
                                competitor, event_format)
                            competitors.append(competitor_info)

                    comp_name_present = check_competitor_present(
                        competitors[0], "one")
                    display_results(
                        event_format, comp_name_present, competitors=competitors)

                else:
                    event_format = "list"
                    for competitor in event["competitors"]:
                        if not country_exists(competitor):
                            continue
                        else:
                            competitor_info = create_competitor_dict(
                                competitor, event_format)
                            competitors.append(competitor_info)

                    competitors.sort(key=lambda x: x["position"])
                    comp_name_present = check_competitor_present(
                        competitors[0], "one")
                    for competitor in competitors:
                        display_results(
                            event_format, comp_name_present, competitor=competitor)

            else:
                for competitor in event["competitors"]:
                    if not country_exists(competitor):
                        continue
                    else:
                        comp_name_present = check_competitor_present(
                            competitor, "two")
                        display_results(
                            "no results", comp_name_present, competitor=competitor)


def main():
    """
    Asks the user what function of the program that would like to use, and runs the appropriate mode.
    """
    print("R - rankings\nE - events\nX - exit\n")
    while True:
        answer = input(
            "Would you like to look at Olympic rankings or events? (R/E/X): ").lower().strip()
        if answer == "x":
            sys.exit()
        elif answer not in ("r", "e"):
            print("That is not an accepted answer")
            time.sleep(1)
            print(f"{RETURN_AND_CLEAR}{RETURN_AND_CLEAR}{RETURN}")
        else:
            break
    print(WIPE_EVERYTHING)
    if answer == "r":
        choose_rankings()
    else:
        events_list()


main()  # starts program
