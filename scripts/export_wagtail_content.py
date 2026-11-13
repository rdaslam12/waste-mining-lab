#!/usr/bin/env python3
"""Export only verified public editorial content from the local Wagtail SQLite database."""

from __future__ import annotations

import json
import re
import sqlite3
import unicodedata
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "db.sqlite3"
CONTENT = ROOT / "src" / "content"


def slugify(value: str) -> str:
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    value = re.sub(r"[^a-zA-Z0-9]+", "-", value).strip("-").lower()
    return value or "entry"


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def rows(connection: sqlite3.Connection, query: str):
    return [dict(row) for row in connection.execute(query)]


def media_path(image_id, images):
    if not image_id or image_id not in images:
        return ""
    return f"/media/{images[image_id]['file']}"


def main() -> None:
    connection = sqlite3.connect(DB)
    connection.row_factory = sqlite3.Row
    integrity = connection.execute("PRAGMA integrity_check").fetchone()[0]
    if integrity != "ok":
        raise RuntimeError(f"Source database integrity check failed: {integrity}")

    images = {row["id"]: row for row in rows(connection, "SELECT id,title,file,description FROM wagtailimages_image")}
    publications = rows(connection, "SELECT * FROM home_publication ORDER BY year DESC,id DESC")
    publication_slugs = {row["id"]: slugify(row["title"]) for row in publications}
    for row in publications:
        payload = {
            "legacy_id": row["id"],
            "slug": publication_slugs[row["id"]],
            "title": row["title"],
            "authors": row["authors"],
            "year": row["year"],
            "venue": row["venue"] or "",
            "doi": row["doi"] or "",
            "publication_type": row["publication_type"],
            "publication_url": row["publication_url"] or "",
            "abstract": row["abstract"] or "",
            "published": row["status"] == "published",
            "featured": bool(row["featured"]),
        }
        write_json(CONTENT / "publications" / f"{payload['slug']}.json", payload)

    areas = rows(connection, "SELECT * FROM home_researcharea ORDER BY sort_order,id")
    area_slugs = {row["id"]: slugify(row["title"]) for row in areas}
    for row in areas:
        payload = {
            "legacy_id": row["id"],
            "slug": area_slugs[row["id"]],
            "title": row["title"],
            "description": row["description"] or "",
            "image": media_path(row["image_id"], images),
            "image_alt": images.get(row["image_id"], {}).get("description", "") if row["image_id"] else "",
            "sort_order": row["sort_order"],
            "published": bool(row["is_published"]),
        }
        write_json(CONTENT / "research-areas" / f"{payload['slug']}.json", payload)

    project_links = {}
    for row in rows(connection, "SELECT researchproject_id,publication_id FROM home_researchproject_publications"):
        project_links.setdefault(row["researchproject_id"], []).append(publication_slugs[row["publication_id"]])
    projects = rows(connection, "SELECT * FROM home_researchproject ORDER BY sort_order,id")
    project_slugs = {row["id"]: row["slug"] or slugify(row["title"]) for row in projects}
    for row in projects:
        payload = {
            "legacy_id": row["id"],
            "slug": project_slugs[row["id"]],
            "title": row["title"],
            "status": row["status"],
            "summary": row["summary"],
            "research_area": area_slugs.get(row["area_id"], ""),
            "image": media_path(row["image_id"], images),
            "image_alt": images.get(row["image_id"], {}).get("description", "") if row["image_id"] else "",
            "start_date": row["start_date"] or "",
            "end_date": row["end_date"] or "",
            "description_html": row["description"] or "",
            "methodology_html": row["methodology"] or "",
            "collaborations": row["collaborations"] or "",
            "funding_notes": row["funding_notes"] or "",
            "external_url": row["external_url"] or "",
            "publications": project_links.get(row["id"], []),
            "monitoring_related": bool(row["monitoring_related"]),
            "sort_order": row["sort_order"],
            "published": bool(row["is_published"]),
        }
        write_json(CONTENT / "research-projects" / f"{payload['slug']}.json", payload)

    for row in rows(connection, "SELECT * FROM home_grant ORDER BY sort_order,id"):
        payload = {
            "legacy_id": row["id"],
            "slug": slugify(row["title"]),
            "title": row["title"],
            "funding_organization": row["funding_organization"],
            "amount_display": row["amount_display"] or "",
            "amount": row["amount"],
            "currency": row["currency"] or "",
            "start_date": row["start_date"] or "",
            "end_date": row["end_date"] or "",
            "role": row["role"] or "",
            "awarded_institution": row["awarded_institution"] or "",
            "category": row["category"],
            "related_project": project_slugs.get(row["related_project_id"], ""),
            "summary": row["summary"] or "",
            "public_source_url": row["public_source_url"] or "",
            "verified": bool(row["is_verified"]),
            "sort_order": row["sort_order"],
            "published": bool(row["is_published"]),
        }
        write_json(CONTENT / "grants" / f"{payload['slug']}.json", payload)

    member_links = {}
    for row in rows(connection, "SELECT teammember_id,researchproject_id FROM home_teammember_projects"):
        member_links.setdefault(row["teammember_id"], []).append(project_slugs[row["researchproject_id"]])
    for row in rows(connection, "SELECT * FROM home_teammember ORDER BY sort_order,id"):
        member_slug = row["slug"] or slugify(row["name"])
        payload = {
            "legacy_id": row["id"],
            "slug": member_slug,
            "name": row["name"],
            "role": row["role"],
            "category": row["category"],
            "affiliation": row["affiliation"] or "",
            "academic_background": row["academic_background"] or "",
            "biography": row["biography"] or "",
            "research_interests": row["research_interests"] or "",
            "image": media_path(row["image_id"], images),
            "image_alt": images.get(row["image_id"], {}).get("description", "") if row["image_id"] else "",
            "featured": bool(row["is_featured"]),
            "email": row["email"] or "",
            "profile_url": row["profile_url"] or "",
            "linkedin_url": row["linkedin_url"] or "",
            "scholar_url": row["scholar_url"] or "",
            "alumni_current_position": row["alumni_current_position"] or "",
            "projects": member_links.get(row["id"], []),
            "sort_order": row["sort_order"],
            "published": bool(row["is_published"]),
        }
        write_json(CONTENT / "team" / f"{payload['slug']}.json", payload)

    activities = rows(connection, "SELECT * FROM home_activity ORDER BY date DESC,id DESC")
    activity_slugs = {row["id"]: slugify(row["title"]) for row in activities}
    galleries = {}
    for row in rows(connection, "SELECT * FROM home_activityimage ORDER BY activity_id,sort_order"):
        image = images.get(row["image_id"], {})
        galleries.setdefault(row["activity_id"], []).append({
            "image": media_path(row["image_id"], images),
            "image_alt": image.get("description") or image.get("title") or "",
            "caption": row["caption"] or "",
        })
    for row in activities:
        payload = {
            "legacy_id": row["id"],
            "slug": activity_slugs[row["id"]],
            "title": row["title"],
            "date": row["date"],
            "category": row["category"],
            "description_html": row["description"] or "",
            "cover_image": media_path(row["cover_image_id"], images),
            "cover_image_alt": images.get(row["cover_image_id"], {}).get("description", "") if row["cover_image_id"] else "",
            "external_url": row["external_url"] or "",
            "related_project": project_slugs.get(row["project_id"], ""),
            "featured": bool(row["featured"]),
            "gallery": galleries.get(row["id"], []),
            "sort_order": row["sort_order"],
            "published": bool(row["is_published"]),
        }
        write_json(CONTENT / "activities" / f"{payload['slug']}.json", payload)

    news_query = """
        SELECT p.id,p.title,p.slug,p.seo_title,p.search_description,p.live,n.*
        FROM home_newsarticlepage n JOIN wagtailcore_page p ON p.id=n.page_ptr_id
        ORDER BY n.date DESC,p.id DESC
    """
    for row in rows(connection, news_query):
        payload = {
            "legacy_id": row["id"],
            "slug": row["slug"],
            "title": row["title"],
            "seo_title": row["seo_title"] or "",
            "search_description": row["search_description"] or row["excerpt"],
            "date": row["date"],
            "category": row["category"],
            "excerpt": row["excerpt"],
            "cover_image": media_path(row["cover_image_id"], images),
            "cover_image_alt": images.get(row["cover_image_id"], {}).get("description", "") if row["cover_image_id"] else "",
            "body_html": row["body"] or "",
            "featured": bool(row["featured"]),
            "related_project": project_slugs.get(row["related_project_id"], ""),
            "related_publication": publication_slugs.get(row["related_publication_id"], ""),
            "related_activity": activity_slugs.get(row["related_activity_id"], ""),
            "published": bool(row["live"]),
        }
        write_json(CONTENT / "news" / f"{payload['slug']}.json", payload)

    homepage = dict(connection.execute("SELECT * FROM home_homepage LIMIT 1").fetchone())
    site_payload = {
        "site_name": "Waste Mining Lab",
        "institution": "North South University",
        "department": "Department of Civil & Environmental Engineering",
        "default_description": "Official research website of Waste Mining Lab at North South University, exploring environmental engineering, waste valorization, resource recovery, and sustainability.",
        "canonical_url": "https://waste-mining-lab.onrender.com",
        "email": "asef.redwan@northsouth.edu",
        "address_html": "North South University<br>Bashundhara, Dhaka-1229, Bangladesh",
        "hero_headline": homepage["hero_headline"] or "Waste Mining Lab",
        "hero_subtitle": homepage["hero_subtitle"] or "",
        "hero_image": "/media/images/Hero_Image.2e16d0ba.fill-1600x1000.png",
        "hero_image_mobile": "/media/images/Hero_Image.2e16d0ba.fill-800x1000.png",
        "hero_image_large": "/media/images/Hero_Image.2e16d0ba.fill-2400x1400.png",
        "hero_image_alt": "Waste Mining Lab research",
        "lab_introduction_html": homepage["lab_introduction"] or "",
        "team_member_count": homepage["team_member_count"],
        "director_name": "Dr. Asef M. Redwan",
        "director_email": "asef.redwan@northsouth.edu",
        "director_profile_url": "https://www.northsouth.edu/faculty-members/seps/cee/dr.-asef-mohammad-redwan.html",
        "director_linkedin_url": "https://www.linkedin.com/in/asef-m-redwan-phd-282a0a64/",
    }
    write_json(CONTENT / "site.json", site_payload)

    section_query = """
        SELECT p.title,p.slug,p.seo_title,p.search_description,s.*
        FROM home_sectionpage s JOIN wagtailcore_page p ON p.id=s.page_ptr_id
        ORDER BY p.path
    """
    for row in rows(connection, section_query):
        payload = {
            "slug": row["slug"],
            "title": row["title"],
            "heading": row["heading"] or "",
            "intro": row["intro"] or "",
            "body_html": row["body"] or "",
            "feature_image": media_path(row["feature_image_id"], images),
            "feature_image_alt": images.get(row["feature_image_id"], {}).get("description", "") if row["feature_image_id"] else "",
            "image_caption": row["image_caption"] or "",
            "methodology_html": row["methodology"] or "",
            "seo_title": row["seo_title"] or "",
            "search_description": row["search_description"] or "",
        }
        write_json(CONTENT / "pages" / f"{payload['slug']}.json", payload)

    connection.close()
    print("Exported public editorial content only; authentication, sessions, tokens, revisions, and admin logs were excluded.")


if __name__ == "__main__":
    main()
