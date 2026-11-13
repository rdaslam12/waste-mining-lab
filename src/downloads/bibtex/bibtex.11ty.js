export default class BibtexTemplate {
  data() {
    return {
      pagination: { data: "catalog.publishedPublications", size: 1, alias: "publication" },
      permalink: ({ publication }) => `/downloads/bibtex/publication-${publication.legacy_id || publication.slug}.bib`,
      eleventyExcludeFromCollections: true,
    };
  }

  render({ publication }) {
    return this.bibtex(publication);
  }
}
