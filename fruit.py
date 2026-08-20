import pygame
import random
import math

pygame.init()

# -----------------------------
# WINDOW
# -----------------------------
WIDTH = 1000
HEIGHT = 700

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Fruit Ninja - Python")

clock = pygame.time.Clock()

# -----------------------------
# COLORS
# -----------------------------
WHITE = (255, 255, 255)
BLACK = (20, 20, 20)
RED = (220, 50, 50)
GREEN = (50, 200, 80)
YELLOW = (255, 220, 50)

# -----------------------------
# FONTS
# -----------------------------
font = pygame.font.Font(None, 45)
big_font = pygame.font.Font(None, 80)

# -----------------------------
# FRUIT TYPES
# -----------------------------
FRUITS = [
    ("APPLE", (220, 40, 40), 25),
    ("WATERMELON", (40, 180, 70), 30),
    ("ORANGE", (255, 150, 30), 20),
    ("BANANA", (255, 220, 50), 20),
    ("KIWI", (130, 180, 40), 25)
]

# -----------------------------
# FRUIT CLASS
# -----------------------------
class Fruit:
    def __init__(self, bomb=False):
        self.radius = random.randint(25, 40)

        self.x = random.randint(80, WIDTH - 80)
        self.y = HEIGHT + self.radius

        self.velocity_x = random.uniform(-4, 4)
        self.velocity_y = random.uniform(-15, -11)

        self.gravity = 0.35

        self.bomb = bomb

        if bomb:
            self.name = "BOMB"
            self.color = BLACK
            self.points = 0
        else:
            self.name, self.color, self.points = random.choice(FRUITS)

        self.sliced = False

    def update(self):
        self.x += self.velocity_x
        self.y += self.velocity_y

        self.velocity_y += self.gravity

    def draw(self):
        if self.sliced:
            return

        pygame.draw.circle(
            screen,
            self.color,
            (int(self.x), int(self.y)),
            self.radius
        )

        # Fruit highlight
        pygame.draw.circle(
            screen,
            WHITE,
            (
                int(self.x - self.radius * 0.35),
                int(self.y - self.radius * 0.35)
            ),
            max(3, self.radius // 6)
        )

        if self.bomb:
            pygame.draw.circle(
                screen,
                RED,
                (int(self.x), int(self.y)),
                self.radius // 2,
                4
            )


# -----------------------------
# PARTICLE CLASS
# -----------------------------
class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color

        self.velocity_x = random.uniform(-5, 5)
        self.velocity_y = random.uniform(-5, 5)

        self.life = 30
        self.size = random.randint(3, 7)

    def update(self):
        self.x += self.velocity_x
        self.y += self.velocity_y

        self.velocity_y += 0.2
        self.life -= 1

    def draw(self):
        if self.life > 0:
            pygame.draw.circle(
                screen,
                self.color,
                (int(self.x), int(self.y)),
                self.size
            )


# -----------------------------
# GAME VARIABLES
# -----------------------------
fruits = []
particles = []

score = 0
lives = 3

game_over = False

spawn_timer = 0
spawn_delay = 35

mouse_positions = []

difficulty_timer = 0


# -----------------------------
# RESET GAME
# -----------------------------
def reset_game():
    global fruits
    global particles
    global score
    global lives
    global game_over
    global spawn_delay
    global difficulty_timer

    fruits = []
    particles = []

    score = 0
    lives = 3

    spawn_delay = 35
    difficulty_timer = 0

    game_over = False


# -----------------------------
# SLICE EFFECT
# -----------------------------
def create_particles(fruit):
    for _ in range(20):
        particles.append(
            Particle(
                fruit.x,
                fruit.y,
                fruit.color
            )
        )


# -----------------------------
# DISTANCE FUNCTION
# -----------------------------
def distance(x1, y1, x2, y2):
    return math.sqrt(
        (x1 - x2) ** 2 +
        (y1 - y2) ** 2
    )


# -----------------------------
# CHECK SLICE
# -----------------------------
def check_slice(fruit, mouse_x, mouse_y):

    if fruit.sliced:
        return False

    dist = distance(
        fruit.x,
        fruit.y,
        mouse_x,
        mouse_y
    )

    if dist < fruit.radius + 15:
        return True

    return False


# -----------------------------
# MAIN GAME LOOP
# -----------------------------
running = True

while running:

    clock.tick(60)

    # -------------------------
    # EVENTS
    # -------------------------
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        # Restart
        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_r and game_over:
                reset_game()

        # Mouse movement
        if event.type == pygame.MOUSEMOTION:

            mouse_x, mouse_y = pygame.mouse.get_pos()

            mouse_positions.append(
                (mouse_x, mouse_y)
            )

            if len(mouse_positions) > 10:
                mouse_positions.pop(0)

    # -------------------------
    # GAME
    # -------------------------
    if not game_over:

        # Spawn fruits
        spawn_timer += 1

        if spawn_timer >= spawn_delay:

            spawn_timer = 0

            # 15% chance of bomb
            bomb = random.random() < 0.15

            fruits.append(Fruit(bomb))

        # Increase difficulty
        difficulty_timer += 1

        if difficulty_timer >= 600:

            difficulty_timer = 0

            if spawn_delay > 15:
                spawn_delay -= 2

        # ---------------------
        # UPDATE FRUITS
        # ---------------------
        for fruit in fruits:

            fruit.update()

            # Fruit falls below screen
            if fruit.y > HEIGHT + 100:

                if not fruit.sliced and not fruit.bomb:

                    lives -= 1

                    if lives <= 0:
                        game_over = True

        # ---------------------
        # SLICE DETECTION
        # ---------------------
        mouse_x, mouse_y = pygame.mouse.get_pos()

        for fruit in fruits:

            if check_slice(
                fruit,
                mouse_x,
                mouse_y
            ):

                fruit.sliced = True

                if fruit.bomb:

                    # Bomb hit
                    lives -= 1

                    create_particles(fruit)

                    if lives <= 0:
                        game_over = True

                else:

                    # Fruit sliced
                    score += fruit.points

                    create_particles(fruit)

        # Remove sliced fruits
        fruits = [
            fruit for fruit in fruits
            if not fruit.sliced
            and fruit.y < HEIGHT + 150
        ]

    # -------------------------
    # UPDATE PARTICLES
    # -------------------------
    for particle in particles:
        particle.update()

    particles = [
        particle for particle in particles
        if particle.life > 0
    ]

    # -------------------------
    # DRAW BACKGROUND
    # -------------------------
    screen.fill((25, 35, 50))

    # Decorative background
    for x in range(0, WIDTH, 50):
        pygame.draw.line(
            screen,
            (30, 45, 60),
            (x, 0),
            (x, HEIGHT)
        )

    # -------------------------
    # DRAW FRUITS
    # -------------------------
    for fruit in fruits:
        fruit.draw()

    # -------------------------
    # DRAW PARTICLES
    # -------------------------
    for particle in particles:
        particle.draw()

    # -------------------------
    # DRAW SLICE TRAIL
    # -------------------------
    if len(mouse_positions) > 1:

        pygame.draw.lines(
            screen,
            WHITE,
            False,
            mouse_positions,
            4
        )

    # -------------------------
    # SCORE
    # -------------------------
    score_text = font.render(
        f"Score: {score}",
        True,
        WHITE
    )

    screen.blit(
        score_text,
        (25, 20)
    )

    # -------------------------
    # LIVES
    # -------------------------
    lives_text = font.render(
        f"Lives: {lives}",
        True,
        WHITE
    )

    screen.blit(
        lives_text,
        (WIDTH - 170, 20)
    )

    # -------------------------
    # GAME OVER
    # -------------------------
    if game_over:

        overlay = pygame.Surface(
            (WIDTH, HEIGHT),
            pygame.SRCALPHA
        )

        overlay.fill((0, 0, 0, 180))

        screen.blit(
            overlay,
            (0, 0)
        )

        game_over_text = big_font.render(
            "GAME OVER",
            True,
            RED
        )

        screen.blit(
            game_over_text,
            (
                WIDTH // 2 -
                game_over_text.get_width() // 2,
                250
            )
        )

        final_score = font.render(
            f"Final Score: {score}",
            True,
            WHITE
        )

        screen.blit(
            final_score,
            (
                WIDTH // 2 -
                final_score.get_width() // 2,
                350
            )
        )

        restart_text = font.render(
            "Press R to Restart",
            True,
            YELLOW
        )

        screen.blit(
            restart_text,
            (
                WIDTH // 2 -
                restart_text.get_width() // 2,
                420
            )
        )

    # -------------------------
    # UPDATE SCREEN
    # -------------------------
    pygame.display.flip()


pygame.quit()
