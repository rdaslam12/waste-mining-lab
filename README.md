# Waste Mining Lab — static site

This branch contains the Eleventy and Pages CMS reconstruction of the Waste Mining Lab website for Cloudflare Pages. The original Django/Wagtail application remains intact on `main` and continues to power the Render production site until a separate deployment decision is made.

## Local development

Use Node.js 20 or newer:

```bash
npm ci
npm start
```

Open `http://localhost:8080/`. Create a production build with `npm run build`; the deployable site is written to `_site/`.

## Validation

```bash
npm run test:all
npm audit
git diff --check
```

`test:all` validates Pages CMS content, builds the site, checks generated routes and private-data exclusions, scans internal links, and exercises create/edit/publish/delete content fixtures. With `npm start` running in another terminal, `npm run test:browser` covers the public routes at desktop, tablet, and mobile widths.

## Content editing

Pages CMS reads [`.pages.yml`](.pages.yml) and the structured JSON records under `src/content/`. Editors can manage publications, research projects and areas, grants, team members, news, activities, and general site content. A record is excluded from the public build while its `published` field is `false`.

The local Wagtail export helper is deliberately read-only and exports public editorial records only:

```bash
python scripts/export_wagtail_content.py --database /absolute/path/to/db.sqlite3
```

It does not export users, passwords, sessions, tokens, revisions, or admin logs.

## Cloudflare Pages

- Branch for the initial preview: `migration/cloudflare-static`
- Build command: `npm run build`
- Output directory: `_site`
- Root directory: repository root
- Required runtime services: none

Do not point the production domain at this branch until its Pages preview has been reviewed and approved. Branch switching does not move traffic between Render and Cloudflare.

See [the migration and recovery runbook](docs/cloudflare-migration.md) for content workflows, deployment, comparison, rollback, database/media recovery, and troubleshooting.
