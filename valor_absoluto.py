#*------------------------------------------------------------------------------------------------
#* Calidad de Software
#* Ingeniería en Informática
#* U.Fasta
#*
#* Dr. Pedro E. Colla (2025) 
#* -----------------------------------------------------------------------------------------------
"""
Este programase encuentra bajo una Licencia Creative Commons Atribución-NoComercial 4.0 Internacional.
Permite: Compartir, adaptar y modificar sin fines comerciales, citando al autor. 
"""

import sys

def valor_absoluto(x):
    if x < 0:
        return -x
    return x

def main():
    if len(sys.argv) != 2:
        print("Uso: python valor_absoluto.py <numero_entero>")
        sys.exit(1)
    
    try:
        numero = int(sys.argv[1])
    except ValueError:
        print("Error: el argumento debe ser un número entero.")
        sys.exit(1)
    
    resultado = valor_absoluto(numero)
    print(f"El valor absoluto de {numero} es {resultado}")

if __name__ == "__main__":
    main()
