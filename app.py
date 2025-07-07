import streamlit as st
import pickle
import networkx as nx
import folium
from streamlit_folium import folium_static
from geopy.distance import great_circle
import pandas as pd

# --- CO₂ calculation helper ---
def calculate_co2(length_meters, emission_rate_g_per_km=150):
    return (length_meters / 1000) * emission_rate_g_per_km

# --- Estimate ventilation penalty if missing ---
def estimate_ventilation(edge):
    highway = edge.get('highway', '')
    if isinstance(highway, list):
        highway = highway[0]
    if highway in ['motorway', 'tunnel']:
        return 3  # low ventilation
    elif highway in ['primary', 'secondary']:
        return 2  # moderate
    else:
        return 1  # good ventilation


# --- Load network data ---
with open("vienna_networks.pkl", "rb") as f:
    vienna_network = pickle.load(f)

# --- Streamlit UI ---
st.set_page_config(page_title="Alofi Sustainability Navigation", layout="wide")
# Hide default Streamlit menu and footer
hide_st_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
"""
st.markdown(hide_st_style, unsafe_allow_html=True)

st.title("🧭 Alofi Sustainability Navigation")

# --- Select Network ---
network_options = {
    "Base Network": "G_base",
    "Traffic-Aware Network": "G_traffic",
    "Sustainable Network": "G_sustainable",
    "Multi-Modal Network": "G_multi"
}
selected_network_name = st.selectbox("Choose Network Type", list(network_options.keys()))
G = vienna_network[network_options[selected_network_name]]

# --- Nearest node finder ---
def find_nearest_node(coord):
    nearest_node = None
    min_dist = float("inf")
    for node_id, data in G.nodes(data=True):
        node_coord = (data["y"], data["x"])
        dist = great_circle(coord, node_coord).meters
        if dist < min_dist:
            min_dist = dist
            nearest_node = node_id
    return nearest_node

# --- Route generator ---
def get_diverse_routes(start_node, end_node, graph, num_routes=5, penalty_factor=2.0):
    routes = []
    G_temp = graph.copy()

    for i in range(num_routes):
        try:
            route = nx.shortest_path(
                G_temp, source=start_node, target=end_node, weight='travel_time'
            )
            routes.append(route)
            for u, v in zip(route[:-1], route[1:]):
                if G_temp.has_edge(u, v):
                    G_temp[u][v]['travel_time'] *= penalty_factor
        except nx.NetworkXNoPath:
            st.warning(f"No path found for route {i+1}")
            break

    return routes

# --- Create Map with Routes ---
def create_map(routes, start_coord, end_coord):
    m = folium.Map(location=start_coord, zoom_start=14)
    colors = ["blue", "green", "red", "purple", "orange"]

    for i, route in enumerate(routes):
        route_coords = [(G.nodes[n]["y"], G.nodes[n]["x"]) for n in route]
        folium.PolyLine(
            locations=route_coords,
            color=colors[i % len(colors)],
            weight=5,
            opacity=0.8,
            tooltip=f"{selected_network_name} Route {i+1}"
        ).add_to(m)

    folium.Marker(location=start_coord, popup="Start", icon=folium.Icon(color="green")).add_to(m)
    folium.Marker(location=end_coord, popup="End", icon=folium.Icon(color="red")).add_to(m)
    return m

# --- Route Summary Table (with sustainability placeholders + CO₂ auto) ---
def summarize_routes(routes):
    summary = []
    for i, route in enumerate(routes):
        total_length = 0
        total_time = 0
        total_co2 = 0
        total_ventilation = 0
        total_score = 0

        for u, v in zip(route[:-1], route[1:]):
            edge = G.get_edge_data(u, v)
            if edge:
                length = edge.get('length', 0)
                travel_time = edge.get('travel_time', 0)

                # CO₂ auto calculation
                calculated_co2 = calculate_co2(length)

                total_length += length
                total_time += travel_time
                total_co2 += calculated_co2
                ventilation = edge.get('ventilation_penalty', estimate_ventilation(edge))
                total_ventilation += ventilation
                vent_count = len(route) - 1
                # Compute sustainability score per edge and add it
                score = 100 - (0.05 * calculated_co2) - (10 * ventilation)
                score = max(0, min(100, score))  # Clamp between 0–100
                total_score += score


        summary.append({
            "Route": f"Route {i+1}",
            "Nodes": len(route),
            "Distance (m)": round(total_length, 1),
            "Travel Time (min)": round(total_time / 60, 1),
            "CO₂ Emissions (g)": round(total_co2, 2),
            "Ventilation Penalty": round(total_ventilation / vent_count, 2),
            "Sustainability Score": round(total_score, 2)
        })

    return pd.DataFrame(summary)

# --- Input Coordinates ---
st.markdown("### 🖱 Click on the map or enter coordinates manually")

use_click = st.checkbox("Use map click for start and end points")

# Defaults
start_lat, start_lon = 48.21315, 16.36005
end_lat, end_lon = 48.21052, 16.37081

if use_click:
    click_map = folium.Map(location=[48.212, 16.365], zoom_start=14)
    click_coords = []

    def click_callback(e):
        lat, lon = e['latlng']['lat'], e['latlng']['lng']
        click_coords.append((lat, lon))

    click_map.add_child(folium.LatLngPopup())

    folium_static(click_map, width=700, height=500)

    st.info("Click twice: first for start, second for end.")
    if len(click_coords) >= 2:
        start_lat, start_lon = click_coords[0]
        end_lat, end_lon = click_coords[1]
else:
    col1, col2 = st.columns(2)
    with col1:
        start_lat = st.text_input("Start Latitude", value="48.21315")
        start_lon = st.text_input("Start Longitude", value="16.36005")
    with col2:
        end_lat = st.text_input("End Latitude", value="48.21052")
        end_lon = st.text_input("End Longitude", value="16.37081")


# --- Generate Button ---
if st.button("Generate Routes"):
    try:
        start_coord = (float(start_lat), float(start_lon))
        end_coord = (float(end_lat), float(end_lon))

        st.info(f"Snapping to nearest nodes on {selected_network_name}...")
        start_node = find_nearest_node(start_coord)
        end_node = find_nearest_node(end_coord)

        if start_node is None or end_node is None:
            st.error("Could not find nearby nodes. Try different coordinates.")
        else:
            st.success(f"Start Node: {start_node}, End Node: {end_node}")
            routes = get_diverse_routes(start_node, end_node, G)

            if not routes:
                st.warning("No routes found. Try closer coordinates.")
            else:
                route_map = create_map(routes, start_coord, end_coord)
                route_table = summarize_routes(routes)

                # Display in Tabs
                tab1, tab2 = st.tabs(["🗺️ Route Map", "📊 Route Summary"])
                with tab1:
                    folium_static(route_map, width=None, height=700)
                with tab2:
                    st.dataframe(route_table, use_container_width=True)
                # --- Download Button ---
                csv = route_table.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download Route Summary as CSV",
                    data=csv,
                    file_name='route_summary.csv',
                    mime='text/csv'
                )


    except Exception as e:
        st.error(f"Error: {e}")
