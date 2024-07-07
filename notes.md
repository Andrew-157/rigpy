Problems so far with server:

  1. Cannot curl
  2. Cannot serve HTML from the file - Done
  3. Do not really understand what makes it work with Browser and how to make valid HTTP response
  4. socket.accept blocks program even for ctrl-C

Send HTTP Response using socket
```python
...
with open("./templates/index.html", "r") as file:
                    html = file.read()
                to_send = "HTTP/1.1 200\r\nOK\r\n\r\n" + html
                conn.sendall(
        bytes(to_send, "utf-8"))
```