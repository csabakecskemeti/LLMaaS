# LLmaaS
Local LLM as a Service

## Components
```
+----------------------------+
|        Web Browser         |
|  - Renders HTML            |
|  - Handles message history |
|  - Displays chat messages  |
+------------+---------------+
             |
             v
+----------------------------+
|    LLmaaS Proxy Server     |
|  - Enables browser access  |
|    to local LLM resource   |
+------------+---------------+
             |
             v
+----------------------------+
|     Local LLM Service      |
|  (e.g., Ollama, Llama.cpp) |
|  - Processes requests      |
|  - Generates responses     |
+----------------------------+
```

## LLmaaS proxy

### Start flask proxy
The proxy takes 2 optional parameters
1 - local Ollama generate URL
2 - model name
(The default values are the same as seen in the example call) 

`python llmaas_proxy.py http://localhost:11434/api/generate llama3.1`

Note current LLmaaS proxy only implemented and tested with Ollama local LLM service!

## Steps to reproduce
- Install Ollama local LLM service
  - Start serving a local model with Ollama (demo has used Llama 3.1)
- Download and start LLmaaS proxy as seen above
- Load [demo page](https://devquasar.com/llmaas/) or use the provided html file locally

## Demo page
[LLmaaS demo](https://devquasar.com/llmaas/)

![til](https://raw.githubusercontent.com/csabakecskemeti/LLmaaS/main/llmaas_demo.gif)

[youtube link to recorded demo](https://youtu.be/OOWGr8jcP5Q?si=ZjEjqksjcj7c97S1)

# Call for contributors
Join me an develop the LLmaaS proxy to make this a generic purpose tool to leverage local LLMs on web.
I'm looking for help to make the proxy more generic support multiple local LLM services without any change on the HTML side.
Also looking for ideas how to make the HTML par more modular and easy to use.

[<img src="https://raw.githubusercontent.com/csabakecskemeti/devquasar/main/dq_logo_black-transparent.png" width="200"/>](https://devquasar.com)

'Make knowledge free for everyone'

<a href='https://ko-fi.com/L4L416YX7C' target='_blank'><img height='36' style='border:0px;height:36px;' src='https://storage.ko-fi.com/cdn/kofi6.png?v=6' border='0' alt='Buy Me a Coffee at ko-fi.com' /></a>
