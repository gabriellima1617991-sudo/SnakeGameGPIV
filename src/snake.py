import pygame
import random
import sys
import os

print(os.getcwd())

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ARQ_RECORDE = os.path.join(BASE_DIR, "data", "recorde.txt")
ARQ_RANKING = os.path.join(BASE_DIR, "data", "ranking.txt")

# ─────────────────────────────────────────
#  CONFIGURAÇÕES GERAIS
# ─────────────────────────────────────────
LARGURA = 600
ALTURA = 600
TAMANHO_CELULA = 30
COLUNAS = LARGURA // TAMANHO_CELULA
LINHAS = ALTURA // TAMANHO_CELULA
FPS = 10

# Paleta de cores
PRETO      = (0,   0,   0)
BRANCO     = (255, 255, 255)
VERDE      = (50,  205,  50)
VERDE_ESCURO = (34, 139, 34)
VERMELHO   = (220,  50,  50)
CINZA      = (40,   40,  40)
CINZA_CLARO = (80,  80,  80)
AMARELO    = (255, 215,   0)

# ─────────────────────────────────────────
#  FUNÇÕES AUXILIARES
# ─────────────────────────────────────────

def desenhar_grade(tela):
    """Desenha a grade de fundo."""
    for x in range(0, LARGURA, TAMANHO_CELULA):
        pygame.draw.line(tela, CINZA_CLARO, (x, 0), (x, ALTURA))
    for y in range(0, ALTURA, TAMANHO_CELULA):
        pygame.draw.line(tela, CINZA_CLARO, (0, y), (LARGURA, y))


def desenhar_cobra(tela, cobra):
    """Desenha cada segmento da cobra."""
    for i, (cx, cy) in enumerate(cobra):
        cor = VERDE_ESCURO if i == 0 else VERDE
        rect = pygame.Rect(cx * TAMANHO_CELULA + 2,
                           cy * TAMANHO_CELULA + 2,
                           TAMANHO_CELULA - 4,
                           TAMANHO_CELULA - 4)
        pygame.draw.rect(tela, cor, rect, border_radius=6)


def desenhar_comida(tela, comida):
    """Desenha a comida como um círculo vermelho."""
    cx, cy = comida
    centro = (cx * TAMANHO_CELULA + TAMANHO_CELULA // 2,
              cy * TAMANHO_CELULA + TAMANHO_CELULA // 2)
    pygame.draw.circle(tela, VERMELHO, centro, TAMANHO_CELULA // 2 - 4)
    pygame.draw.circle(tela, AMARELO,  centro, TAMANHO_CELULA // 4 - 2)


def gerar_comida(cobra):
    """Gera uma posição aleatória para a comida que não coincida com a cobra."""
    while True:
        pos = (random.randint(0, COLUNAS - 1), random.randint(0, LINHAS - 1))
        if pos not in cobra:
            return pos


def mostrar_texto_centralizado(tela, texto, fonte, cor, y):
    """Renderiza texto centralizado horizontalmente."""
    surf = fonte.render(texto, True, cor)
    rect = surf.get_rect(center=(LARGURA // 2, y))
    tela.blit(surf, rect)

def carregar_recorde():
    try:
        with open(ARQ_RECORDE, "r") as arquivo:
            return int(arquivo.read())
    except:
        return 0


def salvar_recorde(pontuacao):
    with open(ARQ_RECORDE, "w") as arquivo:
        arquivo.write(str(pontuacao))


def carregar_ranking():
    try:
        with open(ARQ_RANKING, "r") as arquivo:
            return [int(linha.strip()) for linha in arquivo.readlines()]
    except:
        return []


def salvar_ranking(pontuacao):
    ranking = carregar_ranking()

    ranking.append(pontuacao)

    ranking.sort(reverse=True)

    ranking = ranking[:5]

    with open(ARQ_RANKING, "w") as arquivo: 
        for score in ranking:
            arquivo.write(f"{score}\n")

def tela_inicial(tela, relogio, fonte_grande, fonte_media):
    """Exibe a tela de início e aguarda o jogador pressionar ENTER."""
    while True:
        tela.fill(CINZA)
        desenhar_grade(tela)
        mostrar_texto_centralizado(tela, "🐍  SNAKE",        fonte_grande, VERDE,  180)
        mostrar_texto_centralizado(tela, "Use as setas para mover", fonte_media, BRANCO, 290)
        mostrar_texto_centralizado(tela, "Pressione ENTER para jogar", fonte_media, AMARELO, 340)
        pygame.display.flip()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_RETURN:
                    return


def tela_game_over(tela, relogio, fonte_grande, fonte_media, pontuacao, tempo):
    """Exibe a tela de Game Over e retorna True para reiniciar ou False para sair."""
    while True:
        tela.fill(CINZA)
        desenhar_grade(tela)
        mostrar_texto_centralizado(tela, "GAME OVER",         fonte_grande, VERMELHO, 200)
        mostrar_texto_centralizado(tela, f"Pontuação: {pontuacao}", fonte_media, AMARELO, 280)
        mostrar_texto_centralizado(tela, "ENTER — jogar de novo", fonte_media, VERDE,   340)
        mostrar_texto_centralizado(tela, "ESC   — sair",          fonte_media, BRANCO,  380)
        pygame.display.flip()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_RETURN:
                    return True
                if evento.key == pygame.K_ESCAPE:
                    return False


# ─────────────────────────────────────────
#  LOOP PRINCIPAL DO JOGO
# ─────────────────────────────────────────

def jogar(tela, relogio, fonte_media):
    """Executa uma partida completa. Retorna a pontuação final."""

    # Estado inicial
    cobra     = [(COLUNAS // 2, LINHAS // 2)]
    direcao   = (1, 0)          # começa movendo para a direita
    proxima   = direcao
    comida    = gerar_comida(cobra)
    pontuacao = 0
    tempo_inicio = pygame.time.get_ticks()

    while True:
        relogio.tick(FPS)

        # ── Eventos ──────────────────────────────
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_UP    and direcao != (0, 1):
                    proxima = (0, -1)
                elif evento.key == pygame.K_DOWN  and direcao != (0, -1):
                    proxima = (0, 1)
                elif evento.key == pygame.K_LEFT  and direcao != (1, 0):
                    proxima = (-1, 0)
                elif evento.key == pygame.K_RIGHT and direcao != (-1, 0):
                    proxima = (1, 0)

        # ── Atualização ──────────────────────────
        direcao  = proxima
        cabeca   = (cobra[0][0] + direcao[0],
                    cobra[0][1] + direcao[1])

        # Colisão com as bordas
        
        if not (0 <= cabeca[0] < COLUNAS and 0 <= cabeca[1] < LINHAS):

            recorde = carregar_recorde()

            if pontuacao > recorde:
                salvar_recorde(pontuacao)

            salvar_ranking(pontuacao)

            tempo_atual = (pygame.time.get_ticks() - tempo_inicio) // 1000

            return pontuacao, tempo_atual

        cobra.insert(0, cabeca)
        if cabeca in cobra[1:]:

            recorde = carregar_recorde()

            if pontuacao > recorde:
                salvar_recorde(pontuacao)

            salvar_ranking(pontuacao)

            tempo_atual = (pygame.time.get_ticks() - tempo_inicio) // 1000

            return pontuacao, tempo_atual   


        # Verificar se comeu a comida
        if cabeca == comida:
            pontuacao += 10
            comida = gerar_comida(cobra)
        else:
            cobra.pop()

        # ── Renderização ─────────────────────────
        tela.fill(CINZA)
        desenhar_grade(tela)
        desenhar_comida(tela, comida)
        desenhar_cobra(tela, cobra)

        # HUD — pontuação
        texto_pont = fonte_media.render(f"Pontos: {pontuacao}", True, BRANCO)
        tela.blit(texto_pont, (10, 10))

        tempo_atual = (pygame.time.get_ticks() - tempo_inicio) // 1000

        texto_tempo = fonte_media.render(
        f"Tempo: {tempo_atual}s",
        True,
        BRANCO
    )

        tela.blit(texto_tempo, (450, 10))

        pygame.display.flip()


# ─────────────────────────────────────────
#  INICIALIZAÇÃO
# ─────────────────────────────────────────

def main():
    pygame.init()
    tela   = pygame.display.set_mode((LARGURA, ALTURA))
    pygame.display.set_caption("Snake — Python & Pygame")
    relogio = pygame.time.Clock()

    fonte_grande = pygame.font.SysFont("Arial", 56, bold=True)
    fonte_media  = pygame.font.SysFont("Arial", 28)

    tela_inicial(tela, relogio, fonte_grande, fonte_media)

    while True:
        pontuacao, tempo = jogar(tela, relogio, fonte_media)
        continuar = tela_game_over(tela, relogio, fonte_grande, fonte_media, pontuacao, tempo)
        if not continuar:
            break

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()