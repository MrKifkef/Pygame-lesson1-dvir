import asyncio
import random
import pygame

pygame.init()

WIDTH = 800
HEIGHT = 600

PLAYER_SIZE = 50
TARGET_RADIUS = 25
SPEED = 5
POPUP_DURATION_MS = 500
POPUP_RISE_PIXELS = 40
GAME_DURATION_MS = 60_000
RAINBOW_COLORS = (
    (255, 0, 0),
    (255, 127, 0),
    (255, 255, 0),
    (0, 200, 0),
    (0, 120, 255),
    (75, 0, 180),
    (148, 0, 211),
)
CIRCLE_TYPES = (
    ((255, 0, 0), 1),
    ((0, 200, 0), 2),
    ((0, 100, 255), 3),
)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("My Pygame Game")

x = 375
y = 275
target_x = 600
target_y = 300
target_color = (255, 0, 0)
target_value = 1
score = 0
score_font = pygame.font.Font(None, 36)
popup_font = pygame.font.Font(None, 48)
timer_font = pygame.font.Font(None, 36)
game_over_font = pygame.font.Font(None, 64)
button_font = pygame.font.Font(None, 36)
score_popups = []
score_history = []


def draw_gradient_cube(rect, shift):
    segment_count = len(RAINBOW_COLORS) - 1
    for offset in range(rect.width):
        progress = (offset / max(1, rect.width - 1) + shift) % 1
        color_position = progress * segment_count
        segment = min(int(color_position), segment_count - 1)
        segment_progress = color_position - segment
        start_color = RAINBOW_COLORS[segment]
        end_color = RAINBOW_COLORS[segment + 1]
        color = tuple(
            int(
                start_color[channel]
                + (end_color[channel] - start_color[channel]) * segment_progress
            )
            for channel in range(3)
        )
        pygame.draw.line(
            screen,
            color,
            (rect.left + offset, rect.top),
            (rect.left + offset, rect.bottom - 1),
        )


def choose_target():
    color, value = random.choices(CIRCLE_TYPES, weights=(6, 3, 2))[0]
    return (
        random.randint(TARGET_RADIUS, WIDTH - TARGET_RADIUS),
        random.randint(TARGET_RADIUS, HEIGHT - TARGET_RADIUS),
        color,
        value,
    )


async def main():
    global x, y, target_x, target_y, target_color, target_value
    global score, score_popups, score_history

    running = True
    game_over = False
    score_saved = False
    game_start_time = pygame.time.get_ticks()
    restart_button = pygame.Rect(300, 430, 200, 55)

    while running:

        # EVENTS
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif (
                game_over
                and event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
                and restart_button.collidepoint(event.pos)
            ):
                x = 375
                y = 275
                target_x, target_y, target_color, target_value = choose_target()
                score = 0
                score_popups = []
                game_over = False
                score_saved = False
                game_start_time = pygame.time.get_ticks()

        current_time = pygame.time.get_ticks()
        elapsed_game_time = current_time - game_start_time
        if elapsed_game_time >= GAME_DURATION_MS:
            game_over = True
            if not score_saved:
                score_history.append(score)
                score_history = score_history[-4:]
                score_saved = True

        if not game_over:
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
                score_popups.append({
                    "x": target_x,
                    "y": target_y,
                    "color": target_color,
                    "value": target_value,
                    "start_time": current_time,
                })
                target_x, target_y, target_color, target_value = choose_target()
                score += target_value

        # DRAW
        screen.fill((30, 30, 60))

        if not game_over:
            # Draw the target from its center position and radius.
            pygame.draw.circle(screen, target_color, (target_x, target_y), TARGET_RADIUS)

            gradient_shift = (current_time % 2000) / 2000
            draw_gradient_cube(
                pygame.Rect(x, y, PLAYER_SIZE, PLAYER_SIZE), gradient_shift
            )

        score_text = score_font.render(f"Score: {score}", True, (255, 255, 255))
        # Measure the text so its right edge stays inside the window.
        screen.blit(score_text, (WIDTH - score_text.get_width() - 10, 10))

        remaining_ms = max(0, GAME_DURATION_MS - elapsed_game_time)
        remaining_seconds = (remaining_ms + 999) // 1000
        timer_text = timer_font.render(f"Time: {remaining_seconds}", True, (255, 255, 255))
        screen.blit(timer_text, (10, 10))

        if game_over:
            game_over_text = game_over_font.render("GAME OVER", True, (255, 255, 255))
            game_over_x = (WIDTH - game_over_text.get_width()) / 2
            screen.blit(game_over_text, (game_over_x, 65))

            final_score_text = score_font.render(
                f"Current run: {score}", True, (255, 255, 255)
            )
            final_score_x = (WIDTH - final_score_text.get_width()) / 2
            screen.blit(final_score_text, (final_score_x, 150))

            history_title = score_font.render("Previous runs:", True, (255, 255, 255))
            history_title_x = (WIDTH - history_title.get_width()) / 2
            screen.blit(history_title, (history_title_x, 205))
            previous_scores = score_history[:-1][-3:]
            for index, past_score in enumerate(reversed(previous_scores)):
                history_text = button_font.render(
                    f"Run {index + 1}: {past_score}", True, (220, 220, 220)
                )
                history_x = (WIDTH - history_text.get_width()) / 2
                screen.blit(history_text, (history_x, 245 + index * 35))

            pygame.draw.rect(screen, (50, 150, 80), restart_button, border_radius=8)
            restart_text = button_font.render("Restart", True, (255, 255, 255))
            restart_x = restart_button.centerx - restart_text.get_width() / 2
            restart_y = restart_button.centery - restart_text.get_height() / 2
            screen.blit(restart_text, (restart_x, restart_y))

        current_time = pygame.time.get_ticks()
        active_popups = []
        for popup in score_popups:
            elapsed = current_time - popup["start_time"]
            if elapsed >= POPUP_DURATION_MS:
                continue

            progress = elapsed / POPUP_DURATION_MS
            popup_surface = popup_font.render(
                f"+{popup['value']}", True, popup["color"]
            )
            popup_surface.set_alpha(int(255 * (1 - progress)))
            popup_y = popup["y"] - (POPUP_RISE_PIXELS * progress)
            popup_x = popup["x"] - (popup_surface.get_width() / 2)
            screen.blit(popup_surface, (popup_x, popup_y))
            active_popups.append(popup)

        score_popups = active_popups

        pygame.display.flip()

        await asyncio.sleep(0)

    pygame.quit()


asyncio.run(main())