
import pygame
import random
import math
from game.ship import Ship
from game.meteor import Meteor

WIDTH, HEIGHT = 700, 520
FPS = 60
BG = (8, 5, 20)

# Laser settings
LASER_SPEED = 9
LASER_WIDTH = 4
LASER_HEIGHT = 18
LASER_COLOR = (80, 240, 255)
LASER_GLOW = (30, 120, 255)


class GameEngine:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Meteor Dodge")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("monospace", 26, bold=True)
        self.big_font = pygame.font.SysFont("monospace", 46, bold=True)

        self.stars = [
            (
                random.randint(0, WIDTH),
                random.randint(0, HEIGHT),
                random.randint(1, 3),
            )
            for _ in range(80)
        ]

        self.reset()

    def reset(self):
        self.ship = Ship(WIDTH // 2, HEIGHT - 80)
        self.meteors = []
        self.lasers = []
        self.timer = 0
        self.spawn_interval = 60
        self.score = 0
        self.game_over = False
        self.started = False

    def fire_laser(self):
        """Create a laser projectile at the ship's position."""
        laser = pygame.Rect(
            self.ship.rect.centerx - LASER_WIDTH // 2,
            self.ship.rect.top - LASER_HEIGHT,
            LASER_WIDTH,
            LASER_HEIGHT,
        )
        self.lasers.append(laser)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if self.game_over:
                        self.reset()
                    elif not self.started:
                        self.started = True
                    else:
                        # SPACE fires only during active gameplay.
                        self.fire_laser()

        return True

    def update(self):
        if self.game_over or not self.started:
            return

        keys = pygame.key.get_pressed()
        self.ship.move(keys, WIDTH, HEIGHT)

        self.timer += 1

        if self.timer >= self.spawn_interval:
            self.meteors.append(Meteor(WIDTH))
            self.timer = 0
            self.spawn_interval = max(20, self.spawn_interval - 0.3)

        # Move lasers upward.
        for laser in self.lasers:
            laser.y -= LASER_SPEED

        # Remove lasers that have left the screen.
        self.lasers = [
            laser for laser in self.lasers
            if laser.bottom > 0
        ]

        # Move meteors and check ship collisions.
        for meteor in self.meteors:
            meteor.update()

            if meteor.collides(self.ship.rect):
                self.game_over = True
                break

        # Check laser-meteor collisions.
        # Each laser and meteor can be consumed only once.
        remaining_meteors = []
        hit_meteors = set()

        for laser in self.lasers:
            laser_hit = False

            for meteor in self.meteors:
                meteor_id = id(meteor)

                if meteor_id in hit_meteors:
                    continue

                dx = meteor.x - laser.centerx
                dy = meteor.y - laser.centery
                distance = math.sqrt(dx * dx + dy * dy)

                # Treat the laser as a small circle for collision.
                if distance < meteor.radius + LASER_HEIGHT / 2:
                    hit_meteors.add(meteor_id)
                    laser_hit = True
                    break

            if laser_hit:
                laser.width = 0
                laser.height = 0

        # Keep meteors that were not destroyed and are still on screen.
        for meteor in self.meteors:
            if id(meteor) not in hit_meteors:
                if not meteor.off_screen(HEIGHT):
                    remaining_meteors.append(meteor)

        self.meteors = remaining_meteors

        # Remove lasers that hit meteors.
        self.lasers = [
            laser for laser in self.lasers
            if laser.width > 0 and laser.height > 0
        ]

        self.score += 1

    def draw(self):
        self.screen.fill(BG)

        # Background starfield.
        for sx, sy, sr in self.stars:
            pygame.draw.circle(
                self.screen, (200, 200, 220), (sx, sy), sr
            )

        # Draw meteors.
        for meteor in self.meteors:
            meteor.draw(self.screen)

        # Draw lasers with a glow effect.
        for laser in self.lasers:
            glow_rect = laser.inflate(8, 6)
            pygame.draw.rect(
                self.screen, LASER_GLOW, glow_rect, border_radius=4
            )
            pygame.draw.rect(
                self.screen, LASER_COLOR, laser, border_radius=2
            )

        # Draw the ship.
        self.ship.draw(self.screen)

        # Survival timer.
        sc = self.font.render(
            f"Time: {self.score // 60}s",
            True,
            (200, 200, 240),
        )
        self.screen.blit(sc, (10, 10))

        # Title screen.
        if not self.started:
            msg = self.font.render(
                "Press SPACE to launch",
                True,
                (180, 180, 240),
            )
            self.screen.blit(
                msg,
                (
                    WIDTH // 2 - msg.get_width() // 2,
                    HEIGHT // 2,
                ),
            )

        # Game Over overlay.
        if self.game_over:
            overlay = pygame.Surface(
                (WIDTH, HEIGHT), pygame.SRCALPHA
            )
            overlay.fill((0, 0, 0, 150))
            self.screen.blit(overlay, (0, 0))

            message = self.big_font.render(
                "DESTROYED!", True, (220, 80, 60)
            )
            subtitle = self.font.render(
                f"Survived {self.score // 60}s | SPACE to Restart",
                True,
                (200, 200, 200),
            )

            self.screen.blit(
                message,
                (
                    WIDTH // 2 - message.get_width() // 2,
                    HEIGHT // 2 - 40,
                ),
            )
            self.screen.blit(
                subtitle,
                (
                    WIDTH // 2 - subtitle.get_width() // 2,
                    HEIGHT // 2 + 20,
                ),
            )

        pygame.display.flip()

    def run(self):
        running = True

        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
