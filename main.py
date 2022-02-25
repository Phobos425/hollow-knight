import game
import sqlite3


g = game.game()

if __name__ == '__main__':
        g.gameloop()
        con = sqlite3.connect("result.db")

        cur = con.cursor()
        cur.execute(f"""INSERT INTO result VALUES('{game.delta_time ,game.platformer.coins}')""")

