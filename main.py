import arcade
import math

SPRITE_SCALING = 0.5
SPRITE_SCALING_LASER = 0.8

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "GAME"

MOVEMENT_SPEED = 5
BULLET_SPEED = 5

TEXTURE_LEFT = 0
TEXTURE_RIGHT = 1

class Player(arcade.Sprite):
    def __init__(self):
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

    def update(self):
        # move the player
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

class MyGame(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title)

        self.player_list = None
        self.player_sprite = None

        self.bullet_list = None

        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False

        arcade.set_background_color(arcade.color.AMAZON)
        

    def setup(self):
        self.player_list = arcade.SpriteList()
        self.player_sprite = Player()

        self.bullet_list = arcade.SpriteList()

        self.player_sprite.center_x = 50
        self.player_sprite.center_y = 50
        self.player_list.append(self.player_sprite)

    def on_draw(self):
        # Clear the c=screen first
        self.clear()

        # draw all the sprites
        self.bullet_list.draw()
        self.player_list.draw()

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

    def on_update(self, delta_time):
        # update the sprite location
        self.player_list.update()
        self.bullet_list.update()

        for bullet in self.bullet_list:
            if bullet.bottom > self.width or bullet.top < 0 or bullet.right < 0 or bullet.left > self.width:
                bullet.remove_from_sprite_lists()

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        bullet = arcade.Sprite(":resources:images/space_shooter/laserBlue01.png", SPRITE_SCALING_LASER)

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