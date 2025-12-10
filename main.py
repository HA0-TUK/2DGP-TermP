from pico2d import *
import game_framework
import title_mode

if __name__ == '__main__':
    game_framework.init()
    game_framework.run(title_mode.TitleMode())
    game_framework.quit()
    