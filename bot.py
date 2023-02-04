import random
import time
import os
import osmnx as ox
from igo import *

from staticmap import StaticMap, CircleMarker
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters


# As global variables we declare the graph of Barcelona ("graph"), its digraph,
# ("digraph"), the list of highways ("highways") and congestions
# ("congestions") that we take from the "opendata-ajuntament.barcelona.cat" and
# the intelligent graph ("igraph") that we build depending on the congestions
# of the moment.
# We save this data on global variables so that every user can access to them.
# The list of congestions and consecuently, the intelligent graph, need to be
# updated every five minutes as we have new data for the congestions in
# Barcelona.
# We will have another golbal variable, "time_last_update" where we save the
# time when we do thi s update.

print("Downloading data")
graph = obtain_graph(PLACE, GRAPH_FILENAME)
digraph = obtain_digraph(graph, DIGRAPH_FILENAME)
highways = download_highways(HIGHWAYS_URL)
congestions = download_congestions(CONGESTIONS_URL)
igraph = build_igraph(digraph, highways, congestions)
time_last_update = time.time()
print("Everything is ready")


def update_fields():
    """Function that actualizes the global variables of "congestions", "igraph"
    and "time_last_update". It downloads the congestions and build the new
    igraph depending on them.
    """
    global congestions, igraph, time_last_update
    congestions = download_congestions(CONGESTIONS_URL)
    igraph = build_igraph(digraph, highways, congestions)

    # It saves the time when this update has been done
    time_last_update = time.time()


def need_to_be_updated():
    """Function that determines whether our database of congestions needs to be
    updated. We need to take into account that this data is updated every five
    minutes in the URL.
    """
    # We save the instant hour
    actual_time = time.time()

    # If the hour of the last update is 5 or more that 5 minutes ago, we return
    # True. Otherwise, we return False.
    if actual_time-time_last_update >= 5*60:
        return True
    else:
        return False


def start(update, context):
    """Funciton that starts the conversation and sends a welcome message to the
    user.
    This function will be executed when the Bot receives the /start message.
    """
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Welcome to the iGo bot! \nI will help you to reach the " +
        "location you want in Barcelona in the fastest way as possible!")
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Let's begin. \nUse the /help command to display information " +
        "about the available commands.")


def help(update, context):
    """Function that gives some help information about the different commands
    available in the Bot.
    This function will be executed when the Bot receives the /help message.
    """
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="/start : Starts the conversation. \n/help : Offers help on " +
        "available commands. \n/author : Shows the name of the project " +
        "authors. \n/where + sending your location:  Shows the current " +
        "position of the user. \n/pos + the name or the coordinates of the " +
        "initial position: Allows you to choose the initial position " +
        "without it being your location.  \n/go + the name or the " +
        "coordinates of the destination: Shows the user a map to get from " +
        "their last sent current position to the destination point chosen, " +
        "tells the user the time it will take and the distance he will " +
        "travel.")


def author(update, context):
    """Function that sends a message with the names of the authors of this Bot.
    This function will be executed when the Bot receives the /author message.
    """
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Aina Luis Vidal and Sonia Castro Paniello.")


def where(update, context):
    """Function that asks for the user location.
    This function will be executed when the Bot receives the /where message.
    """
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Send me your location.")


def save_ubi(update, context):
    """Function that saves the user location and sends and imatge locating it
    in a map. If the lecture is not possible, it shows an error.
    This function will be executed when the Bot receives the user location.
    """
    try:
        # It reads the user location
        lat = update.message.location.latitude
        lon = update.message.location.longitude

        # It creates an image with the user location
        file = "%ubi.png" % random.randint(1000000, 9999999)
        map = StaticMap(500, 500)
        map.add_marker(CircleMarker((lon, lat), 'blue', 12))
        image = map.render()
        image.save(file)

        # It sends the image with the user location
        context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=open(file, 'rb'))
        os.remove(file)

        # It saves the user location in a user variable so that it can be used
        # in other functions.
        context.user_data['actual_ubi'] = (lat, lon)

    except Exception as e:
        print(e)
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="It has not been possible to save your location. Please try" +
            " again")


def go(update, context):
    """Function that reads a position and sends an image with the fastest path
    to reach this position from the actual user location. It also says what is
    the aproximate time to reach this position and how many quilometers are
    necessary to reach it.
    If there exist no path to the given destination, it shows an error.
    This function will be executed when the Bot receives the /go message.
    """
    try:
        # It reads the position we want to reach
        pos = ""
        for arg in context.args:
            pos = pos + ' ' + arg
        destination_pos = ox.geocode(pos)
        context.user_data['desti_ubi'] = destination_pos

        # If necessary, it actualizes the congestions data and the igraph
        if need_to_be_updated():
            update_fields()

        # It calculates the fastest path
        origin = context.user_data['actual_ubi']
        destination = context.user_data['desti_ubi']
        ipath = get_shortest_path_with_ispeeds(igraph, origin, destination)
        idistance = get_path_length(igraph, ipath)
        itime = get_path_time(igraph, origin, destination)
        idistance = round(idistance/1000, 2)
        itime = round(itime/60, 2)
        print("length =", idistance, "km")
        print("time =", itime, "mins")

        # It sends the image with the plot of the path
        file = "path_itime.png"
        plot_path(igraph, ipath, file, SIZE)
        context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=open(file, 'rb'))
        os.remove(file)

        # It sends a message with the distance to reach the destination
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="You have to move " + str(idistance) + " km to reach your " +
            "destination.")

        # It sends a message with the approximate time to reach the destination
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="You will approximately spend " + str(itime) + " minutes to" +
            " reach your destination.")

    except Exception as e:
        print(e)
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="There is no path to the given destination. Please try again")


def pos(update, context):
    """Function that saves a given location as the user location and sends an
    imatge locating it in a map. If the lecture is not possible, it shows an
    error.
    This function will be executed when the Bot receives the /pos message.
    """
    try:
        # It reads the location we want to fix as the user location
        pos = ""
        for arg in context.args:
            pos = pos + ' ' + arg
        initial_pos = ox.geocode(pos)
        lat = initial_pos[0]
        lon = initial_pos[1]

        # It creates an image with the user location
        file = "%ubi.png" % random.randint(1000000, 9999999)
        map = StaticMap(500, 500)
        map.add_marker(CircleMarker((lon, lat), 'blue', 12))
        image = map.render()
        image.save(file)

        # It sends the image with the user location
        context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=open(file, 'rb'))
        os.remove(file)

        # It saves this location as the user location in a user variable so
        # that it can be used in other functions.
        context.user_data['actual_ubi'] = initial_pos

    except Exception as e:
        print(e)
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="It has not been possible to save this location. Please try" +
            " again")


def main():
    TOKEN = open('token.txt').read().strip()
    updater = Updater(token=TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # We indicate which function needs to be executed when the Bot receives a
    # particular message from the user or its location.
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('help', help))
    dispatcher.add_handler(CommandHandler('author', author))
    dispatcher.add_handler(CommandHandler('pos', pos))
    dispatcher.add_handler(CommandHandler('where', where))
    dispatcher.add_handler(MessageHandler(Filters.location, save_ubi))
    dispatcher.add_handler(CommandHandler('go', go))

    # We turn on the Bot
    updater.start_polling()
    updater.idle()

main()
