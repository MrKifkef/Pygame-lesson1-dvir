import asyncio
import random
import pygame

pygame.init()

WIDTH = 800
HEIGHT = 600

PLAYER_SIZE = 50
TARGET_RADIUS = 25
SPEED = 10

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("My Pygame Game")

x = 375
y = 275
target_x = 600
target_y = 300
target_color = (255, 0, 0)
score = 0
score_font = pygame.font.Font(None, 36)


async def main():
    global x, y, target_x, target_y, score, target_color

    running = True

    while running:

        # EVENTS
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # INPUT
        keys = pygame.key.get_pressed()

        # WASD provides an alternate layout for the arrow controls.
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            x -= SPEED

        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            x += SPEED

        if keys[pygame.K_UP] or keys[pygame.K_w]:
            y -= SPEED

        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            y += SPEED

        # Keep the entire player square inside the window.
        x = max(0, min(x, WIDTH - PLAYER_SIZE))
        y = max(0, min(y, HEIGHT - PLAYER_SIZE))

        player_rect = pygame.Rect(x, y, PLAYER_SIZE, PLAYER_SIZE)
        # The target rect bounds the circle for pygame's rectangle collision check.
        target_rect = pygame.Rect(
            target_x - TARGET_RADIUS,
            target_y - TARGET_RADIUS,
            TARGET_RADIUS * 2,
            TARGET_RADIUS * 2,
        )
        is_colliding = player_rect.colliderect(target_rect)
        if is_colliding:
            # Limit the center so the target's full diameter stays on-screen.
            target_x = random.randint(TARGET_RADIUS, WIDTH - TARGET_RADIUS)
            target_y = random.randint(TARGET_RADIUS, HEIGHT - TARGET_RADIUS)
            previous_color = target_color
            # Keep choosing until the newly spawned target has a different color.
            while target_color == previous_color:
                target_color = (
                    random.randint(0, 255),
                    random.randint(0, 255),
                    random.randint(0, 255),
                )
            score += 1

        # DRAW
        screen.fill((30, 30, 60))

        # Draw the target from its center position and radius.
        pygame.draw.circle(screen, target_color, (target_x, target_y), TARGET_RADIUS)

        pygame.draw.rect(
            screen,
            (255, 200, 50),
            (x, y, PLAYER_SIZE, PLAYER_SIZE)
        )

        score_text = score_font.render(f"Score: {score}", True, (255, 255, 255))
        # Measure the text so its right edge stays inside the window.
        screen.blit(score_text, (WIDTH - score_text.get_width() - 10, 10))

        pygame.display.flip()

        # Required for running Pygame in the browser
        await asyncio.sleep(0)

    pygame.quit()


asyncio.run(main())