"""
The turtle_adventure module maintains all classes related to the Turtle's
adventure game.
"""
import math
import random
from turtle import RawTurtle
from gamelib import Game, GameElement


class TurtleGameElement(GameElement):
    """
    An abstract class representing all game elemnets related to the Turtle's
    Adventure game
    """

    def __init__(self, game: "TurtleAdventureGame"):
        super().__init__(game)
        self.__game: "TurtleAdventureGame" = game

    @property
    def game(self) -> "TurtleAdventureGame":
        """
        Get reference to the associated TurtleAnvengerGame instance
        """
        return self.__game


class Waypoint(TurtleGameElement):
    """
    Represent the waypoint to which the player will move.
    """

    def __init__(self, game: "TurtleAdventureGame"):
        super().__init__(game)
        self.__id1: int
        self.__id2: int
        self.__active: bool = False

    def create(self) -> None:
        self.__id1 = self.canvas.create_line(0, 0, 0, 0, width=2, fill="green")
        self.__id2 = self.canvas.create_line(0, 0, 0, 0, width=2, fill="green")

    def delete(self) -> None:
        self.canvas.delete(self.__id1)
        self.canvas.delete(self.__id2)

    def update(self) -> None:
        # there is nothing to update because a waypoint is fixed
        pass

    def render(self) -> None:
        if self.is_active:
            self.canvas.itemconfigure(self.__id1, state="normal")
            self.canvas.itemconfigure(self.__id2, state="normal")
            self.canvas.tag_raise(self.__id1)
            self.canvas.tag_raise(self.__id2)
            self.canvas.coords(self.__id1, self.x-10, self.y-10, self.x+10, self.y+10)
            self.canvas.coords(self.__id2, self.x-10, self.y+10, self.x+10, self.y-10)
        else:
            self.canvas.itemconfigure(self.__id1, state="hidden")
            self.canvas.itemconfigure(self.__id2, state="hidden")

    def activate(self, x: float, y: float) -> None:
        """
        Activate this waypoint with the specified location.
        """
        self.__active = True
        self.x = x
        self.y = y

    def deactivate(self) -> None:
        """
        Mark this waypoint as inactive.
        """
        self.__active = False

    @property
    def is_active(self) -> bool:
        """
        Get the flag indicating whether this waypoint is active.
        """
        return self.__active


class Home(TurtleGameElement):
    """
    Represent the player's home.
    """

    def __init__(self, game: "TurtleAdventureGame", pos: tuple[int, int], size: int):
        super().__init__(game)
        self.__id: int
        self.__size: int = size
        x, y = pos
        self.x = x
        self.y = y

    @property
    def size(self) -> int:
        """
        Get or set the size of Home
        """
        return self.__size

    @size.setter
    def size(self, val: int) -> None:
        self.__size = val

    def create(self) -> None:
        self.__id = self.canvas.create_rectangle(0, 0, 0, 0, outline="brown", width=2)

    def delete(self) -> None:
        self.canvas.delete(self.__id)

    def update(self) -> None:
        # there is nothing to update, unless home is allowed to moved
        pass

    def render(self) -> None:
        self.canvas.coords(self.__id,
                           self.x - self.size/2,
                           self.y - self.size/2,
                           self.x + self.size/2,
                           self.y + self.size/2)

    def contains(self, x: float, y: float):
        """
        Check whether home contains the point (x, y).
        """
        x1, x2 = self.x-self.size/2, self.x+self.size/2
        y1, y2 = self.y-self.size/2, self.y+self.size/2
        return x1 <= x <= x2 and y1 <= y <= y2


class Player(TurtleGameElement):
    """
    Represent the main player, implemented using Python's turtle.
    """

    def __init__(self,
                 game: "TurtleAdventureGame",
                 turtle: RawTurtle,
                 speed: float = 5):
        super().__init__(game)
        self.__speed: float = speed
        self.__turtle: RawTurtle = turtle

    def create(self) -> None:
        turtle = RawTurtle(self.canvas)
        turtle.getscreen().tracer(False) # disable turtle's built-in animation
        turtle.shape("turtle")
        turtle.color("green")
        turtle.penup()

        self.__turtle = turtle

    @property
    def speed(self) -> float:
        """
        Give the player's current speed.
        """
        return self.__speed

    @speed.setter
    def speed(self, val: float) -> None:
        self.__speed = val

    def delete(self) -> None:
        pass

    def update(self) -> None:
        # check if player has arrived home
        if self.game.home.contains(self.x, self.y):
            self.game.game_over_win()
        turtle = self.__turtle
        waypoint = self.game.waypoint
        if self.game.waypoint.is_active:
            turtle.setheading(turtle.towards(waypoint.x, waypoint.y))
            turtle.forward(self.speed)
            if turtle.distance(waypoint.x, waypoint.y) < self.speed:
                waypoint.deactivate()

    def render(self) -> None:
        self.__turtle.goto(self.x, self.y)
        self.__turtle.getscreen().update()

    # override original property x's getter/setter to use turtle's methods
    # instead
    @property
    def x(self) -> float:
        return self.__turtle.xcor()

    @x.setter
    def x(self, val: float) -> None:
        self.__turtle.setx(val)

    # override original property y's getter/setter to use turtle's methods
    # instead
    @property
    def y(self) -> float:
        return self.__turtle.ycor()

    @y.setter
    def y(self, val: float) -> None:
        self.__turtle.sety(val)


class Enemy(TurtleGameElement):
    """
    Define an abstract enemy for the Turtle's adventure game
    """

    def __init__(self,
                 game: "TurtleAdventureGame",
                 size: int,
                 color: str):
        super().__init__(game)
        self.__size = size
        self.__color = color

    @property
    def size(self) -> float:
        """
        Get the size of the enemy
        """
        return self.__size

    @property
    def color(self) -> str:
        """
        Get the color of the enemy
        """
        return self.__color

    def spawn_location(self):
        """ Handle the initial location of enemy"""
        if self.game.player.x <= self.game.screen_width/2:
            spawn_x = random.randint(3 * (self.game.screen_width // 4), self.game.screen_width)
        else:
            spawn_x = random.randint(0, 3 * (self.game.screen_width // 4))

        if self.game.player.y <= self.game.screen_height/2:
            spawn_y = random.randint(self.game.screen_height//2, self.game.screen_height)
        else:
            spawn_y = random.randint(0, self.game.screen_height // 2)

        return spawn_x, spawn_y

    def hits_player(self):
        """
        Check whether the enemy is hitting the player
        """
        return (
            (self.x - self.size/2 < self.game.player.x < self.x + self.size/2)
            and
            (self.y - self.size/2 < self.game.player.y < self.y + self.size/2)
        )

class DemoEnemy(Enemy):
    """
    Demo enemy
    """

    def __init__(self,
                 game: "TurtleAdventureGame",
                 size: int,
                 color: str):
        super().__init__(game, size, color)

    def create(self) -> None:
        pass

    def update(self) -> None:
        pass

    def render(self) -> None:
        pass

    def delete(self) -> None:
        pass


class RandomWalkEnemy(Enemy):
    """
    Randomly Walk Enemy
    """
    def __init__(self,
                 game: "TurtleAdventureGame",
                 size: int,
                 color: str):
        super().__init__(game, size, color)
        self.__obj = None
        self.__acc = 0.2
        self.__speed_x = 0
        self.__speed_y = 0
        self.__max_speed = 2

    def create(self) -> None:
        self.__obj = self.canvas.create_oval(0, 0, 0, 0, fill=self.color)

    def update(self) -> None:

        acc_x = random.choice([-self.__acc, self.__acc])
        acc_y = random.choice([-self.__acc, self.__acc])
        self.__speed_x += acc_x
        self.__speed_y += acc_y
        if self.__speed_x > self.__max_speed:
            self.__speed_x = self.__max_speed
        if self.__speed_y > self.__max_speed:
            self.__speed_y = self.__max_speed

        if self.x < 0:
            self.__speed_x = abs(self.__speed_x)
        elif self.x > self.game.screen_height:
            self.__speed_x = -abs(self.__speed_x)
        self.x += self.__speed_x

        if self.y < 0:
            self.__speed_y = abs(self.__speed_y)
        elif self.y > self.game.screen_height:
            self.__speed_y = -abs(self.__speed_y)
        self.y += self.__speed_y
        if self.hits_player():
            self.game.game_over_lose()

    def render(self) -> None:
        self.canvas.coords(self.__obj,
                           self.x - self.size/2,
                           self.y - self.size/2,
                           self.x + self.size/2,
                           self.y + self.size/2)

    def delete(self) -> None:
        pass


class ChasingEnemy(Enemy):
    """ Enemy that will chase the player"""
    def __init__(self,
                 game: "TurtleAdventureGame",
                 size: int,
                 color: str):
        super().__init__(game, size, color)
        self.__obj = None
        self.__speed = 2.75

    def create(self) -> None:
        self.__obj = self.canvas.create_oval(0, 0, 0, 0, fill=self.color)

    def update(self) -> None:
        player_x = self.game.player.x - self.x
        player_y = self.game.player.y - self.y
        deg = math.atan2(player_y, player_x)
        self.x += math.cos(deg) * self.__speed
        self.y += math.sin(deg) * self.__speed
        if self.hits_player():
            self.game.game_over_lose()

    def render(self) -> None:
        self.canvas.coords(self.__obj,
                           self.x - self.size/2,
                           self.y - self.size/2,
                           self.x + self.size/2,
                           self.y + self.size/2)

    def delete(self) -> None:
        pass


class FencingEnemy(Enemy):
    """
        Enemy that walk around home in square pattern
    """

    def __init__(self,
                 game: "TurtleAdventureGame",
                 size: int,
                 color: str):
        super().__init__(game, size, color)
        self.__obj = None
        self.__speed = 3
        self.__path_rad = random.randint(15, 75)
        self.state = self.__move_up

    def create(self) -> None:
        self.__obj = self.canvas.create_oval(0, 0, 0, 0, fill=self.color)

    def __move_up(self):
        self.y -= self.__speed
        if self.y < self.game.home.y - self.__path_rad:
            self.state = self.__move_left

    def __move_left(self):
        self.x -= self.__speed
        if self.x < self.game.home.x - self.__path_rad:
            self.state = self.__move_down

    def __move_down(self):
        self.y += self.__speed
        if self.y > self.game.home.y + self.__path_rad:
            self.state = self.__move_right

    def __move_right(self):
        self.x += self.__speed
        if self.x > self.game.home.x + self.__path_rad:
            self.state = self.__move_up

    def update(self) -> None:
        self.state()
        if self.hits_player():
            self.game.game_over_lose()

    def render(self) -> None:
        self.canvas.coords(self.__obj,
                           self.x - self.size/2,
                           self.y - self.size/2,
                           self.x + self.size/2,
                           self.y + self.size/2)

    def spawn_location(self):
        home_loc = (self.game.home.x, self.game.home.y)
        return home_loc[0] + self.__path_rad, home_loc[1] + self.__path_rad

    def delete(self) -> None:
        pass


class ChargerEnemy(Enemy):
    """
        Enemy that will charge the player at a high speed in a strait line
    """

    def __init__(self,
                 game: "TurtleAdventureGame",
                 size: int,
                 color: str):
        super().__init__(game, size, color)
        self.__obj = None
        self.__speed = 2
        self.__break_acc = 1.5
        self.__break_deg = None
        self.__strike_speed = 25
        self.__hunt_speed = 2
        self.__charge_rad = 150
        self.__charge_speed = 2
        self.__state = self.__hunt
        self.__charge_state = 0
        self.__charge_dir = None
        self.__charge_col = {0: "red", 10: "yellow", 20: "green"}
        self.__charge_loc = None

    def create(self) -> None:
        self.__obj = self.canvas.create_rectangle(0, 0, 0, 0, fill=self.color)

    def __hunt(self):
        player_x = self.game.player.x - self.x
        player_y = self.game.player.y - self.y
        if math.sqrt(player_x ** 2 + player_y**2) <= self.__charge_rad:
            self.__state = self.__charge
            return
        deg = math.atan2(player_y, player_x)
        self.x += math.cos(deg) * self.__speed
        self.y += math.sin(deg) * self.__speed

    def __charge(self):
        if self.__charge_state % 10 == 0:
            self.__charge_state = int(self.__charge_state)
            col = self.__charge_col[self.__charge_state]
            self.canvas.itemconfigure(self.__obj, fill=col)
        self.__charge_state += self.__charge_speed
        if self.__charge_state > max(self.__charge_col.keys()):
            self.__charge_loc = (self.game.player.x, self.game.player.y)
            self.__state = self.__strike
            self.__charge_state = 0
            self.__speed = self.__strike_speed

    def __strike(self):
        player_x = self.__charge_loc[0] - self.x
        player_y = self.__charge_loc[1] - self.y
        deg = math.atan2(player_y, player_x)
        self.x += math.cos(deg) * self.__speed
        self.y += math.sin(deg) * self.__speed
        # break when nearly reach the player
        line = math.sqrt(player_x ** 2 + player_y ** 2)
        if line < 25:
            self.__state = self.__break
            self.__break_deg = deg

    def __break(self):
        self.__speed -= self.__break_acc
        self.x += math.cos(self.__break_deg) * self.__speed
        self.y += math.sin(self.__break_deg) * self.__speed
        if self.__speed <= self.__hunt_speed:
            self.canvas.itemconfigure(self.__obj, fill=self.color)
            self.__state = self.__hunt
            self.__speed = self.__hunt_speed

    def update(self) -> None:
        self.__state()
        if self.hits_player():
            self.game.game_over_lose()

    def render(self) -> None:
        self.canvas.coords(self.__obj,
                           self.x - self.size/2,
                           self.y - self.size/2,
                           self.x + self.size/2,
                           self.y + self.size/2)

    def delete(self) -> None:
        pass


class EnemyGenerator:
    """
    An EnemyGenerator instance is responsible for creating enemies of various
    kinds and scheduling them to appear at certain points in time.
    """

    def __init__(self, game: "TurtleAdventureGame", level: int):
        self.__game: TurtleAdventureGame = game
        self.__level: int = level

        self.create_enemy()

    @property
    def game(self) -> "TurtleAdventureGame":
        """
        Get reference to the associated TurtleAnvengerGame instance
        """
        return self.__game

    @property
    def level(self) -> int:
        """
        Get the game level
        """
        return self.__level

    def create_enemy(self):
        # Type of enemy in list. [Subclass of Enemy, Size, Color, spawn delay, spawn quota]
        enemies_type = [[RandomWalkEnemy, 20, 'red', 10000, 5], [ChasingEnemy, 10, 'yellow', 20000, 2],
                        [FencingEnemy, 15, 'orange', 15000, 2], [ChargerEnemy, 18, 'navy', 25000, 1]]
        # Spawn Initial Enemies
        if self.level < len(enemies_type):
            # init spawn for low level
            low_lvl = {RandomWalkEnemy: 5, ChasingEnemy: 2, FencingEnemy: 4, ChargerEnemy: 1}
            for i in range(self.level):
                amount = low_lvl[enemies_type[i][0]]
                spawn_ls = enemies_type[i]
                self.__spawn_enemy(spawn_ls[0], spawn_ls[1], spawn_ls[2], 100, amount)
        else:
            extra = self.level // 20
            high_lvl = {RandomWalkEnemy: 3 + extra, ChasingEnemy: 4 + extra,
                        FencingEnemy: 3 + extra, ChargerEnemy: 3 + extra}
            for i in enemies_type:
                for j in range(high_lvl[i[0]]):
                    self.__spawn_enemy(i[0], i[1], i[2], i[3]//(1+self.level//10), i[4])

    def __spawn_enemy(self, enemy_type, enemy_size: int,
                     enemy_col: str, delay: int,
                     spawn_quota: int = 100) -> None:
        """
        Create a new enemy, possibly based on the game level
        """
        if spawn_quota > 0:
            new_enemy = enemy_type(self.__game, enemy_size, enemy_col)
            spawn_loc = new_enemy.spawn_location()
            new_enemy.x = spawn_loc[0]
            new_enemy.y = spawn_loc[1]
            self.game.add_element(new_enemy)
            self.game.after(delay, lambda: self.__spawn_enemy(enemy_type, enemy_size,
                                                             enemy_col, delay, spawn_quota-1))


class TurtleAdventureGame(Game):  # pylint: disable=too-many-ancestors
    """
    The main class for Turtle's Adventure.
    """

    # pylint: disable=too-many-instance-attributes
    def __init__(self, parent, screen_width: int, screen_height: int, level: int = 1):
        self.level: int = level
        self.screen_width: int = screen_width
        self.screen_height: int = screen_height
        self.waypoint: Waypoint
        self.player: Player
        self.home: Home
        self.enemies: list[Enemy] = []
        self.enemy_generator: EnemyGenerator
        super().__init__(parent)

    def init_game(self):
        self.canvas.config(width=self.screen_width, height=self.screen_height)
        turtle = RawTurtle(self.canvas)
        # set turtle screen's origin to the top-left corner
        turtle.screen.setworldcoordinates(0, self.screen_height-1, self.screen_width-1, 0)

        self.waypoint = Waypoint(self)
        self.add_element(self.waypoint)
        self.home = Home(self, (self.screen_width-100, self.screen_height//2), 20)
        self.add_element(self.home)
        self.player = Player(self, turtle)
        self.add_element(self.player)
        self.canvas.bind("<Button-1>", lambda e: self.waypoint.activate(e.x, e.y))

        self.enemy_generator = EnemyGenerator(self, level=self.level)

        self.player.x = 50
        self.player.y = self.screen_height//2

    def add_enemy(self, enemy: Enemy) -> None:
        """
        Add a new enemy into the current game
        """
        self.enemies.append(enemy)
        self.add_element(enemy)

    def game_over_win(self) -> None:
        """
        Called when the player wins the game and stop the game
        """
        self.stop()
        font = ("Arial", 36, "bold")
        self.canvas.create_text(self.screen_width/2,
                                self.screen_height/2,
                                text="You Win",
                                font=font,
                                fill="green")

    def game_over_lose(self) -> None:
        """
        Called when the player loses the game and stop the game
        """
        self.stop()
        font = ("Arial", 36, "bold")
        self.canvas.create_text(self.screen_width/2,
                                self.screen_height/2,
                                text="You Lose",
                                font=font,
                                fill="red")
