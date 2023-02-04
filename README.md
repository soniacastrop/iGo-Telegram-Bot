# iGo

iGo is a Telegram Bot that allows, within the city of Barcelona, ​​to guide users from
their current position to a chosen destination by the fastest road by car, using the new concept
of itime (smart time) that takes into account the state of the traffic in real time in certain
sections of the city. It also tells the users how much time they would take and the distance they
 would need to travel to reach the destination.

---

## Installation

The user needs to download **Telegram** on their phone or [Telegram desktop](https://desktop.telegram.org/) on their computer. The user can acces this bot by clicking on the loup and look up **@i_go_bot** or **IGo** or with this link [IGo bot](https://t.me/i_go_bot).

---

## Usage
The [@i_go_bot](t.me/i_go_bot) has five commands. You have to write them and send them as a normal message.

<img src=https://user-images.githubusercontent.com/83398384/120077191-7501f280-c0a9-11eb-8615-9216a1af4db9.png width = 300)>

**/start** : Starts the conversation.

**/help** : Offers help on available orders.

**/author** : Shows the name of the project authors.

**/where + sending your location**:   After receiving the user location, sends him a picture with his current position.

The user can send their location by clicking on the clip icon and then on "location" and "send current location" as the following pictures show.

<img align="left" src=https://user-images.githubusercontent.com/83398384/120077087-eb522500-c0a8-11eb-8cdc-f233cda03864.png width = 300)>
<img align="center" src=https://user-images.githubusercontent.com/83398384/120077091-ec835200-c0a8-11eb-9e85-f1c4cd0ae827.png width = 300)>


**/pos + the name or the coordinates of the initial position**: It allows the user to choose the initial position without it being their location. The bot sends the user a picture with that position.

The coordinates need to be written in order (latitude longitude) with a space in between.

<img align="left" src=https://user-images.githubusercontent.com/83398384/120111119-f4a6c480-c170-11eb-9307-6266342baf8c.png width = 300)>
<img align="center" src=https://user-images.githubusercontent.com/83398384/120076707-4420be00-c0a7-11eb-8e3f-edc24ac0d655.png  width = 300)>

**/go + the name or the coordinates of the destination**: Shows the user a map to get from their last sent current position to the destination point chosen. And tells the user the time it will take and the distance they will travel.

<img src=https://user-images.githubusercontent.com/83398384/120076653-f5732400-c0a6-11eb-98ec-45e787316192.png width = 300)>

*Warning: The user needs to do a /where or /pos command to save an initial position before using the /go command.*

---

## Implementation

All the libraries that need to be installed are mentioned in the _requirements.txt_.

IGo is implemented with two modules:
- _igo.py_ : contains all the code and data structures related to the acquisition and storage of graphs corresponding to maps, congestions and route calculations.
- _bot.py_: contains all the code related to the bot. It uses the _igo.py_ module.

The igo.py module has the following functions:

```python
obtain_graph(PLACE, file_name) # Returns a graph from de given "PLACE".
obtain_digraph(graph, file_name) # Given a "graph" returns its directed graph.
exists_graph(file_name) # Determines whether a graph exists or not in a concret file named "file_name".
download_graph(PLACE) # Downloads and returns a graph from a "PLACE".
load_graph(file_name) # Loads a graph from the file named "file_name" and returns it.
create_digraph(graph) # Given a "graph" returns its directed graph.
save_graph(graph, file_name) # Saves a given "graph" in a file named as the parameter "file_name".
plot_graph(graph) # Plots a given "graph". 
_adapt_to_list(coordinates) # Given a string with a list of "coordinates", separates them and return a list of pairs of coordinates.
download_highways(HIGHWAYS_URL) # Downloads the highways from a given URL and returns a list with all of them.
_show_highways(highways) # Prints the information of all the "highways".
plot_highways(highways, name, SIZE) # Generates a ("SIZE" x "SIZE") PNG file called "name" in which it plots the "highways" in a map of the corresponding city.
download_congestions(CONGESTIONS_URL) # Downloads the congestions from a given URL and returns a list with all of them.
_show_congestions(congestions) # Prints the information of all the "congestions".
plot_congestions(highways, congestions, name, SIZE)  # Generates a ("SIZE" x "SIZE") PNG file called "name" in which it plots the "highways" with different colours depending on the "congestions" of the "highways" in a map of the corresponding city.
_colour(congestion) # Given a number of "congestion" it returns a color.
_factor(congestion) #  Given a number of "congestion", it returns a factor depending on it.
spread_congestions(digraph, highways, congestions) # Spreads the congestions of the highways to the edges of the osmnx graph.
new_itime_attribute(digraph)  # For every edge in the "digraph", it creates a new attribute called "itime" which represents the aproximate time needed to travel through this edge.
build_igraph(digraph, highways, congestions) # Builds an intelligent graph adding a new attribute to the edges of our "digraph" called "itime". 
get_shortest_path_with_ispeeds(igraph, actual_ubi, desti_ubi) # Returns a list of nodes corresponding to the fastest path to go from "actual_ubi" to "desti_ubi" depending on the "itime".
get_path_time(igraph, actual_ubi, desti_ubi) # Returns the time to travel the shortest path to go from "actual_ubi" to "desti_ubi".
get_path_length(igraph, path) # returns the length in meters of this path.
plot_path(igraph, path, name, SIZE) # Generates a ("SIZE" x "SIZE") PNG file called "name" in which it plots the "path" given in a map of the corresponding city.
```

The bot.py module has the following functions:
```python
update_fields() # Actualizes the global variables of "congestions", "igraph" and "time_last_update".
need_to_be_updated() # Determines if our database of congestions needs to be updated.
start(update, context) # Starts the conversation.
help(update, context) # Gives some help information about the commands.
author(update, context) # Sends a message with the names of the authors.
where(update, context) # Asks for the user location.
ave_ubi(update, context) # Saves the user location and sends and imatge locating it in a map.
go(update, context) # Reads a position and sends an image with the fastest path to reach this position from the actual user location.
pos(update, context) # Saves a given location as the user location and sends an imatge locating it in a map.

```
---

## Authors and acknowledgment

The authors of this project are:
- Aina Luis Vidal  -  aina.luis@estudiantat.upc.edu
- Sonia Castro Paniello  -  sonia.castro@estudiantat.upc.edu

Acknowledgements to Jordi Cortadella and Jordi Petit, professors at the [UPC](https://www.upc.edu/ca) for their collaboration and help with the project.

