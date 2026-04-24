from kivy.config import Config
#Config.set('graphics', 'width', '360')
#Config.set('graphics', 'height', '640')
#Config.set('graphics', 'resizable', False)
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

# 1. Crea esta nueva clase para el cartel de "Perdiste"
class GameOverPopup(Popup):
    juego = ObjectProperty(None)
    puntaje_final = NumericProperty(0)

    def salir_al_menu_desde_popup(self):
        self.dismiss() # Cierra el cartel
        self.juego.ir_al_menu() # Usa la función que ya arreglamos en Juego

class Juego(Widget):
    label_cuenta_visual = ObjectProperty(None)  # Conecta con el ID del KV
    astronauta = ObjectProperty(None)
    puntaje = NumericProperty(0)
    velocidad_juego = NumericProperty(-3)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.sonido_beep = SoundLoader.load('assets/sonido.mp3')
        self.lista_meteoritos = []
        self.ejecutando = False
        self.evento_meteoritos = None
        self.evento_update = None

    def comenzar(self):
        # 1. DETENER RELOJES PREVIOS (Esto soluciona la caída rápida)
        Clock.unschedule(self.evento_meteoritos)
        Clock.unschedule(self.evento_update)

        # Limpiar antes de empezar
        for m in self.lista_meteoritos: self.remove_widget(m)
        self.lista_meteoritos = []
        self.puntaje = 0
        self.velocidad_juego = -3
        self.astronauta.pos = (dp(50), self.height / 2)
        self.astronauta.velocidad_y = 0
        self.ejecutando = False  # Reiniciamos el estado

        # Iniciar cuenta regresiva en lugar de empezar directo
        self.cuenta = 3
        self.label_cuenta_visual.text = "PREPARADOS"  # Texto inicial
        Clock.schedule_interval(self.cuenta_regresiva, 1)

    def borrar_label(self, dt):
        self.label_cuenta_visual.text = ""

    def cuenta_regresiva(self, dt):
        if self.cuenta > 0:
            self.label_cuenta_visual.text = str(self.cuenta)
            self.cuenta -= 1
            return True
        else:
            self.label_cuenta_visual.text = "¡YA!"

            # Iniciamos el juego real
            self.iniciar_juego_real()

            # Programamos borrar el texto "¡YA!" en medio segundo
            Clock.schedule_once(self.borrar_label, 0.5)
            return False

    def limpiar_texto_y_empezar(self, dt):
        self.label_cuenta_visual.text = ""  # Borramos el texto
        self.iniciar_juego_real()  # Aquí activas tus meteoritos y gravedad

    def iniciar_juego_real(self):
        # Si ya está ejecutando, no creamos más relojes
        if not self.ejecutando:
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

        # 1. Definimos los radios para una colisión circular justa
        radio_nave = dp(18)
        radio_meteorito = dp(25)
        distancia_minima = radio_nave + radio_meteorito

        for m in self.lista_meteoritos[:]:
            m.mover()

            # 2. CALCULAMOS LA DISTANCIA REAL (Esto reemplaza al collide_widget)
            dx = self.astronauta.center_x - m.center_x
            dy = self.astronauta.center_y - m.center_y
            distancia_actual = (dx ** 2 + dy ** 2) ** 0.5

            # 3. COMPROBAMOS EL CHOQUE
            # Si la distancia es menor a la suma de radios O si toca el suelo
            if distancia_actual < distancia_minima or self.astronauta.y < 0:
                self.game_over()
                break  # Detenemos el chequeo de este frame

            # 4. PUNTAJE Y LIMPIEZA
            if m.right < 0:
                self.remove_widget(m)
                if m in self.lista_meteoritos:
                    self.lista_meteoritos.remove(m)
                self.puntaje += 1

                try:
                    if self.sonido_beep and App.get_running_app().sonido_habilitado:
                        self.sonido_beep.play()
                except Exception as e:
                    print(f"Error de audio: {e}")  # Evita que la app se cierre si falla el sonido

                if self.puntaje % 5 == 0:
                    self.velocidad_juego -= 0.5

    def on_touch_down(self, touch):
        if self.ejecutando: self.astronauta.saltar()

    def game_over(self):
        self.pausar()
        # En lugar de ir al menú, abrimos el popup de puntaje
        p = GameOverPopup(juego=self, puntaje_final=self.puntaje)
        p.open()

    def reanudar(self):
        # Solo activamos los relojes si no están corriendo
        if not self.ejecutando:
            self.evento_meteoritos = Clock.schedule_interval(self.crear_meteorito, 1.5)
            self.evento_update = Clock.schedule_interval(self.update, 1.0 / 60.0)
            self.ejecutando = True

    def reiniciar_juego(self):
        # Limpiamos meteoritos antes de empezar
        for m in self.lista_meteoritos:
            self.remove_widget(m)
        self.lista_meteoritos = []
        self.puntaje = 0
        self.velocidad_juego = -3
        self.comenzar()  # Llama a tu función que inicia los relojes

    def ir_al_menu(self):
        self.pausar()  # Detenemos todo por seguridad
        app = App.get_running_app()
        if app.root:
            app.root.current = 'menu'


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

