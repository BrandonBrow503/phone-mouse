import sys,json,time,urllib.request,websocket
port,pin=sys.argv[1],sys.argv[2]
for i in range(60):
    try: urllib.request.urlopen("http://127.0.0.1:%s/ping?pin=%s"%(port,pin)); break
    except Exception: time.sleep(1)
page=urllib.request.urlopen("http://127.0.0.1:%s/?pin=%s"%(port,pin)).read()
assert b"Phone Mouse" in page
ws=websocket.create_connection("ws://127.0.0.1:%s/ws?pin=%s"%(port,pin)); ws.send(json.dumps({"t":"m","x":40,"y":20})); time.sleep(.5); ws.close()
urllib.request.urlopen(urllib.request.Request("http://127.0.0.1:%s/cmd?pin=%s"%(port,pin),b'[{"t":"m","x":10,"y":10}]'))
print("binary smoke OK")
