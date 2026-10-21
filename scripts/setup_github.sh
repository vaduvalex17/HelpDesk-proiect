#!/usr/bin/env bash
# Creează în repository-ul GitHub label-urile, milestone-urile și issue-urile #1–#36 din ROADMAP.md.
# Rulează O SINGURĂ DATĂ, pe un repository nou, ÎNAINTE de orice issue sau pull request
# (issue-urile și PR-urile împart aceeași numerotare pe GitHub).
# Utilizare:  bash scripts/setup_github.sh <utilizator>/helpdesk-it
set -euo pipefail
REPO="${1:?Utilizare: bash scripts/setup_github.sh <utilizator>/helpdesk-it}"

echo "== Label-uri"
label() { gh label create "$1" --repo "$REPO" --color "$2" --description "$3" --force; }
label "cerință"        "1D76DB" "Funcționalitate cerută de client"
label "documentație"   "0E8A16" "Rapoarte, diagrame, manuale"
label "infrastructură" "5319E7" "Repository, CI, Docker, deploy"
label "bug"            "D73A4A" "Eroare de corectat"
label "must"           "B60205" "MoSCoW: obligatoriu"
label "should"         "FBCA04" "MoSCoW: de dorit"
label "could"          "C2E0C6" "MoSCoW: bonus, opțional"

echo "== Milestone-uri"
milestone() {
  if ! gh api "repos/$REPO/milestones?state=all" --jq '.[].title' | grep -qxF "$1"; then
    gh api "repos/$REPO/milestones" -f title="$1" -f due_on="$2T23:59:59Z" -f description="$3" >/dev/null
  fi
}
milestone "0 – Inițiere" "2026-10-23" "Carta proiectului, minuta ședinței, raportul preliminar"
milestone "1 – Raport 1: Propunere" "2026-11-01" "Specificații, tehnologii, diagrama cazurilor de utilizare"
milestone "2 – Raport 2: Proiectare și MVP" "2026-11-29" "Diagrame de proiectare + implementare minimală funcțională"
milestone "3 – Final" "2027-01-15" "Aplicația completă, documentație, prezentare"

echo "== Issue-uri"
issue() { # $1 = numărul așteptat, $2 = titlu, $3 = milestone, $4 = label-uri; corpul vine pe stdin
  local url nr
  url=$(gh issue create --repo "$REPO" --title "$2" --milestone "$3" --label "$4" --body-file -)
  nr="${url##*/}"
  if [ "$nr" != "$1" ]; then
    echo "ATENȚIE: issue-ul '$2' a primit #$nr în loc de #$1 – numerotarea din ROADMAP.md nu mai corespunde." >&2
    exit 1
  fi
  echo "  #$nr $2"
}

issue 1 "Carta proiectului și minuta ședinței de inițiere" "0 – Inițiere" "documentație,must" <<'EOF'
**Când:** 22–23 oct

**Ce faci:**
- [x] Ședința de inițiere cu clientul (minuta)
- [x] Completarea cartei proiectului pe șablonul cursului
- [x] Urcarea fișierelor în `docs/`

**Gata când:** `docs/Carta proiectului - HelpDesk IT.pdf` și `docs/Minuta intalnirii - HelpDesk IT.pdf` există în repository.

**De ce:** Carta „autorizează” proiectul: scop, obiective, echipă, termene, buget. Toate celelalte documente pornesc de la ea.

_Detalii: ROADMAP.md_
EOF
issue 2 "Raport preliminar: Tehnologii și instrumente pentru dezvoltarea programelor" "0 – Inițiere" "documentație,must" <<'EOF'
**Când:** 21–23 oct

**Ce faci:**
- [x] Redactare raport (introducere, istoric, categorii, concluzii, referințe)
- [x] Export PDF și încărcare pe Classroom
- [x] Urcare în `docs/`

**Gata când:** Raportul e predat și se află în `docs/`.

**De ce:** Primul livrabil notat (20%). Justifică alegerea uneltelor folosite în proiect.

_Detalii: ROADMAP.md_
EOF
issue 3 "Creează repository-ul GitHub" "1 – Raport 1: Propunere" "infrastructură,must" <<'EOF'
**Când:** 24 oct

**Ce faci:**
- [ ] Pe github.com: New repository → `helpdesk-it`, bifează „Add README”, `.gitignore` = Python, licență MIT
- [ ] `git clone` pe calculator
- [ ] Copiază folderul `docs/` și fișierul `ROADMAP.md`
- [ ] `git add . && git commit -m "docs: carta, minuta, raport preliminar (#1 #2)"` și `git push`
- [ ] Invită clientul/profesorul ca colaboratori (Settings → Collaborators) – acțiune din minută

**Gata când:** Repository-ul e vizibil online și conține documentele de inițiere.

**De ce:** Repository-ul este „sursa adevărului”: tot ce faci de acum lasă urme aici.

_Detalii: ROADMAP.md_
EOF
issue 4 "Configurează board-ul Kanban, label-urile și milestone-urile" "1 – Raport 1: Propunere" "infrastructură,must" <<'EOF'
**Când:** 24–25 oct

**Ce faci:**
- [ ] Instalează GitHub CLI (`gh`) și rulează `gh auth login`
- [ ] Rulează `bash scripts/setup_github.sh <utilizator>/helpdesk-it` (creează label-uri, milestones și toate issue-urile)
- [ ] Pe GitHub: Projects → New project → Board, cu coloanele Todo / In progress / Done
- [ ] Adaugă toate issue-urile în board (Add items → selectează repository-ul)
- [ ] În setările proiectului activează workflow-urile „Item closed → Done” și „Pull request merged → Done”

**Gata când:** Board-ul arată toate issue-urile, fiecare cu milestone și label-uri.

**De ce:** Board-ul este planul vizibil al proiectului; profesorul vede progresul fără să întrebe.

_Detalii: ROADMAP.md_
EOF
issue 5 "Specificațiile aplicației (cerințe funcționale și nefuncționale)" "1 – Raport 1: Propunere" "cerință,documentație,must" <<'EOF'
**Când:** 26–28 oct

**Ce faci:**
- [ ] Creează `docs/specificatii.md`
- [ ] Scrie actorii: Angajat, Tehnician IT, Manager IT
- [ ] Scrie cerințele funcționale F1–F12 (ex.: F1 Autentificare, F2 Creare tichet, F3 Lista tichetelor mele …)
- [ ] Scrie cerințele nefuncționale (pagini sub 2 s, parole criptate, date de test fictive – GDPR, interfață în română)
- [ ] Commit `docs: specificatii (#5)` → PR → merge

**Gata când:** Fiecare cerință are un cod (F1, F2 …) folosit mai departe în issues și teste.

**De ce:** Codurile cerințelor sunt baza trasabilității: cerință → issue → cod → test.

_Detalii: ROADMAP.md_
EOF
issue 6 "Diagrama cazurilor de utilizare (PlantUML)" "1 – Raport 1: Propunere" "documentație,must" <<'EOF'
**Când:** 28–29 oct

**Ce faci:**
- [ ] Creează `docs/diagrame/use-case.puml`
- [ ] Desenează cei 3 actori și cazurile de utilizare (Deschide tichet, Preia tichet, Atribuie tichet, Schimbă status, Comentează, Vezi statistici, Administrează utilizatori)
- [ ] Generează imaginea (extensia PlantUML din VS Code sau plantuml.com) → `use-case.png`
- [ ] Commit `docs: diagrama cazurilor de utilizare (#6)`

**Gata când:** Diagrama acoperă toate cerințele F1–F12.

**De ce:** Cerută explicit în Raportul 1. Fiind text, diagrama e versionată ca și codul.

_Detalii: ROADMAP.md_
EOF
issue 7 "Descrierea tehnologiilor folosite" "1 – Raport 1: Propunere" "documentație,must" <<'EOF'
**Când:** 29–30 oct

**Ce faci:**
- [ ] Listează tehnologiile: Python, Flask, SQLAlchemy, SQLite, Bootstrap, pytest, Ruff, GitHub Actions, Docker, Render
- [ ] Pentru fiecare: o frază „ce este” + o frază „de ce l-am ales”
- [ ] Poți refolosi tabelul 3 din raportul preliminar

**Gata când:** Secțiunea „Tehnologii” e scrisă.

**De ce:** Cerută explicit în Raportul 1.

_Detalii: ROADMAP.md_
EOF
issue 8 "Redactează și predă Raportul 1" "1 – Raport 1: Propunere" "documentație,must" <<'EOF'
**Când:** 30 oct – 1 nov

**Ce faci:**
- [ ] Reunește specificațiile, tehnologiile și diagrama într-un document
- [ ] Adaugă o captură de ecran cu board-ul GitHub (dovada de trasabilitate)
- [ ] Export PDF în `docs/` → commit → predare pe Classroom
- [ ] Creează tag-ul: `git tag v0.1-propunere && git push --tags`

**Gata când:** Raportul 1 e predat, tag-ul `v0.1-propunere` există.

**De ce:** Tag-ul marchează exact starea proiectului la predare.

_Detalii: ROADMAP.md_
EOF
issue 9 "Modelul bazei de date (ERD)" "2 – Raport 2: Proiectare și MVP" "documentație,must" <<'EOF'
**Când:** 2–4 nov

**Ce faci:**
- [ ] Tabelele: `User` (nume, email, parolă hash, rol), `Category`, `Ticket` (titlu, descriere, prioritate, status, autor, tehnician, categorie, date), `Comment`, `TicketHistory`
- [ ] Desenează relațiile (un User are mai multe Ticket etc.) în `docs/diagrame/erd.puml`
- [ ] Commit `docs: ERD (#9)`

**Gata când:** Diagrama ERD conține cele 5 tabele și relațiile lor.

**De ce:** Baza de date se proiectează înainte de cod, ca să nu o refaci ulterior.

_Detalii: ROADMAP.md_
EOF
issue 10 "Diagrama de arhitectură și structura folderelor" "2 – Raport 2: Proiectare și MVP" "documentație,must" <<'EOF'
**Când:** 4–6 nov

**Ce faci:**
- [ ] Desenează: Browser → Flask (rute + șabloane) → SQLAlchemy → SQLite
- [ ] Scrie structura folderelor din ROADMAP în `docs/arhitectura.md`
- [ ] Commit `docs: arhitectura (#10)`

**Gata când:** Documentul explică pe ce strat stă fiecare fișier.

**De ce:** Necesară pentru partea de „proiectare” din Raportul 2.

_Detalii: ROADMAP.md_
EOF
issue 11 "Machete (wireframes) pentru ecranele principale" "2 – Raport 2: Proiectare și MVP" "documentație,should" <<'EOF'
**Când:** 6–8 nov

**Ce faci:**
- [ ] În draw.io sau pe hârtie: Login, Lista tichetelor, Tichet nou, Detaliu tichet, Dashboard
- [ ] Salvează imaginile în `docs/machete/`
- [ ] Commit `docs: machete interfata (#11)`

**Gata când:** 5 machete în `docs/machete/`.

**De ce:** Arăți clientului cum va arăta aplicația înainte s-o construiești.

_Detalii: ROADMAP.md_
EOF
issue 12 "Scheletul aplicației Flask" "2 – Raport 2: Proiectare și MVP" "infrastructură,must" <<'EOF'
**Când:** 9–10 nov

**Ce faci:**
- [ ] `python -m venv .venv` și activează mediul virtual
- [ ] `pip install flask flask-sqlalchemy flask-login` → `pip freeze > requirements.txt`
- [ ] Creează `app/__init__.py` cu funcția `create_app()` și o rută `/` care afișează „HelpDesk IT”
- [ ] Rulează `flask --app app run` și deschide http://127.0.0.1:5000
- [ ] Commit `feat: schelet aplicatie Flask (#12)`

**Gata când:** Pagina de start se deschide în browser.

**De ce:** Primul cod care rulează; toate funcționalitățile se vor adăuga peste el.

_Detalii: ROADMAP.md_
EOF
issue 13 "Linter (Ruff) și teste (pytest) – primul test" "2 – Raport 2: Proiectare și MVP" "infrastructură,must" <<'EOF'
**Când:** 10–11 nov

**Ce faci:**
- [ ] `pip install ruff pytest` și adaugă-le în `requirements.txt`
- [ ] Creează `tests/test_home.py`: pagina `/` răspunde cu codul 200
- [ ] Rulează `ruff check .` și `pytest` – ambele trebuie să treacă
- [ ] Commit `test: primul test (#13)`

**Gata când:** `pytest` afișează „1 passed”.

**De ce:** Testele dovedesc că aplicația funcționează; linterul păstrează codul curat.

_Detalii: ROADMAP.md_
EOF
issue 14 "Integrare continuă cu GitHub Actions" "2 – Raport 2: Proiectare și MVP" "infrastructură,must" <<'EOF'
**Când:** 11–12 nov

**Ce faci:**
- [ ] Creează `.github/workflows/ci.yml`: la fiecare push/PR instalează Python, rulează `ruff check .` și `pytest`
- [ ] Push → verifică tab-ul „Actions” (bifă verde)
- [ ] Adaugă badge-ul CI în README
- [ ] Commit `ci: workflow lint + teste (#14)`

**Gata când:** Fiecare PR afișează automat bifa verde/roșie.

**De ce:** De acum, nicio modificare nu intră în `main` fără teste trecute – dovadă clară de calitate.

_Detalii: ROADMAP.md_
EOF
issue 15 "Modelele bazei de date și datele de test" "2 – Raport 2: Proiectare și MVP" "cerință,must" <<'EOF'
**Când:** 12–15 nov

**Ce faci:**
- [ ] Scrie în `app/models.py` clasele `User`, `Category`, `Ticket` după ERD (#9)
- [ ] Creează `seed.py`: 3 utilizatori (câte unul pe rol), 4 categorii (hardware, software, rețea, conturi)
- [ ] Rulează `python seed.py` și verifică datele
- [ ] Commit `feat: modele + seed (#15)`

**Gata când:** Baza `helpdesk.db` conține utilizatorii și categoriile de test.

**De ce:** Datele fictive permit testarea fără date personale reale (GDPR – constrângere din cartă).

_Detalii: ROADMAP.md_
EOF
issue 16 "Autentificare (login / logout) – F1" "2 – Raport 2: Proiectare și MVP" "cerință,must" <<'EOF'
**Când:** 16–17 nov

**Ce faci:**
- [ ] Pagina `/login` cu email și parolă
- [ ] Parolele se verifică cu `check_password_hash` (nu se salvează niciodată în clar)
- [ ] Flask-Login ține minte utilizatorul; buton Logout
- [ ] Paginile interne sunt protejate cu `@login_required`
- [ ] Commit `feat: autentificare (#16)`

**Gata când:** Te poți loga cu un utilizator din seed; fără login ești redirecționat la `/login`.

**De ce:** Fiecare tichet trebuie să aibă un autor, deci trebuie să știm cine e logat.

_Detalii: ROADMAP.md_
EOF
issue 17 "Creare tichet – F2" "2 – Raport 2: Proiectare și MVP" "cerință,must" <<'EOF'
**Când:** 18–19 nov

**Ce faci:**
- [ ] `git switch -c feature/17-creare-tichet`
- [ ] Pagina `/tickets/new`: titlu, descriere, categorie, prioritate (Scăzută / Medie / Ridicată / Critică)
- [ ] La salvare: status „Nou”, autor = utilizatorul logat
- [ ] Commit `feat: formular creare tichet (#17)`
- [ ] Test + commit `test: creare tichet (#17)` → PR „Closes #17”

**Gata când:** Tichetul creat apare în baza de date cu status „Nou”.

**De ce:** Funcționalitatea principală a aplicației.

_Detalii: ROADMAP.md_
EOF
issue 18 "Lista „Tichetele mele” – F3" "2 – Raport 2: Proiectare și MVP" "cerință,must" <<'EOF'
**Când:** 20–21 nov

**Ce faci:**
- [ ] Pagina `/tickets` cu un tabel: număr, titlu, prioritate, status, dată
- [ ] Angajatul își vede doar tichetele lui
- [ ] Culori Bootstrap pentru prioritate (badge-uri)
- [ ] Commit `feat: lista tichete (#18)`

**Gata când:** Fiecare utilizator își vede doar propriile tichete.

**De ce:** Angajatul urmărește statusul cererilor sale – nevoia principală din minută.

_Detalii: ROADMAP.md_
EOF
issue 19 "Pagina de detaliu a tichetului – F4" "2 – Raport 2: Proiectare și MVP" "cerință,must" <<'EOF'
**Când:** 21–22 nov

**Ce faci:**
- [ ] Ruta `/tickets/<id>` afișează toate câmpurile
- [ ] Un angajat nu poate deschide tichetul altcuiva (cod 403)
- [ ] Commit `feat: detaliu tichet (#19)`

**Gata când:** Click pe un tichet din listă deschide pagina lui.

**De ce:** Locul unde vor apărea ulterior statusul, istoricul și comentariile.

_Detalii: ROADMAP.md_
EOF
issue 20 "Teste pentru funcționalitățile MVP" "2 – Raport 2: Proiectare și MVP" "infrastructură,must" <<'EOF'
**Când:** 23–25 nov

**Ce faci:**
- [ ] Fixture pytest cu o bază de date temporară
- [ ] Teste: login corect/greșit, creare tichet, „tichetele mele” nu arată tichetele altora, 403 pe tichet străin
- [ ] Commit `test: teste MVP (#20)`

**Gata când:** CI verde, minimum 6 teste.

**De ce:** Dovada că MVP-ul funcționează – se prezintă în Raportul 2.

_Detalii: ROADMAP.md_
EOF
issue 21 "Redactează și predă Raportul 2" "2 – Raport 2: Proiectare și MVP" "documentație,must" <<'EOF'
**Când:** 26–29 nov

**Ce faci:**
- [ ] Include: ERD, arhitectura, machetele, capturi de ecran din aplicație
- [ ] Secțiune „Trasabilitate”: captură board, listă de PR-uri, istoricul CI
- [ ] Export PDF în `docs/` → predare
- [ ] `git tag v0.2-mvp && git push --tags`

**Gata când:** Raportul 2 e predat, tag-ul `v0.2-mvp` există.

**De ce:** Al doilea livrabil intermediar (20%).

_Detalii: ROADMAP.md_
EOF
issue 22 "Roluri și permisiuni – F5" "3 – Final" "cerință,must" <<'EOF'
**Când:** 30 nov – 2 dec

**Ce faci:**
- [ ] Decorator `role_required("tehnician", "manager")`
- [ ] Meniul afișează doar paginile permise rolului
- [ ] Teste pentru accesul interzis
- [ ] Commit `feat: roluri si permisiuni (#22)`

**Gata când:** Un angajat primește 403 pe paginile de tehnician/manager.

**De ce:** Cei 3 actori din diagrama cazurilor de utilizare au drepturi diferite.

_Detalii: ROADMAP.md_
EOF
issue 23 "Panoul tehnicianului: preluare tichete – F6" "3 – Final" "cerință,must" <<'EOF'
**Când:** 3–6 dec

**Ce faci:**
- [ ] Pagina `/tech`: tichetele neatribuite + tichetele mele
- [ ] Butonul „Preia” setează tehnicianul și statusul „În lucru”
- [ ] Commit `feat: panou tehnician (#23)`

**Gata când:** Un tehnician poate prelua un tichet nou.

**De ce:** Fluxul principal: cerere → preluare → rezolvare.

_Detalii: ROADMAP.md_
EOF
issue 24 "Managerul atribuie tichete – F7" "3 – Final" "cerință,must" <<'EOF'
**Când:** 7–9 dec

**Ce faci:**
- [ ] Pe pagina tichetului, managerul alege un tehnician dintr-o listă
- [ ] Test pentru atribuire
- [ ] Commit `feat: atribuire tichet (#24)`

**Gata când:** Managerul poate atribui orice tichet oricărui tehnician.

**De ce:** Cerință din minută: managerul distribuie munca.

_Detalii: ROADMAP.md_
EOF
issue 25 "Schimbare status și istoric – F8" "3 – Final" "cerință,must" <<'EOF'
**Când:** 10–13 dec

**Ce faci:**
- [ ] Statusuri: Nou → În lucru → Rezolvat → Închis
- [ ] Fiecare schimbare se salvează în `TicketHistory` (cine, când, din ce în ce)
- [ ] Istoricul se afișează pe pagina tichetului
- [ ] Commit `feat: status + istoric (#25)`

**Gata când:** Pagina tichetului arată cronologia completă.

**De ce:** Trasabilitate și în aplicație, nu doar în proces – obiectiv din cartă.

_Detalii: ROADMAP.md_
EOF
issue 26 "Comentarii pe tichet – F9" "3 – Final" "cerință,must" <<'EOF'
**Când:** 14–17 dec

**Ce faci:**
- [ ] Modelul `Comment` + formular pe pagina tichetului
- [ ] Afișare: autor, dată, text
- [ ] Commit `feat: comentarii (#26)`

**Gata când:** Angajatul și tehnicianul pot discuta pe tichet.

**De ce:** Înlocuiește emailurile și telefoanele pierdute (problema clientului).

_Detalii: ROADMAP.md_
EOF
issue 27 "Filtrare și căutare tichete – F10" "3 – Final" "cerință,should" <<'EOF'
**Când:** 18–20 dec

**Ce faci:**
- [ ] Filtre după status, prioritate, categorie
- [ ] Căutare în titlu
- [ ] Commit `feat: filtrare si cautare (#27)`

**Gata când:** Lista se filtrează corect.

**De ce:** Opțional (should): dacă apar întârzieri, se amână primul.

_Detalii: ROADMAP.md_
EOF
issue 28 "Dashboard cu statistici – F11" "3 – Final" "cerință,must" <<'EOF'
**Când:** 21–28 dec

**Ce faci:**
- [ ] Pagina `/dashboard` doar pentru manager
- [ ] Grafice Chart.js: tichete pe categorie, pe status, pe tehnician
- [ ] Commit `feat: dashboard (#28)`

**Gata când:** Managerul vede 3 grafice cu date reale din baza de date.

**De ce:** Obiectiv din cartă: rapoarte pentru managerul IT.

_Detalii: ROADMAP.md_
EOF
issue 29 "Alertă SLA – tichete fără reacție peste 4 ore" "3 – Final" "cerință,must" <<'EOF'
**Când:** 29 dec – 3 ian

**Ce faci:**
- [ ] Funcție care găsește tichetele „Nou” mai vechi de 4 ore
- [ ] Evidențiere cu roșu în listă și pe dashboard
- [ ] Test cu un tichet „îmbătrânit” artificial
- [ ] Commit `feat: alerta SLA (#29)`

**Gata când:** Tichetele întârziate apar marcate.

**De ce:** Obiectiv din cartă: primă reacție sub 4 ore lucrătoare.

_Detalii: ROADMAP.md_
EOF
issue 30 "Administrare utilizatori și categorii – F12" "3 – Final" "cerință,must" <<'EOF'
**Când:** 4–6 ian

**Ce faci:**
- [ ] Pagini pentru manager: listă, adăugare, dezactivare utilizatori; listă/adăugare categorii
- [ ] Commit `feat: administrare (#30)`

**Gata când:** Managerul poate adăuga un utilizator nou care se poate loga.

**De ce:** Clientul trebuie să poată folosi aplicația fără programator.

_Detalii: ROADMAP.md_
EOF
issue 31 "Notificări email (opțional)" "3 – Final" "cerință,could" <<'EOF'
**Când:** 6–7 ian

**Ce faci:**
- [ ] Flask-Mail: email la atribuire și la rezolvare
- [ ] În dezvoltare, emailurile se afișează în consolă
- [ ] Commit `feat: notificari email (#31)`

**Gata când:** Atribuirea unui tichet generează un email.

**De ce:** Bonus (could) – primul tăiat dacă timpul nu ajunge.

_Detalii: ROADMAP.md_
EOF
issue 32 "Docker: Dockerfile și docker-compose" "3 – Final" "infrastructură,must" <<'EOF'
**Când:** 7–8 ian

**Ce faci:**
- [ ] `Dockerfile` bazat pe `python:3.12-slim`, pornire cu gunicorn
- [ ] `docker-compose.yml` cu volum pentru baza de date
- [ ] `docker compose up` → aplicația merge pe http://localhost:8000
- [ ] Commit `chore: docker (#32)`

**Gata când:** Aplicația pornește identic pe orice calculator cu Docker.

**De ce:** Planul B pentru demo, conform riscului din cartă (Render poate „adormi”).

_Detalii: ROADMAP.md_
EOF
issue 33 "Deploy pe Render" "3 – Final" "infrastructură,must" <<'EOF'
**Când:** 9–10 ian

**Ce faci:**
- [ ] Cont Render → New Web Service → conectează repository-ul
- [ ] Setează comanda de pornire și variabila `SECRET_KEY`
- [ ] Pune link-ul live în README
- [ ] Commit `docs: link aplicatie live (#33)`

**Gata când:** Aplicația e accesibilă online.

**De ce:** Livrabil din cartă: „cod GitHub + link live”.

_Detalii: ROADMAP.md_
EOF
issue 34 "Testare finală și corectarea erorilor" "3 – Final" "bug,must" <<'EOF'
**Când:** 11–12 ian

**Ce faci:**
- [ ] Parcurge toate cazurile de utilizare cu fiecare rol
- [ ] Fiecare problemă găsită → issue nou cu label `bug`
- [ ] Rezolvă bug-urile pe branch-uri `fix/…`

**Gata când:** Niciun bug deschis cu label `must`; CI verde.

**De ce:** Bug-urile documentate ca issues sunt și ele trasabilitate.

_Detalii: ROADMAP.md_
EOF
issue 35 "Documentație și manual de utilizare" "3 – Final" "documentație,must" <<'EOF'
**Când:** 12–13 ian

**Ce faci:**
- [ ] README: descriere, instalare, rulare, testare, Docker, link live
- [ ] `docs/manual-utilizare.md` cu capturi de ecran pentru fiecare rol
- [ ] Commit `docs: manual (#35)`

**Gata când:** Un om nou poate instala și folosi aplicația doar citind documentația.

**De ce:** Face parte din „predarea către client”.

_Detalii: ROADMAP.md_
EOF
issue 36 "Raport final și prezentare" "3 – Final" "documentație,must" <<'EOF'
**Când:** 13–15 ian

**Ce faci:**
- [ ] Raport final: rezumat, cerințe vs. realizat, diagrame, trasabilitate (statistici din GitHub: issues, PR-uri, commit-uri)
- [ ] Prezentare de 10 minute + demo live
- [ ] `git tag v1.0 && git push --tags`

**Gata când:** Proiect predat, tag `v1.0`.

**De ce:** 40% din nota finală.

_Detalii: ROADMAP.md_
EOF

echo "== Închid issue-urile deja finalizate (#1–#3)"
for n in 1 2 3; do gh issue close "$n" --repo "$REPO" --reason completed --comment "Finalizat – vezi docs/ și istoricul de commit-uri."; done
echo "Gata. Pasul următor: issue #4 – creează board-ul în GitHub Projects și adaugă issue-urile."
