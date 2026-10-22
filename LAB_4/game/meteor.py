
import pygame
import random
import math


class Meteor:
    LARGE_RADIUS_THRESHOLD = 20
    FRAGMENT_RADIUS_FACTOR = 0.55

    def __init__(
        self,
        width,
        x=None,
        y=-30,
        radius=None,
        vx=None,
        vy=None,
        color=None,
    ):
        # Randomized values are used for naturally spawned meteors.
        self.x = random.randint(0, width) if x is None else x
        self.y = y
        self.radius = random.randint(12, 28) if radius is None else radius

        if vx is None or vy is None:
            angle = random.uniform(70, 110)
            speed = random.uniform(2, 5)
            self.vx = math.cos(math.radians(angle)) * speed
            self.vy = math.sin(math.radians(angle)) * speed
        else:
            self.vx = vx
            self.vy = vy

        self.color = color or (
            random.randint(160, 220),
            random.randint(80, 120),
            random.randint(40, 80),
        )

        self.rot = random.uniform(0, 360)
        self.rot_speed = random.uniform(-3, 3)

    def split(self, width):
        """Split a large meteor into two outward-moving fragments.

        Small meteors do not split and are destroyed completely.
        """
        if self.radius < self.LARGE_RADIUS_THRESHOLD:
            return []

        child_radius = max(
            7,
            int(self.radius * self.FRAGMENT_RADIUS_FACTOR),
        )

        # Give the fragments a slight color variation.
        child_color = tuple(
            min(255, channel + 15) for channel in self.color
        )

        # Diverge in opposite directions while retaining some of
        # the parent's momentum.
        spread_angle = random.uniform(30, 45)
        parent_angle = math.atan2(self.vy, self.vx)
        parent_speed = math.hypot(self.vx, self.vy)

        fragments = []

        for direction in (-1, 1):
            angle = parent_angle + math.radians(
                direction * spread_angle
            )

            speed = max(2.5, parent_speed * 1.15)

            fragment = Meteor(
                width=width,
                x=self.x + direction * child_radius * 0.7,
                y=self.y,
                radius=child_radius,
                vx=math.cos(angle) * speed,
                vy=math.sin(angle) * speed,
                color=child_color,
            )

            fragments.append(fragment)

        return fragments

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.rot = (self.rot + self.rot_speed) % 360

    def off_screen(self, height):
        return (
            self.y > height + 60
            or self.x < -60
            or self.x > 760
        )

    def collides(self, rect):
        cx, cy = rect.centerx, rect.centery
        dx, dy = self.x - cx, self.y - cy

        return math.hypot(dx, dy) < self.radius + 16

    def draw(self, screen):
        points = []

        for i in range(7):
            angle = math.radians(self.rot + i * (360 / 7))
            radius = self.radius * (0.8 + 0.2 * (i % 2))

            points.append(
                (
                    int(self.x + radius * math.cos(angle)),
                    int(self.y + radius * math.sin(angle)),
                )
            )

        pygame.draw.polygon(screen, self.color, points)

        inner_points = [
            (
                int(self.x + (self.radius * 0.5) *
                    (0.8 + 0.2 * (i % 2)) *
                    math.cos(math.radians(self.rot + i * (360 / 7)))),
                int(self.y + (self.radius * 0.5) *
                    (0.8 + 0.2 * (i % 2)) *
                    math.sin(math.radians(self.rot + i * (360 / 7)))),
            )
            for i in range(7)
        ]

        darker_color = tuple(
            max(0, channel - 40) for channel in self.color
        )

        pygame.draw.polygon(screen, darker_color, inner_points)
