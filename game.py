import pygame
import random
import sys

# Inicializar pygame
pygame.init()

# Configurações da tela
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 400
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Dinossauro Runner - Realista")

# Cores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
GREEN = (50, 150, 50)
DARK_GREEN = (30, 100, 30)
RED = (200, 0, 0)
DARK_RED = (150, 0, 0)
BROWN = (139, 69, 19)

# Clock para FPS
clock = pygame.time.Clock()
FPS = 60

# Fonte
font = pygame.font.Font(None, 36)
big_font = pygame.font.Font(None, 72)

# Classe do Dinossauro Realista
class Dinosaur(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.width = 60
        self.height = 85
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.x = 50
        self.rect.y = SCREEN_HEIGHT - 125
        self.vel_y = 0
        self.jumping = False
        self.animation_frame = 0
        
    def jump(self):
        if not self.jumping:
            self.vel_y = -18
            self.jumping = True
    
    def update(self):
        # Gravidade
        self.vel_y += 0.7
        self.rect.y += self.vel_y
        
        # Limitar ao chão
        if self.rect.y >= SCREEN_HEIGHT - 125:
            self.rect.y = SCREEN_HEIGHT - 125
            self.jumping = False
            self.vel_y = 0
        
        # Animar pernas
        self.animation_frame += 1
    
    def draw(self, surface):
        self.image.fill((0, 0, 0, 0))
        
        # Corpo principal (elipse)
        body_x = 12
        body_y = 35
        pygame.draw.ellipse(self.image, GREEN, (body_x, body_y, 36, 32))
        
        # Pescoço
        pygame.draw.rect(self.image, GREEN, (22, 15, 16, 22))
        
        # Cabeça (triangular)
        pygame.draw.polygon(self.image, DARK_GREEN, [
            (22, 10),   # topo
            (35, 5),    # ponta do focinho
            (38, 15),   # queixo
            (28, 18)    # trás da cabeça
        ])
        
        # Olho
        pygame.draw.circle(self.image, BLACK, (32, 10), 2)
        pygame.draw.circle(self.image, WHITE, (33, 9), 1)
        
        # Cauda dinâmica
        if self.jumping:
            pygame.draw.line(self.image, DARK_GREEN, (10, 48), (-5, 35), 4)
        else:
            pygame.draw.line(self.image, DARK_GREEN, (10, 48), (-8, 42), 4)
        
        # Pernas traseiras (animadas)
        perna_offset = 5 if (self.animation_frame // 5) % 2 == 0 and not self.jumping else 0
        pygame.draw.line(self.image, DARK_GREEN, (42, 65), (42, 80 + perna_offset), 5)
        pygame.draw.line(self.image, DARK_GREEN, (30, 65), (30, 80 - perna_offset), 5)
        
        # Pernas dianteiras
        pygame.draw.line(self.image, DARK_GREEN, (26, 65), (24, 80), 4)
        pygame.draw.line(self.image, DARK_GREEN, (36, 65), (38, 80), 4)
        
        surface.blit(self.image, self.rect)

# Classe do Obstáculo (cactus baixo - precisa pular)
class LowObstacle(pygame.sprite.Sprite):
    def __init__(self, speed):
        super().__init__()
        self.width = 25
        self.height = 50
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.x = SCREEN_WIDTH
        self.rect.y = SCREEN_HEIGHT - 100
        self.speed = speed
        self.type = "low"
    
    def update(self):
        self.rect.x -= self.speed
    
    def draw(self, surface):
        # Desenha cactus baixo
        # Tronco principal
        pygame.draw.rect(self.image, BROWN, (8, 20, 10, 30))
        # Picos
        pygame.draw.polygon(self.image, RED, [(3, 25), (5, 20), (8, 25)])
        pygame.draw.polygon(self.image, RED, [(17, 25), (20, 20), (22, 25)])
        pygame.draw.polygon(self.image, RED, [(3, 40), (5, 35), (8, 40)])
        pygame.draw.polygon(self.image, RED, [(17, 40), (20, 35), (22, 40)])
        pygame.draw.circle(self.image, RED, (12, 15), 3)
        
        surface.blit(self.image, self.rect)

# Classe do Obstáculo Alto (árvore - precisa desviar)
class HighObstacle(pygame.sprite.Sprite):
    def __init__(self, speed):
        super().__init__()
        self.width = 40
        self.height = 100
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.x = SCREEN_WIDTH
        self.rect.y = SCREEN_HEIGHT - 150
        self.speed = speed
        self.type = "high"
    
    def update(self):
        self.rect.x -= self.speed
    
    def draw(self, surface):
        # Desenha árvore
        # Tronco
        pygame.draw.rect(self.image, BROWN, (15, 50, 10, 50))
        # Galhos
        pygame.draw.rect(self.image, BROWN, (8, 40, 24, 8))
        pygame.draw.rect(self.image, BROWN, (8, 30, 24, 6))
        # Copa
        pygame.draw.polygon(self.image, GREEN, [(20, 5), (5, 25), (35, 25)])
        pygame.draw.polygon(self.image, DARK_GREEN, [(20, 15), (8, 30), (32, 30)])
        
        surface.blit(self.image, self.rect)

# Plataforma para pular (estrutura suspensa)
class Platform(pygame.sprite.Sprite):
    def __init__(self, speed):
        super().__init__()
        self.width = 50
        self.height = 20
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.x = SCREEN_WIDTH
        self.rect.y = SCREEN_HEIGHT - 200
        self.speed = speed
        self.type = "platform"
    
    def update(self):
        self.rect.x -= self.speed
    
    def draw(self, surface):
        # Desenha plataforma de madeira
        pygame.draw.rect(self.image, BROWN, (0, 0, self.width, self.height))
        pygame.draw.line(self.image, (100, 50, 0), (0, 10), (self.width, 10), 2)
        # Correntes
        pygame.draw.line(self.image, (100, 100, 100), (10, 0), (10, -20), 2)
        pygame.draw.line(self.image, (100, 100, 100), (40, 0), (40, -20), 2)
        
        surface.blit(self.image, self.rect)

# Função principal do jogo
def main():
    running = True
    game_started = False
    game_over = False
    score = 0
    speed = 7
    spawn_timer = 0
    spawn_rate = 120
    
    dinosaur = Dinosaur()
    obstacles = pygame.sprite.Group()
    
    while running:
        clock.tick(FPS)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if not game_started:
                        game_started = True
                        game_over = False
                        score = 0
                        speed = 7
                        spawn_timer = 0
                        obstacles.empty()
                    elif game_over:
                        game_started = True
                        game_over = False
                        score = 0
                        speed = 7
                        spawn_timer = 0
                        obstacles.empty()
                    else:
                        dinosaur.jump()
        
        if game_started and not game_over:
            # Atualizar posições
            dinosaur.update()
            obstacles.update()
            
            # Gerar obstáculos variados
            spawn_timer += 1
            if spawn_timer >= spawn_rate:
                obstacle_type = random.choices(
                    [LowObstacle, HighObstacle, Platform],
                    weights=[50, 35, 15],  # Mais cactus baixo, depois árvore, depois plataforma
                    k=1
                )[0]
                new_obstacle = obstacle_type(speed)
                obstacles.add(new_obstacle)
                spawn_timer = 0
                spawn_rate = max(70, spawn_rate - 1)
            
            # Verificar colisões
            for obstacle in obstacles:
                collision_detected = False
                if obstacle.type == "low":
                    # Colisão com cactus baixo
                    if dinosaur.rect.colliderect(obstacle.rect):
                        game_over = True
                elif obstacle.type == "high":
                    # Colisão com árvore
                    if dinosaur.rect.colliderect(obstacle.rect):
                        game_over = True
                elif obstacle.type == "platform":
                    # Plataforma permite pular em cima
                    if (dinosaur.vel_y > 0 and  # Caindo
                        dinosaur.rect.bottom >= obstacle.rect.top and
                        dinosaur.rect.bottom <= obstacle.rect.top + 10 and
                        dinosaur.rect.centerx >= obstacle.rect.left and
                        dinosaur.rect.centerx <= obstacle.rect.right):
                        dinosaur.vel_y = -15  # Pula automaticamente
                    elif (dinosaur.rect.colliderect(obstacle.rect) and
                          dinosaur.rect.bottom > obstacle.rect.top + 10):
                        game_over = True
            
            # Remover obstáculos fora da tela e aumentar score
            for obstacle in obstacles:
                if obstacle.rect.x < -100:
                    obstacles.remove(obstacle)
                    score += 1
                    speed += 0.15
            
            # Aumentar dificuldade
            if score % 5 == 0 and score > 0:
                speed = 7 + (score // 5) * 1.2
        
        # Desenhar
        screen.fill(WHITE)
        
        # Desenhar nuvens decorativas
        for i in range(3):
            cloud_x = (i * 300 + int(score * 0.5)) % SCREEN_WIDTH
            pygame.draw.circle(screen, GRAY, (cloud_x, 50), 25)
            pygame.draw.circle(screen, GRAY, (cloud_x + 20, 40), 30)
            pygame.draw.circle(screen, GRAY, (cloud_x + 35, 50), 25)
        
        # Desenhar líneas do chão
        for i in range(0, SCREEN_WIDTH, 50):
            pygame.draw.line(screen, GRAY, (i, SCREEN_HEIGHT - 100), (i + 25, SCREEN_HEIGHT - 100), 2)
        pygame.draw.line(screen, GRAY, (0, SCREEN_HEIGHT - 100), (SCREEN_WIDTH, SCREEN_HEIGHT - 100), 3)
        
        if game_started:
            dinosaur.draw(screen)
            for obstacle in obstacles:
                obstacle.draw(screen)
            
            # Desenhar score
            score_text = font.render(f"Score: {score}", True, BLACK)
            screen.blit(score_text, (10, 10))
            
            # Desenhar velocidade
            speed_text = font.render(f"Speed: {speed:.1f}", True, BLACK)
            screen.blit(speed_text, (SCREEN_WIDTH - 200, 10))
            
            if game_over:
                game_over_text = big_font.render("GAME OVER!", True, RED)
                restart_text = font.render("Aperte ESPAÇO para recomeçar", True, BLACK)
                
                text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
                restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30))
                
                screen.blit(game_over_text, text_rect)
                screen.blit(restart_text, restart_rect)
        else:
            if not game_started:
                title_text = big_font.render("Dinossauro Runner", True, DARK_GREEN)
                start_text = font.render("Aperte ESPAÇO para começar", True, BLACK)
                info_text = font.render("Desvie dos cactus, pule sobre as árvores e plataformas!", True, BLACK)
                
                title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 80))
                start_rect = start_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
                info_rect = info_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60))
                
                screen.blit(title_text, title_rect)
                screen.blit(start_text, start_rect)
                screen.blit(info_text, info_rect)
        
        pygame.display.flip()
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
