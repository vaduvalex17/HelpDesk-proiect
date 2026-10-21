# Specificațiile aplicației HelpDesk IT

**Client:** TechNova Solutions SRL  
**Versiune:** 1.0 (Raport 1 – Propunere)  
**Issue:** #5

## 1. Scopul aplicației
HelpDesk IT este o aplicație web prin care angajații TechNova raportează problemele tehnice sub formă de **tichete**, iar departamentul IT le preia, le rezolvă și le urmărește până la închidere. Aplicația înlocuiește cererile trimise azi prin email și telefon, care se pierd și nu pot fi urmărite.

## 2. Actori

| Actor | Descriere | Ce poate face, pe scurt |
|---|---|---|
| **Angajat** | Orice angajat TechNova care are o problemă tehnică. | Deschide tichete, își vede propriile tichete, comentează pe ele. |
| **Tehnician IT** | Membru al echipei IT care rezolvă tichetele. | Preia tichete, schimbă statusul, comentează. |
| **Manager IT** | Coordonatorul echipei IT. | Tot ce poate tehnicianul, plus atribuire, statistici și administrare. |

## 3. Cerințe funcționale

Prioritatea folosește metoda MoSCoW: **Must** (obligatoriu), **Should** (de dorit), **Could** (bonus).

| Cod | Cerință | Descriere | Actori | Prioritate | Issue |
|---|---|---|---|---|---|
| **F1** | Autentificare | Utilizatorul se autentifică cu email și parolă și se poate deconecta. Paginile interne nu pot fi accesate fără autentificare. | Toți | Must | #16 |
| **F2** | Creare tichet | Angajatul deschide un tichet cu titlu, descriere, categorie și prioritate (Scăzută / Medie / Ridicată / Critică). Tichetul nou are statusul „Nou”. | Angajat | Must | #17 |
| **F3** | Lista „Tichetele mele” | Angajatul vede lista propriilor tichete: număr, titlu, prioritate, status, dată. Nu vede tichetele altor angajați. | Angajat | Must | #18 |
| **F4** | Detaliu tichet | Pagina unui tichet afișează toate informațiile lui. Un angajat nu poate deschide tichetul altui angajat. | Toți | Must | #19 |
| **F5** | Roluri și permisiuni | Fiecare utilizator are un rol (angajat, tehnician, manager). Meniul și paginile disponibile depind de rol. | Toți | Must | #22 |
| **F6** | Preluare tichet | Tehnicianul vede tichetele neatribuite și le poate prelua; tichetul trece în statusul „În lucru”. | Tehnician | Must | #23 |
| **F7** | Atribuire tichet | Managerul atribuie orice tichet unui tehnician. | Manager | Must | #24 |
| **F8** | Schimbare status și istoric | Statusul trece prin etapele Nou → În lucru → Rezolvat → Închis. Fiecare schimbare se înregistrează (cine, când, din ce status în ce status) și se afișează pe pagina tichetului. | Tehnician, Manager | Must | #25 |
| **F9** | Comentarii | Angajatul și tehnicianul pot adăuga comentarii pe tichet; fiecare comentariu are autor și dată. | Toți | Must | #26 |
| **F10** | Filtrare și căutare | Lista de tichete se poate filtra după status, prioritate și categorie și se poate căuta după titlu. | Toți | Should | #27 |
| **F11** | Dashboard cu statistici | Managerul vede grafice cu tichetele pe categorie, pe status și pe tehnician. | Manager | Must | #28 |
| **F12** | Administrare | Managerul adaugă și dezactivează utilizatori și gestionează categoriile de tichete. | Manager | Must | #30 |
| **F13** | Alertă SLA | Tichetele cu statusul „Nou” mai vechi de 4 ore sunt evidențiate în listă și pe dashboard. | Tehnician, Manager | Must | #29 |
| **F14** | Notificări email | Angajatul primește un email când tichetul lui este atribuit sau rezolvat. | Angajat | Could | #31 |

## 4. Cerințe nefuncționale

| Cod | Categorie | Cerință |
|---|---|---|
| **N1** | Performanță | Paginile se încarcă în mai puțin de 2 secunde pentru o bază de până la 1.000 de tichete. |
| **N2** | Securitate | Parolele se salvează doar sub formă de hash (niciodată în clar). Accesul la pagini este verificat pe server, în funcție de rol. |
| **N3** | Protecția datelor (GDPR) | În dezvoltare și testare se folosesc doar date fictive, fără date personale reale. |
| **N4** | Utilizabilitate | Interfața este în limba română și se poate folosi pe calculator și pe telefon (design responsive, Bootstrap 5). |
| **N5** | Calitate | Codul trece de linter (Ruff), iar funcționalitățile principale sunt acoperite de teste automate (pytest), rulate la fiecare pull request (GitHub Actions). |
| **N6** | Portabilitate | Aplicația rulează identic local, în Docker și online (Render). |
| **N7** | Trasabilitate | Fiecare cerință are un cod, un issue pe GitHub, commit-uri și teste asociate. |

## 5. Constrângeri
- Termen final: 15.01.2027.
- Stack: Python 3.12, Flask, SQLAlchemy, SQLite, Bootstrap 5.

## 6. Trasabilitate
Codurile de mai sus se folosesc în toate etapele: în titlurile issue-urilor, în mesajele de commit și în numele testelor.

Exemplu: **F2** „Creare tichet” → issue **#17** → commit-uri `feat: … (#17)` → PR cu `Closes #17` → test în `tests/test_tickets.py`.
