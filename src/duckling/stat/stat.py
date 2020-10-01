import os
import logging
import random
import string
import threading

from tabulate import tabulate
from duckling.lib.udp import MaexchenUdpClient


class MaexchenStat(object):
    def __init__(self, bot_name="stat_bot", ):
        """
        Creates a Scoreboard in the terminal.

        :param bot_name: The name of the Bot.
        """
        self._udp_client = MaexchenUdpClient()

        # Set or generate the bot name
        if bot_name:
            self._bot_name = bot_name
        else:
            self._bot_name = \
                ''.join(random.choice(string.ascii_lowercase) for _ in range(6))

        # Placeholders
        self._stats = []

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

        self._main_loop()

    def close(self):
        """
        Closes the Bots connection.
        """
        print("--- Closing")
        self._stop_main = False
        self._udp_client.send_message("UNREGISTER")
        _ = self._udp_client.await_commands("UNREGISTERED")
        print("--- Unregistered")
        self._udp_client.close()

    def _main_loop(self):
        """
        Runs the main loop which listens for messages from the server.
        """
        num_steps = 1000
        while True:
            message = self._udp_client.await_message()
            # Join the round
            if message.startswith("SCORE"):
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
                    diff_dict[player] = (self._stats[-1][player] - self._stats[-temp_num_steps].get(player, 0)) / temp_num_steps

                diff_dict = {k: v for k, v in sorted(diff_dict.items(), key=lambda item: item[1], reverse=True)}

                table = {"Bot Name": [], "Score": []}

                for bot in diff_dict:
                    table["Bot Name"].append(bot)
                    table["Score"].append('{:.08f}'.format(diff_dict[bot]))

                print(tabulate(table))


class MaexchenRegisterError(Exception):
    def __init__(self, message):
        super().__init__(message)


if __name__ == "__main__":
    stat_client = MaexchenStat()
    stat_client.start()