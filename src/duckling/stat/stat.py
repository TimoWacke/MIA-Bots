import os
import logging
import random
import string
import threading

from tabulate import tabulate
from duckling.lib.udp import MaexchenUdpClient

class MaexchenStat(object):
    def __init__(self, bot_name="", show=True, tablefmt=None):
        """
        Creates a Scoreboard in the terminal.

        :param bot_name: The name of the Bot.
        :param show: Show the highscore in the terminal.
        """
        self._udp_client = MaexchenUdpClient()

        # Set or generate the bot name
        if bot_name:
            self._bot_name = bot_name
        else:
            self._bot_name = \
                ''.join(random.choice(string.ascii_lowercase) for _ in range(6))

        self._highscore_table = "No highscore yet!"

        self._show = show
        self._tablefmt = tablefmt

        # Placeholders
        self._stats = []
        self.stop_main = False

    def start(self):
        """
        Start the game for your bot (non blocking).
        It joins the game on the next possibility.
        """
        print("--- Starting")
        # Register
        self._udp_client.send_message(f"REGISTER_SPECTATOR;{self._bot_name}")
        msg = self._udp_client.await_message()
        if msg.startswith("REJECTED"):
            raise MaexchenRegisterError("--- Connection rejected")
        elif not msg.startswith("REGISTERED"):
            raise MaexchenRegisterError(f"--- Connection not accepted. Got: '{msg}'")

        try:
            self._main_loop()
        except KeyboardInterrupt:
            self.close()
            exit(0)

    def close(self):
        """
        Closes the Bots connection.
        """
        self.stop_main = False
        print("--- Closing", self._bot_name)
        self._udp_client.send_message("UNREGISTER")
        print("--- Unregistered")
        self._udp_client.close()

    def get_highscore_table(self):
        """
        Returns the highscore table
        """
        return self._highscore_table

    def _main_loop(self):
        """
        Runs the main loop which listens for messages from the server.
        """
        num_steps = 500
        while not self.stop_main:
            message = self._udp_client.await_message()
            # Join the round
            if message.startswith("SCORE"):
                if self._show:
                    os.system('clear')
                    print("\nScoreboard:")
                bot_dict = {}
                bots = message.split(";")[1]
                bots = bots.split(",")
                for bot in bots:
                    player, score = bot.split(":")
                    bot_dict[player] = int(score)

                self._stats.append(bot_dict)

                diff_dict = {}
                if len(self._stats) > num_steps:
                    temp_num_steps = num_steps
                else:
                    temp_num_steps = len(self._stats)

                for player in self._stats[-1].keys():
                    diff_dict[player] = (self._stats[-1][player] - self._stats[-temp_num_steps].get(player, 0))

                diff_dict = {k: v for k, v in sorted(diff_dict.items(), key=lambda item: item[1], reverse=True)}

                table = {"Bot Name": [], "Score": []}

                for bot in diff_dict:
                    if diff_dict[bot] > 0:
                        table["Bot Name"].append(bot)
                        table["Score"].append(diff_dict[bot])

                self._highscore_table = tabulate(table, tablefmt=self._tablefmt, floatfmt=".4f", headers=['Bot', f'Score (last {num_steps} Rounds)'])

                if self._show:
                    print(self._highscore_table)


class MaexchenRegisterError(Exception):
    def __init__(self, message):
        super().__init__(message)


if __name__ == "__main__":
    stat_client = MaexchenStat()
    stat_client.start()
