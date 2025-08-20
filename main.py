import pygame
import random
import sqlite3
from pygame import mixer

# Инициализация PyGame
pygame.init()
mixer.init()

# Экран
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Космический стрелок")

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# Шрифты
font_small = pygame.font.SysFont('arial', 20)
font_medium = pygame.font.SysFont('arial', 30)
font_large = pygame.font.SysFont('arial', 50)

# Загрузка изображений и звуков
try:
    player_img = pygame.image.load('player.png')
    player_img = pygame.transform.scale(player_img, (80, 80))
except:
    player_img = pygame.Surface((80, 80))
    player_img.fill(GREEN)

try:
    asteroid_img = pygame.image.load('asteroid.png')
    asteroid_img = pygame.transform.scale(asteroid_img, (50, 50))
except:
    asteroid_img = pygame.Surface((50, 50))
    asteroid_img.fill(RED)

try:
    bullet_img = pygame.image.load('bullet.png')
    bullet_img = pygame.transform.scale(bullet_img, (20, 30))
except:
    bullet_img = pygame.Surface((10, 20))
    bullet_img.fill(YELLOW)

try:
    background_img = pygame.image.load('background.png')
    background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))
except:
    background_img = pygame.Surface((WIDTH, HEIGHT))
    background_img.fill(BLACK)

try:
    explosion_sound = mixer.Sound('explosion.wav')
    shoot_sound = mixer.Sound('shoot.wav')
    mixer.music.load('background.mp3')
    mixer.music.play(-1)
    mixer.music.set_volume(0.5)
except:
    print("Звуки не загружены")


class Player:
    def __init__(self):
        self.img = player_img
        self.x = WIDTH // 2
        self.y = HEIGHT - 100
        self.speed = 5
        self.rect = self.img.get_rect(center=(self.x, self.y))
        self.lives = 3
        self.score = 0
        self.bullets = []
        self.cooldown = 0

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.x > 0:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] and self.x < WIDTH - 50:
            self.x += self.speed
        if keys[pygame.K_UP] and self.y > 0:
            self.y -= self.speed
        if keys[pygame.K_DOWN] and self.y < HEIGHT - 50:
            self.y += self.speed

        self.rect = self.img.get_rect(center=(self.x, self.y))

        if self.cooldown > 0:
            self.cooldown -= 1

    def shoot(self):
        if self.cooldown == 0:
            bullet = Bullet(self.x, self.y)
            self.bullets.append(bullet)
            try:
                shoot_sound.play()
            except:
                pass
            self.cooldown = 20

    def draw(self, screen):
        screen.blit(self.img, self.rect)
        for bullet in self.bullets:
            bullet.draw(screen)

    def check_bullets(self):
        for bullet in self.bullets[:]:
            bullet.update()
            if bullet.y < 0:
                self.bullets.remove(bullet)


class Bullet:
    def __init__(self, x, y):
        self.img = bullet_img
        self.x = x
        self.y = y
        self.speed = 7
        self.rect = self.img.get_rect(center=(self.x, self.y))

    def update(self):
        self.y -= self.speed
        self.rect = self.img.get_rect(center=(self.x, self.y))

    def draw(self, screen):
        screen.blit(self.img, self.rect)


class Asteroid:
    def __init__(self):
        self.img = asteroid_img
        self.x = random.randint(0, WIDTH - 40)
        self.y = random.randint(-100, -40)
        self.speed = random.randint(1, 4)
        self.rect = self.img.get_rect(center=(self.x, self.y))

    def update(self):
        self.y += self.speed
        self.rect = self.img.get_rect(center=(self.x, self.y))
        if self.y > HEIGHT:
            return True
        return False

    def draw(self, screen):
        screen.blit(self.img, self.rect)


class GameDB:
    def __init__(self):
        self.conn = sqlite3.connect('space_shooter.db')
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                score INTEGER NOT NULL
            )
        ''')
        self.conn.commit()

    def add_score(self, name, score):
        self.cursor.execute('INSERT INTO scores (name, score) VALUES (?, ?)', (name, score))
        self.conn.commit()

    def get_top_scores(self, limit=5):
        self.cursor.execute('SELECT name, score FROM scores ORDER BY score DESC LIMIT ?', (limit,))
        return self.cursor.fetchall()

    def close(self):
        self.conn.close()


def show_text(screen, text, font, color, x, y):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    screen.blit(text_surface, text_rect)


def get_player_name(screen):
    name = ""
    input_active = True

    while input_active:
        screen.fill(BLACK)
        show_text(screen, "Введите ваш никнейм:", font_medium, WHITE, WIDTH // 2, HEIGHT // 2 - 50)

        # Поле ввода
        pygame.draw.rect(screen, WHITE, (WIDTH // 2 - 150, HEIGHT // 2, 300, 40), 2)
        show_text(screen, name, font_medium, WHITE, WIDTH // 2, HEIGHT // 2 + 20)

        show_text(screen, "Нажмите Enter чтобы продолжить", font_small, WHITE, WIDTH // 2, HEIGHT // 2 + 100)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and name:
                    input_active = False
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                else:
                    if len(name) < 15 and event.unicode.isalnum():
                        name += event.unicode

        pygame.display.flip()

    return name


def game_over_screen(screen, score, db):
    screen.fill(BLACK)
    show_text(screen, "Игра окончена!", font_large, RED, WIDTH // 2, HEIGHT // 2 - 100)
    show_text(screen, f"Ваш счет: {score}", font_medium, WHITE, WIDTH // 2, HEIGHT // 2 - 30)

    # Топ-5 игроков
    show_text(screen, "Топ-5 игроков:", font_medium, WHITE, WIDTH // 2, HEIGHT // 2 + 30)

    top_players = db.get_top_scores()
    y_offset = HEIGHT // 2 + 80
    for i, (name, score) in enumerate(top_players, 1):
        show_text(screen, f"{i}. {name}: {score}", font_small, WHITE, WIDTH // 2, y_offset)
        y_offset += 30

    show_text(screen, "Нажмите любую клавишу для выхода", font_small, WHITE, WIDTH // 2, HEIGHT - 50)
    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                waiting = False
            if event.type == pygame.KEYDOWN:
                waiting = False

    return False


def main():
    running = True
    clock = pygame.time.Clock()
    db = GameDB()

    # Получаем имя игрока
    player_name = get_player_name(screen)
    if not player_name:
        return

    # Инициализация игры
    player = Player()
    asteroids = []
    asteroid_spawn_timer = 0
    game_active = True

    while running:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and game_active:
                if event.key == pygame.K_SPACE:
                    player.shoot()

        if game_active:
            # Обновление игрока
            player.update()
            player.check_bullets()

            # Спавн астероидов
            asteroid_spawn_timer += 1
            if asteroid_spawn_timer >= 60:
                asteroids.append(Asteroid())
                asteroid_spawn_timer = 0

            # Обновление астероидов
            for asteroid in asteroids[:]:
                if asteroid.update():  # Если астероид ушел за экран
                    asteroids.remove(asteroid)

                # Проверка столкновения с игроком
                if player.rect.colliderect(asteroid.rect):
                    try:
                        explosion_sound.play()
                    except:
                        pass
                    player.lives -= 1
                    asteroids.remove(asteroid)
                    if player.lives <= 0:
                        game_active = False
                        db.add_score(player_name, player.score)

            # Проверка столкновения пуль с астероидами
            for bullet in player.bullets[:]:
                for asteroid in asteroids[:]:
                    if bullet.rect.colliderect(asteroid.rect):
                        try:
                            explosion_sound.play()
                        except:
                            pass
                        player.score += 10
                        if bullet in player.bullets:
                            player.bullets.remove(bullet)
                        if asteroid in asteroids:
                            asteroids.remove(asteroid)
                        break

        # Отрисовка
        screen.blit(background_img, (0, 0))

        if game_active:
            player.draw(screen)
            for asteroid in asteroids:
                asteroid.draw(screen)

            # Отрисовка жизней и счета
            show_text(screen, f"Жизни: {player.lives}", font_small, WHITE, 70, 20)
            show_text(screen, f"Счет: {player.score}", font_small, WHITE, 70, 50)
            show_text(screen, "Управление: стрелки, стрельба: пробел", font_small, WHITE, WIDTH // 2, 20)
        else:
            running = game_over_screen(screen, player.score, db)

        pygame.display.flip()

    db.close()
    pygame.quit()


if __name__ == "__main__":
    main()