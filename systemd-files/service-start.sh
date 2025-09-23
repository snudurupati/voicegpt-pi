sudo systemctl daemon-reload
sudo systemctl enable --now llama-server
sudo systemctl status -l llama-server

#day-to-day commands
journalctl -u llama-server -f    # live logs
sudo systemctl restart llama-server   # restart after changes
sudo systemctl disable --now llama-server  # stop & disable autostart
