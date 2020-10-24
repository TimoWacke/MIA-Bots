import threading

from flask import Flask, Markup, send_from_directory
from duckling.stat.stat import MaexchenStat


app = Flask(__name__, static_url_path='')

# Make a Maexchen Statistics object which logs the stats and generates the highscores
maexchen_stats = MaexchenStat(show=False, tablefmt="html")

threading.Thread(target=maexchen_stats.start, args=()).start()

@app.route('/')
def show_page():
    return send_from_directory("", "index.html")

@app.route('/api/highscore')
def get_highscore():
    return(maexchen_stats.get_highscore_table())

if __name__ == "__main__":
    app.run()
