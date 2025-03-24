import pygetwindow as gw

def list_window_titles():
    """Lists the titles of all open windows."""
    windows = gw.getAllTitles()
    for title in windows:
        if title:  # Ignore empty titles
            print(title)

if __name__ == "__main__":
    list_window_titles()