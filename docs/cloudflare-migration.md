# Cloudflare migration and recovery runbook

## Deployment topology

The two implementations are intentionally independent:

- `main` is the preserved Django/Wagtail application hosted by Render.
- `migration/cloudflare-static` is the Eleventy site intended for a separate Cloudflare Pages project.
- `backup/pre-cloudflare-migration-20261113` and `pre-cloudflare-migration-20261113` preserve the verified source commit.

Checking out a Git branch only changes source files. It does not redirect traffic, replace a Django service with a static host, alter DNS, or stop Render. Keep Render active until a Cloudflare preview has been accepted and a separate domain cutover is explicitly authorized.

## Run locally

Install Node.js 20 or later, then run `npm ci` and `npm start`. The preview is available at `http://localhost:8080/`. The production build command is `npm run build`; its output is `_site/`.

Run the full checks before publishing:

```bash
npm run test:all
npm audit
```

Then keep `npm start` running in one terminal and execute `npm run test:browser` in another terminal.

No Python, Django, Wagtail, database, or application server is needed at runtime. Python is used only by the optional, read-only legacy content export helper.

## Edit content with Pages CMS

1. Sign in to Pages CMS with a GitHub account that has access to this repository.
2. Select `rdaslam12/waste-mining-lab` and the `migration/cloudflare-static` branch.
3. Choose Publications, Research Projects, Research Areas, Grants, Team Members, News and Announcements, Activities and Galleries, or Homepage and General Site Content.
4. Save editorial changes. Pages CMS commits structured JSON and uploaded media to this branch.
5. Set `published` to `false` for a draft. Draft records remain in Git but are omitted from public indexes, detail pages, relationships, sitemap entries, and downloads.
6. Review the automatic Cloudflare Pages preview/build before treating a change as published.

The repository configuration was validated locally against its content model. A real authenticated Pages CMS save cannot be tested without the repository owner's GitHub/Pages CMS session; complete one small draft-save/delete check after connecting the repository.

Media uploads are stored under `src/media/`. Do not upload private documents, credentials, raw databases, or personal records. Content relationships use stable slugs; rename related records carefully and update references when Pages CMS prompts for them.

## Create the initial Cloudflare Pages preview

In Cloudflare, create a Pages project connected to the GitHub repository and use:

- Production branch: `migration/cloudflare-static` for the isolated initial static deployment
- Framework preset: Eleventy, or no preset with the values below
- Build command: `npm run build`
- Build output directory: `_site`
- Root directory: leave blank (repository root)
- Environment variables: none required

Cloudflare supplies `CF_PAGES_URL`; the build uses it for canonical URLs and the sitemap. `SITE_URL` may be set later to the final `https://` custom-domain origin. Do not configure the public domain or change DNS during preview validation.

Every push to the configured branch triggers a build. Keep the Cloudflare project branch pinned to the migration branch; do not merge into `main` merely to deploy the static site.

## Compare Render and Cloudflare

Open the same route on both hosts and compare at desktop and mobile widths. At minimum review `/`, `/publications/`, `/research/`, `/grants/`, `/team/`, `/activity/`, `/news/`, `/waste-monitoring/`, and `/contact/`, plus every research/news detail page and a BibTeX download. Check navigation, responsive wrapping, typography, images, filter/search behavior, galleries, links, metadata, redirects, and the deliberately empty Waste Monitoring state.

Do not deactivate Render after this comparison. Domain cutover is a separate operation that should be scheduled only after content owners approve the preview and a fresh production-content export has been reconciled.

## Add a custom domain later

After explicit approval, add the domain in the Cloudflare Pages Custom Domains panel and follow the displayed DNS instructions. Set `SITE_URL` to the final canonical origin and rebuild. Verify HTTPS, redirects, sitemap/canonical URLs, email and external links, then monitor both hosts. Do not delete the Render service during the initial cutover; retain it for rollback.

## Content migration status

The checked-in SQLite database passed its integrity check and produced 27 public editorial records: 9 publications, 5 research projects, 4 research areas, 5 grants, 1 team member, 3 news items, and 0 activities.

The public Render pages were checked against these collections and showed matching public record counts and content during migration. This does not prove that an inaccessible Render database has no unpublished or newly added records. Before a future domain cutover, obtain a fresh production export and reconcile it without overwriting the source database.

For an authorized Render operator, a safe Django JSON export can exclude private framework data:

```bash
python manage.py dumpdata home.Publication home.ResearchArea home.ResearchProject home.Grant home.TeamMember home.Activity home.NewsItem home.HomePage home.PublicationsPage home.ResearchPage home.GrantsPage home.TeamPage home.ActivityPage home.NewsPage home.WasteMonitoringPage home.ContactPage --natural-foreign --natural-primary --indent 2 > public-editorial-content.json
```

Store that export outside the repository, inspect it for private fields, and compare it with the static records before importing anything. Never export or publish `auth`, `sessions`, Wagtail users, password hashes, API tokens, admin logs, or revisions.

## Preserve both implementations

- Make Django fixes on a branch based on `main` and deploy them through the existing Render workflow.
- Make static-site changes on a branch based on `migration/cloudflare-static` and deploy them through Cloudflare Pages.
- Do not force-push, rebase, or delete `main`, the backup branch, the backup tag, or the migration branch.
- Periodically clone and verify the repository and keep external database/media backups under restricted access.

## Restore the Django/Wagtail version

The verified source baseline is commit `3afbf5623036efc49d243a43520e5ae8d950adef`. It is addressable as both the backup branch and annotated tag above. A complete local filesystem archive and Git bundle were also created outside the repository under:

`/Users/towhidaslamraad/Documents/NSU - CSE/Projects/Waste Mining Lab Website/backups/waste-mining-lab-pre-cloudflare-20261113-154754`

The directory contains `project-files.tar.gz`, `repository-all-refs.bundle`, `SHA256SUMS`, and `BACKUP-MANIFEST.md`. Verify checksums before recovery:

```bash
cd "/Users/towhidaslamraad/Documents/NSU - CSE/Projects/Waste Mining Lab Website/backups/waste-mining-lab-pre-cloudflare-20261113-154754"
shasum -a 256 -c SHA256SUMS
git bundle verify repository-all-refs.bundle
gzip -t project-files.tar.gz
```

Restore source by cloning the backup branch/tag into a new directory instead of overwriting an active checkout. Extract the archive only into a new empty recovery directory, keep permissions restricted, and follow the preserved Django setup. Configure secrets from an approved secret store; do not copy credentials into Git. The archive contains the original SQLite databases and uploaded media.

If DNS had later been moved to Cloudflare, rollback hosting by restoring the previous approved DNS/Render domain configuration while keeping the static Pages project available for diagnosis. Git rollback alone cannot redirect users back to Render.

## Troubleshooting

- **Install fails:** confirm Node.js 20+, remove only the disposable local `node_modules` directory, and rerun `npm ci` from the lockfile.
- **Build fails:** run `npm run test:content` first. It reports malformed JSON, unsupported Pages CMS configuration, duplicate slugs, and broken relationships.
- **Missing page:** confirm the record has `published: true`, a unique slug, and valid relationship slugs, then rebuild.
- **Missing image:** use a repository-relative path beginning `/media/` and ensure the file exists under `src/media/` with matching case.
- **Broken internal link:** run `npm run build && npm run test:links`.
- **Unexpected layout:** run `npm run test:browser`, compare the same route/viewport with Render, and inspect browser console errors.
- **Cloudflare build mismatch:** confirm the branch, root directory, build command, output directory, Node version, and most recent build log.
- **Pages CMS cannot save:** confirm GitHub access to the repository/branch and validate `.pages.yml`; do not weaken repository permissions to bypass the error.
- **Content missing from Render:** pause cutover, request a fresh authorized editorial-only export, and reconcile it. Never replace or edit the live database as part of diagnosis.
