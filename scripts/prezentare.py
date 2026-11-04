"""Pornește HelpDesk IT pentru prezentare și deschide aplicația în browser.

Funcționează pe Windows, Linux și macOS și folosește doar biblioteca standard Python,
deci se poate rula înainte de a instala ceva.

Ce face, pe rând:
    1. creează mediul virtual „.venv” (doar prima dată);
    2. instalează dependențele din requirements.txt (doar când s-au schimbat);
    3. recreează baza de date cu utilizatorii de test și câteva tichete demonstrative;
    4. pornește serverul Flask pe primul port liber începând de la 5000;
    5. deschide pagina de login în browserul implicit.

Utilizare (din folderul proiectului):
    python scripts/prezentare.py               # Windows: py scripts\\prezentare.py
    python scripts/prezentare.py --pastreaza   # nu reseta datele (păstrează tichetele create)

Oprire: Ctrl+C în fereastra terminalului.
"""

import os
import socket
import subprocess
import sys
import time
import venv
import webbrowser
from pathlib import Path

RADACINA = Path(__file__).resolve().parent.parent  # folderul proiectului
VENV = RADACINA / ".venv"
CERINTE = RADACINA / "requirements.txt"
MARCAJ = VENV / ".instalat"  # fișier gol: când există și e mai nou decât requirements.txt,
#                              dependențele sunt deja instalate

CONTURI = [
    ("Angajat", "angajat@technova.test"),
    ("Tehnician", "tehnician@technova.test"),
    ("Manager", "manager@technova.test"),
]
PAROLA = "parola123"


def pas(mesaj):
    """Afișează un pas al pornirii, ca să se vadă ce se întâmplă."""
    print(f"\n==> {mesaj}", flush=True)


def python_din_venv():
    """Calea către Python-ul din .venv (diferă între Windows și Linux/macOS)."""
    if os.name == "nt":
        return VENV / "Scripts" / "python.exe"
    return VENV / "bin" / "python"


def pregateste_mediul():
    """Creează .venv și instalează dependențele, doar dacă e nevoie."""
    # Scriptul poate fi pornit cu un Python vechi al sistemului, deci verificăm versiunea.
    if sys.version_info < (3, 12):  # noqa: UP036
        sys.exit("Este nevoie de Python 3.12 sau mai nou. Descarcă-l de pe python.org.")

    if not python_din_venv().exists():
        pas("Creez mediul virtual .venv (doar prima dată)")
        venv.create(VENV, with_pip=True)

    if not MARCAJ.exists() or CERINTE.stat().st_mtime > MARCAJ.stat().st_mtime:
        pas("Instalez dependențele (Flask, SQLAlchemy, Flask-Login)")
        subprocess.run(
            [python_din_venv(), "-m", "pip", "install", "-q", "--disable-pip-version-check",
             "-r", CERINTE],
            check=True,
        )
        MARCAJ.touch()


def pregateste_datele(pastreaza):
    """Recreează baza de date cu datele demo, cu excepția cazului --pastreaza."""
    baza = RADACINA / "instance" / "helpdesk.db"
    if pastreaza and baza.exists():
        pas("Păstrez datele existente (--pastreaza)")
        return
    pas("Creez baza de date cu utilizatori de test și tichete demonstrative")
    subprocess.run([python_din_venv(), "seed.py", "--demo"], cwd=RADACINA, check=True)


def port_liber(start=5000):
    """Primul port liber începând cu „start” (pe macOS, 5000 e ocupat uneori de AirPlay)."""
    for port in range(start, start + 50):
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", port)) != 0:
                return port
    sys.exit("Nu am găsit niciun port liber între 5000 și 5049.")


def asteapta_serverul(port, proces, secunde=30):
    """Așteaptă până când serverul răspunde pe port. Returnează False dacă a căzut."""
    limita = time.time() + secunde
    while time.time() < limita:
        if proces.poll() is not None:  # procesul s-a oprit → eroare la pornire
            return False
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", port)) == 0:
                return True
        time.sleep(0.3)
    return False


def main():
    os.chdir(RADACINA)
    pregateste_mediul()
    pregateste_datele(pastreaza="--pastreaza" in sys.argv)

    port = port_liber()
    adresa = f"http://127.0.0.1:{port}/login"
    pas(f"Pornesc serverul pe {adresa}")
    server = subprocess.Popen(
        [python_din_venv(), "-m", "flask", "--app", "app", "run", "--port", str(port)],
        cwd=RADACINA,
    )
    try:
        if not asteapta_serverul(port, server):
            sys.exit("Serverul nu a pornit. Verifică mesajele de eroare de mai sus.")
        webbrowser.open(adresa)

        print("\n" + "=" * 62)
        print(f"  HelpDesk IT rulează pe  {adresa}")
        print("  (dacă browserul nu s-a deschis, copiază adresa de mai sus)\n")
        print("  Conturi de test:")
        for rol, email in CONTURI:
            print(f"    {rol:<10} {email}")
        print(f"  Parola pentru toate:  {PAROLA}\n")
        print("  Oprire: Ctrl+C")
        print("=" * 62 + "\n", flush=True)
        server.wait()
    except KeyboardInterrupt:
        print("\nOpresc serverul...")
    finally:
        if server.poll() is None:
            server.terminate()
            server.wait()


if __name__ == "__main__":
    main()
