import socket
import threading
import json
import signal
import sys
import board 
import copy

HOST = '127.0.0.1'
PORT = 65432

class Server:
    def __init__(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((HOST, PORT))
        self.server_socket.listen(2)
        self.board = board.Board()
        
        self.clients = []  # Lista przechowująca gniazda klientów
        self.lock = threading.Lock() # Blokada do synchronizacji dostępu do planszy
        
        self.turn = "WILK" 
        
        print(f"Serwer uruchomiony na {HOST}:{PORT}. Oczekiwanie na graczy...")

        signal.signal(signal.SIGINT, self.signal_handler)


    def signal_handler(self, sig, frame):
        print("\nZamykanie serwera (Otrzymano SIGINT)...")
        self.broadcast({"type": "EXIT", "msg": "Serwer został wyłączony."})
        for c in self.clients:
            c.close()
        sys.exit(0)

    def broadcast(self, message):
        """Wysyła wiadomość do wszystkich połączonych klientów."""
        data = (json.dumps(message) + "\n").encode('utf-8')
        for client in self.clients:
            try:
                client.sendall(data)
            except:
                self.clients.remove(client)

    def handle_client(self, client_socket, player_type):
        """Wątek obsługujący pojedynczego gracza."""
        print(f"Połączono: {player_type}")
        
        # Wyślij graczowi informację, kim jest
        init_msg = {"type": "INIT", "role": player_type, "board": self.board.grid}
        client_socket.sendall((json.dumps(init_msg) + "\n").encode('utf-8'))


        buffer = ""
        while True:
            try:
                data = client_socket.recv(1024)
                if not data:
                    break

                buffer += data.decode('utf-8')

                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    if not line.strip():
                        continue

                    move = json.loads(line)

                    with self.lock:
                        if self.turn != player_type:
                            client_socket.sendall((json.dumps({"type": "ERROR", "msg": "To nie jest Twoja tura!"}) + "\n").encode('utf-8'))
                            continue

                        fr, fc = move["from"]
                        tr, tc = move["to"]
                        print(f"Próba ruchu: {player_type} z {fr, fc} na {tr, tc}")
                        is_valid, msg = self.board.validate_move(fr, fc, tr, tc, player_type)
                        print(f"Wynik walidacji: {is_valid}, powód: {msg}")
                        if is_valid:
                            self.board.move_piece(fr, fc, tr, tc)
                            winner = self.board.check_winner()

                            self.turn = "OWCE" if player_type == "WILK" else "WILK"

                            current_grid = copy.deepcopy(self.board.grid)

                            response = {
                                "type": "UPDATE",
                                "board": current_grid,
                                "turn": self.turn
                            }

                            if winner:
                                response["winner"] = winner
                                print(f"Koniec gry! Zwycięzca: {winner}")

                            self.broadcast(response)
                            print(f"Ruch poprawny: {player_type} z {fr,fc} na {tr,tc}. Tura: {self.turn}")
                        else:
                            client_socket.sendall((json.dumps({"type": "ERROR", "msg": "Ruch niedozwolony lub nie Twoja tura!"}) + "\n").encode('utf-8'))
            
            except Exception as e:
                print(f"Błąd gracza {player_type}: {e}")
                break

        client_socket.close()

    def run(self):
        roles = ["WILK", "OWCE"]
        while len(self.clients) < 2:
            conn, addr = self.server_socket.accept()
            self.clients.append(conn)
            role = roles[len(self.clients)-1]
            # Każdy gracz dostaje swój wątek
            thread = threading.Thread(target=self.handle_client, args=(conn, role))
            thread.start()

if __name__ == "__main__":
    server = Server()
    server.run()