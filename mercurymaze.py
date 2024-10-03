import time
from pimoroni import RGBLED
from picographics import PicoGraphics, DISPLAY_PICO_DISPLAY_2
from lsm6ds3 import LSM6DS3, NORMAL_MODE_104HZ
from pimoroni_i2c import PimoroniI2C

# Initialize the display
display = PicoGraphics(display=DISPLAY_PICO_DISPLAY_2)

# Create pens for colors
black_pen = display.create_pen(0, 0, 0)
white_pen = display.create_pen(255, 255, 255)
silver_pen = display.create_pen(192, 192, 192)  # Silver mercury ball color

# Screen dimensions
DISPLAY_WIDTH = 320
DISPLAY_HEIGHT = 240

# Initialize I2C and the LSM6DS3 sensor for tilt control
i2c = PimoroniI2C(sda=4, scl=5)
motion_sensor = LSM6DS3(i2c, mode=NORMAL_MODE_104HZ)

# Ball properties
ball_x = 40  # Start position of the ball
ball_y = 40
ball_radius = 8  # Simulate the mercury blob size
ball_speed = 0.1  # Adjust the speed factor for faster movement
ball_velocity_x = 0  # X-axis velocity
ball_velocity_y = 0  # Y-axis velocity

# Damping factor to simulate resistance (like friction)
damping = 0.98  # Reduce damping to allow more momentum and fluidity

# Maze layout: 0 = free space, 1 = wall
maze = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 1],
    [1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1, 1, 1, 0, 1],
    [1, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1, 0, 1],
    [1, 0, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 0, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1],
    [1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
]

# Dimensions of the maze cells
cell_width = DISPLAY_WIDTH // len(maze[0])
cell_height = DISPLAY_HEIGHT // len(maze)

# Draw the square maze
def draw_maze():
    display.set_pen(white_pen)
    for row in range(len(maze)):
        for col in range(len(maze[0])):
            if maze[row][col] == 1:
                display.rectangle(col * cell_width, row * cell_height, cell_width, cell_height)

# Draw the mercury blob with a highlight for the shine effect
def draw_mercury_blob():
    # Set pen to silver for the mercury ball
    display.set_pen(silver_pen)
    display.circle(int(ball_x), int(ball_y), ball_radius)  # Convert ball_x and ball_y to integers
    
    # Set pen to white for the highlight shine effect
    display.set_pen(white_pen)  # White for highlight
    display.circle(int(ball_x) - 3, int(ball_y) - 3, 3)  # Convert ball_x and ball_y to integers for highlight

# Check if ball is hitting the walls by considering the ball's radius
def check_wall_collision(new_x, new_y):
    # Check the grid position at the edge of the ball's radius in the direction of movement
    left = int((new_x - ball_radius) // cell_width)
    right = int((new_x + ball_radius) // cell_width)
    top = int((new_y - ball_radius) // cell_height)
    bottom = int((new_y + ball_radius) // cell_height)

    # Check for collisions only in the direction of movement
    if ball_velocity_x < 0 and maze[int(ball_y // cell_height)][left] == 1:  # Moving left
        return True
    if ball_velocity_x > 0 and maze[int(ball_y // cell_height)][right] == 1:  # Moving right
        return True
    if ball_velocity_y < 0 and maze[top][int(ball_x // cell_width)] == 1:  # Moving up
        return True
    if ball_velocity_y > 0 and maze[bottom][int(ball_x // cell_width)] == 1:  # Moving down
        return True
    
    return False

# Main game loop
while True:
    # Clear the screen
    display.set_pen(black_pen)  # Black background
    display.clear()

    # Get accelerometer data
    ax, ay, az, gx, gy, gz = motion_sensor.get_readings()

    # Swap and invert axes to correct the movement direction
    # ax affects Y-axis, ay affects X-axis
    ball_velocity_x += (ball_speed * (ay / 5000))  # Adjust X-axis based on Y tilt
    ball_velocity_y += (ball_speed * (-ax / 5000))  # Adjust Y-axis based on X tilt

    # Apply damping to simulate fluid resistance (friction)
    ball_velocity_x *= damping
    ball_velocity_y *= damping

    # Calculate potential new ball positions
    new_ball_x = ball_x + ball_velocity_x
    new_ball_y = ball_y + ball_velocity_y

    # Check for wall collisions considering only movement direction
    if not check_wall_collision(new_ball_x, ball_y):
        ball_x = new_ball_x
    if not check_wall_collision(ball_x, new_ball_y):
        ball_y = new_ball_y

    # Ensure the mercury blob stays within the screen bounds
    ball_x = max(ball_radius, min(DISPLAY_WIDTH - ball_radius, ball_x))
    ball_y = max(ball_radius, min(DISPLAY_HEIGHT - ball_radius, ball_y))

    # Draw the maze and mercury blob
    draw_maze()
    draw_mercury_blob()

    # Update the display
    display.update()

    # Small delay for game speed control
    time.sleep(0.01)

