import requests
from lxml import html
import time
from PIL import Image, ImageDraw, ImageFont
import ctypes
import json

#initialize sensitive variables from json file. All of this can be hardcoded for personal use
sensitiveData = json.load(open("passwords.txt"))
username1 = sensitiveData['axxessU']
username2 = sensitiveData['telkomU']
password1= sensitiveData['axxessP']
password2= sensitiveData['telkomP']
wallpaperLocation = sensitiveData['wallpaperLocation']
wallpaperSaveLocation = sensitiveData['wallpaperSaveLocation']
routerUsername = sensitiveData['routerU']
routerPassword = sensitiveData['routerP']

session_requests = requests.session()

response = session_requests.get("http://"+routerUsername+":"+routerPassword+"@routerlogin.net/BAS_pppoe.htm") 

tree1 = html.fromstring(response.text)
#gets the current ISP login for the router using xpath
current = list(set(tree1.xpath("//input[@name='pppoe_username']/@value")))[0]

#if the current ISP login is ISP 1 then it needs to change to ISP 2
if current == username1:
    password = password2
    username = username2
elif current == username2:
    password = password1
    username = username1
#This will never happen as it cannot be set to nothing    
else:
    print("Not set to anything")
    exit()

response.close()

#Creates the payload from the form data posted in Chromes network tab. Could probably remove a few, but that gives unpredictable results
payload ={
"pppoe_username": username, 
"pppoe_passwd": password,
'pppoe_servicename':'Telkom',
'pppoe_dod':'0',
'WANAssign':'Dynamic',
'DNSAssign':'0',
'en_nat':'1',
'MACAssign':'0',
'apply':'Apply',
'runtest':'no',
'wan_ipaddr':'105.226.110.250',
'pppoe_localip':'0.0.0.0',
'wan_dns1_pri':'8.8.4.4',
'wan_dns1_sec':'169.1.1.10',
'wan_hwaddr_sel':'0',
'wan_hwaddr_def':'204E7F25EFCB',
'wan_hwaddr2':'204E7F25EFCB',
'wan_hwaddr_pc':'3C5282D16AD0',
'opendns_parental_ctrl':'0',
'gui_region':'English',
}

#defines the headers for the POST. My router does not work with the default headers. Also pulled from Chromes Network tab
headers = {
"Accept" : "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
"Accept-Encoding": "gzip, deflate",
"Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
"Authorization": "Basic YWRtaW46cGFzc3dvcmQ=",
"Cache-Control": "max-age=0",
"Connection": "keep-alive",
"Content-Length": "644",
"Content-Type": "application/x-www-form-urlencoded",
"Host": "routerlogin.net",
"Origin": "http://routerlogin.net",
"Referer": "http://routerlogin.net/BAS_pppoe.htm",
"Upgrade-Insecure-Requests": "1",
"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36"
}

#This part gets the latest action url as it changes every 180 seconds. It then appends the action to the original URL to get the POST URL
result = session_requests.get("http://"+routerUsername+":"+routerPassword+"@routerlogin.net/BAS_pppoe.htm")
tree = html.fromstring(result.text)
action = list(set(tree.xpath("//form[@name='formname']/@action")))[0]
result1 = session_requests.post("http://"+routerUsername+":"+routerPassword+"@routerlogin.net/"+ action, data =payload, headers=headers)

#Very messy
#The router takes exatly 49.6 seconds to boot up after data was posted. This is just a progress percentage that displays on the dekstop wallpaper. Very resource intensive, especailly on the disk usage, but I thought it was an interesting concept.
toolbar_width = 32
for i in range(toolbar_width):
    # update the bar
    progress = str(round(float(i*2*1.6129)/float(toolbar_width*3.125)*100,1))+"%"
    image = Image.open(wallpaperLocation)
    draw = ImageDraw.Draw(image)
    # desired size
    font = ImageFont.truetype(r"Roboto-Black.ttf", size=45) 
    # starting position of the message
    (x, y) = (7000, 4100)
    #Writes the message. Shows the current ISP and the ISP it is changing to as well as the progress percentage.
    message = "Current login: " + current + "\nchanging to: "+username+"\n" + progress
    color = 'rgb(255, 0, 0)'
    draw.text((x, y), message, fill=color, font=font)
    # save the edited image 
    image.save(wallpaperSaveLocation)
    #This part changes the desktop wallpaper
    SPI_SETDESKTOPWALLPAPER=20
    ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKTOPWALLPAPER, 0,wallpaperSaveLocation, 3)

#The final part. This just changes the desktop wallpaper to the current login until you run this again.
image = Image.open(wallpaperLocation)
 
draw = ImageDraw.Draw(image)
# desired size 
font = ImageFont.truetype(r"Roboto-Black.ttf", size=45)
 
# starting position of the message
 
(x, y) = (7000, 4100)

result1 = session_requests.get("http://"+routerUsername+":"+routerPassword+"@routerlogin.net/BAS_pppoe.htm")
tree1 = html.fromstring(result1.text)
message = "Current login: "+list(set(tree1.xpath("//input[@name='pppoe_username']/@value")))[0]
color = 'rgb(255, 0, 0)' # black color
 
# draw the message on the background
draw.text((x, y), message, fill=color, font=font)

# save the edited image
image.save(wallpaperSaveLocation)

#This part changes the desktop wallpaper
SPI_SETDESKTOPWALLPAPER=20
ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKTOPWALLPAPER, 0,wallpaperSaveLocation, 3)