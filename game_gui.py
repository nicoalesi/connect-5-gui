import pygame
import sys

from abc import ABC, abstractmethod


class BaseGUI (ABC):
    """
    Abstract class for Connect-5 GUI.

    :ivar pygame.Surface screen: Main display surface.
    :ivar pygame.time.Clock clock: Frame-rate controller.
    :ivar list[pygame.event.Event] events: Events collected during the current frame.
    :ivar list[list[int]] board: Board state represented as a 10x10 grid.
    :ivar bool running: Flag indicating whether the main loop should continue running.
    :ivar bool game_over: Flag indicating whether the game has ended.
    :ivar tuple[int, int] last_move: Coordinates of the most recently played move.
    :ivar int plies: Number of moves played since the start of the game.
    """

    BOARD_SIZE = 10
    CELL_SIZE = 60
    PADDING = 40

    WIDTH = CELL_SIZE * BOARD_SIZE + (PADDING * 2)
    HEIGHT = CELL_SIZE * BOARD_SIZE + (PADDING * 2)

    COLOR_BG = (219, 172, 116)
    COLOR_GRID = (40, 40, 40)
    COLOR_BLACK = (10, 10, 10)
    COLOR_WHITE = (245, 245, 245)
    COLOR_HOVER = (180, 140, 90)

    COLOR_PIECES = {
        1: "White",
        2: "Black"
    }

    def __init__ (self):
        """
        Initialize Pygame, create the display window and declare the shared
        game state variables used by all GUI implementations.
        """

        pygame.init()

        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Connect-5 GUI")
        self.clock = pygame.time.Clock()
        self.events = []

        self.board = [[0] * self.BOARD_SIZE for _ in range(self.BOARD_SIZE)]
        self.running = True
        self.game_over = False
        self.last_move = (-1, -1)
        self.plies = 0
    

    @abstractmethod
    def _handle_turn (self):
        ...

    @abstractmethod
    def _stop (self):
        ...

    def run (self):
        """
        Execute the main application loop.

        Processe window events, delegate turn handling to the active GUI
        implementation, check for game termination conditions, render the
        current board state and maintain a fixed frame rate until the
        application is closed.
        """

        while self.running:
            self.events = pygame.event.get()
            self._handle_general_events()

            if not self.game_over:
                self._handle_turn()
                self._check_game_end()

            self._draw()
            self.clock.tick(60)

        self._stop()

    def _handle_general_events (self):
        """
        Process window management events.
        """

        for event in self.events:
            if event.type == pygame.QUIT:
                self.running = False

    def _check_game_end (self):
        """
        Determine whether the most recent move ended the game.

        Examine the position stored in ``last_move`` and check for five
        consecutive pieces of the same color in all horizontal, vertical and
        diagonal directions. Also detect draw conditions when the board is
        completely filled.

        Set ``game_over`` to ``True`` when a winning line or draw is found.
        """

        if self.last_move == (-1, -1):
            return

        row, col = self.last_move
        color = self.board[row][col]

        # 1. Horizontal (Right)
        # 2. Vertical (Down)
        # 3. Diagonal (Down-right)
        # 4. Antidiagonal (Up-right)
        directions = [(0, 1), (1, 0), (1, 1), (-1, 1)]

        # Check for 5 adjacent pieces in every direction
        for dr, dc in directions:
            count = 1

            r, c = row + dr, col + dc
            while (
                0 <= r < self.BOARD_SIZE and
                0 <= c < self.BOARD_SIZE and
                self.board[r][c] == color
            ):
                count += 1
                r += dr
                c += dc

            r, c = row - dr, col - dc
            while (
                0 <= r < self.BOARD_SIZE and
                0 <= c < self.BOARD_SIZE and
                self.board[r][c] == color
            ):
                count += 1
                r -= dr
                c -= dc

            if count >= 5:
                print(f"Game over. {self.COLOR_PIECES[color]} has won!")
                self.game_over = True
        
        # Check for draw
        if self.plies >= self.BOARD_SIZE**2:
            print("Game over. It's a draw!")
            self.game_over = True

    def _draw (self):
        """
        Render the current game state.
        """

        self.screen.fill(self.COLOR_BG)
        
        x, y = pygame.mouse.get_pos()

        col = (x - self.PADDING) // self.CELL_SIZE
        row = (y - self.PADDING) // self.CELL_SIZE

        # Highlight cell currently hovered over
        if 0 <= row < self.BOARD_SIZE and 0 <= col < self.BOARD_SIZE:
            if self.board[row][col] == 0:
                left = self.PADDING + col * self.CELL_SIZE
                top = self.PADDING + row * self.CELL_SIZE

                pygame.draw.rect(
                    self.screen,
                    self.COLOR_HOVER,
                    (left, top, self.CELL_SIZE, self.CELL_SIZE)
                )

        # Draw Grid Lines
        for i in range(self.BOARD_SIZE + 1):
            start_pos_v = (self.PADDING + i * self.CELL_SIZE, self.PADDING)
            end_pos_v = (self.PADDING + i * self.CELL_SIZE, self.HEIGHT - self.PADDING)
            pygame.draw.line(self.screen, self.COLOR_GRID, start_pos_v, end_pos_v, 2)
            
            start_pos_h = (self.PADDING, self.PADDING + i * self.CELL_SIZE)
            end_pos_h = (self.WIDTH - self.PADDING, self.PADDING + i * self.CELL_SIZE)
            pygame.draw.line(self.screen, self.COLOR_GRID, start_pos_h, end_pos_h, 2)

        # Draw pieces
        for row in range(self.BOARD_SIZE):
            for col in range(self.BOARD_SIZE):
                piece = self.board[row][col]

                if piece != 0:
                    center_x = self.PADDING + col * self.CELL_SIZE + (self.CELL_SIZE // 2)
                    center_y = self.PADDING + row * self.CELL_SIZE + (self.CELL_SIZE // 2)
                    radius = int(self.CELL_SIZE * 0.4)
                    
                    color = self.COLOR_WHITE if piece == 1 else self.COLOR_BLACK
                    pygame.draw.circle(self.screen, color, (center_x, center_y), radius)

        pygame.display.flip()


class PVA_GUI (BaseGUI):
    """
    Player vs. Agent Connect-5 GUI.

    :ivar AgentInterface agent: Interface used to communicate with the agent.
    :ivar int search_depth: Agent's search depth.
    :ivar bool player_turn: Flag indicating whether it's the player's turn.
    """
    
    def __init__ (self, agent_interface, agent_depth):
        """
        Declare state variables and link agent interface.

        :param AgentInterface agent_interface: Agent interface that generates moves.
        :param int agent_depth: Search depth used by the agent.
        """

        super().__init__()
        self.agent = agent_interface
        self.search_depth = agent_depth

        self.player_turn = True

    def _handle_turn (self):
        """
        Handle the current turn.
        """

        if self.player_turn:
            self._handle_player_turn()
        else:
            self._handle_agent_turn()

    def _handle_player_turn (self):
        """
        Convert the clicked screen position into a board move, update the
        board state and trigger the agent search for the next move.
        """

        for event in self.events:
            if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
                continue

            x, y = event.pos

            column = (x - self.PADDING) // self.CELL_SIZE
            row = (y - self.PADDING) // self.CELL_SIZE
            
            if column < 0 or self.BOARD_SIZE <= column:
                continue
            
            if row < 0 or self.BOARD_SIZE <= row:
                continue
            
            target_row = -1
            for row in range(self.BOARD_SIZE - 1, -1, -1):
                if self.board[row][column] == 0:
                    target_row = row
                    break

            if target_row == -1:
                continue
            
            self.board[target_row][column] = 1
            self.last_move = (target_row, column)

            self.agent.register_move(f"{target_row * 10 + column}")
            self.plies += 1
            self.player_turn = False
            self.agent.trigger_search(depth = self.search_depth)

    def _handle_agent_turn (self):
        """
        Poll the agent for a pending move and update the board when one is
        available.
        """

        move = self.agent.get_move()
        
        if move is not None:
            row = move // 10
            col = move % 10

            if row < 0 or self.BOARD_SIZE <= row:
                return
            
            if col < 0 or self.BOARD_SIZE <= col:
                return

            if self.board[row][col] != 0:
                return

            self.board[row][col] = 2
            self.last_move = (row, col)

            self.agent.register_move(str(move))
            self.plies += 1
            self.player_turn = True

    def _stop (self):
        """
        Shut down the agent and close the application.
        """

        self.agent.terminate()
        pygame.quit()
        sys.exit()


class AVA_GUI (BaseGUI):
    """
    Agent vs. Agent Connect-5 GUI.

    :ivar dict[int, AgentInterface] agents: Agent interfaces indexed by their IDs.
    :ivar dict[int, int] search_depths: Search depths indexed by their IDs.
    :ivar int curr_agent: ID of the agent whose turn is currently being processed.
    """

    def __init__(self, agent_interfaces, agent_depths):
        """
        Declare state variables, link agent interfaces and ignite agent search.

        :param dict[int, AgentInterface] agent_interfaces: Agent interfaces that generates moves,
        indexed by their IDs.
        :param dict[int, int] agent_depths: Search depths used by the agents, indexed by their IDs.
        """

        super().__init__()
        self.agents = agent_interfaces
        self.search_depths = agent_depths

        self.curr_agent = 1
        self.agents[self.curr_agent].trigger_search(depth = self.search_depths[self.curr_agent])

    def _handle_turn (self):
        """
        Handle the current turn polling the agent for a pending move and updating the board when one is
        available.
        """

        move = self.agents[self.curr_agent].get_move()
        
        if move is not None:
            row = move // 10
            col = move % 10

            if row < 0 or self.BOARD_SIZE <= row:
                return
            
            if col < 0 or self.BOARD_SIZE <= col:
                return

            if self.board[row][col] != 0:
                return

            self.board[row][col] = self.curr_agent
            self.last_move = (row, col)

            for agent in self.agents.values():
                agent.register_move(str(move))
            
            self.plies += 1

            # Agent switch:
            # 1 -> 2  (01 ^ 11 = 10)
            # 2 -> 1  (10 ^ 11 = 01)
            self.curr_agent ^= 3

            self.agents[self.curr_agent].trigger_search(depth = self.search_depths[self.curr_agent])

    def _stop (self):
        """
        Shut down the agents and close the application.
        """

        for agent in self.agents.values():
            agent.terminate()

        pygame.quit()
        sys.exit()
