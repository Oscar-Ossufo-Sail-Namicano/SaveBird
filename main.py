import kivy
kivy.require('2.3.0')

from kivy.app import App
from kivy.uix.image import Image
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.uix.widget import Widget
from kivy.core.audio import SoundLoader
from kivy.properties import NumericProperty, ListProperty, ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.behaviors.button import ButtonBehavior
from kivy.graphics import Color, Ellipse, Rectangle
from kivy.core.window import Window
import webbrowser
from random import random
import json
from kivy.uix.popup import Popup

class Manage_All_Screens(ScreenManager):
    pass

class CustomizedButton(ButtonBehavior, Label):
    button_color1 = ListProperty([0.1,0.5,0.7,1])
    button_color2 = ListProperty([0.1,0.1,0.1,1])
    def __init__(self, **kwargs):
        super(CustomizedButton, self).__init__(**kwargs)
        self.update_button_design()

    def on_pos(self, *args):
        self.update_button_design()

    def on_size(self, *args):
        self.update_button_design()

    def on_press(self, *args):
        self.button_color1, self.button_color2 = self.button_color2, self.button_color1

    def on_release(self, *args):
        self.button_color1, self.button_color2 = self.button_color2, self.button_color1

    def on_button_color1(self, *args):
        self.update_button_design()

    def update_button_design(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(rgba=self.button_color1)
            Ellipse(size=(self.height, self.height),
                    pos=self.pos)
            Ellipse(size=(self.height, self.height),
                    pos=(self.x+self.width-self.height, self.y))
            Rectangle(size=(self.width-self.height, self.height),
                      pos=(self.x+self.height/2, self.y))

class Menu_screen(Screen):
    def on_pre_enter(self, *args):
        Window.bind(on_request_close=self.exit_confirmation)
    
    def on_enter(self, *args):
        global triler_music
        triler_music.play()
    
    def music_player(self, music):
        music.play()

    def on_pre_leave(self, *args):
            triler_music.stop()
    
    def exit_confirmation(self, *args, **kwargs):
        confirmation_content = BoxLayout(orientation="vertical")
        pop = Popup(title="Confirmation", content=confirmation_content, size_hint=(None, None), size = (self.width/2, self.height/2))

        question = Label(text='Do you really need to exit?')
        yesORnot = BoxLayout(spacing='20dp', padding='20dp')
        no = CustomizedButton(text='No!', on_release=pop.dismiss)
        yes = CustomizedButton(text='Yes', on_release=App.get_running_app().stop)
        yesORnot.add_widget(no)
        yesORnot.add_widget(yes)

        confirmation_content.add_widget(question)
        confirmation_content.add_widget(yesORnot)

        pop.open()
        return True
    
    def popup_about(self, *args):
        all_content_container_about = BoxLayout(orientation="vertical")
        software_about_container = BoxLayout(spacing="10dp", size_hint_y=0.4)
        dev_about = BoxLayout(size_hint_y=2.4)
        #empty = Widget(size_hint_x = 0.7)
        
        game_name = Label(text="[size=15sp][b]SAVE BIRD[/b][/size]\n[size=10sp]Version 1.0[/size]\n[size=10sp]Free Software[/size]",
                          halign="center",size_hint_y=0.1, markup=True)
        software_about_container.add_widget(game_name)
        #software_about_container.add_widget(empty)
        contacts = BoxLayout(spacing="10dp", padding=("100dp","5dp"), size_hint_y=0.3)

        whatsappLink ='https://wa.me/258842244136?text=%2AFROM%20SAVE%20BIRD:%2A%0A_Write%20your%20message%20bellow/Escreva%20sua%20mensagem%20abaixo_%0A%0A'
        facebookLink = 'https://www.facebook.com/profile.php?id=61558684890222'
        contacts.add_widget(CustomizedButton(text="Whatsapp", on_release=lambda b: webbrowser.open(whatsappLink)))
        contacts.add_widget(CustomizedButton(text='Facebook', on_release=lambda a: webbrowser.open(facebookLink)))

        #company_logo = Image(source="D:/CSM/python/saveBird/images/logo.png")
        dev_info_text = "[size=15sp][b]\nCiências Sem Mistérios-CSM[/b][/b]\n[size=10sp](Science, Technology and Creativity Development)\nProgramer:\nOscar Ossufo Sail Namicano\nonamicanosail01@gmail.com[/size]\n\n"
        special_thanks = '[size=15sp][b]Special thanks\n[/size][/b][size=10sp]MSc. Ossufo Sail Namicano\nHermenegilda Garcias\nMiguel Logossa\nLucas A. Pedro\nVictoria Nyoka[/size]'
        dev_info = Label(text= dev_info_text+special_thanks+"\n[b]Contact us:[/b]", size_hint_x=0.5, halign='center', markup=True)
        #dev_about.add_widget(company_logo)
        dev_about.add_widget(dev_info)

        popup = Popup(title="About", content=all_content_container_about)
        
        close_popup_box = BoxLayout(size_hint_y=0.2)
        close_popup_button = CustomizedButton(text="Close", on_release=popup.dismiss)
        close_popup_box.add_widget(close_popup_button)

        all_content_container_about.add_widget(software_about_container)
        all_content_container_about.add_widget(dev_about)
        all_content_container_about.add_widget(contacts)
        all_content_container_about.add_widget(close_popup_box)
        popup.open()

class Game_screen(Screen):
    obstacles = [] #Armazena os obstaculos postos na tela, para facilitar sua eliminacao
    score = NumericProperty(0)
    scored_up = False #Variavel que nos indica se ja se tem score suficiente para passar de nivel
    data_path = ""

    def on_pre_enter(self, *args):
        #antes de entrar deve#antes de entrar deve
        #zerrar a velocidade e a posicao do player
        self.ids.player.speed = 0
        self.ids.player.y = self.height/2
        self.score = 0

    def best_score_saver(self, *args):
        """
        Este metodo abre o ficheiro do score mais alto
        e compara com o actual score. Se o actual score for mais alto
        ele salva este score como sendo a pontuacao mais alta adquirida
        """
        #O App.get_running_app().user_data_dir retorna o full path
        #do local onde sao salvos os dados do aplicativo
        #No windows ee: C:\Users\usuario\AppData\Roaming\aplicativo\
        #Usamos este directorio para salvar o score mais alto
        self.data_path = App.get_running_app().user_data_dir+"/"
        
        try:
            with open(self.data_path+"best-score.json", "r") as old_best_score:
                loaded_score = json.load(old_best_score)
                if loaded_score < self.score:
                    with open(self.data_path+"best-score.json", "w") as actual_best_score:
                        json.dump(self.score, actual_best_score)

        except FileNotFoundError:
            """
            Se der erro ee porque nao existe o ficheiro
            e nao tem nenhuma pontuacao salva, entao criamos ele
            e escrevemo nele a pontuacao actual
            """
            with open(self.data_path+"best-score.json", "w") as actual:
                json.dump(self.score, actual)

    def on_enter(self, *args):
        global background_music
        """
        este metodo ee executado depois de entrara na tela em causa
        """
        Clock.schedule_interval(self.update_player_position_y, 1/30)
        #Clock agenda a execucao do metodo update_player_position_y
        #por noos criado para ser chamado 30 vezes por segundo (1/30)

        Clock.schedule_interval(self.putObstacle_on_screen, 1.2)
        #agenda execucao do adicionador de obstaculos na tela para 1 em 1 segundo

        background_music.loop = True #Para que a musica volte a tocar depois de terminar
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
        
        low_obstacle_height = (self.height - gap) * random() #A altura aleatoria do obstaculo de baixo
        obstacle_down = Obstacle(x = self.width, width =self.width*0.05, height = low_obstacle_height)
        obstacle_up = Obstacle(x = self.width, width =self.width*0.05, y = low_obstacle_height+gap, height = self.height-low_obstacle_height-gap)
        #Obstacle ee uma classe que herda de widget para desenhar os obstaculos
        #aqui ee instacada esta classe para ser adicionado na tela o obstaculo
        self.add_widget(obstacle_down, 3)
        self.add_widget(obstacle_up, 3)
        self.obstacles.append(obstacle_down)
        self.obstacles.append(obstacle_up)

    def put_pipe_on_screen(self, *args):

        gap = self.height * 0.3 #espaco entre o obstaculo de baixo e de cima
        
        low_obstacle_height = (self.height - gap) * random() #A altura aleatoria do obstaculo de baixo
        obstacle_down = Down_pipe(x = self.width, width =self.width*0.05, height = low_obstacle_height)
        obstacle_up = Up_pipe(x = self.width, width =self.width*0.05, y = low_obstacle_height+gap, height = self.height-low_obstacle_height-gap)
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
        #a gravidade ainda fica actuando.
        Clock.unschedule(self.putObstacle_on_screen, 1.2)
        Clock.unschedule(self.put_pipe_on_screen, 0.95)
        self.scored_up = False
        #setamos o scored_up para false, pois deve voltar ao nivel inferior
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

#***********************************************************************************************************#
#                                        Area de imeplementacao dos obstaculos                              #
class Obstacle(Widget):
    """
    Ostaculo liso (nao baseado em imagem) implentado atraves do canvas
    do kivy
    """
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
                #Verificamos se a posicao do obstaculo ee menor (ultrapassou a tela) que a do player
                #e se tambem ainda nao foi pontuado o score.

                self.gameScreen.score += 0.5
                #Adicionamos 0.5 ao score pois conta por 2, entao temos que contar pela metade

                if self.gameScreen.score > 30 and not App.get_running_app().root.get_screen("stage").scored_up:
                    #aqui verificamos a pontuacao se daa para ir ao proximo nivel.
                    #App.get_running_app().root.get_screen("stage").scored_up - ee uma flag que nos indica se a pessoa
                    #ja esta no nivel superior ou ainda
                    Clock.unschedule(self.gameScreen.putObstacle_on_screen, 1.2) #Cancelamos as barras lisas
                    Clock.schedule_interval(self.gameScreen.put_pipe_on_screen, 0.95)

                    App.get_running_app().root.get_screen("stage").scored_up = True
                self.pontued = True

                #Apos verificar se o player ultrapassou o
                #obstaculo, comparamoas a pontuacao actual
                #com a antiga para reposicao da antiga caso 
                #esta seja inferio. Essa toda magica ee feita
                #na funcao abaixo chamada:
                self.gameScreen.best_score_saver()
        

    def vanishObstacle(self, *args):
        self.gameScreen.remove_widget(self)
        #depois que o obstaculo atravessa a tela (no x)
        #ee eliminado dela
        self.gameScreen.obstacles.remove(self)
        #depois que o obstaculo atravessa a tela (no x)
        #ee eliminado da lista de obstaculos da tela

class pipe_Obstacle(Image):
    """
    Esta classe ee o mesmo codigo da classe Obstacle()
    a unica diferenca, ee que esta herda de Image.
    Pode ser reaproveitada para adicionar diferentes tipos de 
    obstaculos.
    """
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

                #Apos verificar se o player ultrapassou o
                #obstaculo, comparamoas a pontuacao actual
                #com a antiga para reposicao da antiga caso 
                #esta seja inferio. Essa toda magica ee feita
                #na funcao abaixo chamada:
                self.gameScreen.best_score_saver()

    def vanishObstacle(self, *args):
        self.gameScreen.remove_widget(self)
        #depois que o obstaculo atravessa a tela (no x)
        #ee eliminado dela
        self.gameScreen.obstacles.remove(self)
        #depois que o obstaculo atravessa a tela (no x)
        #ee eliminado da lista de obstaculos da tela

class Down_pipe(pipe_Obstacle):
    """
    Herda da nossa classe pipe_obstacle para dar vida a um cano (image)
    virado para cima
    """
    pass

class Up_pipe(pipe_Obstacle):
    pass

#               Fim da implentacao dos obstaculos                               #
#################################################################################   

class Game_over_screen(Screen):
    def score_loader(self):
        """
        abre o ficheiro gravado que contem a pontuacao mais alta
        para mostrar ao usuario essa pontuacao com a pontuacao que
        ele conseguiu actualmente no jogo        
        """
        self.screenGame = App.get_running_app().root.get_screen("stage")
        try:
            with open(self.screenGame.data_path+"best-score.json", "r") as best:
                self.ids.old_and_actual_score.text = f"Best Score: {str(int(json.load(best)))}\nYour Score: {int(self.screenGame.score)}"
                #App.get_running_app().root.get_screen("stage").score
                #ee uma forma de acessar a classe de ecraa do jogo (palco/stage)
                #e pegar o valor guardado na variavel score

        except FileNotFoundError:
            pass
    def on_pre_enter(self, *args):
        self.score_loader()

class Player(Image):
    speed = NumericProperty(0)

class saveBird(App):
    """def build(self):
        player = Image(source="players/player1.png")
        layout = FloatLayout()
        layout.add_widget(player)

        Quando nao se deinfine o metodo build 
        o python procura no arquivo .kv a classe que nao
        possui os sinais <> e retorna essa mesma
        return layout"""
    pass

#Nas linhas abaixo carregamos todos os efeitos sonoros do jogo
triler_music = SoundLoader.load("sounds/[MENU-SOUND]-birds-chirping-near-the-river.wav")
fly_music = SoundLoader.load("sounds/[FLY1]-basketball-ball-hitting-the-net.wav")
beat_on_obstacle_sound = SoundLoader.load("sounds/[BEAT1]-hitting-golf-ball.wav")
background_music = SoundLoader.load("sounds/[EDIT]-game-music-loop.wav")

saveBird().run()