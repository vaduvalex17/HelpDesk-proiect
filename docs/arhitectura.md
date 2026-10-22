# Arhitectura aplicației HelpDesk IT

**Issue:** #10

Aplicația are trei straturi, într-un singur proces Flask: prezentare (rute + șabloane), logică și acces la date (modele SQLAlchemy), stocare (SQLite).

```
┌──────────┐   HTTP    ┌───────────────────────────────────────────┐
│ Browser  │ ────────> │ Flask                                     │
│ (HTML,   │ <──────── │  ├─ Blueprint-uri: auth, tickets, admin   │
│ Bootstrap│           │  ├─ Șabloane Jinja2 (templates/)          │
│ Chart.js)│           │  └─ Flask-Login (sesiune, roluri)         │
└──────────┘           └───────────────┬───────────────────────────┘
                                       │ obiecte Python
                               ┌───────▼────────┐
                               │ SQLAlchemy ORM │  app/models.py
                               └───────┬────────┘
                                       │ SQL
                               ┌───────▼────────┐
                               │ SQLite         │  instance/helpdesk.db
                               └────────────────┘
```

## Structura folderelor

| Cale | Strat | Rol | Issue-uri |
|---|---|---|---|
| `app/__init__.py` | Configurare | `create_app()`: creează aplicația, conectează extensiile și blueprint-urile | #12 |
| `app/extensions.py` | Configurare | Instanțele `db` (SQLAlchemy) și `login_manager` | #12, #16 |
| `app/models.py` | Date | `User`, `Category`, `Ticket`, `Comment`, `TicketHistory` (vezi `diagrame/erd.puml`) | #15, #25, #26 |
| `app/auth/` | Prezentare | Login / logout | #16 |
| `app/tickets/` | Prezentare | Creare, listă, detaliu, preluare, status, comentarii, filtrare | #17–#19, #23–#27 |
| `app/admin/` | Prezentare | Dashboard, utilizatori, categorii | #28–#30 |
| `app/templates/` | Prezentare | Pagini HTML (Jinja2 + Bootstrap 5) | toate |
| `app/static/` | Prezentare | CSS și JavaScript propriu | toate |
| `tests/` | Calitate | Teste pytest | #13, #20 … |
| `seed.py` | Date | Date fictive de test (GDPR – N3) | #15 |
| `.github/workflows/ci.yml` | Calitate | Ruff + pytest la fiecare push / PR | #14 |
| `Dockerfile`, `docker-compose.yml` | Livrare | Rulare în container | #32 |

## Fluxul unei cereri (exemplu: F2 – Creare tichet)

1. Browserul trimite `POST /tickets/new` cu formularul completat.
2. Flask-Login verifică sesiunea; dacă utilizatorul nu e autentificat, îl trimite la `/login`.
3. Ruta din `app/tickets/` validează datele și creează un obiect `Ticket` cu status „Nou”.
4. SQLAlchemy salvează tichetul în SQLite.
5. Ruta redirecționează la pagina tichetului, generată din șablonul Jinja2.
