import wifi

print("Available WiFi networks:")
for n in wifi.radio.start_scanning_networks():
    print("\t%s\t\tRSSI: %d\tChannel: %d" % (str(n.ssid, "utf-8"), n.rssi, n.channel))
wifi.radio.stop_scanning_networks()