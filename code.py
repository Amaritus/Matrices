import board
import busio
import time
import random
import displayio
import terminalio
from adafruit_matrixportal.matrixportal import MatrixPortal
from adafruit_matrixportal.graphics import Graphics
from digitalio import DigitalInOut
import adafruit_esp32spi
from adafruit_esp32spi import adafruit_esp32spi
import adafruit_esp32spi.adafruit_esp32spi_socket as socket
import adafruit_esp32spi.adafruit_esp32spi_requests as requests
from adafruit_esp32spi import adafruit_esp32spi_wifimanager
import neopixel
from adafruit_bitmap_font import bitmap_font
from adafruit_display_text import label

#release any displays from prior usage
#displayio.release_displays()




#initialize matrix, build scrolling msg params, static boot msg, vars for msg creation...
matrixportal = MatrixPortal(status_neopixel=board.NEOPIXEL, debug=True)

font_file=terminalio.FONT
#font_file = "fonts/Roboto-Light-24.bdf"
#scrolling msg params
matrixportal.add_text(
    text_position=(0, (matrixportal.graphics.display.height // 2) -1),
    text_font=font_file,
    scrolling=True,
)
#static msg params
matrixportal.add_text(
    text_position=(0, (matrixportal.graphics.display.height // 2) -1),
    text_font=font_file,
)
#vars for msg creation CREATE NEW FEEDS
QUOTES_FEED = "sign-quotes.signtext"
COLORS_FEED = "sign-quotes.signcolor"
SCROLL_DELAY = 0.02 #Controls the scrolling speed
UPDATE_DELAY = 600 #Access feeds every 10 minutes to check for new text & colors

#create empty containers, data pulled from feed hosted on my Adafruit IO site
quotes = [] #holds a list of strings
colors = [] #holds a list of color values
last_color = None
last_quote = None

def update_data():
    print("Updating data from Adafruit IO")
    matrixportal.set_text("PAM!", 1)
    #retrieve text and colors from feed on AIO
    try:
        quotes_data = matrixportal.get_io_data(QUOTES_FEED)
        quotes.clear()
        for json_data in quotes_data:
            quotes.append(matrixportal.network.json_traverse(json_data, ["value"]))
        print(quotes)
    # pylint: disable=broad-except
    except Exception as error:
        print(error)

    try:
        color_data = matrixportal.get_io_data(COLORS_FEED)
        colors.clear()
        for json_data in color_data:
            colors.append(matrixportal.network.json_traverse(json_data, ["value"]))
        print(colors)
    # pylint: disable=broad-except
    except Exception as error:
        print(error)
    #If the feeds are empty, tell user in serial monitor
    if not quotes or not colors:
        raise RuntimeError("Feeds are empty, add text and colors")
    matrixportal.set_text(" ", 1)

#Function calls and declaring vars for randomizing logic loops
update_data()
last_update = time.monotonic()
matrixportal.set_text(" ", 1)
quote_index = None
color_index = None

while True:
    # Randomize text gotten from text feed
    if len(quotes) > 1 and last_quote is not None:
        while quote_index == last_quote:
            quote_index = random.randrange(0, len(quotes))
    else:
        quote_index = random.randrange(0, len(quotes))
    last_quote = quote_index

    # Randomize colors gotten from colors feed
    if len(colors) > 1 and last_color is not None:
        while color_index == last_color:
            color_index = random.randrange(0, len(colors))
    else:
        color_index = random.randrange(0, len(colors))
    last_color = color_index

    # Set the quote text
    matrixportal.set_text(quotes[quote_index])

    # Set the text color
    matrixportal.set_text_color(colors[color_index])

    # Scroll the message, add scroll speed argument
    matrixportal.scroll_text(SCROLL_DELAY)

    if time.monotonic() > last_update + UPDATE_DELAY:
        update_data() #call function to make next message
        last_update = time.monotonic()


"""
#get wifi info
try:
    from secrets import secrets
except ImportError:
    print("Wifi secrets are stored in secrets file! Please update/enter info...")
    raise

print("esp32 wifi connection test")

TEXT_URL = "http://wifitest.adafruit.com/testwifi/index.html"
#JSON_URL = "http://api.coindesk.com/v1/bpi/currentprice/USD.json"

#This board has integrated esp32 module with predefined pins...
esp32_cs = DigitalInOut(board.ESP_CS)
esp32_ready = DigitalInOut(board.ESP_BUSY)
esp32_reset = DigitalInOut(board.ESP_RESET)
spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
esp = adafruit_esp32spi.ESP_SPIcontrol(spi, esp32_cs, esp32_ready, esp32_reset)

requests.set_socket(socket, esp)

if esp.status == adafruit_esp32spi.WL_IDLE_STATUS:
    print("ESP32 found & currently idle")
print("Firmware ver: ", esp.firmware_version)
print("MAC addr: ", [hex(i) for i in esp.MAC_address])

for ap in esp.scan_networks():
    print("\t%s\t\tRSSI: %d" % (str(ap["ssid"], "utf-8"), ap["rssi"]))

print("Connecting to AP...")
while not esp.is_connected:
    try:
        esp.connect_AP(secrets["ssid"], secrets["password"])
    except RuntimeError as e:
        print("couldn't connect to AP, retrying: ", e)
        continue
    print("Connected to: ", str(esp.ssid, "utf-8"), "\tRSSI:", esp.rssi)
    print("My IP address is: ", esp.pretty_ip(esp.ip_address))
    print(
    "IP lookup adafruit.com: %s" % esp.pretty_ip(esp.get_host_by_name("adafruit.com"))
)
print("Ping google.com: %d ms" % esp.ping("google.com"))

# esp._debug = True
print("Fetching text from", TEXT_URL)
r = requests.get(TEXT_URL)
print("+" * 20)
print(r.text)
print("+" * 20)
r.close()

print()
print("Fetching json from", JSON_URL)
r = requests.get(JSON_URL)
print("-" * 40)
print(r.json())
print("-" * 40)
r.close()

print("Done!")

#Code for testing connectivity to Adafruit IO feeds
status_light = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=0.2)

wifi = adafruit_esp32spi_wifimanager.ESPSPI_WiFiManager(esp, secrets, status_light)

counter = 0
"""
"""
while True:
    try:
        print("Posting data...", end="")
        data = counter
        feed = "test"
        payload = {"value": data}
        response = wifi.post(
            "https://io.adafruit.com/api/v2/"
            + secrets["aio_username"]
            + "/feeds/"
            + feed
            + "/data",
            json=payload,
            headers={"X-AIO-KEY": secrets["aio_key"]},
        )
        print(response.json())
        response.close()
        counter = counter + 1
        print("OK")
    except (ValueError, RuntimeError) as e:
        print("Failed to get data, retrying\n", e)
        wifi.reset()
        continue
    response = None
    time.sleep(5)
"""
