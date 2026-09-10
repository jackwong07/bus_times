# Add Q66 and B62


#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os
picdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'pic')
libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

import logging
from waveshare_epd import epd2in13_V4
import time
from PIL import Image,ImageDraw,ImageFont
import traceback

from datetime import datetime
from zoneinfo import ZoneInfo
import requests

# API Key for MTA Bus Time API https://groups.google.com/g/mtadeveloperresources
API_KEY = 'c148cb26-1a9a-4073-abc7-70b21c262f96'
STOP_MONITORING_URL = 'https://bustime-classic.mta.info/api/siri/stop-monitoring.json'
broadway_ns = 550685
broadway_ew = 552169

broadway_ns_url = "{}?key={}&OperatorRef=MTA&MonitoringRef={}".format(STOP_MONITORING_URL, API_KEY, broadway_ns)
broadway_ew_url = "{}?key={}&OperatorRef=MTA&MonitoringRef={}".format(STOP_MONITORING_URL, API_KEY, broadway_ew)

def find_values_by_key (data, target_key):
    if isinstance(data, dict):
        for key, value in data.items():
            if key == target_key:
                yield value
            # Recursively check the value if it's a nested dict or list
            yield from find_values_by_key(value, target_key)
    elif isinstance(data, list):
        for item in data:
            yield from find_values_by_key(item, target_key)

def convert_timedelta (duration):
    days, seconds = duration.days, duration.seconds
    hours = duration.days * 24 + seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = duration.seconds % 60
    minutes_full = hours * 60 + minutes
    return hours, minutes, seconds, minutes_full


logging.basicConfig(level=logging.DEBUG)

font24 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 24)
font11 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 11)


def main():
    try:
        # 1. Initialize the e-paper display
        epd = epd2in13_V4.EPD()
        print("Initializing and clearing e-Paper...")
        epd.init()
        epd.Clear() # Clear screen to fresh white state
        
        # # CLOCK TIME
        # # # partial update
        # time_image = Image.new('1', (epd.height, epd.width), 255)
        # time_draw = ImageDraw.Draw(time_image)
        # epd.displayPartBaseImage(epd.getbuffer(time_image))
        # num = 0
        # while (True):
        #     time_draw.rectangle((120, 80, 220, 105), fill = 255)
        #     time_draw.text((120, 80), time.strftime('%H:%M:%S'), font = font24, fill = 0)
        #     epd.displayPartial(epd.getbuffer(time_image))
        #     num = num + 1
        #     if(num == 10):
        #         break
        
        ## Clearing board and drawing line
        bus_image = Image.new('1', (epd.height, epd.width), 255)
        bus_draw = ImageDraw.Draw(bus_image)
        # draw.rectangle((x1, y1, x2, y2)) - 122px by 250px
        bus_draw.rectangle((0, 42, 250, 43), fill = 0)     
        bus_draw.rectangle((0, 89, 250, 90), fill = 0)     
        epd.displayPartBaseImage(epd.getbuffer(bus_image))
    
        # # BUS TIMES
        # num = 0
        while (True):
            # Current Time
            now = datetime.now(ZoneInfo("America/New_York"))

            # North, South bus stop 550685
            response_ns = requests.get(broadway_ns_url)
            data_object_ns = response_ns.json()
            all_buses_ns = list(find_values_by_key(data_object_ns,"LineRef"))
            all_expectedtimes_ns = list(find_values_by_key(data_object_ns,"ExpectedArrivalTime"))
            # Creating bus dictionary that combines buses and arrival times
            bus_dict_ns = {}
            for all_buses_ns, all_expectedtimes_ns in zip(all_buses_ns, all_expectedtimes_ns):
                # If key doesn't exist, set it to [] first, then append the value
                bus_dict_ns.setdefault(all_buses_ns, []).append(all_expectedtimes_ns)

            # East, West bus stop 552169
            response_ew = requests.get(broadway_ew_url)
            data_object_ew = response_ew.json()
            all_buses_ew = list(find_values_by_key(data_object_ew,"LineRef"))
            all_expectedtimes_ew = list(find_values_by_key(data_object_ew,"ExpectedArrivalTime"))
            # Creating bus dictionary that combines buses and arrival times
            bus_dict_ew = {}
            for all_buses_ew, all_expectedtimes_ew in zip(all_buses_ew, all_expectedtimes_ew):
                # If key doesn't exist, set it to [] first, then append the value
                bus_dict_ew.setdefault(all_buses_ew, []).append(all_expectedtimes_ew)


            # Display BUS 1 from NS
            bus_q100 = "MTABC_Q100"
            # bus_draw.rectangle((120, 80, 220, 105), fill = 255)
            bus_draw.text((0, 0), f"{bus_q100} to F Train: 5 minute walk", font = font11, fill = 0)    
                        
            try:
                bus_draw.rectangle((0, 14, 250, 28), fill = 255)
                arrivaltime = datetime.fromisoformat(bus_dict_ns[bus_q100][0])
                difference = arrivaltime - now
                hours, minutes, seconds, minutes_full = convert_timedelta(difference)
                bus_draw.text((0, 14), f"1. {minutes_full} minute, {seconds} seconds")
                epd.displayPartial(epd.getbuffer(bus_image))            
            except IndexError:
                pass 
                        
            try:
                bus_draw.rectangle((0, 28, 250, 40), fill = 255)
                arrivaltime = datetime.fromisoformat(bus_dict_ns[bus_q100][1])
                difference = arrivaltime - now
                hours, minutes, seconds, minutes_full = convert_timedelta(difference)
                bus_draw.text((0, 28), f"2. {minutes_full} minute, {seconds} seconds")      
                epd.displayPartial(epd.getbuffer(bus_image))            
            except IndexError:
                pass 


            # Display BUS 2 from NS
            bus_q69 = "MTABC_Q69"
            bus_draw.text((0, 45), f"{bus_q69} to F Train: 5 minute walk", font = font11, fill = 0)    
                        
            try:
                bus_draw.rectangle((0, 59, 250, 73), fill = 255)
                arrivaltime = datetime.fromisoformat(bus_dict_ns[bus_q69][0])
                difference = arrivaltime - now
                hours, minutes, seconds, minutes_full = convert_timedelta(difference)
                bus_draw.text((0, 59), f"1. {minutes_full} minute, {seconds} seconds")
                epd.displayPartial(epd.getbuffer(bus_image))            
            except IndexError:
                pass 
            
            try:
                bus_draw.rectangle((0, 73, 250, 87), fill = 255)
                arrivaltime = datetime.fromisoformat(bus_dict_ns[bus_q69][1])
                difference = arrivaltime - now
                hours, minutes, seconds, minutes_full = convert_timedelta(difference)
                bus_draw.text((0, 73), f"2. {minutes_full} minute, {seconds} seconds")      
                epd.displayPartial(epd.getbuffer(bus_image))
            except IndexError:
                pass 


            # Display BUS 1 from EW
            bus_q104 = "MTABC_Q104"
            # bus_draw.rectangle((120, 80, 220, 105), fill = 255)
            bus_draw.text((0, 92), f"{bus_q104} to N Train: 3 minute walk", font = font11, fill = 0)    
                        
            try:
                bus_draw.rectangle((0, 106, 250, 120), fill = 255)
                arrivaltime = datetime.fromisoformat(bus_dict_ew[bus_q104][0])
                difference = arrivaltime - now
                hours, minutes, seconds, minutes_full = convert_timedelta(difference)
                bus_draw.text((0, 106), f"1. {minutes_full} minute, {seconds} seconds")
                epd.displayPartial(epd.getbuffer(bus_image))            
            except IndexError:
                pass
            
            try:
                bus_draw.rectangle((0, 120, 250, 134), fill = 255)
                arrivaltime = datetime.fromisoformat(bus_dict_ew[bus_q104][1])
                difference = arrivaltime - now
                hours, minutes, seconds, minutes_full = convert_timedelta(difference)
                bus_draw.text((0, 120), f"2. {minutes_full} minute, {seconds} seconds")      
                epd.displayPartial(epd.getbuffer(bus_image))
            except IndexError:
                pass     


            epd.displayPartial(epd.getbuffer(bus_image))            
            time.sleep(3)
            # num = num + 1            
            # if (num == 3):
            #     break    

        # 6. Put the display panel into deep sleep to prevent screen burn
        # print("Putting display to sleep...")
        epd.sleep()

    except IOError as e:
        print(f"IOError encountered: {e}")
        
    except KeyboardInterrupt:    
        print("Script execution stopped by user.")
        epd2in13_V4.epdconfig.module_exit()
        sys.exit()

if __name__ == '__main__':
    main()
    
    
    
    
    
        # # 2. Setup the image buffer (Canvas dimensions match screen specs)
        # # Note: epd.width is the short side, epd.height is the long side
        # print(f"Display Dimensions: {epd.width}x{epd.height}")
        
        # # Create a new, pure white image template in 1-bit pixel mode (black/white)
        # image = Image.new('1', (epd.height, epd.width), 255) 
        # draw = ImageDraw.Draw(image)

        # # 4. Draw elements onto the canvas buffer
        # # Draw a horizontal divider line: draw.line((x_start, y_start, x_end, y_end), fill=0)
        # draw.line((10, 35, 240, 35), fill=0)
        
        # # Add text to canvas: draw.text((x, y), "text", font=font, fill=0)
        # draw.text((10, 10), "Raspberry Pi Status", font=font24, fill=0)
        # draw.text((10, 50), "System Status: Online", font=font24, fill=0)
        # draw.text((10, 75), "E-Paper Display Active!", font=font24, fill=0)

        # # 5. Push the finished image buffer to the physical panel
        # print("Writing canvas buffer to display...")
        # # If your layout is landscape, we rotate the final output image 90 degrees if needed
        # # Or swap width/height matching your target orientation
        # epd.display(epd.getbuffer(image))
