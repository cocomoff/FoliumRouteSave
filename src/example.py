import os
import folium
from os.path import join, dirname
from dotenv import load_dotenv
import openrouteservice
from openrouteservice import convert
import asyncio
from pyppeteer import launch


async def main(coord, lat, long):
    # foliumでサイズ(600, 400)の地図を描画
    m = folium.Map(location=(lat, long), tiles='cartodbpositron', zoom_start=14)
    folium.vector_layers.PolyLine(locations=coord, color="tomato", weight=5, opacity=0.75, line_cap="round", line_join="round").add_to(m)
    m.save("map.html")

    browser = await launch(headless=True)
    page = await browser.newPage()
    await page.goto(f"file://{os.path.abspath('.')}/map.html")
    await page.setViewport({'width': 1080, 'height': 1080})
    await page.waitFor(5000)
    await page.screenshot({'path': 'map.png'})
    os.remove("map.html")


if __name__ == '__main__':
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

    asyncio.get_event_loop().run_until_complete(main(coord, mean_lat, mean_long))