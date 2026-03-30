from ursina import *
from random import randint, choice, random
from math import sin, cos, radians
import json
import os

# ===== INICIALIZAÇÃO =====
app = Ursina(title="Dinossauro 3D Runner", fullscreen=False, vsync=False)
window.size = (1400, 800)
window.color = rgb(135, 206, 235)

# Configuração de câmera
camera.position = (0, 8, -20)
camera.rotation_x = 25
camera.fov = 60

# ===== CORES =====
VERDE = rgb(34, 177, 76)
VERDE_ESCURO = rgb(20, 100, 50)
MARROM = rgb(180, 100, 30)
CINZA = rgb(150, 150, 150)
VERMELHO = rgb(255, 50, 50)
OURO = rgb(255, 215, 0)
CIANO = rgb(0, 255, 255)

# ===== SISTEMA DE RANKING =====
RANKING_FILE = "ranking_dino.json"

def carregar_ranking():
    if os.path.exists(RANKING_FILE):
        try:
            with open(RANKING_FILE, 'r') as f:
                return json.load(f)
        except:
            return []
    return []

def salvar_ranking(pontos, combo):
    ranking = carregar_ranking()
    ranking.append({"pontos": pontos, "combo": combo})
    ranking.sort(key=lambda x: x["pontos"], reverse=True)
    ranking = ranking[:5]
    with open(RANKING_FILE, 'w') as f:
        json.dump(ranking, f)

# ===== CLASSE DO DINOSSAURO =====
class Dinossauro(Entity):
    def __init__(self):
        super().__init__()
        self.corpo = Entity(model='cube', position=(0, 0, 0), scale=(1.2, 0.8, 2), color=VERDE, parent=self)
        self.pescoco = Entity(model='cube', position=(0, 0.6, -0.8), scale=(0.6, 0.6, 0.8), color=VERDE, parent=self)
        self.cabeca = Entity(model='cube', position=(0, 1.0, -1.4), scale=(0.6, 0.7, 0.7), color=VERDE_ESCURO, parent=self)
        Entity(model='sphere', position=(0.2, 1.2, -1.8), scale=(0.15, 0.15, 0.15), color=color.white, parent=self)
        Entity(model='sphere', position=(0.2, 1.2, -1.85), scale=(0.08, 0.08, 0.08), color=color.black, parent=self)
        
        self.perna_tr = Entity(model='cube', position=(0.4, -0.4, 0.5), scale=(0.3, 1.0, 0.4), color=VERDE_ESCURO, parent=self)
        self.perna_tl = Entity(model='cube', position=(-0.4, -0.4, 0.5), scale=(0.3, 1.0, 0.4), color=VERDE_ESCURO, parent=self)
        self.perna_fr = Entity(model='cube', position=(0.4, -0.4, -0.8), scale=(0.3, 1.0, 0.4), color=VERDE_ESCURO, parent=self)
        self.perna_fl = Entity(model='cube', position=(-0.4, -0.4, -0.8), scale=(0.3, 1.0, 0.4), color=VERDE_ESCURO, parent=self)
        self.cauda = Entity(model='cube', position=(0, 0.2, 1.3), scale=(0.3, 0.3, 1.5), color=VERDE, parent=self)
        
        self.escudo = Entity(model='sphere', position=(0, 0, 0), scale=(1.8, 1.8, 1.8), color=CIANO, opacity=0.2, parent=self, wireframe=True)
        self.escudo.visible = False
        
        self.position = (0, 0, 0)
        self.velocidade_y = 0
        self.saltando = False
        self.potencia_salto = 0.5
        self.tempo_anim = 0
        self.tem_escudo = False
        self.tempo_escudo = 0
        self.velocidade_extra = 0
        self.tempo_velocidade = 0
        self.dobro_pontos = False
        self.tempo_dobro = 0

    def saltar(self):
        if not self.saltando:
            self.velocidade_y = self.potencia_salto
            self.saltando = True

    def atualizar_physics(self, dt):
        self.velocidade_y -= 0.025
        self.y += self.velocidade_y
        
        if self.y <= 0:
            self.y = 0
            self.velocidade_y = 0
            self.saltando = False
        
        self.tempo_anim += dt
        if not self.saltando:
            offset = sin(self.tempo_anim * 8) * 0.15
            self.perna_fr.y = -0.4 + offset
            self.perna_fl.y = -0.4 - offset
            self.perna_tr.y = -0.4 - offset
            self.perna_tl.y = -0.4 + offset
        
        self.cauda.rotation_z = sin(self.tempo_anim * 6) * 15 if not self.saltando else -20
        
        if self.tem_escudo:
            self.tempo_escudo -= dt
            if self.tempo_escudo <= 0:
                self.tem_escudo = False
                self.escudo.visible = False
        
        if self.velocidade_extra > 0:
            self.tempo_velocidade -= dt
            if self.tempo_velocidade <= 0:
                self.velocidade_extra = 0
        
        if self.dobro_pontos:
            self.tempo_dobro -= dt
            if self.tempo_dobro <= 0:
                self.dobro_pontos = False

    def ativar_escudo(self):
        self.tem_escudo = True
        self.tempo_escudo = 5
        self.escudo.visible = True

    def ativar_velocidade(self):
        self.velocidade_extra = 3
        self.tempo_velocidade = 4

    def ativar_dobro_pontos(self):
        self.dobro_pontos = True
        self.tempo_dobro = 6

# ===== CLASSE DO OBSTÁCULO =====
class Obstaculo(Entity):
    def __init__(self, tipo="cacto"):
        super().__init__()
        self.tipo = tipo
        self.position = (0, 0, 25)
        self.velocidade = 0.6
        self.passou = False
        
        if tipo == "cacto":
            Entity(model='cube', position=(0, 0.5, 0), scale=(0.5, 1.2, 0.5), color=VERDE, parent=self)
            for i in range(4):
                ang = (i * 90)
                x = cos(radians(ang)) * 0.4
                z = sin(radians(ang)) * 0.4
                Entity(model='sphere', position=(x, 0.6, z), scale=(0.2, 0.3, 0.2), color=VERMELHO, parent=self)
        elif tipo == "rocha":
            Entity(model='sphere', position=(0, 0.4, 0), scale=(0.8, 0.8, 0.8), color=CINZA, parent=self)
        elif tipo == "arvore":
            Entity(model='cube', position=(0, 0.8, 0), scale=(0.5, 1.5, 0.5), color=MARROM, parent=self)
            Entity(model='sphere', position=(0, 2.0, 0), scale=(1.5, 1.5, 1.5), color=VERDE, parent=self)
        elif tipo == "parede":
            Entity(model='cube', position=(0, 0.7, 0), scale=(2.0, 1.4, 0.4), color=CINZA, parent=self)

# ===== CLASSE POWER-UP =====
class PowerUp(Entity):
    def __init__(self, tipo="escudo"):
        super().__init__()
        self.tipo = tipo
        self.position = (0, 1.5, 25)
        self.velocidade = 0.6
        self.coletado = False
        
        if tipo == "escudo":
            Entity(model='sphere', position=(0, 0, 0), scale=(0.6, 0.6, 0.6), color=CIANO, parent=self)
        elif tipo == "velocidade":
            Entity(model='cube', position=(0, 0, 0), scale=(0.5, 0.5, 0.5), color=OURO, parent=self)
        elif tipo == "dobro":
            Entity(model='sphere', position=(0, 0, 0), scale=(0.4, 0.4, 0.4), color=VERMELHO, parent=self)
            Entity(model='sphere', position=(0, 0, 0), scale=(0.5, 0.5, 0.5), color=VERMELHO, opacity=0.3, parent=self)

# ===== VARIÁVEIS DO JOGO =====
dinossauro = Dinossauro()
obstaculos = []
powerups = []
pontos = 0
combo = 0
velocidade_base = 0.5
nivel = 1
game_over = False
tempo_spawn = 2
tempo_powerup = 0

# ===== UI =====
texto_pontos = Text(text='Pontos: 0', position=(-0.9, 0.45), scale=2, color=color.white)
texto_combo = Text(text='', position=(-0.9, 0.35), scale=1.5, color=OURO)
texto_nivel = Text(text='Nível: 1', position=(0.6, 0.45), scale=1.5, color=color.white)
texto_game_over = Text(text='', position=(0, 0.3), scale=2.5, color=VERMELHO)
instrucoes = Text(text='ESPAÇO = Pular | ESC = Sair', position=(0, -0.45), scale=1.2, color=color.white)

luz = DirectionalLight(direction=(1, 1, 1), color=color.white, intensity=1.5)
ambient = AmbientLight(intensity=0.7)

def atualizar_ui():
    global pontos, combo, nivel
    texto_pontos.text = f'Pontos: {int(pontos)}'
    if combo > 1:
        texto_combo.text = f'Combo: {combo}x'
    else:
        texto_combo.text = ''
    nivel = 1 + (int(pontos) // 50)
    texto_nivel.text = f'Nível: {nivel}'

def criar_obstaculo():
    global tempo_spawn, velocidade_base, nivel
    tempo_spawn -= time.dt
    spawn_rate = max(1.2, 3 - (nivel * 0.15))
    if tempo_spawn <= 0:
        tipos = ["cacto", "rocha", "arvore"]
        if nivel >= 3:
            tipos.append("parede")
        tipo = choice(tipos)
        obst = Obstaculo(tipo)
        obst.velocidade = velocidade_base + (nivel * 0.1)
        obstaculos.append(obst)
        tempo_spawn = spawn_rate

def criar_powerup():
    global tempo_powerup
    tempo_powerup -= time.dt
    if tempo_powerup <= 0 and random() < 0.08:
        tipo = choice(["escudo", "velocidade", "dobro"])
        pw = PowerUp(tipo)
        pw.velocidade = velocidade_base
        powerups.append(pw)
        tempo_powerup = 5

def verificar_colisoes():
    global pontos, combo, game_over
    for obst in obstaculos[:]:
        dist = distance(dinossauro.position, obst.position)
        if dist < 1.5:
            if dinossauro.tem_escudo:
                dinossauro.tem_escudo = False
                dinossauro.escudo.visible = False
                obstaculos.remove(obst)
            else:
                game_over = True
                salvar_ranking(int(pontos), combo)
                return
        if obst.position.z < dinossauro.position.z and not obst.passou:
            obst.passou = True
            aproveita = 1 if not dinossauro.dobro_pontos else 2
            pontos += aproveita
            combo += 1
            velocidade_base += 0.02

def verificar_powerups():
    for pw in powerups[:]:
        dist = distance(dinossauro.position, pw.position)
        if dist < 1.2:
            if pw.tipo == "escudo":
                dinossauro.ativar_escudo()
            elif pw.tipo == "velocidade":
                dinossauro.ativar_velocidade()
            elif pw.tipo == "dobro":
                dinossauro.ativar_dobro_pontos()
            powerups.remove(pw)
            destroy(pw)

def limpar_fora_tela():
    for obst in obstaculos[:]:
        if obst.position.z < -10:
            obstaculos.remove(obst)
            destroy(obst)
    for pw in powerups[:]:
        if pw.position.z < -10:
            powerups.remove(pw)
            destroy(pw)

def mostrar_ranking():
    ranking = carregar_ranking()
    texto = "TOP 5:\n"
    for i, entrada in enumerate(ranking[:5]):
        texto += f"{i+1}. {entrada['pontos']} pts\n"
    return texto

def resetar_jogo():
    global dinossauro, obstaculos, powerups, pontos, combo, game_over, tempo_spawn, velocidade_base
    game_over = False
    pontos = 0
    combo = 0
    velocidade_base = 0.5
    tempo_spawn = 2
    dinossauro.position = (0, 0, 0)
    dinossauro.velocidade_y = 0
    dinossauro.saltando = False
    dinossauro.tem_escudo = False
    dinossauro.escudo.visible = False
    for obst in obstaculos:
        destroy(obst)
    obstaculos = []
    for pw in powerups:
        destroy(pw)
    powerups = []
    texto_game_over.text = ''
    instrucoes.visible = True

def update():
    global game_over, dinossauro, tempo_spawn, obstaculos, powerups, pontos, combo, velocidade_base, tempo_powerup
    if game_over:
        return
    if held_keys['space']:
        dinossauro.saltar()
    dinossauro.atualizar_physics(time.dt)
    camera.x = dinossauro.x
    camera.y = dinossauro.y + 8
    camera.z = dinossauro.z - 20
    criar_obstaculo()
    criar_powerup()
    for obst in obstaculos:
        obst.position -= (Vec3(0, 0, obst.velocidade) + (dinossauro.velocidade_extra * Vec3(0, 0, 0.2)))
    for pw in powerups:
        pw.position -= Vec3(0, 0, pw.velocidade)
        pw.rotation_y += 100 * time.dt
    verificar_colisoes()
    verificar_powerups()
    limpar_fora_tela()
    if combo > 0:
        velocidade_base = 0.5 + (combo * 0.008)
    atualizar_ui()

def input_handle(key):
    global game_over
    if key == 'space' and game_over:
        resetar_jogo()
    if key == 'esc':
        application.quit()

overlay = Entity(model='quad', scale=(2, 2), color=(0, 0, 0, 0.7), z=-5)
overlay.visible = False

def always():
    global game_over
    if game_over:
        overlay.visible = True
        instrucoes.visible = False
        ranking_text = mostrar_ranking()
        texto_game_over.text = f"GAME OVER!\nPontos: {int(pontos)}\nCombo: {combo}\n\nEspaço para jogar novamente\n\n{ranking_text}"
    else:
        overlay.visible = False

app.run()
