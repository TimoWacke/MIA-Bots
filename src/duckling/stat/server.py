import threading
import atexit

from flask import Flask, Markup, send_from_directory
from duckling.stat.stat import MaexchenStat


app = Flask(__name__, static_url_path='')

# Make a Maexchen Statistics object which logs the stats and generates the highscores
maexchen_stats = MaexchenStat(show=False, tablefmt="html")

#Start stat calculation in the background
maexchen_stat_calc_thread = threading.Thread(target=maexchen_stats.start, args=())
maexchen_stat_calc_thread.start()

def close():
    maexchen_stats.stop_main = True
    maexchen_stat_calc_thread.join()
    maexchen_stats .close()

atexit.register(close)

@app.route('/')
def show_page():
    return send_from_directory("", "index.html")

@app.route('/api/highscore')
def get_highscore():
    return(maexchen_stats.get_highscore_table())

if __name__ == "__main__":
    app.run()
