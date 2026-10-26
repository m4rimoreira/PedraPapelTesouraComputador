"""Jogo reconstruído a partir do projeto anterior de webcam e gestos."""
import random
import time
from collections import Counter
import cv2
from cvzone.HandTrackingModule import HandDetector

GESTOS = {"Pedra": (0, 1), "Tesoura": (2,), "Papel": (5,)}
OPCOES = ("Pedra", "Papel", "Tesoura")

def classificar(dedos):
    total = sum(dedos)
    for gesto, contagens in GESTOS.items():
        if total in contagens:
            return gesto
    return None

def resultado(jogador, computador):
    if jogador == computador:
        return "Empate"
    vence = {"Pedra": "Tesoura", "Papel": "Pedra", "Tesoura": "Papel"}
    return "Você venceu!" if vence[jogador] == computador else "Computador venceu!"

def main():
    camera = cv2.VideoCapture(0)
    if not camera.isOpened():
        raise RuntimeError("Não foi possível abrir a webcam")
    detector = HandDetector(detectionCon=0.85, maxHands=1)
    placar = [0, 0]
    inicio = None
    ultimo = "Pressione ESPAÇO para jogar"
    historico = []
    try:
        while True:
            ok, frame = camera.read()
            if not ok:
                break
            frame = cv2.flip(frame, 1)
            hands, frame = detector.findHands(frame, draw=True, flipType=False)
            gesto = classificar(detector.fingersUp(hands[0])) if hands else None
            if inicio is not None:
                segundos = 3 - int(time.monotonic() - inicio)
                if segundos > 0:
                    ultimo = f"Prepare-se: {segundos}"
                    if gesto:
                        historico.append(gesto)
                else:
                    jogador = Counter(historico[-20:]).most_common(1)
                    jogador = jogador[0][0] if jogador else None
                    if jogador:
                        pc = random.choice(OPCOES)
                        fim = resultado(jogador, pc)
                        if fim == "Você venceu!": placar[0] += 1
                        elif fim == "Computador venceu!": placar[1] += 1
                        ultimo = f"{jogador} x {pc} - {fim}"
                    else:
                        ultimo = "Gesto não reconhecido. Tente novamente."
                    inicio = None
            cv2.putText(frame, ultimo, (20, 45), cv2.FONT_HERSHEY_SIMPLEX, .7, (200, 180, 255), 2)
            cv2.putText(frame, f"Voce {placar[0]} x {placar[1]} PC", (20, 85), cv2.FONT_HERSHEY_SIMPLEX, .8, (255, 255, 255), 2)
            cv2.putText(frame, "ESPACO: jogar | ESC: sair", (20, frame.shape[0]-20), cv2.FONT_HERSHEY_SIMPLEX, .6, (255,255,255), 2)
            cv2.imshow("Pedra, Papel e Tesoura", frame)
            tecla = cv2.waitKey(1) & 0xFF
            if tecla == 27:
                break
            if tecla == 32 and inicio is None:
                inicio = time.monotonic()
                historico = []
    finally:
        camera.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
