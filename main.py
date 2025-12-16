import pygame
import sys
import random

# ----- Config -----
WIDTH, HEIGHT = 900, 600
FPS = 60
PADDLE_WIDTH, PADDLE_HEIGHT = 12, 100
BALL_SIZE = 16
PADDLE_SPEED = 6
BALL_SPEED = 5
WINNING_SCORE = 7
FONT_NAME = None  # default font

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# ----- Initialization -----
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pong - Python + Pygame")
clock = pygame.time.Clock()
font = pygame.font.Font(FONT_NAME, 36)
small_font = pygame.font.Font(FONT_NAME, 20)

# ----- Game objects -----
class Paddle:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, PADDLE_WIDTH, PADDLE_HEIGHT)
        self.speed = 0

    def move(self):
        self.rect.y += self.speed
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT

    def draw(self, surf):
        pygame.draw.rect(surf, WHITE, self.rect)

class Ball:
    def __init__(self):
        self.rect = pygame.Rect(0, 0, BALL_SIZE, BALL_SIZE)
        self.pos_x = 0.0
        self.pos_y = 0.0
        self.vel = [0.0, 0.0]
        self.reset()

    def reset(self, direction=None):
        self.rect.center = (WIDTH // 2, HEIGHT // 2)
        self.pos_x = float(self.rect.x)
        self.pos_y = float(self.rect.y)
        dir_x = direction if direction is not None else random.choice([-1, 1])
        dir_y = random.choice([-1, 1]) * random.uniform(0.4, 1)
        self.vel = [BALL_SPEED * dir_x, BALL_SPEED * dir_y]

    def move(self):
        # float-based movement
        self.pos_x += self.vel[0]
        self.pos_y += self.vel[1]
        self.rect.x = int(self.pos_x)
        self.rect.y = int(self.pos_y)

        # bounce off top/bottom
        if self.rect.top <= 0:
            self.rect.top = 0
            self.pos_y = self.rect.y
            self.vel[1] = -self.vel[1]
        if self.rect.bottom >= HEIGHT:
            self.rect.bottom = HEIGHT
            self.pos_y = self.rect.y
            self.vel[1] = -self.vel[1]

    def draw(self, surf):
        pygame.draw.ellipse(surf, WHITE, self.rect)

# ----- Helper -----
def draw_centered_text(surf, text, y, font_obj, color=WHITE):
    txt = font_obj.render(text, True, color)
    rect = txt.get_rect(center=(WIDTH//2, y))
    surf.blit(txt, rect)

# ----- Setup -----
left = Paddle(30, HEIGHT//2 - PADDLE_HEIGHT//2)
right = Paddle(WIDTH - 30 - PADDLE_WIDTH, HEIGHT//2 - PADDLE_HEIGHT//2)
ball = Ball()
score_left = 0
score_right = 0
state = 'start'
winner = None
AI_ENABLED = False  # toggle AI with 'A' key on start/gameover screens

# ----- Main loop -----
running = True
while running:
    clock.tick(FPS)

    # --- Event handling ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            if state == 'start' and event.key in (pygame.K_SPACE, pygame.K_RETURN):
                state = 'playing'
                score_left, score_right = 0, 0
                ball.reset(direction=random.choice([-1, 1]))
            if state == 'gameover' and event.key in (pygame.K_SPACE, pygame.K_RETURN):
                state = 'start'
            if event.key == pygame.K_a and state != 'playing':
                AI_ENABLED = not AI_ENABLED
                pygame.time.wait(160)  # avoid rapid toggle

    # --- Paddle input ---
    keys = pygame.key.get_pressed()
    # Left paddle
    if keys[pygame.K_w]:
        left.speed = -PADDLE_SPEED
    elif keys[pygame.K_s]:
        left.speed = PADDLE_SPEED
    else:
        left.speed = 0
    # Right paddle (if not AI)
    if not AI_ENABLED:
        if keys[pygame.K_UP]:
            right.speed = -PADDLE_SPEED
        elif keys[pygame.K_DOWN]:
            right.speed = PADDLE_SPEED
        else:
            right.speed = 0

    # --- Update logic ---
    if state == 'playing':
        left.move()

        # Right paddle AI (can be scored against)
        if AI_ENABLED:
            ai_speed = 4  # max AI speed (less than player speed)
            # small dead zone so AI doesn't jitter
            if ball.rect.centery < right.rect.centery - 5:
                right.speed = -ai_speed
            elif ball.rect.centery > right.rect.centery + 5:
                right.speed = ai_speed
            else:
                right.speed = 0
        right.move()
        ball.move()

        # Paddle collision
        if ball.rect.colliderect(left.rect):
            ball.rect.left = left.rect.right
            ball.pos_x = float(ball.rect.x)
            ball.vel[0] = -ball.vel[0]
            offset = (ball.rect.centery - left.rect.centery) / (PADDLE_HEIGHT/2)
            ball.vel[1] += offset * 2
        if ball.rect.colliderect(right.rect):
            ball.rect.right = right.rect.left
            ball.pos_x = float(ball.rect.x)
            ball.vel[0] = -ball.vel[0]
            offset = (ball.rect.centery - right.rect.centery) / (PADDLE_HEIGHT/2)
            ball.vel[1] += offset * 2

        # Scoring
        if ball.rect.left <= 0:
            score_right += 1
            if score_right >= WINNING_SCORE:
                state = 'gameover'
                winner = 'Right player' if not AI_ENABLED else 'Computer'
            ball.reset(direction=1)
        if ball.rect.right >= WIDTH:
            score_left += 1
            if score_left >= WINNING_SCORE:
                state = 'gameover'
                winner = 'Left player'
            ball.reset(direction=-1)

    # --- Draw ---
    screen.fill(BLACK)
    if state == 'start':
        draw_centered_text(screen, "PONG", HEIGHT//2 - 80, font)
        draw_centered_text(screen, "Press SPACE or ENTER to start", HEIGHT//2 - 20, small_font)
        draw_centered_text(screen, "Left: W/S   Right: Up/Down   ESC to quit", HEIGHT//2 + 20, small_font)
        draw_centered_text(screen, f"First to {WINNING_SCORE} wins", HEIGHT//2 + 60, small_font)
        draw_centered_text(screen, "Press A to toggle AI (currently: " + ("ON" if AI_ENABLED else "OFF") + ")", HEIGHT//2 + 100, small_font)
    elif state == 'playing':
        # center dashed line
        dash_h = 20
        for y in range(0, HEIGHT, dash_h*2):
            pygame.draw.rect(screen, WHITE, (WIDTH//2 - 2, y, 4, dash_h))
        left.draw(screen)
        right.draw(screen)
        ball.draw(screen)
        # scores
        left_score_surf = font.render(str(score_left), True, WHITE)
        right_score_surf = font.render(str(score_right), True, WHITE)
        screen.blit(left_score_surf, (WIDTH//4 - left_score_surf.get_width()//2, 20))
        screen.blit(right_score_surf, (3*WIDTH//4 - right_score_surf.get_width()//2, 20))
    elif state == 'gameover':
        draw_centered_text(screen, f"{winner} wins!", HEIGHT//2 - 20, font)
        draw_centered_text(screen, "Press SPACE to go to start", HEIGHT//2 + 30, small_font)
        draw_centered_text(screen, "Press ESC to quit", HEIGHT//2 + 60, small_font)

    pygame.display.flip()

pygame.quit()
sys.exit()
