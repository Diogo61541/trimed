import pygame
import random
import json
from enum import Enum

# ===== CONFIGURAÇÃO =====
WIDTH, HEIGHT = 1200, 800
TILE_SIZE = 40
FPS = 60

# Cores
VERDE = (34, 177, 76)
VERDE_ESCURO = (20, 100, 50)
MARROM = (180, 100, 30)
CINZA = (150, 150, 150)
VERMELHO = (255, 50, 50)
AZUL = (50, 100, 200)
BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)
OURO = (255, 215, 0)
AGUA = (100, 150, 200)

# Tipos de Tile
class TileType(Enum):
    GRASS = 0
    WATER = 1
    ROCK = 2
    TREE = 3
    LAVA = 4
    HOUSE = 5

# Tipos de Creature
class CreatureType(Enum):
    PLAYER = 0
    GOBLIN = 1
    ORC = 2
    SPIDER = 3

# ===== CLASSE DE ITEM =====
class Item:
    def __init__(self, name, item_type, damage=0, defense=0, spell_power=0):
        self.name = name
        self.item_type = item_type  # 'weapon', 'armor', 'potion', 'spell'
        self.damage = damage
        self.defense = defense
        self.spell_power = spell_power

# ===== CLASSE CREATURE =====
class Creature:
    def __init__(self, name, x, y, max_hp, level=1, creature_type=CreatureType.PLAYER):
        self.name = name
        self.x = x
        self.y = y
        self.max_hp = max_hp
        self.hp = max_hp
        self.level = level
        self.exp = 0
        self.creature_type = creature_type
        self.inventory = []
        self.equipment = {}
        self.direction = 'down'
        
        # Stats
        self.mana = 100 + (level * 10)
        self.max_mana = self.mana
        self.stamina = 100
        self.max_stamina = 100
        
    def take_damage(self, damage):
        self.hp = max(0, self.hp - damage)
        return self.hp <= 0  # Retorna True se morreu
    
    def heal(self, amount):
        self.hp = min(self.max_hp, self.hp + amount)
    
    def gain_exp(self, amount):
        self.exp += amount
        if self.exp >= (self.level * 100):
            self.level_up()
    
    def level_up(self):
        self.level += 1
        self.max_hp += 10
        self.hp = self.max_hp
        self.max_mana += 10
        self.mana = self.max_mana

# ===== CLASSE DO MAPA =====
class GameMap:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.tiles = [[TileType.GRASS for _ in range(width)] for _ in range(height)]
        self.creatures = []
        self.items = {}
        self.spawn_points = []
        
        self.generate_map()
    
    def generate_map(self):
        # Gerar água
        for y in range(5):
            for x in range(self.width):
                self.tiles[y][x] = TileType.WATER
        
        # Gerar árvores
        for _ in range(15):
            x = random.randint(0, self.width - 1)
            y = random.randint(5, self.height - 1)
            self.tiles[y][x] = TileType.TREE
        
        # Gerar rochas
        for _ in range(10):
            x = random.randint(0, self.width - 1)
            y = random.randint(5, self.height - 1)
            self.tiles[y][x] = TileType.ROCK
        
        # Gerar lava
        for y in range(self.height - 3, self.height):
            for x in range(self.width):
                self.tiles[y][x] = TileType.LAVA
        
        # Spawn points
        for i in range(5):
            x = random.randint(5, self.width - 5)
            y = random.randint(10, self.height - 10)
            self.spawn_points.append((x, y))
    
    def is_walkable(self, x, y):
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return False
        tile = self.tiles[y][x]
        return tile in [TileType.GRASS, TileType.HOUSE]
    
    def add_creature(self, creature):
        self.creatures.append(creature)
    
    def remove_creature(self, creature):
        if creature in self.creatures:
            self.creatures.remove(creature)
    
    def is_creature_at(self, x, y):
        for creature in self.creatures:
            if creature.x == x and creature.y == y:
                return creature
        return None

# ===== CLASSE DO JOGO =====
class TibiaGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Open Tibia - Python Edition")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)
        self.font_small = pygame.font.Font(None, 16)
        
        # Criar mapa
        self.map = GameMap(30, 20)
        
        # Criar player
        spawn = random.choice(self.map.spawn_points)
        self.player = Creature("Player", spawn[0], spawn[1], max_hp=100, level=1)
        self.map.add_creature(self.player)
        
        # Criar inimigos
        self.spawn_enemies()
        
        # Variáveis de jogo
        self.running = True
        self.selected_hotkey = None
        self.combat_log = []
        
        # Equipamento básico
        self.player.equipment['weapon'] = Item("Sword", "weapon", damage=5)
        self.player.equipment['armor'] = Item("Leather Armor", "armor", defense=3)
    
    def spawn_enemies(self):
        enemies_data = [
            ("Goblin", CreatureType.GOBLIN, 20, 1),
            ("Orc", CreatureType.ORC, 40, 3),
            ("Spider", CreatureType.SPIDER, 15, 1),
        ]
        
        for _ in range(8):
            data = random.choice(enemies_data)
            x = random.randint(5, self.map.width - 5)
            y = random.randint(10, self.map.height - 10)
            
            if self.map.is_walkable(x, y) and not self.map.is_creature_at(x, y):
                enemy = Creature(data[0], x, y, max_hp=data[2], level=data[3], creature_type=data[1])
                self.map.add_creature(enemy)
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.move_player(0, -1)
                elif event.key == pygame.K_DOWN:
                    self.move_player(0, 1)
                elif event.key == pygame.K_LEFT:
                    self.move_player(-1, 0)
                elif event.key == pygame.K_RIGHT:
                    self.move_player(1, 0)
                
                # Atacar
                elif event.key == pygame.K_SPACE:
                    self.attack_nearby()
                
                # Curar (H)
                elif event.key == pygame.K_h and self.player.hp < self.player.max_hp:
                    heal_amount = 30
                    self.player.heal(heal_amount)
                    self.add_combat_log(f"You healed for {heal_amount} HP")
                
                # Sair
                elif event.key == pygame.K_ESCAPE:
                    self.running = False
    
    def move_player(self, dx, dy):
        new_x = self.player.x + dx
        new_y = self.player.y + dy
        
        if self.map.is_walkable(new_x, new_y):
            creature = self.map.is_creature_at(new_x, new_y)
            if creature and creature != self.player:
                # Não pode andar, está ocupado
                return
            
            self.player.x = new_x
            self.player.y = new_y
    
    def attack_nearby(self):
        # Verificar inimigos adjacentes
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                
                target_x = self.player.x + dx
                target_y = self.player.y + dy
                target = self.map.is_creature_at(target_x, target_y)
                
                if target and target != self.player:
                    damage = random.randint(5, 15) + self.player.equipment.get('weapon', Item("Fist", "weapon", damage=1)).damage
                    target.take_damage(damage)
                    self.add_combat_log(f"You hit {target.name} for {damage} damage!")
                    
                    # Inimigo contra-ataca
                    if target.hp > 0:
                        enemy_damage = random.randint(2, 8)
                        self.player.take_damage(enemy_damage)
                        self.add_combat_log(f"{target.name} hit you for {enemy_damage} damage!")
                    else:
                        self.add_combat_log(f"{target.name} has been defeated!")
                        self.player.gain_exp(target.level * 10)
                        self.map.remove_creature(target)
    
    def add_combat_log(self, message):
        self.combat_log.append(message)
        if len(self.combat_log) > 10:
            self.combat_log.pop(0)
    
    def update(self):
        # IA dos inimigos
        for creature in self.map.creatures:
            if creature == self.player:
                continue
            
            # Verificar se player está perto
            dist = abs(creature.x - self.player.x) + abs(creature.y - self.player.y)
            
            if dist <= 3:
                # Mover em direção ao player
                if creature.x < self.player.x:
                    new_x = creature.x + 1
                elif creature.x > self.player.x:
                    new_x = creature.x - 1
                else:
                    new_x = creature.x
                
                if creature.y < self.player.y:
                    new_y = creature.y + 1
                elif creature.y > self.player.y:
                    new_y = creature.y - 1
                else:
                    new_y = creature.y
                
                if self.map.is_walkable(new_x, new_y) and not self.map.is_creature_at(new_x, new_y):
                    creature.x = new_x
                    creature.y = new_y
                
                # Atacar se adjacente
                if dist <= 1:
                    damage = random.randint(3, 10)
                    self.player.take_damage(damage)
                    self.add_combat_log(f"{creature.name} hit you for {damage} damage!")
    
    def draw(self):
        self.screen.fill(AZUL)
        
        # Calcular viewport
        viewport_x = max(0, min(self.player.x - 7, self.map.width - 15))
        viewport_y = max(0, min(self.player.y - 5, self.map.height - 10))
        
        # Desenhar tiles
        for y in range(10):
            for x in range(15):
                map_x = viewport_x + x
                map_y = viewport_y + y
                
                if map_x < self.map.width and map_y < self.map.height:
                    tile = self.map.tiles[map_y][map_x]
                    rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                    
                    if tile == TileType.GRASS:
                        pygame.draw.rect(self.screen, VERDE, rect)
                    elif tile == TileType.WATER:
                        pygame.draw.rect(self.screen, AGUA, rect)
                    elif tile == TileType.TREE:
                        pygame.draw.rect(self.screen, VERDE_ESCURO, rect)
                    elif tile == TileType.ROCK:
                        pygame.draw.rect(self.screen, CINZA, rect)
                    elif tile == TileType.LAVA:
                        pygame.draw.rect(self.screen, VERMELHO, rect)
                    
                    pygame.draw.rect(self.screen, PRETO, rect, 1)
        
        # Desenhar creatures
        for creature in self.map.creatures:
            screen_x = (creature.x - viewport_x) * TILE_SIZE
            screen_y = (creature.y - viewport_y) * TILE_SIZE
            
            if 0 <= screen_x < WIDTH and 0 <= screen_y < HEIGHT:
                if creature == self.player:
                    color = OURO
                elif creature.creature_type == CreatureType.GOBLIN:
                    color = VERDE
                elif creature.creature_type == CreatureType.ORC:
                    color = VERMELHO
                elif creature.creature_type == CreatureType.SPIDER:
                    color = CINZA
                else:
                    color = BRANCO
                
                pygame.draw.circle(self.screen, color, (screen_x + TILE_SIZE // 2, screen_y + TILE_SIZE // 2), 15)
                
                # HP bar
                if creature != self.player:
                    hp_ratio = creature.hp / creature.max_hp
                    pygame.draw.rect(self.screen, VERMELHO, (screen_x, screen_y - 5, TILE_SIZE, 3))
                    pygame.draw.rect(self.screen, VERDE, (screen_x, screen_y - 5, TILE_SIZE * hp_ratio, 3))
        
        # UI
        ui_x = 15 * TILE_SIZE + 20
        ui_y = 20
        
        # Player info
        player_text = [
            f"Player: {self.player.name}",
            f"Level: {self.player.level}",
            f"HP: {self.player.hp}/{self.player.max_hp}",
            f"Mana: {self.player.mana}/{self.player.max_mana}",
            f"EXP: {self.player.exp}",
        ]
        
        for i, text in enumerate(player_text):
            surf = self.font.render(text, True, BRANCO)
            self.screen.blit(surf, (ui_x, ui_y + i * 25))
        
        # Combat log
        log_y = ui_y + 160
        log_title = self.font.render("Combat Log:", True, OURO)
        self.screen.blit(log_title, (ui_x, log_y))
        
        for i, log in enumerate(self.combat_log[-5:]):
            surf = self.font_small.render(log, True, BRANCO)
            self.screen.blit(surf, (ui_x, log_y + 30 + i * 20))
        
        # Controles
        controls = [
            "Arrows: Move",
            "Space: Attack",
            "H: Heal",
            "ESC: Quit"
        ]
        for i, control in enumerate(controls):
            surf = self.font_small.render(control, True, BRANCO)
            self.screen.blit(surf, (20, HEIGHT - 100 + i * 20))
        
        pygame.display.flip()
    
    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()

# ===== EXECUTAR JOGO =====
game = TibiaGame()
game.run()
