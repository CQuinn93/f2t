from kivy import *

from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.recyclegridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button


class MyGrid(GridLayout):
    def __init__(self,**kwargs):
        super(MyGrid, self).__init__(**kwargs)
        self.cols = 1

        self.inside = GridLayout()
        self.inside.cols = 2

        self.add_widget(Label(text="First2Twenty"))

        self.inside.add_widget(Label(text="Player 1"))
        self.player1 = TextInput(multiline = False)
        self.inside.add_widget(self.player1)

        self.inside.add_widget(Label(text="Player 2"))
        self.player2 = TextInput(multiline=False)
        self.inside.add_widget(self.player2)

        self.inside.add_widget(Label(text="Player 3"))
        self.player3 = TextInput(multiline=False)
        self.inside.add_widget(self.player3)

        self.inside.add_widget(Label(text="Player 4"))
        self.player4 = TextInput(multiline=False)
        self.inside.add_widget(self.player4)

        self.inside.add_widget(Label(text="Player 5"))
        self.player5 = TextInput(multiline=False)
        self.inside.add_widget(self.player5)

        self.inside.add_widget(Label(text="player 6"))
        self.player6 = TextInput(multiline=False)
        self.inside.add_widget(self.player6)

        self.inside.add_widget(Label(text="player 8"))
        self.player8 = TextInput(multiline=False)
        self.inside.add_widget(self.player8)

        self.inside.add_widget(Label(text="player 9"))
        self.player9 = TextInput(multiline=False)
        self.inside.add_widget(self.player9)

        self.inside.add_widget(Label(text="player 10"))
        self.player10 = TextInput(multiline=False)
        self.inside.add_widget(self.player10)

        self.inside.add_widget(Label(text="player 11"))
        self.player11 = TextInput(multiline=False)
        self.inside.add_widget(self.player11)

        self.inside.add_widget(Label(text="player 12"))
        self.player12 = TextInput(multiline=False)
        self.inside.add_widget(self.player12)

        self.inside.add_widget(Label(text="player 13"))
        self.player13 = TextInput(multiline=False)
        self.inside.add_widget(self.player13)

        self.inside.add_widget(Label(text="player 14"))
        self.player14 = TextInput(multiline=False)
        self.inside.add_widget(self.player14)

        self.inside.add_widget(Label(text="player 15"))
        self.player15 = TextInput(multiline=False)
        self.inside.add_widget(self.player15)

        self.inside.add_widget(Label(text="player 16"))
        self.player16 = TextInput(multiline=False)
        self.inside.add_widget(self.player16)

        self.inside.add_widget(Label(text="player 17"))
        self.player17 = TextInput(multiline=False)
        self.inside.add_widget(self.player17)

        self.inside.add_widget(Label(text="player 18"))
        self.player18 = TextInput(multiline=False)
        self.inside.add_widget(self.player18)

        self.inside.add_widget(Label(text="player 19"))
        self.player19 = TextInput(multiline=False)
        self.inside.add_widget(self.player19)

        self.inside.add_widget(Label(text="player 20"))
        self.player20 = TextInput(multiline=False)
        self.inside.add_widget(self.player20)

        self.add_widget(self.inside)
        
        self.submit = Button(text = "Submit",font_size=40)
        self.add_widget(self.submit)



class MyApp(App):
    def build(self):
        return MyGrid()


if __name__=="__main__":
    MyApp().run()


