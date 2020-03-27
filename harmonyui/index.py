from app import app 
from components import sidebar

app.layout = sidebar.layout

if __name__ == "__main__":
    app.run_server(port=8888, debug=True)