[Unit]
Description=llama.cpp REST server (local LLM)
After=network-online.target
Wants=network-online.target

[Service]
User=snudurupati
WorkingDirectory=/srv/llm/llama.cpp
EnvironmentFile=/etc/default/llama-server
ExecStart=/srv/llm/llama.cpp/build/bin/llama-server --host 0.0.0.0 --port 8080
Restart=always
RestartSec=2

[Install]
WantedBy=multi-user.target

