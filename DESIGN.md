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
  hero-fallback: "#183f2d"
  hero-highlight: "#9de6a6"
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
  hero-headline:
    fontFamily: '"DM Sans", "Helvetica Neue", Arial, sans-serif'
    fontSize: "clamp(3rem, 6.2vw, 6rem)"
    fontWeight: 700
    lineHeight: 1.02
    letterSpacing: "-0.04em"
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
  pinned-research-hero:
    backgroundColor: "{colors.forest-deep}"
    textColor: "{colors.white}"
    typography: "{typography.hero-headline}"
    height: "100svh"
---

# Design System: Waste Mining Lab

## Overview

**Creative North Star: "The Living Lab"**

The supplied Stadler Lab screenshot still establishes the composition: a centered title, separate navigation, full-width research media, mission band, and narrow research column. Original botanical marks introduce the environmental focus; the homepage hero now lets an authentic Wagtail-managed photograph lead while retaining an honest forest botanical fallback, and the portrait remains clearly labeled until authentic team imagery is available.

## Colors

Warm near-white is the dominant ground. Deep forest green holds the mission, footer, and hero fallback; sage supports the remaining labeled image placeholder. Blue remains a restrained current-navigation cue. Forest green carries headings and small accents, while the pinned hero alone uses a brighter leaf green to emphasize key words and its active progress marker. Thin pale green dividers separate sections.

## Typography

Locally hosted DM Sans carries the title, navigation, research prose, and contact details. Locally hosted Newsreader gives the mission and section headings an academic editorial voice. Body copy stays within a 65ch measure. The title is compact and strong, while the mission has a larger, softer rhythm.

## Layout

The title area is centered and approximately 9–12.75rem tall. The navigation row follows under a full-width rule. The research hero spans the viewport and pins for one viewport-height scene while the opaque mission surface scrolls over it; its photograph uses a full-bleed cover crop rather than a panoramic strip. Research and team content use a 60rem maximum width, with 1.5rem gutters. At compact widths, the hero shortens to 88svh, moves its shade toward the lower edge, scales the display copy, and hides the redundant research anchor; navigation wraps if needed, the portrait stacks above the director details, and the footer becomes one column. Short landscape viewports keep a full-height hero with a smaller headline and tighter footer offset.

## Elevation & Depth

The page remains predominantly flat. Paper, forest, and sage sections create hierarchy, and there are no floating shapes or layered cards. The pinned hero is the sole depth exception: a dark directional image shade preserves copy contrast, text receives a restrained ambient shadow, and the mission surface uses a soft top shadow to clarify that it is passing over the pinned photograph.

## Shapes

Images and placeholders are rectangular with square corners. Botanical sprigs and the hero fallback's leaf forms are original vector geometry. Dividers are one pixel. The page does not use card containers. Compact rounded forms are reserved for small hero controls; they do not establish a card or container radius.

## Components

### Lab title and navigation

The lab name occupies its own centered row, flanked by small leaf sprigs. Home, Research, Team, and Contact form a simple horizontal link row. Home is blue only when it is the current page. A short underline grows on hover and keyboard focus.

### Pinned research hero

Wagtail's existing hero image fills a full-width pinned cover scene, with responsive renditions for mobile, desktop, and large displays. Without an image, a deep forest botanical illustration fills the same space and exposes an accessible missing-image label. A dark directional shade protects large white DM Sans copy, while bright leaf green marks the emphasized phrase.

The exact research messages rotate in this order: “Turning waste into value.”, “Recovering resources. Restoring balance.”, and “Rethinking waste for a sustainable future.” The active message changes every seven seconds only while the hero is visible and the page is active. Progress controls support direct selection, and a Play/Pause control exposes the state. Reduced-motion preference disables automatic rotation, slide transitions, and breathing motion, keeps the first message visible, and hides the unnecessary toggle. The research anchor remains visible on larger viewports and is omitted on compact layouts where vertical space is tighter.

### Mission and introduction

The existing editable subtitle appears in the forest mission band, followed by a quiet research anchor. The existing editable lab introduction appears in the light research section. Both have factual fallbacks.

### Featured team

Only Dr. Asef M. Redwan is shown. The portrait remains a labeled placeholder until an authentic photograph is available.

### Footer

The footer uses deep green, with the lab name and university address to the left, email and copyright to the right. It stacks on small screens.

## Do's and Don'ts

- Do preserve the title → navigation → pinned research hero → mission → research → team → footer sequence.
- Do use authentic photographs with meaningful Wagtail image descriptions when they become available.
- Do keep hero motion optional, pausable, visibility-aware, and disabled for reduced-motion users.
- Do keep content factual and aligned within the centered content column.
- Don't copy Rice University assets, imagery, or institution-specific content.
- Don't reuse the hero's image shade, ambient shadow, bright highlight, or looping motion as general decoration elsewhere.
- Don't add unrelated decorative graphics, cards, gradients, or autonomous motion to this reference-led homepage.
