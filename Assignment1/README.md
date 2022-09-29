## **NOTE: If the code is not run on the same device, replace "localhost" with the IP address of the device where the servers are running.**

## Overview

This repository contains two parts: a web server and a web proxy server. Each part has its own Python file (`webserver.py` and `proxyserver.py`) and specific instructions on how to run them.

### Part A - Web Server

#### Overview
`webserver.py` is designed to teach the basics of socket programming for TCP connections in Python. The server performs the following tasks:
- Accepts and parses HTTP requests.
- Retrieves the requested file from the server’s file system.
- Creates an HTTP response message with the requested file and header lines.
- Sends the response to the client.
- If the requested file is not found, sends a "404 Not Found" HTTP response.

#### Instructions On How to Run
1. Open a terminal in this directory.
2. Run the Python file with `python webserver.py`.
3. Type the URL in your browser: `http://localhost:6789/HelloWorld.html`.
4. The browser should display "Hello World" as shown in `ReceiveHTMLFromServer.PNG`.
5. Accessing a file not in the directory will result in a "404 Not Found" HTTP response.

### Part B - Web Proxy

#### Overview
`proxyserver.py` demonstrates the functionality of a basic web proxy server with caching capabilities. The proxy server performs the following tasks:
- Forwards client requests to the web server.
- Receives responses from the web server and sends them to the client.
- Caches web pages to improve performance.
- Handles simple GET-requests and can manage various objects, including HTML pages and images.

#### Instructions On How to Run
1. Open a terminal in this directory.
2. Run the Python file with `python proxyserver.py`.
3. Type the URLs in your browser. The following URLs will work with the proxy server, and the HTML files should appear in the server directory:
    - `http://localhost:8888/gaia.cs.umass.edu/wireshark-labs/HTTP-wireshark-file1.html`
    - `http://localhost:8888/gaia.cs.umass.edu/wireshark-labs/HTTP-wireshark-file2.html`
    - `http://localhost:8888/gaia.cs.umass.edu/wireshark-labs/HTTP-wireshark-file3.html`
    - `http://localhost:8888/gaia.cs.umass.edu/wireshark-labs/HTTP-wireshark-file4.html`
    
    **Note:** The server the proxy is trying to reach does not include `https://` in the URL the client is trying to reach.
    
    You can also access image files from the server cache such as:
    - `http://localhost:8888/JPG_File.jpg`
    - `http://localhost:8888/PNG_File.png`
