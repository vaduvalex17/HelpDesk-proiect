# Tehnologii utilizate – HelpDesk IT

**Versiune:** 1.0 (Raport 1 – Propunere)  
**Issue:** #7

Aplicația folosește Python 3.12 cu Flask pe server, SQLite prin SQLAlchemy pentru date și Bootstrap 5 în interfață. Toate uneltele sunt gratuite și open-source, cu excepția serviciilor GitHub și Render, folosite în planul gratuit.

| Strat | Tehnologie | Ce este | De ce am ales-o |
|---|---|---|---|
| Limbaj | **Python 3.12** | Limbaj de programare de nivel înalt | Sintaxă clară, ecosistem bogat pentru aplicații web și testare |
| Backend | **Flask** | Micro-framework web pentru Python | Ușor de învățat, suficient pentru o aplicație de mărime medie; extensii pentru login (Flask-Login) și email (Flask-Mail) |
| Acces la date | **SQLAlchemy** | ORM: lucrează cu tabelele ca și cu clase Python | Elimină SQL-ul scris de mână și permite schimbarea ulterioară a bazei de date |
| Bază de date | **SQLite** | Bază de date relațională într-un singur fișier | Fără server de instalat; suficientă pentru 1.000 de tichete (N1) |
| Interfață | **Jinja2 + Bootstrap 5** | Șabloane HTML generate pe server + bibliotecă CSS | Design responsive pe calculator și telefon fără CSS scris de la zero (N4) |
| Grafice | **Chart.js** | Bibliotecă JavaScript pentru grafice | Graficele dashboard-ului managerului (F11) cu puțin cod |
| Testare | **pytest** | Framework de teste automate | Teste scurte și lizibile, cu bază de date temporară (N5) |
| Calitate cod | **Ruff** | Linter și formatter pentru Python | Foarte rapid; păstrează codul uniform (N5) |
| Versionare | **Git + GitHub** | Control al versiunilor + găzduire repository | Issues, board Kanban, pull requests și milestones asigură trasabilitatea (N7) |
| Integrare continuă | **GitHub Actions** | Rulează automat linterul și testele | Niciun cod nu intră în `main` fără teste trecute (N5) |
| Containerizare | **Docker** | Rulează aplicația într-un container izolat | Aceeași rulare pe orice calculator; plan B pentru demo (N6) |
| Găzduire | **Render** | Platformă cloud pentru aplicații web | Deploy direct din GitHub, plan gratuit (N6) |
| Diagrame | **PlantUML** | Diagrame UML descrise în text | Diagramele sunt versionate în Git, la fel ca și codul |
| Editor | **Visual Studio Code** | Editor de cod | Extensii pentru Python, Git și PlantUML |

## Arhitectura pe scurt

```
Browser ──HTTP──> Flask (rute + șabloane Jinja2) ──> SQLAlchemy ──> SQLite
                        │
                        └── Flask-Login (sesiune), Flask-Mail (notificări, opțional)
```
