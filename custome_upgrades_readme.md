

Update  before 6 august 2026
Socket flag to true (unsafe ) 
and remove null values coming in nfo shoonya

  socketio.run(app, host=host_ip, port=port, debug=debug, reloader_options=reloader_options,allow_unsafe_werkzeug=True)


# Ensure no string 'nan' or empty values slip into brsymbol or symbol (added 3 aug 2026)
    df = df[df["brsymbol"].astype(str).str.lower() != "nan"]
    df = df[df["brsymbol"].astype(str).str.strip() != ""]
