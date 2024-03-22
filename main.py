from kivy.app import App
from kivy.uix.image import Image
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.uix.widget import Widget
from kivy.core.audio import SoundLoader
from kivy.properties import NumericProperty, ListProperty
from random import random

class Manage_All_Screens(ScreenManager):
    pass

class Menu_screen(Screen):
    def on_enter(self, *args):
        global triler_music
        triler_music.play()
    
    def music_player(self, music):
        music.play()

    def on_pre_leave(self, *args):
            triler_music.stop()

class Game_screen(Screen):
    obstacles = [] #Armazena os obstaculos postos na tela, para facilitar sua eliminacao
    score = NumericProperty(0)
    def on_pre_enter(self, *args):
        #antes de entrar deve#antes de entrar deve
        #zerrar a velocidade e a posicao do player
        self.ids.player.speed = 0
        self.ids.player.y = self.height/2
        self.score = 0

    def on_enter(self, *args):
        global background_music
        """
        este metodo ee executado depois de entrara na tela em causa
        """
        Clock.schedule_interval(self.update_player_position_y, 1/30)
        #Clock agenda a execucao do metodo update_player_position_y
        #por noos criado para ser chamado 30 vezes poe segundo ()1/20

        Clock.schedule_interval(self.putObstacle_on_screen, 1)
        #agenda execucao do adicionador de obstaculos na tela para 1 em 1 segundo
        background_music.loop = True # Para que a musica volte a tocar depois de terminar
        background_music.volume = 0.5
        background_music.play()
    
    def on_pre_leave(self, *args):
        background_music.stop()

    def update_player_position_y(self, *args):
        global beat_on_obstacle_sound, fly_music

        self.ids.player.speed += -self.height*3 * 1/30
            #actualiza a velocidade/speed do player
            #o numero self.height pusemos a negativo por que a gravidade ee para baixo
        self.ids.player.y += self.ids.player.speed * 1/30
        if self.ids.player.y < 0 or self.ids.player.y > self.height:
            self.gameOverProcess()
            #este 'if' trata da logica de queda ou subida total
            #do player
        elif self.playerCollided():
            #se entra nesta condicao ee porque detectamos uma colisao
            fly_music.stop() #temos que parar o som do voo quando o player bate no obstaculo
            beat_on_obstacle_sound.volume = 0.9
            beat_on_obstacle_sound.play()
            self.gameOverProcess()

    def putObstacle_on_screen(self, *args):

        gap = self.height * 0.3 #espaco entre o obstaculo de baixo e de cima
        
        low_obstacle_height = (self.height - gap) * random() #A altura aletoria do obstaculo de baixo
        obstacle_down = Obstacle(x = self.width, width =self.width*0.05, height = low_obstacle_height)
        obstacle_up = Obstacle(x = self.width, width =self.width*0.05, y = low_obstacle_height+gap, height = self.height-low_obstacle_height-gap)
        #Obstacle ee uma classe que herda de widget para desenhar os obstaculos
        #aqui ee instacada esta classe para ser adicionado na tela o obstaculo
        self.add_widget(obstacle_down, 3)
        self.add_widget(obstacle_up, 3)
        self.obstacles.append(obstacle_down)
        self.obstacles.append(obstacle_up)

    def gameOverProcess(self, *args):
        App.get_running_app().root.current = "gameOverScreen"
        Clock.unschedule(self.update_player_position_y, 1/30)
        #Usamos o Clock.unschedule para desagendar a
        #chamada do metodo actualizador da gravidade
        #pois, quando estamos na tela do game over, 
        #a gravidade aindfa fica actuando.
        Clock.unschedule(self.putObstacle_on_screen, 1)
        for obst in self.obstacles:
            obst.anime_obstacle.cancel(obst)
            self.remove_widget(obst)
            self.obstacles = []

    def collision_detection(self, widgetA, widgetB):
        """
        Este ee o algoritmo Axis Aligned Bounding Boxes (AABB)
        para deteccao de colisao entre dois objectos.
        """
        if widgetB.x <= widgetA.x + widgetA.width and \
          widgetB.x + widgetB.width >= widgetA.x and \
          widgetB.y <= widgetA.y + widgetA.height and \
          widgetB.y + widgetB.height >= widgetA.y:
            return True
        return False
    
    def playerCollided(self):
        collided = False
        for obstacle in self.obstacles:
            if self.collision_detection(self.ids.player, obstacle):
                collided = True
                break
        return collided
    
    def on_touch_down(self, *args):
        global fly_music
        self.ids.player.speed = self.height * 0.7 # muda o sentido da queda livre, se o 0,7 aumentar, maior sera a velocidade
        fly_music.play() #play the bird flying sound

class Obstacle(Widget):
    obstacleColor = ListProperty([0.3, 0.2, 0.2, 1])
    gameScreen = None
    pontued = False
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.anime_obstacle = Animation(x = -self.width, duration = 3)
        self.anime_obstacle.bind(on_complete = self.vanishObstacle)
        self.anime_obstacle.start(self)
        self.gameScreen = App.get_running_app().root.get_screen("stage")
    

    def on_x(self, *args):
        """
        on_x ee um metodo padrao do widget "Widget" que ee 
        chamado sempre que o parametro x muda. entao vamos
        saber se o obstaculo ultrapassou o player
        a esquerda para adicionarmos uma pontuacao no jogo
        """
        if self.gameScreen:
            if self.x < self.gameScreen.ids.player.x and not self.pontued:
                self.gameScreen.score += 0.5
                self.pontued = True

    def vanishObstacle(self, *args):
        self.gameScreen.remove_widget(self)
        #depois que o obstaculo atravessa a tela (no x)
        #ee eliminado dela
        self.gameScreen.obstacles.remove(self)
        #depois que o obstaculo atravessa a tela (no x)
        #ee eliminado da lista de obstaculos da tela

class Game_over_screen(Screen):
    pass

class Player(Image):
    speed = NumericProperty(0)



class saveBird(App):
    """def build(self):
        player = Image(source="players/player1.png")
        layout = FloatLayout()
        layout.add_widget(player)

        Quando nao se deinfine o metodo build 
        o python procura no arquivo .kv a classe que nao
        possui o sinais <> e retorna essa mesma
        return layout"""
    pass

#Nas linhas abaixo carregamos todos os efeitos sonoros do jogo
triler_music = SoundLoader.load("sounds/[MENU-SOUND]-birds-chirping-near-the-river.wav")
fly_music = SoundLoader.load("sounds/[FLY1]-basketball-ball-hitting-the-net.wav")
beat_on_obstacle_sound = SoundLoader.load("sounds/[BEAT1]-hitting-golf-ball.wav")
background_music = SoundLoader.load("sounds/[EDIT]-game-music-loop.wav")

saveBird().run()