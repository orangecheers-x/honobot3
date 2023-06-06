import poe
import os
key = os.getenv('POE_TOKEN')
client = poe.Client(key,
                    proxy="http://192.168.1.24:7891")
message = "Summarize the GNU GPL v3"
for chunk in client.send_message("chinchilla", message):
    pass
print(chunk["text"])
