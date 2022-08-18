import os
import folium
from os.path import join, dirname
from dotenv import load_dotenv
import openrouteservice
# from branca.element import Figure
from openrouteservice import convert
import asyncio
from pyppeteer import launch

def draw(lat=35.685, lon=139.733, zoom_start=14):
    """
    Draw an OSM map using Folium, and return its map object.
    """
    m = folium.Map(location=(lat, lon), zoom_start=zoom_start)
    return m


def draw_with_route(coord, lat=35.685, lon=139.733, zoom_start=14):
    """
    Draw an OSM map using Folium, and return its map object.

    Input
    =====
    - coord: list of (lat, lon) elements to draw.
    """
    m = draw(lat, lon, zoom_start)
    folium.vector_layers.PolyLine(locations=coord).add_to(m)
    return m


async def save_with_file(name="map.png"):
    dot_env_path = join(dirname(__name__), ".env")
    load_dotenv(dot_env_path, verbose=True)
    ORS_KEY = os.environ.get("orskey")

    client = openrouteservice.Client(key=ORS_KEY)

    p1 = 35.70318768906786, 139.75197158765246
    p2 = 35.67431306373605, 139.71574523662844
    p1r = tuple(reversed(p1))
    p2r = tuple(reversed(p2))
    mean_lat = (p1[0] + p2[0]) / 2
    mean_long = (p1[1] + p2[1]) / 2

    # 経路計算 (Directions V2)
    routedict = client.directions((p1r, p2r), profile="foot-walking")
    geom = routedict["routes"][0]["geometry"]
    decoded = convert.decode_polyline(geom)
    coord = [(p[1], p[0]) for p in decoded["coordinates"]]

    # foliumでサイズ(600, 400)の地図を描画
    m = draw_with_route(coord, mean_lat, mean_long, zoom_start=14)

    m.save("map.html")
    browser = await launch(headless=True)
    page = await browser.newPage()
    await page.goto(f"file://{os.path.abspath('.')}/map.html")
    await page.setViewport({'width': 1200, 'height': 1200})
    await page.screenshot({'path': name})
    os.remove("map.html")


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(save_with_file("map.png"))
