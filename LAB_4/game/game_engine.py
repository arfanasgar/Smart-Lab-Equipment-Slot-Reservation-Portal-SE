
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

# Shield-orb settings
ORB_RADIUS = 12
ORB_SPEED = 2.2
ORB_COLOR = (80, 255, 160)
SHIELD_COLOR = (80, 220, 255)


class ShieldOrb:
    """A collectible orb that grants one-hit meteor protection."""

    def __init__(self):
        self.x = random.randint(ORB_RADIUS + 8, WIDTH - ORB_RADIUS - 8)
        self.y = -ORB_RADIUS
        self.radius = ORB_RADIUS
        self.speed = ORB_SPEED

    def update(self):
        self.y += self.speed

    def off_screen(self):
        return self.y - self.radius > HEIGHT

    def collides(self, rect):
        dx = self.x - rect.centerx
        dy = self.y - rect.centery
        return math.hypot(dx, dy) < self.radius + 18

    def draw(self, screen):
        # Outer glow, orb body, and a simple plus symbol.
        center = (int(self.x), int(self.y))
        pygame.draw.circle(screen, (25, 100, 75), center, self.radius + 5)
        pygame.draw.circle(screen, ORB_COLOR, center, self.radius)
        pygame.draw.line(
            screen, (240, 255, 245),
            (center[0] - 5, center[1]), (center[0] + 5, center[1]), 3
        )
        pygame.draw.line(
            screen, (240, 255, 245),
            (center[0], center[1] - 5), (center[0], center[1] + 5), 3
        )


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
        self.shield_orbs = []
        self.shield_active = False

        self.timer = 0
        self.orb_timer = 0
        self.next_orb_spawn = random.randint(8 * FPS, 12 * FPS)
        self.spawn_interval = 60
        self.score = 0

        self.game_over = False
        self.started = False

    def fire_laser(self):
        """Fire an upward-moving laser from the ship."""
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
            self.spawn_interval = max(
                20, self.spawn_interval - 0.3
            )

        # Occasionally spawn a collectible shield orb.
        self.orb_timer += 1
        if self.orb_timer >= self.next_orb_spawn:
            self.shield_orbs.append(ShieldOrb())
            self.orb_timer = 0
            self.next_orb_spawn = random.randint(8 * FPS, 12 * FPS)

        # Move and collect shield orbs.
        for orb in self.shield_orbs:
            orb.update()
            if orb.collides(self.ship.rect):
                self.shield_active = True

        self.shield_orbs = [
            orb for orb in self.shield_orbs
            if not orb.off_screen() and not orb.collides(self.ship.rect)
        ]

        # Move lasers.
        for laser in self.lasers:
            laser.y -= LASER_SPEED

        self.lasers = [
            laser for laser in self.lasers
            if laser.bottom > 0
        ]

        # Update meteors and resolve ship collisions. An active shield
        # absorbs exactly one collision and destroys that meteor.
        shield_absorbed_meteor = None
        for meteor in self.meteors:
            meteor.update()

            if meteor.collides(self.ship.rect):
                if self.shield_active:
                    self.shield_active = False
                    shield_absorbed_meteor = id(meteor)
                    break
                self.game_over = True
                break

        if self.game_over:
            return

        if shield_absorbed_meteor is not None:
            self.meteors = [
                meteor for meteor in self.meteors
                if id(meteor) != shield_absorbed_meteor
            ]

        # Resolve laser collisions without modifying the meteor list
        # while iterating through it.
        destroyed_ids = set()
        consumed_lasers = set()
        new_fragments = []

        for laser_index, laser in enumerate(self.lasers):
            for meteor in self.meteors:
                meteor_id = id(meteor)

                # A meteor can only be destroyed once per frame.
                if meteor_id in destroyed_ids:
                    continue

                dx = meteor.x - laser.centerx
                dy = meteor.y - laser.centery

                # Approximate the laser as a circle for collision.
                distance = math.hypot(dx, dy)

                if distance < meteor.radius + LASER_HEIGHT / 2:
                    destroyed_ids.add(meteor_id)
                    consumed_lasers.add(laser_index)

                    # Large meteors split; small ones disappear.
                    new_fragments.extend(meteor.split(WIDTH))
                    break

        # Keep only lasers that have not hit a meteor.
        self.lasers = [
            laser
            for index, laser in enumerate(self.lasers)
            if index not in consumed_lasers
        ]

        # Remove destroyed and off-screen meteors.
        self.meteors = [
            meteor for meteor in self.meteors
            if id(meteor) not in destroyed_ids
            and not meteor.off_screen(HEIGHT)
        ]

        # Add fragments after collision processing to avoid modifying
        # the meteor list while iterating over it.
        self.meteors.extend(new_fragments)

        self.score += 1

    def draw(self):
        self.screen.fill(BG)

        # Background starfield.
        for sx, sy, sr in self.stars:
            pygame.draw.circle(
                self.screen,
                (200, 200, 220),
                (sx, sy),
                sr,
            )

        # Meteors and fragments.
        for meteor in self.meteors:
            meteor.draw(self.screen)

        # Collectible shield orbs.
        for orb in self.shield_orbs:
            orb.draw(self.screen)

        # Laser glow and core.
        for laser in self.lasers:
            pygame.draw.rect(
                self.screen,
                LASER_GLOW,
                laser.inflate(8, 6),
                border_radius=4,
            )

            pygame.draw.rect(
                self.screen,
                LASER_COLOR,
                laser,
                border_radius=2,
            )

        # Draw a visible barrier while the one-hit shield is active.
        if self.shield_active:
            shield_center = self.ship.rect.center
            pygame.draw.circle(
                self.screen, SHIELD_COLOR, shield_center, 29, 3
            )
            pygame.draw.circle(
                self.screen, (35, 100, 150), shield_center, 33, 1
            )

        self.ship.draw(self.screen)

        # Shield status HUD.
        if self.shield_active:
            shield_text = self.font.render(
                "SHIELD READY", True, SHIELD_COLOR
            )
            self.screen.blit(shield_text, (10, 42))

        # Survival timer.
        timer_text = self.font.render(
            f"Time: {self.score // 60}s",
            True,
            (200, 200, 240),
        )

        self.screen.blit(timer_text, (10, 10))

        # Title screen.
        if not self.started:
            message = self.font.render(
                "Press SPACE to launch",
                True,
                (180, 180, 240),
            )

            self.screen.blit(
                message,
                (
                    WIDTH // 2 - message.get_width() // 2,
                    HEIGHT // 2,
                ),
            )

        # Game Over overlay.
        if self.game_over:
            overlay = pygame.Surface(
                (WIDTH, HEIGHT),
                pygame.SRCALPHA,
            )

            overlay.fill((0, 0, 0, 150))
            self.screen.blit(overlay, (0, 0))

            message = self.big_font.render(
                "DESTROYED!",
                True,
                (220, 80, 60),
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

