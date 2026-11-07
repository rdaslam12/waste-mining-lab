# Product

<!-- impeccable:product-schema 1 -->

> This record was inferred from the explicit project brief because the structured
> product-question tool was unavailable in the active execution mode.

## Platform

web

## Users

- Inferred: prospective students, research collaborators, academic peers, and visitors seeking an introduction to Waste Mining Lab.
- Inferred primary job: quickly understand the lab's research focus, institutional affiliation, and how to make contact.

## Product Purpose

The official website foundation for Waste Mining Lab, a research laboratory led by Assistant Professor Asef M. Redwan at North South University, Bangladesh. The initial release introduces the lab and its broad research areas while creating an expandable Wagtail-managed foundation.

## Positioning

Waste Mining Lab focuses on environmental sustainability, resource recovery, and waste valorization in an academic research setting.

## Operating Context

The public site is read on desktop, tablet, and mobile. Administrators maintain homepage content through Wagtail's existing CMS and admin login.

## Capabilities and Constraints

- Existing stack: Django 6.1.3, Wagtail 8.1, Python 3.12, and SQLite.
- Reuse the existing `HomePage` model and Wagtail admin.
- Administrators can edit the hero headline, hero subtitle, hero image, and lab introduction.
- Keep authentication and existing Wagtail functionality intact.
- Use lightweight CSS without a frontend framework or unnecessary dependencies.
- Do not add News, Publications, People, Grants, or automations in this phase.

## Brand Commitments

- Name: Waste Mining Lab.
- Academic, professional, restrained voice.
- Visual direction supplied in the brief: a clean research-lab aesthetic inspired by the Stadler Lab website, using forest green, off-white, charcoal, and restrained typography. No assets may be copied from the reference.

## Evidence on Hand

- Confirmed leader: Assistant Professor Asef M. Redwan, presented publicly as Dr. Asef M. Redwan.
- Confirmed affiliation: North South University, Bangladesh.
- Confirmed address: North South University, Bashundhara, Dhaka-1229, Bangladesh.
- Confirmed contact: asef.redwan@northsouth.edu.
- No faculty achievements, funded projects, publication records, lab members, or owned visual assets were supplied; future work must not fabricate them.

## Product Principles

- Make the lab's purpose and affiliation immediately clear.
- Keep factual content honest and easy to update.
- Preserve Wagtail's editorial workflow and admin experience.
- Build a responsive, accessible foundation that can expand without redesigning the core structure.
