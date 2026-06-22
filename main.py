import argparse
import json
import os
import sys

from agent_interface import AgentInterface
from game_gui import PVA_GUI, AVA_GUI


def main ():
    """
    Entry point of the Connect-5 GUI application.

    Load configuration from a file, initialize agent interfaces based on
    the selected mode and launch the corresponding GUI.
    """

    config_file = get_config_file()
    config = load_config(config_file)

    if config["mode"] == "PVA":
        agent_cfg = config["agents"]["1"]
        agent = AgentInterface(agent_cfg["binary"])
        depth = agent_cfg["depth"]

        gui = PVA_GUI(agent, depth)

    elif config["mode"] == "AVA":
        agents = {}
        depths = {}

        for id, cfg in config["agents"].items():
            agents[int(id)] = AgentInterface(cfg["binary"])
            depths[int(id)] = cfg["depth"]

        gui = AVA_GUI(agents, depths)

    else:
        print("An error has occurred.")
        sys.exit(1)

    gui.run()


def get_config_file ():
    """
    Parse command-line arguments to get the configuration file path.
    Validate that the provided file exists before returning it.

    :return: Path to the configuration file.
    :rtype: str
    """

    parser = argparse.ArgumentParser(
        description = "Connect-5 GUI linked to custom agents."
    )

    parser.add_argument(
        "config_file",
        type = str,
        help = "Path to the configuration file."
    )

    args = parser.parse_args()

    if not os.path.exists(args.config_file):
        print(f"Error: The config file '{args.config_file}' could not be found.")
        sys.exit(1)

    return args.config_file


def load_config (path):
    """
    Load and parse a JSON configuration file.

    :param str path: Path to the configuration file.
    :return: Parsed data.
    :rtype: dict
    """

    with open(path) as file:
        return json.load(file)


if __name__ == "__main__":
    main()
