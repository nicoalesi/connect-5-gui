import os
import queue
import subprocess
import threading


class AgentInterface ():
    """
    Interface to communicate with the connect-5 agent process asynchronously.

    The class launches the agent as a subprocess, sends commands through stdin
    and reads responses from stdout using a background thread. The agent's
    responses are stored in a queue so they can be retrieved without blocking
    the main thread.

    :ivar list[str] move_history: Sequence of moves played in the current game.
    :ivar subprocess.Popen process: Running agent subprocess instance.
    :ivar queue.Queue output_queue: Queue containing agent responses.
    :ivar threading.Thread reader_thread: Background thread reading agent output.
    """

    def __init__ (self, command):
        """
        Initialize background process and spin up a worker thread to capture
        the agent's stdout asynchronously.

        :param list[str] command: Agent launch command.
        """

        self.move_history = []

        self.process = subprocess.Popen(
            command,
            stdin = subprocess.PIPE,
            stdout = subprocess.PIPE,
            stderr = subprocess.PIPE,
            text = True,
            bufsize = 1,
            cwd = os.path.dirname(command)
        )

        # Queue to store agent's responses
        self.output_queue = queue.Queue()

        self.reader_thread = threading.Thread(
            target = self._enqueue_output,
            daemon = True
        )

        self.reader_thread.start()


    def _enqueue_output (self):
        """
        Target function for the worker thread.
        Read the agent's output and add it to the output queue.
        """

        while True:
            line = self.process.stdout.readline()
            if not line:
                break

            line = line.replace("bestmove ", "")
            self.output_queue.put(line.strip())

        self.process.stdout.close()


    def register_move (self, move):
        """
        Append a move to the move history.
        Both player and agent's moves must be added.

        :param str move: Move's numerical representation.
        """

        self.move_history.append(move)


    def trigger_search (self, depth = 6):
        """
        Send the complete state history to set up agent's board representation.
        Send the 'go' command to trigger the agent's search.

        :param int depth: Agent's search depth.
        """

        if self.move_history:
            position_cmd = "position startpos moves " + " ".join(self.move_history) + "\n"
        else:
            position_cmd = "position startpos\n"

        go_cmd = f"go {depth}\n"

        self.process.stdin.write(position_cmd)
        self.process.stdin.write(go_cmd)
        self.process.stdin.flush()
        

    def get_move (self):
        """
        Get the next move produced by the agent, if available.

        :return: The next move or None if no move is currently available.
        :rtype: int | None
        """

        try:
            move = self.output_queue.get_nowait()
            return int(move)
        except queue.Empty:
            return None


    def terminate (self):
        """
        Terminate the agent subprocess and wait for it to exit.
        """

        if self.process:
            self.process.terminate()
            self.process.wait()
