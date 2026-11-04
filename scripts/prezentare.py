"""Pornește HelpDesk IT pentru prezentare și deschide aplicația în browser.

Pe Windows nu se rulează direct: se pornește cu dublu-clic pe fișierele din folderul
proiectului „1. Porneste aplicatia.bat” și „2. Ruleaza testele.bat”, care găsesc
(sau instalează) Python și apoi apelează acest script.

Folosește doar biblioteca standard Python, deci merge înainte de a instala ceva.

Ce face, pe rând:
    1. creează mediul virtual „.venv” (doar prima dată);
    2. instalează dependențele din requirements.txt (doar când s-au schimbat);
    3. recreează baza de date cu utilizatorii de test și câteva tichete demonstrative;
    4. pornește serverul Flask pe primul port liber începând de la 5000;
    5. deschide pagina de login în browserul implicit.

Utilizare din terminal (din folderul proiectului):
    python scripts/prezentare.py               # pornește aplicația
    python scripts/prezentare.py --pastreaza   # nu reseta datele (păstrează tichetele create)
    python scripts/prezentare.py --teste       # rulează testele automate și afișează rezultatul

Oprire: închiderea ferestrei sau Ctrl+C.
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

CONTURI = [
    ("Angajat", "angajat@technova.test"),
    ("Tehnician", "tehnician@technova.test"),
    ("Manager", "manager@technova.test"),
]
PAROLA = "parola123"


def pas(mesaj):
    """Afișează un pas al pornirii, ca să se vadă ce se întâmplă."""
    print(f"\n==> {mesaj}", flush=True)


def chenar(*randuri):
    """Afișează un mesaj important într-un chenar, ca să iasă în evidență."""
    print("\n" + "=" * 62)
    for rand in randuri:
        print(f"  {rand}")
    print("=" * 62 + "\n", flush=True)


def python_din_venv():
    """Calea către Python-ul din .venv (diferă între Windows și Linux/macOS)."""
    if os.name == "nt":
        return VENV / "Scripts" / "python.exe"
    return VENV / "bin" / "python"


def instaleaza(fisier_cerinte, descriere):
    """Instalează pachetele din fișierul dat, doar dacă nu au fost deja instalate.

    Marcajul (un fișier gol) stă lângă Python-ul din .venv: dacă cineva copiază un .venv
    făcut pe alt sistem de operare, marcajul lipsește și instalarea se reface.
    """
    cerinte = RADACINA / fisier_cerinte
    marcaj = python_din_venv().parent / f".instalat-{cerinte.stem}"
    if marcaj.exists() and marcaj.stat().st_mtime >= cerinte.stat().st_mtime:
        return
    pas(f"Instalez {descriere} (doar prima dată, are nevoie de internet)")
    subprocess.run(
        [python_din_venv(), "-m", "pip", "install", "-q", "--disable-pip-version-check",
         "-r", cerinte],
        check=True,
    )
    marcaj.touch()


def pregateste_mediul():
    """Creează .venv și instalează dependențele aplicației, doar dacă e nevoie."""
    # Scriptul poate fi pornit cu un Python vechi al sistemului, deci verificăm versiunea.
    if sys.version_info < (3, 12):  # noqa: UP036
        sys.exit("Este nevoie de Python 3.12 sau mai nou.")

    if not python_din_venv().exists():
        pas("Pregătesc aplicația pentru prima pornire (durează 1-2 minute)")
        venv.create(VENV, with_pip=True)
    instaleaza("requirements.txt", "bibliotecile aplicației")


def pregateste_datele(pastreaza):
    """Recreează baza de date cu datele demo, cu excepția cazului --pastreaza."""
    baza = RADACINA / "instance" / "helpdesk.db"
    if pastreaza and baza.exists():
        pas("Păstrez datele existente (--pastreaza)")
        return
    pas("Creez datele de test: 3 conturi și 4 tichete demonstrative")
    subprocess.run([python_din_venv(), "seed.py", "--demo"], cwd=RADACINA, check=True)


def port_liber(start=5000):
    """Primul port liber începând cu „start” (dacă 5000 e ocupat de alt program)."""
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


def porneste_aplicatia(pastreaza):
    """Pregătește totul, pornește serverul și deschide browserul; rulează până la oprire."""
    pregateste_mediul()
    pregateste_datele(pastreaza)

    port = port_liber()
    adresa = f"http://127.0.0.1:{port}/login"
    pas("Pornesc aplicația")
    server = subprocess.Popen(
        [python_din_venv(), "-m", "flask", "--app", "app", "run", "--port", str(port)],
        cwd=RADACINA,
    )
    try:
        if not asteapta_serverul(port, server):
            sys.exit("Aplicația nu a pornit. Fă o poză acestei ferestre și trimite-o echipei.")
        webbrowser.open(adresa)
        chenar(
            "APLICAȚIA ESTE PORNITĂ – s-a deschis în browser.",
            f"Dacă browserul nu s-a deschis, scrie în el:  {adresa}",
            "",
            "Conturi de test:",
            *(f"  {rol:<10} {email}" for rol, email in CONTURI),
            f"Parola pentru toate:  {PAROLA}",
            "",
            "NU închide această fereastră cât timp prezinți.",
            "La final, închide fereastra (X) ca să oprești aplicația.",
        )
        server.wait()
    except KeyboardInterrupt:
        print("\nOpresc aplicația...")
    finally:
        if server.poll() is None:
            server.terminate()
            server.wait()


def ruleaza_testele():
    """Instalează pytest (doar prima dată) și rulează testele automate."""
    pregateste_mediul()
    instaleaza("requirements-dev.txt", "uneltele de testare (pytest, Ruff)")
    pas("Rulez testele automate")
    rezultat = subprocess.run([python_din_venv(), "-m", "pytest", "-q"], cwd=RADACINA)
    if rezultat.returncode == 0:
        chenar("REZULTAT: TOATE TESTELE AU TRECUT.",
               "Rândul cu „passed” de mai sus arată câte teste au rulat.")
    else:
        chenar("REZULTAT: UNELE TESTE AU EȘUAT.",
               "Fă o poză acestei ferestre și trimite-o echipei.")
    return rezultat.returncode


def main():
    os.chdir(RADACINA)
    if "--teste" in sys.argv:
        sys.exit(ruleaza_testele())
    porneste_aplicatia(pastreaza="--pastreaza" in sys.argv)


if __name__ == "__main__":
    main()
