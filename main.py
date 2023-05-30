import arcade
import math
import random

SPRITE_SCALING = 0.5
SPRITE_SCALING_LASER = 0.8
ENEMY_SPRITE_SCALING = 0.3

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "GAME"

MOVEMENT_SPEED = 5
BULLET_SPEED = 5
ENEMY_SPRITE_SPEED = 0.5

TEXTURE_LEFT = 0
TEXTURE_RIGHT = 1

COIN_COUNT = 10
PLAYER_HEALTH = 5
BULLET_DAMAGE = 1
INDICATOR_BAR_OFFSET = 32

class Enemy(arcade.Sprite):

    def follow_player(self, player_sprite):

        # Move the enemy on the screen
        self.center_x += self.change_x
        self.center_y += self.change_y

        # How quickly the enemy will start to chase the player
        # and how quickly it will change direction
        if random.randrange(100) == 0:
            start_x = self.center_x
            start_y = self.center_y

            # Find the player on the screen
            dest_x = player_sprite.center_x
            dest_y = player_sprite.center_y

            # Set the destination of the enemy sprite
            x_diff = dest_x - start_x
            y_diff = dest_y - start_y
            angle = math.atan2(y_diff, x_diff)

            # Set the Speed of the enemy Sprite
            self.change_x = math.cos(angle) * ENEMY_SPRITE_SPEED
            self.change_y = math.sin(angle) * ENEMY_SPRITE_SPEED

class Player(arcade.Sprite):
    def __init__(self, ind_bar_list):
        super().__init__()

        self.textures = []

        texture = arcade.load_texture(":resources:images/animated_characters/female_adventurer/femaleAdventurer_walk5.png")
        self.textures.append(texture)

        texture = arcade.load_texture(":resources:images/animated_characters/female_adventurer/femaleAdventurer_walk5.png", flipped_horizontally=True)
        self.textures.append(texture)

        # Set the scaling of the Spite (self.scale is part of arcade.Sprite)
        self.scale = SPRITE_SCALING

        # Set the sprite as a texture (self.texture is part of arcade.Sprite)
        self.texture = texture

        self.health_bar  = IndicatorBar(self, ind_bar_list, (self.center_x, self.center_y))
        self.health = PLAYER_HEALTH

    def update(self):
        # move the player on the screen
        self.center_x += self.change_x
        self.center_y += self.change_y

        # Decide which texture to use
        if self.change_x < 0:
            self.texture = self.textures[TEXTURE_LEFT]
        elif self.change_x > 0:
            self.texture = self.textures[TEXTURE_RIGHT]

        # check to see if sprite is out of bounds
        if self.left < 0:
            self.left = 0
        elif self.right > SCREEN_WIDTH - 1:
            self.right = SCREEN_WIDTH - 1

        if self.bottom < 0:
            self.bottom = 0
        elif self.top > SCREEN_HEIGHT - 1:
            self.top = SCREEN_HEIGHT - 1

class IndicatorBar:
    def __init__(self, owner, sprite_list, position = (0,0), full_color = arcade.color.GREEN, background_color = arcade.color.BLACK, width = 100, height = 4, border_size = 4):

        self.owner = owner
        self.sprite_list = sprite_list

        self._box_width: int = width
        self._box_height: int = height
        self._half_box_width: int = self._box_width // 2
        self._center_x: float = 0.0
        self._center_y: float = 0.0
        self._fullness: float = 0.0

        # Create the boxes needed to represent the indicator bar
        self._background_box = arcade.SpriteSolidColor(
            self._box_width + border_size,
            self._box_height + border_size,
            background_color,
        )
        self._full_box = arcade.SpriteSolidColor(
            self._box_width,
            self._box_height,
            full_color,
        )
        self.sprite_list.append(self._background_box)
        self.sprite_list.append(self._full_box)

        # Set the fullness and position of the bar
        self.fullness = 1.0
        self.position = position

    def __repr__(self) -> str:
        return f"<IndicatorBar (Owner={self.owner})>"

    @property
    def background_box(self):
        """Returns the background box of the indicator bar."""
        return self._background_box

    @property
    def full_box(self):
        """Returns the full box of the indicator bar."""
        return self._full_box

    @property
    def fullness(self):
        """Returns the fullness of the bar."""
        return self._fullness

    @fullness.setter
    def fullness(self, new_fullness):
        """Sets the fullness of the bar."""
        # Check if new_fullness if valid
        if not (0.0 <= new_fullness <= 1.0):
            raise ValueError(
                f"Got {new_fullness}, but fullness must be between 0.0 and 1.0."
            )

        # Set the size of the bar
        self._fullness = new_fullness
        if new_fullness == 0.0:
            # Set the full_box to not be visible since it is not full anymore
            self.full_box.visible = False
        else:
            # Set the full_box to be visible incase it wasn't then update the bar
            self.full_box.visible = True
            self.full_box.width = self._box_width * new_fullness
            self.full_box.left = self._center_x - (self._box_width // 2)

    @property
    def position(self):
        """Returns the current position of the bar."""
        return self._center_x, self._center_y

    @position.setter
    def position(self, new_position) -> None:
        """Sets the new position of the bar."""
        # Check if the position has changed. If so, change the bar's position
        if new_position != self.position:
            self._center_x, self._center_y = new_position
            self.background_box.position = new_position
            self.full_box.position = new_position

            # Make sure full_box is to the left of the bar instead of the middle
            self.full_box.left = self._center_x - (self._box_width // 2)

class MyGame(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title)

        self.player_list = None
        self.player_sprite = None
        self.health_bar_list = None

        self.bullet_list = None
        self.enemy_list = None

        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False

        self.game_over = False

        self.firing_sound = arcade.sound.load_sound(":resources:sounds/laser1.wav")
        self.hit_enemy = arcade.sound.load_sound(":resources:sounds/phaseJump1.wav")

        

        arcade.set_background_color(arcade.color.AMAZON)
        

    def setup(self):
        self.health_bar_list = arcade.SpriteList()
        self.player_list = arcade.SpriteList()
        self.player_sprite = Player(self.health_bar_list)

        self.bullet_list = arcade.SpriteList()

        self.enemy_list = arcade.SpriteList()

        self.score = 0

        # Set the starting position of the player Sprite
        self.player_sprite.center_x = 50
        self.player_sprite.center_y = 50
        self.player_list.append(self.player_sprite)

        # Create the enemies and append them to the list
        for i in range(COIN_COUNT):
            enemy = Enemy(":resources:images/items/coinGold.png", ENEMY_SPRITE_SCALING)
            enemy.center_x = random.randrange(SCREEN_WIDTH)
            enemy.center_y = random.randrange(SCREEN_HEIGHT)

            self.enemy_list.append(enemy)

    def update_player_speed(self):

        # Calculate speed based on the keys pressed
        self.player_sprite.change_x = 0
        self.player_sprite.change_y = 0

        if self.up_pressed and not self.down_pressed:
            self.player_sprite.change_y = MOVEMENT_SPEED
        elif self.down_pressed and not self.up_pressed:
            self.player_sprite.change_y = -MOVEMENT_SPEED
        if self.left_pressed and not self.right_pressed:
            self.player_sprite.change_x = -MOVEMENT_SPEED
        elif self.right_pressed and not self.left_pressed:
            self.player_sprite.change_x = MOVEMENT_SPEED

    def on_draw(self):
        # Clear the screen first
        self.clear()

        # draw all the sprites
        self.bullet_list.draw()
        self.player_list.draw()
        self.enemy_list.draw()
        self.health_bar_list.draw()

        screen_score = f"Score: {self.score}"
        arcade.draw_text(screen_score, 10, 20, arcade.color.YELLOW, 14)

        if self.game_over:
            arcade.draw_text("Game Over", 250, 300, arcade.color.YELLOW, 40)

    def on_update(self, delta_time):
        # update the sprite location
        self.player_list.update()
        self.bullet_list.update()

        # Make the bar follow the player
        self.player_sprite.health_bar.position = (
            self.player_sprite.center_x,
            self.player_sprite.center_y + INDICATOR_BAR_OFFSET,
        )

        # Check to see if player is hit by enemy
        if self.player_sprite.health <= 0:
            self.game_over = True
                    
        else:
            for enemy in self.enemy_list:
                if arcade.check_for_collision(enemy, self.player_sprite):
                    self.player_sprite.health -= BULLET_DAMAGE
                    self.player_sprite.health_bar.fullness = (self.player_sprite.health / PLAYER_HEALTH)
                    enemy.remove_from_sprite_lists()

            for bullet in self.bullet_list:
                
                # Check to see if any bullet hits the enemy 
                hit_list = arcade.check_for_collision_with_list(bullet, self.enemy_list)

                # remove bullet from sprite list if it hits enemy
                if len(hit_list) > 0:
                    bullet.remove_from_sprite_lists()

                # if an enmy is in the hit list remove it from the sprite list
                # add one point to score
                for enemy in hit_list:
                    enemy.remove_from_sprite_lists()
                    arcade.play_sound(self.hit_enemy)
                    self.score += 1

                # if bullet goes off screen remove it from the sprite list
                if bullet.bottom > self.width or bullet.top < 0 or bullet.right < 0 or bullet.left > self.width:
                    bullet.remove_from_sprite_lists()

        # for every enemy in enemy list call follow player 
        # and send it a player sprite object
        for enemy in self.enemy_list:
            enemy.follow_player(self.player_sprite)

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        bullet = arcade.Sprite(":resources:images/space_shooter/laserBlue01.png", SPRITE_SCALING_LASER)
        
        # bullet starts at player x and y center
        start_x = self.player_sprite.center_x
        start_y = self.player_sprite.center_y
        bullet.center_x = start_x
        bullet.center_y = start_y

        # where is the bullet going (Mouse pointer location on screen. Argument passed in to on_mouse_press when mouse is clicked)
        dest_x = x
        dest_y = y

        # Calculate the angle the bullet will travel to destination
        x_diff = dest_x - start_x
        y_diff = dest_y - start_y
        angle = math.atan2(y_diff, x_diff)

        # angle the bullet to look more normal
        bullet.angle = math.degrees(angle)
        print(f"Bullet angle: {bullet.angle:.2f}")

        # set how fast the bullet will travel
        bullet.change_x = math.cos(angle) * BULLET_SPEED
        bullet.change_y = math.sin(angle) * BULLET_SPEED

        arcade.play_sound(self.firing_sound)

        self.bullet_list.append(bullet)

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed. """

        if key == arcade.key.W:
            self.up_pressed = True
            self.update_player_speed()
        elif key == arcade.key.S:
            self.down_pressed = True
            self.update_player_speed()
        elif key == arcade.key.A:
            self.left_pressed = True
            self.update_player_speed()
        elif key == arcade.key.D:
            self.right_pressed = True
            self.update_player_speed()

    def on_key_release(self, key, modifiers):
        """Called when the user releases a key. """

        if key == arcade.key.W:
            self.up_pressed = False
            self.update_player_speed()
        elif key == arcade.key.S:
            self.down_pressed = False
            self.update_player_speed()
        elif key == arcade.key.A:
            self.left_pressed = False
            self.update_player_speed()
        elif key == arcade.key.D:
            self.right_pressed = False
            self.update_player_speed()


def main():
    game = MyGame(SCREEN_WIDTH,SCREEN_HEIGHT, SCREEN_TITLE)
    game.setup()
    arcade.run()

if __name__ == '__main__':
    main()