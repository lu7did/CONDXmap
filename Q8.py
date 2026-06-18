#!/usr/bin/env python3
#*====================================================================================================================
#* Q8.py
#* Programa demo para elaborar sobre condiciones de UX
#*
#* python Q8.py <N> {1..8}
#*
#* Calidad de Software FIM481
#* 
#* Copyright Dr. Pedro E. Colla (2025,2026)
#*
#* License: MIT
#*
#*====================================================================================================================
 
import sys
import random
import time
import matplotlib.pyplot as plt


# ============================================================
# Utilidad: entero -> numerales chinos (simplificado y práctico)
# Soporta bien hasta 99999 (万). Para más, cae a dígitos.
# ============================================================

_CN_DIG = ["零", "一", "二", "三", "四", "五", "六", "七", "八", "九"]
_CN_UNIT = ["", "十", "百", "千"]
_CN_BIG = ["", "万"]

def int_to_chinese(n: int) -> str:
    if n == 0:
        return "零"
    if n < 0:
        return "负" + int_to_chinese(-n)

    # Para no complicar demasiado el toy project:
    # soportamos hasta 99999 (万). Para más, devolvemos dígitos chinos.
    if n > 99999:
        return "".join(_CN_DIG[int(ch)] for ch in str(n))

    def chunk_to_cn(x: int) -> str:
        # x en 0..9999
        s = ""
        zero_pending = False
        digits = list(map(int, f"{x:04d}"))
        for i, d in enumerate(digits):
            pos = 3 - i  # miles..unidades
            if d == 0:
                zero_pending = True if s else False
                continue
            if zero_pending:
                s += "零"
                zero_pending = False
            s += _CN_DIG[d] + _CN_UNIT[pos]
        return s

    high = n // 10000
    low = n % 10000

    if high == 0:
        cn = chunk_to_cn(low)
    else:
        cn = chunk_to_cn(high) + "万"
        if low != 0:
            # si low es pequeño, se suele insertar "零"
            if low < 1000:
                cn += "零"
            cn += chunk_to_cn(low)

    # Normalización común: 10..19 se escribe "十X" (no "一十X")
    if cn.startswith("一十"):
        cn = cn[1:]

    return cn


# ============================================================
# Opción 1 — Salida optimizada
# ============================================================

def opcion_1(N):
    lines = [f"2 x {i} = {2*i}\n" for i in range(1, N+1)]
    sys.stdout.write("".join(lines))


# ============================================================
# Opción 2 — Colores
# ============================================================

def opcion_2(N):
    GREEN_LIGHT = "\033[92m"
    BG_GREEN_DARK = "\033[42m"
    RESET = "\033[0m"

    lines = [
        f"{GREEN_LIGHT}{BG_GREEN_DARK}2 x {i} = {2*i}{RESET}\n"
        for i in range(1, N+1)
    ]
    sys.stdout.write("".join(lines))


# ============================================================
# Opción 3 — Legibilidad
# ============================================================

def _ruido_tipografico(texto):
    return "".join(ch + (" " * random.randint(0, 2)) for ch in texto)


def opcion_3(N):
    RESET = "\033[0m"
    style1 = "\033[92;42m"
    style2 = "\033[32;42m"
    style3 = "\033[2;32;42m"

    buffer = []

    buffer.append("\n=== NIVEL 1 ===\n")
    for i in range(1, N+1):
        buffer.append(f"{style1}2 x {i} = {2*i}{RESET}\n")

    buffer.append("\n=== NIVEL 2 ===\n")
    for i in range(1, N+1):
        buffer.append(f"{style2}2 x {i} = {2*i}{RESET}\n")

    buffer.append("\n=== NIVEL 3 ===\n")
    for i in range(1, N+1):
        txt = _ruido_tipografico(f"2 x {i} = {2*i}")
        buffer.append(f"{style3}{txt}{RESET}\n")

    sys.stdout.write("".join(buffer))


# ============================================================
# Opción 4 — Aleatorio
# ============================================================

def opcion_4(N):
    numeros = list(range(1, N+1))
    random.shuffle(numeros)
    lines = [f"2 x {i} = {2*i}\n" for i in numeros]
    sys.stdout.write("".join(lines))


# ============================================================
# Opción 5 — Retardo
# ============================================================

def opcion_5(N):
    for i in range(1, N+1):
        sys.stdout.write(f"2 x {i} = {2*i}\n")
        sys.stdout.flush()
        time.sleep(5)


# ============================================================
# Opción 6 — Concatenado
# ============================================================

def opcion_6(N):
    buffer = "".join(f"2x{i}={2*i}" for i in range(1, N+1))
    sys.stdout.write(buffer + "\n")


# ============================================================
# Opción 7 — Binario
# ============================================================

def opcion_7(N):
    lines = [
        f"{bin(2)} x {bin(i)} = {bin(2*i)}\n"
        for i in range(1, N+1)
    ]
    sys.stdout.write("".join(lines))


# ============================================================
# Opción 8 — Ábaco avanzado
# ============================================================

def opcion_8(N):
    x = list(range(1, N+1))
    y = [2*i for i in x]

    plt.figure()
    plt.plot(x, y, marker="o")
    plt.title("Ábaco avanzado — Tabla del 2")
    plt.xlabel("Multiplicador")
    plt.ylabel("Resultado")
    plt.grid(True)
    plt.show()


# ============================================================
# Opción 9 — Caracteres chinos
# ============================================================

def opcion_9(N):
    dos = int_to_chinese(2)
    lines = [
        f"{dos} 乘 {int_to_chinese(i)} 等于 {int_to_chinese(2*i)}\n"
        for i in range(1, N+1)
    ]
    sys.stdout.write("".join(lines))


# ============================================================
# Dispatcher
# ============================================================

FUNCIONES = {
    1: opcion_1,
    2: opcion_2,
    3: opcion_3,
    4: opcion_4,
    5: opcion_5,
    6: opcion_6,
    7: opcion_7,
    8: opcion_8,
    9: opcion_9,
}


# ============================================================
# Main
# ============================================================

def main():
    if len(sys.argv) != 3:
        print("Uso: python programa.py <N> <opcion>")
        sys.exit(1)

    try:
        N = int(sys.argv[1])
        opcion = int(sys.argv[2])
    except ValueError:
        print("Argumentos deben ser numéricos.")
        sys.exit(1)

    if N <= 0:
        print("N debe ser positivo.")
        sys.exit(1)

    func = FUNCIONES.get(opcion)
    if not func:
        print(f"Opción {opcion} no implementada.")
        sys.exit(1)

    func(N)


if __name__ == "__main__":
    main()

