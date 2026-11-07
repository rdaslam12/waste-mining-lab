---
name: "Waste Mining Lab"
description: "An academic lab homepage with a restrained botanical visual language."
colors:
  ink: "#202c27"
  muted: "#52635a"
  accent-blue: "#2874b8"
  forest: "#1c5038"
  forest-deep: "#102c22"
  sage: "#e2ece1"
  divider: "#cddbd0"
  white: "#ffffff"
  page-paper: "#fbfcf9"
  mission-white: "#f2f6ed"
  photo-stem: "#3d7658"
  photo-leaf: "#5c8a64"
  team-paper: "#f2f6ee"
  portrait-sage: "#dbe8da"
  footer-deep: "#10251d"
  footer-copy: "#d8e6d9"
  mission-link: "#d1e7d5"
typography:
  display:
    fontFamily: '"DM Sans", "Helvetica Neue", Arial, sans-serif'
    fontSize: "clamp(2.2rem, 3.4vw, 4rem)"
    fontWeight: 700
    lineHeight: 1.15
    letterSpacing: "-0.025em"
  mission:
    fontFamily: '"Newsreader", Georgia, serif'
    fontSize: "clamp(1.65rem, 2.4vw, 2.45rem)"
    fontWeight: 400
    lineHeight: 1.35
    letterSpacing: "-0.015em"
  body:
    fontFamily: '"DM Sans", "Helvetica Neue", Arial, sans-serif'
    fontSize: "1rem"
    lineHeight: 1.65
  navigation:
    fontFamily: '"DM Sans", "Helvetica Neue", Arial, sans-serif'
    fontSize: "clamp(0.95rem, 1.2vw, 1.25rem)"
    fontWeight: 400
  section-heading:
    fontFamily: '"Newsreader", Georgia, serif'
    fontSize: "clamp(2.4rem, 3.6vw, 3.7rem)"
    fontWeight: 400
  research-copy:
    fontFamily: '"DM Sans", "Helvetica Neue", Arial, sans-serif'
    fontSize: "clamp(1.08rem, 1.35vw, 1.3rem)"
    lineHeight: 1.62
  team-heading:
    fontFamily: '"DM Sans", "Helvetica Neue", Arial, sans-serif'
    fontSize: "clamp(1.7rem, 2.1vw, 2.2rem)"
    fontWeight: 600
  compact-display:
    fontFamily: '"DM Sans", "Helvetica Neue", Arial, sans-serif'
    fontSize: "clamp(1.7rem, 6.7vw, 2.7rem)"
    fontWeight: 700
  compact-navigation:
    fontFamily: '"DM Sans", "Helvetica Neue", Arial, sans-serif'
    fontSize: "0.94rem"
  small-copy:
    fontFamily: '"DM Sans", "Helvetica Neue", Arial, sans-serif'
    fontSize: "1.05rem"
  footer-detail:
    fontFamily: '"DM Sans", "Helvetica Neue", Arial, sans-serif'
    fontSize: "0.95rem"
  photo-caption:
    fontFamily: '"DM Sans", "Helvetica Neue", Arial, sans-serif'
    fontSize: "clamp(1.2rem, 1.6vw, 1.75rem)"
    fontWeight: 600
  action-label:
    fontFamily: '"DM Sans", "Helvetica Neue", Arial, sans-serif'
    fontSize: "0.78rem"
    fontWeight: 700
  action-arrow:
    fontFamily: '"DM Sans", "Helvetica Neue", Arial, sans-serif'
    fontSize: "1.15rem"
  footer-name:
    fontFamily: '"DM Sans", "Helvetica Neue", Arial, sans-serif'
    fontSize: "1.5rem"
    fontWeight: 600
spacing:
  content-gutter: "1.5rem"
  section-space: "clamp(3.5rem, 6vw, 6rem)"
components:
  mission-band:
    backgroundColor: "{colors.forest-deep}"
    textColor: "{colors.mission-white}"
    padding: "clamp(3rem, 5vw, 5.5rem) 1.5rem"
  research-copy:
    textColor: "{colors.ink}"
    typography: "{typography.research-copy}"
  institutional-footer:
    backgroundColor: "{colors.footer-deep}"
    textColor: "{colors.footer-copy}"
---

# Design System: Waste Mining Lab

## Overview

**Creative North Star: "The Living Lab"**

The supplied Stadler Lab screenshot still establishes the composition: a centered title, separate navigation, panoramic media, mission band, and narrow research column. Original botanical marks introduce the environmental focus while the photograph and portrait areas remain clearly labeled placeholders until authentic lab imagery is available.

## Colors

Warm near-white is the dominant ground. Deep forest green holds the mission and footer; sage supports the labeled image placeholders. Blue remains a restrained current-navigation cue. Forest green carries headings and small accents. Thin pale green dividers separate sections.

## Typography

Locally hosted DM Sans carries the title, navigation, research prose, and contact details. Locally hosted Newsreader gives the mission and section headings an academic editorial voice. Body copy stays within a 65ch measure. The title is compact and strong, while the mission has a larger, softer rhythm.

## Layout

The title area is centered and approximately 9–12.75rem tall. The navigation row follows under a full-width rule. The research image spans the viewport and uses a shallow panoramic crop. The mission band is centered and full width. Research and team content use a 60rem maximum width, with 1.5rem gutters. At widths below 42rem, navigation wraps if needed, a mobile botanical composition replaces the wide illustration, the portrait stacks above the director details, and the footer becomes one column.

## Elevation & Depth

The page is flat. Paper, forest, and sage sections create hierarchy. There are no shadows, floating shapes, or layered cards.

## Shapes

Images and placeholders are rectangular with square corners. Botanical sprigs and the banner's leaf forms are original vector geometry. Dividers are one pixel. The page does not use card containers.

## Components

### Lab title and navigation

The lab name occupies its own centered row, flanked by small leaf sprigs. Home, Research, Team, and Contact form a simple horizontal link row. Home is blue only when it is the current page. A short underline grows on hover and keyboard focus.

### Research photograph

Wagtail's existing hero image fills a full-width panoramic area. Without an image, the same area clearly says that a Waste Mining Lab research photograph is pending, over a botanical line drawing. Stems draw once on load and leaves become more visible; all imagery and text remain visible by default. The narrow viewport uses an independent composition so its plants stay in frame.

### Mission and introduction

The existing editable subtitle appears in the forest mission band, followed by a quiet research anchor. The existing editable lab introduction appears in the light research section. Both have factual fallbacks.

### Featured team

Only Dr. Asef M. Redwan is shown. The portrait remains a labeled placeholder until an authentic photograph is available.

### Footer

The footer uses deep green, with the lab name and university address to the left, email and copyright to the right. It stacks on small screens.

## Do's and Don'ts

- Do preserve the title → navigation → panoramic image → mission → research → team → footer sequence.
- Do use authentic photographs with meaningful Wagtail image descriptions when they become available.
- Do keep content factual and aligned within the centered content column.
- Don't copy Rice University assets, imagery, or institution-specific content.
- Don't add unrelated decorative graphics, cards, gradients, or looping motion to this reference-led homepage.
