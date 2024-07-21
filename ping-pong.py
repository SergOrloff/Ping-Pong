import pygame
import sys
import random

# Инициализация Pygame
pygame.init()

# Цвета
GREY = (172, 172, 172)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)

# Размеры экрана
WIDTH = 1280
HEIGHT = 720

# Состояния игры
MENU = 0
GAME = 1
WIN = 2
LOSE = 3
PAUSE = 4
ROUND_WIN = 5

# Режимы игры
PLAYER_VS_PLAYER = 0
PLAYER_VS_COMPUTER = 1

# Счёт
score1 = 0
score2 = 0
wins1 = 0
wins2 = 0

# Максимальная скорость мяча
MAX_SPEED = 10

# Загрузка звуков
bounce_sound = pygame.mixer.Sound('sound/click.mp3')
score_sound = pygame.mixer.Sound('sound/ura.mp3')
win_sound = pygame.mixer.Sound('sound/win.mp3')
lose_sound = pygame.mixer.Sound('sound/lose.mp3')

# Загрузка фонового изображения
background_image = pygame.image.load('images/background.png')

# Класс для игрового объекта (ракетка)
class Paddle(pygame.sprite.Sprite):
    def __init__(self, color, width, height, is_player=True):
        super().__init__()
        self.image = pygame.Surface([width, height])
        self.image.fill(color)
        self.rect = self.image.get_rect()

        self.is_player = is_player

    def move_up(self, pixels):
        self.rect.y -= pixels
        if self.rect.y < 0:
            self.rect.y = 0

    def move_down(self, pixels):
        self.rect.y += pixels
        if self.rect.y > HEIGHT - self.rect.height:
            self.rect.y = HEIGHT - self.rect.height

    def auto_move(self, ball):
        if ball.rect.y < self.rect.y + self.rect.height // 2:
            self.move_up(5)
        elif ball.rect.y > self.rect.y + self.rect.height // 2:
            self.move_down(5)

# Класс для мяча
class Ball(pygame.sprite.Sprite):
    def __init__(self, color, width, height):
        super().__init__()
        self.image = pygame.Surface([width, height])
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.speed = [5, 5]

    def update(self):
        self.rect.x += self.speed[0]
        self.rect.y += self.speed[1]

        if self.rect.y <= 0 or self.rect.y >= HEIGHT - self.rect.height:
            self.speed[1] = -self.speed[1]
            bounce_sound.play()

    def accelerate(self):
        self.speed[0] *= 1.1
        self.speed[1] *= 1.1
        # Ограничение максимальной скорости
        self.speed[0] = max(min(self.speed[0], MAX_SPEED), -MAX_SPEED)
        self.speed[1] = max(min(self.speed[1], MAX_SPEED), -MAX_SPEED)

# Функция для отображения текста на экране
def display_text(text, font, size, color, x, y):
    font = pygame.font.Font(font, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.center = (x, y)
    screen.blit(text_surface, text_rect)

# Создание экрана
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ping Pong")

# Создание спрайтов
all_sprites = pygame.sprite.Group()
paddle1 = Paddle(WHITE, 10, 100, True)  # Игрок
paddle1.rect.x = 20
paddle1.rect.y = HEIGHT // 2 - 50
paddle2 = Paddle(WHITE, 10, 100, False)  # Компьютер
paddle2.rect.x = WIDTH - 30
paddle2.rect.y = HEIGHT // 2 - 50
ball = Ball(WHITE, 10, 10)
ball.rect.x = WIDTH // 2
ball.rect.y = HEIGHT // 2

all_sprites.add(paddle1, paddle2, ball)

clock = pygame.time.Clock()

# Игровое состояние
game_state = MENU

# Режим игры
game_mode = PLAYER_VS_PLAYER

def reset_round():
    global score1, score2
    score1 = 0
    score2 = 0
    ball.rect.x = WIDTH // 2
    ball.rect.y = HEIGHT // 2
    ball.speed = [5, 5]
    ball.image.fill(WHITE)

# Основной игровой цикл
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # Обработка нажатий клавиш в меню
        if game_state == MENU:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    game_mode = PLAYER_VS_PLAYER
                    game_state = GAME
                    paddle2.is_player = True
                elif event.key == pygame.K_2:
                    game_mode = PLAYER_VS_COMPUTER
                    game_state = GAME
                    paddle2.is_player = False

        elif game_state == GAME:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    game_state = PAUSE

        elif game_state == PAUSE:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    game_state = GAME

        elif game_state == WIN or game_state == LOSE:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    game_state = MENU
                    wins1 = 0
                    wins2 = 0
                    reset_round()

    # Обработка нажатий клавиш в игре
    if game_state == GAME:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            paddle1.move_up(5)
        if keys[pygame.K_s]:
            paddle1.move_down(5)

        if game_mode == PLAYER_VS_PLAYER:
            if keys[pygame.K_UP]:
                paddle2.move_up(5)
            if keys[pygame.K_DOWN]:
                paddle2.move_down(5)
        elif game_mode == PLAYER_VS_COMPUTER:
            paddle2.auto_move(ball)

    # Логика игры в зависимости от состояния
    if game_state == GAME:
        # Обновление позиций мяча и ракеток
        ball.update()

        # Проверка на столкновение мяча с ракетками
        if pygame.sprite.collide_rect(ball, paddle1) or pygame.sprite.collide_rect(ball, paddle2):
            ball.speed[0] = -ball.speed[0]
            ball.accelerate()
            ball.image.fill(RED)  # Изменение цвета мяча при столкновении
            bounce_sound.play()  # Воспроизведение звука столкновения

        # Проверка условия победы или поражения
        if ball.rect.x <= 0:
            score2 += 1
            ball.rect.x = WIDTH // 2
            ball.rect.y = HEIGHT // 2
            ball.speed = [5, 5]
            ball.image.fill(WHITE)
            score_sound.play()  # Воспроизведение звука гола
        elif ball.rect.x >= WIDTH - ball.rect.width:
            score1 += 1
            ball.rect.x = WIDTH // 2
            ball.rect.y = HEIGHT // 2
            ball.speed = [-5, -5]
            ball.image.fill(WHITE)
            score_sound.play()  # Воспроизведение звука гола

        # Проверка окончания раунда
        if score1 >= 10:
            wins1 += 1
            if wins1 >= 3:
                game_state = WIN
                win_sound.play()
            else:
                game_state = ROUND_WIN
            reset_round()
        elif score2 >= 10:
            wins2 += 1
            if wins2 >= 3:
                game_state = LOSE
                lose_sound.play()
            else:
                game_state = ROUND_WIN
            reset_round()

        # Очистка экрана и отрисовка фонового изображения
        screen.blit(background_image, (0, 0))
        pygame.draw.line(screen, WHITE, [WIDTH // 2, 0], [WIDTH // 2, HEIGHT], 5)


        # # Очистка экрана
        # screen.fill(GREY)
        # pygame.draw.line(screen, WHITE, [WIDTH // 2, 0], [WIDTH // 2, HEIGHT], 5)

        # Отображение счёта и количества побед
        display_text(f"{score1}", None, 50, WHITE, WIDTH // 4, 50)
        display_text(f"{score2}", None, 50, WHITE, 3 * WIDTH // 4, 50)
        display_text(f"Побед: {wins1}", None, 30, WHITE, WIDTH // 4, 100)
        display_text(f"Побед: {wins2}", None, 30, WHITE, 3 * WIDTH // 4, 100)

        all_sprites.draw(screen)

    elif game_state == WIN:
        # screen.fill(GREY)
        display_text("Игрок 1 выигрывает игру!", None, 60, WHITE, WIDTH // 2, HEIGHT // 2)
        display_text("Нажмите Enter для возвращения в меню", None, 40, WHITE, WIDTH // 2, HEIGHT // 1.5)

    elif game_state == LOSE:
        # screen.fill(GREY)
        display_text("Игрок 2 выигрывает игру!", None, 60, WHITE, WIDTH // 2, HEIGHT // 2)
        display_text("Нажмите Enter для возвращения в меню", None, 40, WHITE, WIDTH // 2, HEIGHT // 1.5)

    elif game_state == ROUND_WIN:
        # screen.fill(GREY)
        display_text(f"Раунд закончился", None, 60, RED, WIDTH // 2, HEIGHT // 2)
        display_text("Нажмите 'P' для продолжения", None, 40, GREEN, WIDTH // 2, HEIGHT // 1.5)

        keys = pygame.key.get_pressed()
        if keys[pygame.K_p]:
            game_state = GAME

    elif game_state == MENU:
        screen.blit(background_image, (0, 0))
        # screen.fill(GREY)
        display_text("Пинг-Понг", None, 140, GREEN, WIDTH // 2, HEIGHT // 4)
        display_text("Нажмите '1' для     ДВУХ     игроков", None, 50, YELLOW, WIDTH // 2, HEIGHT // 1.5)
        display_text("Нажмите '2' для     ОДНОГО  игрока", None, 50, YELLOW, WIDTH // 2, HEIGHT // 1.3)

    elif game_state == PAUSE:
        display_text("Приостановлено", None, 60, WHITE, WIDTH // 2, HEIGHT // 2)
        display_text("Нажмите 'P' для возобновления игры", None, 40, WHITE, WIDTH // 2, HEIGHT // 1.5)

    # Показать экран
    pygame.display.flip()

    # Ограничение скорости кадров
    clock.tick(60)