import pygame
import socket
import threading
import json
import queue

WIDTH, HEIGHT = 600, 600
SQUARE_SIZE = WIDTH // 8
WHITE = (245, 245, 220)
BLACK = (101, 67, 33)
RED = (200, 0, 0)
GRAY = (150, 150, 150)

class Client:
    def __init__(self, host='127.0.0.1', port=65432):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.font = pygame.font.SysFont('Arial', 32)
        
        # Komunikacja
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        self.msg_queue = queue.Queue()
        
        # Stan gry
        self.board = []
        self.role = None  # "WILK" lub "OWCE"
        self.turn = None
        self.selected_sq = None # Zaznaczone pole (r, c)
        self.running = True
        self.winner = None

        # Wątek sieciowy
        threading.Thread(target=self.receive_data, daemon=True).start()

    # def receive_data(self):
    #     """Nasłuchiwanie wiadomości z serwera."""
    #     while self.running:
    #         try:
    #             data = self.socket.recv(4096).decode('utf-8')
    #             if not data: break
                
    #             # Obsługa wielu JSONów w jednym pakiecie
    #             messages = data.replace('}{', '}\n{').split('\n')
    #             for msg_str in messages:
    #                 msg = json.loads(msg_str)
    #                 self.msg_queue.put(msg)
    #         except:
    #             break



    def receive_data(self):
        buffer = ""
        while self.running:
            try:
                data = self.socket.recv(4096).decode('utf-8')
                if not data: break
                
                buffer += data
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    if line.strip():
                        msg = json.loads(line)
                        self.msg_queue.put(msg)
            except:
                break


    def handle_messages(self):
        """Przetwarzanie wiadomości w głównym wątku GUI."""
        while not self.msg_queue.empty():
            msg = self.msg_queue.get()
            if msg["type"] == "INIT":
                self.role = msg["role"]
                self.board = msg["board"]
                self.turn = "WILK" # Wilk zawsze zaczyna
                pygame.display.set_caption(f"Grasz jako: {self.role}")
            
            elif msg["type"] == "UPDATE":
                self.board = msg["board"]
                self.turn = msg["turn"]
                if "winner" in msg:
                    self.winner = msg["winner"]

    def draw(self):
        self.screen.fill(WHITE)
        for r in range(8):
            for c in range(8):
                if (r + c) % 2 != 0:
                    pygame.draw.rect(self.screen, BLACK, (c*SQUARE_SIZE, r*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
                
                piece = self.board[r][c] if self.board else 0
                if piece == 1: # Owca
                    pygame.draw.circle(self.screen, (255, 255, 255), (c*SQUARE_SIZE+SQUARE_SIZE//2, r*SQUARE_SIZE+SQUARE_SIZE//2), 30)
                elif piece == 2: # Wilk
                    pygame.draw.circle(self.screen, RED, (c*SQUARE_SIZE+SQUARE_SIZE//2, r*SQUARE_SIZE+SQUARE_SIZE//2), 30)

        # Podświetlenie zaznaczenia
        if self.selected_sq:
            r, c = self.selected_sq
            pygame.draw.rect(self.screen, (0, 255, 0), (c*SQUARE_SIZE, r*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), 3)

        # Wyświetlanie statusu
        status_txt = f"Twoja tura ({self.role})" if self.turn == self.role else "Czekaj na przeciwnika..."
        if self.winner: status_txt = f"KONIEC: Wygrały {self.winner}!"
        
        txt_surf = self.font.render(status_txt, True, (0, 0, 255))
        self.screen.blit(txt_surf, (10, 10))

    def run(self):
        clock = pygame.time.Clock()
        while self.running:
            self.handle_messages()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                
                if event.type == pygame.MOUSEBUTTONDOWN and not self.winner:
                    if self.turn == self.role:
                        x, y = pygame.mouse.get_pos()
                        r, c = y // SQUARE_SIZE, x // SQUARE_SIZE
                        
                        if self.selected_sq:
                            # Próba wykonania ruchu
                            move = {
                                "type": "MOVE",
                                "from": self.selected_sq,
                                "to": [r, c]
                            }
                            self.socket.sendall((json.dumps(move) + "\n").encode('utf-8'))
                            self.selected_sq = None
                        else:
                            # Zaznaczanie tylko swoich pionków
                            piece = self.board[r][c]
                            if (self.role == "WILK" and piece == 2) or (self.role == "OWCE" and piece == 1):
                                self.selected_sq = (r, c)

            self.draw()
            pygame.display.flip()
            clock.tick(60)
        
        pygame.quit()

if __name__ == "__main__":
    client = Client()
    client.run()