import pygame
import random
import time
import os

# Initialize pygame
pygame.init()

# Game dimensions
WIDTH = 800
HEIGHT = 600
ROAD_WIDTH = 300
LANE_WIDTH = ROAD_WIDTH // 3

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GRAY = (100, 100, 100)

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Car Racing Game")
clock = pygame.time.Clock()

# Load images or create simple shapes for cars
def create_car_surface(color, width=40, height=60):
    car = pygame.Surface((width, height), pygame.SRCALPHA)
    pygame.draw.rect(car, color, (0, 0, width, height), border_radius=5)
    pygame.draw.rect(car, BLACK, (0, 0, width, height), 2, border_radius=5)  # Border
    pygame.draw.rect(car, BLACK, (5, 5, width-10, 10))  # Windshield
    pygame.draw.rect(car, BLACK, (5, height-15, width-10, 10))  # Rear window
    return car

# Player car
player_car = create_car_surface(RED)
player_x = WIDTH // 2
player_y = HEIGHT - 100
player_speed = 5
player_lane = 1  # 0: left, 1: middle, 2: right

# Enemy cars
class EnemyCar:
    def __init__(self):
        self.width = 40
        self.height = 60
        self.lane = random.randint(0, 2)
        self.x = (WIDTH - ROAD_WIDTH) // 2 + self.lane * LANE_WIDTH + (LANE_WIDTH - self.width) // 2
        self.y = -self.height
        self.speed = random.randint(3, 7)
        self.color = random.choice([BLUE, GREEN, YELLOW])
        self.surface = create_car_surface(self.color)
    
    def move(self):
        self.y += self.speed
    
    def draw(self, surface):
        surface.blit(self.surface, (self.x, self.y))
    
    def is_off_screen(self):
        return self.y > HEIGHT

# Game variables
enemy_cars = []
spawn_timer = 0
score = 0
high_score = 0
game_over = False
game_started = False
speed_factor = 1.0

# No sound effects
sound_enabled = False

# Load high score if exists
high_score_file = "high_score.txt"
if os.path.exists(high_score_file):
    try:
        with open(high_score_file, "r") as f:
            high_score = int(f.read().strip())
    except:
        high_score = 0

# Road markings
road_marks = []
for i in range(-1, HEIGHT // 40 + 1):
    road_marks.append(pygame.Rect(WIDTH // 2 - 5, i * 40, 10, 20))

# Main game loop
running = True
while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if not game_started:
                game_started = True
            elif game_over:
                # Reset game
                enemy_cars = []
                score = 0
                game_over = False
                speed_factor = 1.0
                player_lane = 1
                player_x = (WIDTH - ROAD_WIDTH) // 2 + player_lane * LANE_WIDTH + (LANE_WIDTH - player_car.get_width()) // 2
            elif event.key == pygame.K_LEFT and player_lane > 0:
                player_lane -= 1
            elif event.key == pygame.K_RIGHT and player_lane < 2:
                player_lane += 1
    
    if not game_started:
        # Show start screen
        screen.fill(BLACK)
        font = pygame.font.SysFont(None, 64)
        title = font.render("CAR RACING", True, WHITE)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//3))
        
        # Show high score on start screen
        if high_score > 0:
            font = pygame.font.SysFont(None, 36)
            high_score_text = font.render(f"High Score: {high_score}", True, YELLOW)
            screen.blit(high_score_text, (WIDTH//2 - high_score_text.get_width()//2, HEIGHT//2 - 50))
        
        font = pygame.font.SysFont(None, 36)
        instruction = font.render("Press any key to start", True, WHITE)
        screen.blit(instruction, (WIDTH//2 - instruction.get_width()//2, HEIGHT//2))
        
        font = pygame.font.SysFont(None, 24)
        controls = font.render("Use LEFT and RIGHT arrow keys to move", True, WHITE)
        screen.blit(controls, (WIDTH//2 - controls.get_width()//2, HEIGHT//2 + 50))
        
        pygame.display.flip()
        clock.tick(60)
        continue
    
    if game_over:
        # Show game over screen
        screen.fill(BLACK)
        font = pygame.font.SysFont(None, 64)
        title = font.render("GAME OVER", True, RED)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//3))
        
        font = pygame.font.SysFont(None, 36)
        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//2))
        
        # Show high score
        high_score_text = font.render(f"High Score: {high_score}", True, YELLOW)
        screen.blit(high_score_text, (WIDTH//2 - high_score_text.get_width()//2, HEIGHT//2 + 50))
        
        instruction = font.render("Press any key to restart", True, WHITE)
        screen.blit(instruction, (WIDTH//2 - instruction.get_width()//2, HEIGHT//2 + 100))
        
        pygame.display.flip()
        clock.tick(60)
        continue
    
    # Game logic
    if not game_over:
        # Move player car to target lane smoothly
        target_x = (WIDTH - ROAD_WIDTH) // 2 + player_lane * LANE_WIDTH + (LANE_WIDTH - player_car.get_width()) // 2
        if player_x < target_x:
            player_x = min(player_x + player_speed, target_x)
        elif player_x > target_x:
            player_x = max(player_x - player_speed, target_x)
        
        # Spawn enemy cars
        spawn_timer += 1
        if spawn_timer > 60 // speed_factor:
            enemy_cars.append(EnemyCar())
            spawn_timer = 0
        
        # Move enemy cars
        for car in enemy_cars[:]:
            car.move()
            if car.is_off_screen():
                enemy_cars.remove(car)
                score += 1
                # Increase difficulty every 10 points
                if score % 10 == 0:
                    speed_factor += 0.2
        
        # Move road markings
        for mark in road_marks:
            mark.y += 5 * speed_factor
            if mark.y > HEIGHT:
                mark.y = -40
        
        # Check for collisions
        player_rect = pygame.Rect(player_x, player_y, player_car.get_width(), player_car.get_height())
        for car in enemy_cars:
            car_rect = pygame.Rect(car.x, car.y, car.width, car.height)
            if player_rect.colliderect(car_rect):
                # Update high score if current score is higher
                if score > high_score:
                    high_score = score
                    # Save high score to file
                    with open(high_score_file, "w") as f:
                        f.write(str(high_score))
                
                game_over = True
    
    # Draw everything
    screen.fill(BLACK)
    
    # Draw road
    road_x = (WIDTH - ROAD_WIDTH) // 2
    pygame.draw.rect(screen, GRAY, (road_x, 0, ROAD_WIDTH, HEIGHT))
    
    # Draw lane markings
    for i in range(1, 3):
        lane_x = road_x + i * LANE_WIDTH - 5
        for y in range(-40, HEIGHT, 40):
            pygame.draw.rect(screen, WHITE, (lane_x, y + int(time.time() * 250) % 40, 10, 20))
    
    # Draw player car
    screen.blit(player_car, (player_x, player_y))
    
    # Draw enemy cars
    for car in enemy_cars:
        car.draw(screen)
    
    # Draw score and high score
    font = pygame.font.SysFont(None, 36)
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))
    
    high_score_text = font.render(f"High Score: {high_score}", True, YELLOW)
    screen.blit(high_score_text, (10, 50))
    
    # Update display
    pygame.display.flip()
    clock.tick(60)

# Save high score before quitting
if score > high_score:
    with open(high_score_file, "w") as f:
        f.write(str(score))

# Quit pygame
pygame.quit()