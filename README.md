 #  Delivery Routing 

A smart, interactive delivery routing system built with Python and Folium—learned as part of my study of real-world routing algorithms.

## What I Learned

- **Routing Algorithms in Action:** Integrated OSRM's public API to calculate realistic driving routes between pickup and delivery points, helping me understand how modern routing engines work behind the scenes.
- **Interactive Mapping with Folium & Leaflet:** Created a dynamic UI where users can set locations by map clicks or address search, visualize routes, and even animate delivery progress.
- **Geolocation Basics:** Used browser geolocation to center the map on the user's current position, making the tool more user-friendly.
- **Custom UI in Python Web Maps:** Designed modern, responsive control panels using HTML/CSS inside Folium/Leaflet maps, improving user experience.
- **API Integration:** Practiced fetching and handling data from geocoding and routing APIs (Nominatim & OSRM).

## Features

- **Click-to-Set Locations:** Easily choose pickup and delivery points on the map.
- **Live GPS Support:** Auto-detects and centers on your current location (with permission).
- **Address Search:** Search for precise locations with autocomplete.
- **Route Calculation:** Visualize the optimal route and get live distance, ETA, and duration.
- **Delivery Animation:** Watch a delivery vehicle move along the route for a realistic effect.
- **Easy Reset:** Clear all and start over with a single click.

## Usage

1. Run the Python script to generate `delivery_router_pro.html`.
2. Open the HTML file in your browser.
3. Allow location access for the best experience.
4. Set pickup/delivery by clicking the map or searching addresses.
5. Calculate the route and hit "Start Delivery Animation" to see it in action!

---


This project was a hands-on way to learn about mapping, UI design, API integration, and, most importantly, the foundations of routing algorithms used in real-world delivery systems.
