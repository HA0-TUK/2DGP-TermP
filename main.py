from pico2d import *
import game_framework
import play_mode

if __name__ == '__main__':
    game_framework.init()
    game_framework.run(play_mode.PlayMode())
    game_framework.quit()
