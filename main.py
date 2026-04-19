from kivy.config import Config
Config.set('graphics', 'width', '360')
Config.set('graphics', 'height', '640')
Config.set('graphics', 'resizable', False)
import random
from kivy.metrics import dp  # <--- IMPORTANTE: Importa dp para que funcione arriba
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.uix.popup import Popup
from kivy.properties import NumericProperty, ObjectProperty
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.uix.checkbox import CheckBox
from kivy.properties import NumericProperty, ObjectProperty, BooleanProperty


class Meteorito(Widget):
    velocidad_x = NumericProperty(-3)

    def mover(self):
        self.x += self.velocidad_x


class Astronauta(Widget):
    velocidad_y = NumericProperty(0)
    gravedad = -0.5
    impulso_salto = 12

    def mover(self):
        self.velocidad_y += self.gravedad
        self.y += self.velocidad_y

        # Evitar que la nave se salga por arriba de la pantalla
        if self.top > self.parent.height:
            self.top = self.parent.height
            self.velocidad_y = 0
    def saltar(self):
        self.velocidad_y = self.impulso_salto


class AjustesPopup(Popup):
    juego = ObjectProperty(None)


class Juego(Widget):
    astronauta = ObjectProperty(None)
    puntaje = NumericProperty(0)
    velocidad_juego = NumericProperty(-3)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.sonido_beep = SoundLoader.load('assets/sonido.mp3')
        self.lista_meteoritos = []
        self.ejecutando = False

    def comenzar(self):
        if not self.ejecutando:
            # Ponemos la nave en una posición visible (X=50, Y=mitad de pantalla)
            self.astronauta.pos = (dp(50), self.height / 2)
            self.evento_meteoritos = Clock.schedule_interval(self.crear_meteorito, 1.5)
            self.evento_update = Clock.schedule_interval(self.update, 1.0 / 60.0)
            self.ejecutando = True

    def pausar(self):
        Clock.unschedule(self.evento_meteoritos)
        Clock.unschedule(self.evento_update)
        self.ejecutando = False

    def crear_meteorito(self, dt):
        m = Meteorito()
        m.x = self.width
        #margen = self.height * 0.1
        m.y = random.randint(int(dp(50)), int(self.height - dp(100)))
        m.velocidad_x = self.velocidad_juego
        self.add_widget(m)
        self.lista_meteoritos.append(m)

    def update(self, dt):
        self.astronauta.mover()
        for m in self.lista_meteoritos[:]:
            m.mover()
            if self.astronauta.collide_widget(m) or self.astronauta.y < 0:
                self.game_over()
            if m.right < 0:
                self.remove_widget(m)
                self.lista_meteoritos.remove(m)
                self.puntaje += 1
                # Solo suena si la app tiene el sonido habilitado
                if self.sonido_beep and App.get_running_app().sonido_habilitado:
                    self.sonido_beep.play()

                if self.puntaje % 5 == 0: self.velocidad_juego -= 0.5

    def on_touch_down(self, touch):
        if self.ejecutando: self.astronauta.saltar()

    def game_over(self):
        self.pausar()
        print(f"GAME OVER - Puntaje: {self.puntaje}")
        # Limpiar meteoritos
        for m in self.lista_meteoritos: self.remove_widget(m)
        self.lista_meteoritos = []
        self.puntaje = 0
        self.velocidad_juego = -3
        App.get_running_app().root.current = 'menu'

    def ir_al_menu(self):
        self.game_over()  # Esto limpia meteoritos y resetea puntaje
        App.get_running_app().root.current = 'menu'


class MenuScreen(Screen):
    pass


class JuegoScreen(Screen):
    juego_widget = ObjectProperty(None)

    def on_enter(self):  # Al entrar a la pantalla, inicia el juego
        self.juego_widget.comenzar()

    def abrir_popup_ajustes(self):
        # Esta función crea y abre el popup
        p = AjustesPopup(juego=self.juego_widget)
        p.open()

class AstroApp(App):
    sonido_habilitado = BooleanProperty(True)  # <--- ESTO FALTABA
    def build(self):
        # El ScreenManager se define en el archivo .kv automáticamente
        pass


if __name__ == "__main__":
    AstroApp().run()

