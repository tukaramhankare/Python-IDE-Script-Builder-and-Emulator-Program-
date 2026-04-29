import webview
import os

# Get the absolute path to your HTML file
html_path = os.path.abspath("index.html")   # Change if your file has different name

def main():
    # Create the window
    window = webview.create_window(
        title="AI Python IDE",      # Change the title as you like
        url=html_path,              # Load your HTML file
        width=1400,
        height=860,
        min_size=(900, 600),
        text_select=True,
        background_color="#1e1e1e"
    )
    
    # Start the app
    webview.start()

if __name__ == "__main__":
    main()