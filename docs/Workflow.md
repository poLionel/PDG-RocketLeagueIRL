 # 1. Architecture du repo

```arduino
rocket-league-physique/
├── server/        # ???
├── cars/          # ???
├── mobile/        # appli .NET MAUI
├── infra/         # docker-compose, scripts Ansible/Terraform
└── docs/          # schémas, spécs, README, wiki…
```

# 2. Système de branches (Git-flow)

develop

    - Branche d’intégration continue.
    - On y merge toutes les feature/* et bugfix/*.

feature/xxx & bugfix/yyy

    - Branches filles de develop (git checkout -b feature/123-nouvelle-cam).
    - PR → merge → CI runs.

release/vX.Y.Z

    - Créée depuis develop quand on est prêt pour une version.
    - Stabilisation (QA, tests E2E) sans intégrer de nouvelles features.
    - Puis merge → main + tag vX.Y.Z → déploiement.
    - Merge aussi vers develop pour récupérer correctifs.

main

    - Branche de production, jamais de merges directs de features.
    - Chaque tag vX.Y.Z sur main déclenche le CD.

hotfix/vX.Y.Z

    - Branche crée depuis main pour corriger urgemment un bug.
    - Corrections en branches filles (hotfix/vX.Y.Z-fix…) → PR → merge dans hotfix/vX.Y.Z.
    - Merge → main + tag → déploiement immédiat.
    - Merge → develop pour propager la correction.


# 3. Tags Git & Releases
- Format sémantique : vMaJEUR.MINOR.PATCH (ex. v1.0.0, v1.2.2)
- Création anotée :

```bash
git tag -a v1.1.2 -m "Hotfix v1.1.2 - Crash x fix"
git push origin v.1.1.2
```

- Usage
    - Reste figé sur le commit de release
    - Déclencheur CD (dans cd.yml)

- Github Releases : associez notes de version et artefacts (Docker, firmware,...)

# 4. Pipelines Github Actions
## 1) .github/workflows/ci.yml
    - Déchencheurs : push & pull_request sur develop, feature/*, bugfix/*
    - Jobs (parallèles) :
        - Test AppMobile (dotnet test)
        - Test Server
        - Test Firmware
    - Objectif : feedback rapide, qualité du code

## 2) .github/workflows/e2e.yml (todo : à voir si besoin)

## 3) .github/workflows/cd.yml
    - Déclencheur : push de tags v*.*.*
    - Job :
        - A voir mais build & push docker images, générer binaire, ...

# 5. Outils & environnements
    - Issue tracker : Github Issues + Project (kanban), templates, labels(bug, feature, etc)
    - Docs : dossier docs/
    - autres ? 
