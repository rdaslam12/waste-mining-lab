"""
Idempotent, reproducible management command to populate verified academic content
for Waste Mining Lab at North South University.

Primary sources:
- NSU faculty profile: https://www.northsouth.edu/faculty-members/seps/cee/dr.-asef-mohammad-redwan.html
- Primary publisher records (ACS Omega, ESPR Springer, RSC, Bioresource Technology, ES&T, IJEST, IJGW, LNCE)
- Idaho National Laboratory (INL) & US Department of Energy (DOE) awards
- ITN-BUET & UIU funded research initiatives

Usage:
    python manage.py import_verified_academic_data [--dry-run] [--force-update]
"""

from datetime import date
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from wagtail.models import Page
from home.models import (
    Activity,
    Grant,
    HomePage,
    NewsArticlePage,
    Publication,
    ResearchArea,
    ResearchProject,
    SectionPage,
    TeamMember,
)


class Command(BaseCommand):
    help = "Import and synchronize verified academic research records for Waste Mining Lab."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Simulate the import process without writing changes to the database.",
        )
        parser.add_argument(
            "--force-update",
            action="store_true",
            help="Update existing records with fresh verified metadata.",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        force_update = options["force_update"]

        if dry_run:
            self.stdout.write(self.style.WARNING("Running in DRY-RUN mode. No changes will be saved."))

        # 1. Research Areas
        self.stdout.write("\n=== 1. Research Areas ===")
        areas = self.import_research_areas(dry_run, force_update)

        # 2. Verified Publications
        self.stdout.write("\n=== 2. Publications ===")
        pubs = self.import_publications(dry_run, force_update)

        # 3. Research Projects
        self.stdout.write("\n=== 3. Research Projects ===")
        projects = self.import_research_projects(areas, pubs, dry_run, force_update)

        # 4. Grants & Funding
        self.stdout.write("\n=== 4. Grants & Funding ===")
        grants = self.import_grants(projects, dry_run, force_update)

        # 5. Team Director
        self.stdout.write("\n=== 5. Team Director ===")
        director = self.import_team_director(projects, dry_run, force_update)

        # 6. Verified News & Announcements
        self.stdout.write("\n=== 6. News & Announcements ===")
        news = self.import_news(projects, pubs, dry_run, force_update)

        # 7. Update Homepage metadata and statistics
        self.stdout.write("\n=== 7. Homepage Synchronisation ===")
        self.sync_homepage(dry_run)

        self.stdout.write(self.style.SUCCESS("\n[SUCCESS] Verified academic data import completed cleanly."))

    def import_research_areas(self, dry_run, force_update):
        area_definitions = [
            {
                "title": "Environmental sustainability",
                "description": "Understanding environmental systems, climate resilience, and ecosystem interactions to inform sustainable management of water, soils, and natural resources.",
                "sort_order": 1,
            },
            {
                "title": "Waste valorization",
                "description": "Investigating biochemical, thermal, and mechanical conversion routes to transform discarded organic and industrial residues into valuable bio-products.",
                "sort_order": 2,
            },
            {
                "title": "Resource recovery",
                "description": "Developing microbial and engineered technologies to reclaim technology-critical materials, rare earth elements, and nutrients from complex waste streams.",
                "sort_order": 3,
            },
            {
                "title": "Environmental engineering",
                "description": "Designing packed bed bioreactors, continuous-flow wastewater systems, and Zero Liquid Discharge (ZLD) processes for industrial pollution control.",
                "sort_order": 4,
            },
        ]
        results = {}
        for item in area_definitions:
            existing = ResearchArea.objects.filter(title=item["title"]).first()
            if existing:
                if force_update and not dry_run:
                    existing.description = item["description"]
                    existing.sort_order = item["sort_order"]
                    existing.is_published = True
                    existing.save()
                    self.stdout.write(f"  [UPDATED] Area: {item['title']}")
                else:
                    self.stdout.write(f"  [EXISTS]  Area: {item['title']}")
                results[item["title"]] = existing
            else:
                if not dry_run:
                    obj = ResearchArea.objects.create(
                        title=item["title"],
                        description=item["description"],
                        sort_order=item["sort_order"],
                        is_published=True,
                    )
                    results[item["title"]] = obj
                    self.stdout.write(self.style.SUCCESS(f"  [CREATED] Area: {item['title']}"))
                else:
                    self.stdout.write(self.style.SUCCESS(f"  [WOULD CREATE] Area: {item['title']}"))
        return results

    def import_publications(self, dry_run, force_update):
        publication_records = [
            {
                "doi": "10.1021/acsomega.5c09729",
                "title": "Characterization of Protein Expression Patterns in Clostridium sporogenes upon Exposure to Rare Earth versus Nonrare Earth Elements",
                "authors": "Jeremy A. Sabo, Gabriella Morales, Michelle R. Walton, Yoshiko Fujita, David W. Reed, Payton J. Walker, Chelsea C. St. Germain, Asef M. Redwan",
                "year": 2026,
                "venue": "ACS Omega",
                "publication_type": Publication.PublicationType.JOURNAL,
                "publication_url": "https://doi.org/10.1021/acsomega.5c09729",
                "abstract": (
                    "To better understand the interactions of rare earth elements (REE) with anaerobic microorganisms, "
                    "we explored the proteome response of a Clostridium strain to europium (Eu) and its adjacent lanthanide, "
                    "samarium (Sm), comparing them with the well-studied metals iron, calcium, and zinc. Our findings showed that "
                    "Eu and Sm induced a number of proteomic changes consistent with Fe, Ca, and Zn, but Eu enhanced expression "
                    "for ATP synthase and electron transfer flavoproteins, while Sm increased expression of proteins associated with "
                    "butyric acid metabolism. In contrast, Fe reduced ATP synthase protein expression, and Fe and Ca demonstrated a "
                    "greater expression change for amino acid metabolism, transcription, and ribosome activity. Differences in ABC "
                    "transporter protein expressions were observed for the REE. Further characterization of proteins that respond "
                    "to REE can provide sequence and structural insights to support the design of REE binding molecules or bioinspired "
                    "systems for REE capture. Given the potential environmental benefits of biological enrichment methods, identifying "
                    "proteins and metabolic pathways interacting with REE offers an important opportunity to advance the sustainability "
                    "of supply chains for these metals critical to modern technologies."
                ),
                "featured": True,
            },
            {
                "doi": "10.1007/s11356-025-37256-9",
                "title": "Impact of europium and samarium on growth and metabolism of two anaerobic wastewater microorganisms: Sporacetigenium mesophilum and Clostridium sporogenes",
                "authors": "Asef Mohammad Redwan, David William Reed, Jeffery Dale St. Jeor, Gaurav Das, Andre Anderko, Yoshiko Fujita",
                "year": 2026,
                "venue": "Environmental Science and Pollution Research",
                "publication_type": Publication.PublicationType.JOURNAL,
                "publication_url": "https://doi.org/10.1007/s11356-025-37256-9",
                "abstract": (
                    "Increases in environmental fluxes of rare earth elements (REEs) stemming from increased demand for these technology "
                    "critical elements may affect microbial ecosystem functions important for pollutant degradation and nutrient cycling. "
                    "This study investigates the responses of Sporacetigenium mesophilum and Clostridium sporogenes, two anaerobic fermenters, "
                    "to varying concentrations of two REE, namely europium and samarium. Eu and Sm are adjacent lanthanides but differ significantly "
                    "in their redox behavior. We tested Eu and Sm concentrations ranging from < 1 to 600 µM. Despite the close phylogenetic "
                    "relatedness of the two bacteria, we observed species-specific as well as REE-specific and incubation time-dependent sensitivities. "
                    "S. mesophilum exhibited pronounced inhibition of hydrogen production and growth with exposure to >= 60 µM of Eu, but with 6 µM Eu, "
                    "a hormetic effect was observed—hydrogen production was enhanced relative to the control. With Sm, the only impact observed on "
                    "S. mesophilum was inhibition at the highest concentration (600 µM) tested. For C. sporogenes, growth inhibition was observed "
                    "only at 600 µM Eu or Sm, and no hormesis was observed with either REE. This study offers valuable insights into REE impacts "
                    "under anaerobic conditions, essential for understanding potential disruptions to organic matter degradation and nutrient cycling."
                ),
                "featured": True,
            },
            {
                "doi": "10.1039/D6EW00039H",
                "title": "Impact of ZVI and sulfidated ZVI on sulfate-reducing microbial communities and implications for groundwater remediation",
                "authors": "Nofil Khan, Asef Redwan, Syful Islam, Lingfei Fan, Weile Yan, Kayleigh Millerick",
                "year": 2026,
                "venue": "Environmental Science: Water Research & Technology",
                "publication_type": Publication.PublicationType.JOURNAL,
                "publication_url": "https://doi.org/10.1039/d6ew00039h",
                "abstract": (
                    "Sulfur-modified zero valent iron (ZVI) is a common groundwater remediation strategy, and biologically produced sulfur "
                    "species may enhance ZVI reactivity and specificity at remediation sites. However, the impact of ZVI on sulfate-reducing bacteria "
                    "remains complex. This study shows that sulfidation enhances ZVI compatibility with sulfate-reducing bacteria, shifts microbial "
                    "community composition favorably, and supports integrated abiotic-biotic ZVI-SRB strategies for in situ remediation under sulfidic conditions."
                ),
                "featured": True,
            },
            {
                "doi": "10.1016/j.biortech.2021.125738",
                "title": "Anaerobic bacterial responses to carbonaceous materials and implications for contaminant transformation: Cellular, metabolic, and community level findings",
                "authors": "Asef Mohammad Redwan, Kayleigh Millerick",
                "year": 2021,
                "venue": "Bioresource Technology",
                "publication_type": Publication.PublicationType.JOURNAL,
                "publication_url": "https://doi.org/10.1016/j.biortech.2021.125738",
                "abstract": (
                    "Carbonaceous materials (CM) enhance the abundance and activity of bacteria capable of persistent organic (micro)pollutant (POP) "
                    "degradation. This review synthesizes anaerobic bacterial responses to minimally modified CM in non-fuel cell bioremediation "
                    "applications at three stages: attachment, metabolism, and biofilm genetic composition. Established relationships between biological "
                    "behavior and CM surface properties are identified, but temporal relationships are not well understood, making it difficult to "
                    "connect substratum properties and 'pioneer' bacteria with mature microorganism-CM systems. Stark differences in laboratory methodology "
                    "at each temporal stage results in observational, but not causative, linkages as system complexity increases. This review is the first "
                    "to critically examine relationships between material and cellular properties with respect to time, highlighting critical knowledge "
                    "gaps that must be addressed to tailor CM properties for optimized microbial activity in bioremediation."
                ),
                "featured": True,
            },
            {
                "doi": "10.1021/acs.est.0c07702",
                "title": "Effect of Copresence of Zerovalent Iron and Sulfate Reducing Bacteria on Reductive Dechlorination of Trichloroethylene",
                "authors": "Syful Islam, Asef Redwan, Kayleigh Millerick, Jan Filip, Lingfei Fan, Weile Yan",
                "year": 2021,
                "venue": "Environmental Science & Technology",
                "publication_type": Publication.PublicationType.JOURNAL,
                "publication_url": "https://doi.org/10.1021/acs.est.0c07702",
                "abstract": (
                    "Sulfur amendment of zerovalent iron (ZVI) materials has been shown to improve the reactivity and selectivity of ZVI toward a select "
                    "group of organohalide contaminants in groundwater, most notably trichloroethene (TCE). In previous studies, chemical or mechanochemical "
                    "sulfidation methods were used; however, the potential of using sulfate-reducing bacteria (SRB) to enable sulfur amendment has not been "
                    "closely examined. In this study, lab-synthesized nanoscale ZVI (nZVI) and Peerless iron particles (ZVIPLS) were treated in a "
                    "sulfate-reducing monoculture (D. desulfuricans) and an enrichment culture derived from freshwater sediments (AMR-1) prior to reactivity "
                    "assessments with TCE as the model contaminant. ZVI conditioned in both cultures exhibited higher dechlorination efficiencies compared "
                    "to unamended ZVIs. Product distribution data show that, in the SRB-ZVI system, abiotic dechlorination is the dominant reduction pathway, "
                    "demonstrating how SRB-ZVI synergy overcomes limitations of standalone biological or abiotic dechlorination."
                ),
                "featured": False,
            },
            {
                "doi": "10.1007/s13762-021-03434-8",
                "title": "How dynamic is the heavy metals pollution in the Buriganga River of Bangladesh? A spatiotemporal assessment based on environmental indices",
                "authors": "N. Majed, M. I. H. Real, A. Redwan, H. M. Azam",
                "year": 2022,
                "venue": "International Journal of Environmental Science and Technology",
                "publication_type": Publication.PublicationType.JOURNAL,
                "publication_url": "https://doi.org/10.1007/s13762-021-03434-8",
                "abstract": (
                    "Frequent discharge of heavy metals from textiles, tanneries and other anthropogenic sources occurs in Dhaka City, contaminating major "
                    "rivers. Accumulation of heavy metals (Cr, Cd, Pb, Ni, Zn) in water, sediment, phytoplankton and fish species was investigated in "
                    "Buriganga River at three distinct discharge points (Basila Bridge, Hazaribagh, Babu Bazar). Chromium (Cr) was found at alarming "
                    "levels (103 mg/kg in soil, 163 mg/kg in plants) near the Hazaribagh tannery waste discharge point. Biological samples showed clear "
                    "evidence of bioaccumulation. This study emphasizes the necessity of controlling point and nonpoint urban pollution sources."
                ),
                "featured": False,
            },
            {
                "doi": "10.1504/ijgw.2019.104269",
                "title": "Characterisation of spatio-temporal trend in temperature extremes for environmental decision making in Bangladesh",
                "authors": "Md. Mohsan Khudri, Md. Shaddam Hossain Bagmar, Asef Mohammad Redwan",
                "year": 2019,
                "venue": "International Journal of Global Warming",
                "publication_type": Publication.PublicationType.JOURNAL,
                "publication_url": "https://doi.org/10.1504/ijgw.2019.104269",
                "abstract": (
                    "Spatial and sequential variability of extreme temperature events affects environmental decision making. This study analysed trends in "
                    "monthly data of temperature extremes from 23 meteorological stations across Bangladesh using the Mann-Kendall test and Sen's slope "
                    "estimator. Most stations exhibited significant upward trends in both temperature extremes, with the greatest concentration of significant "
                    "trends detected during monsoon and post-monsoon seasons, informing regional climate vulnerability frameworks."
                ),
                "featured": False,
            },
            {
                "doi": "10.1007/978-981-10-8016-6_105",
                "title": "Heavy Metal Contamination in Environmental Compartments of Buriganga River in Dhaka City",
                "authors": "Md. Isreq Hossen Real, Asef Redwan, Md. Mosheur Rahman Shourov, Hossain Azam, Nehreen Majed",
                "year": 2019,
                "venue": "Lecture Notes in Civil Engineering (Springer)",
                "publication_type": Publication.PublicationType.BOOK_CHAPTER,
                "publication_url": "https://doi.org/10.1007/978-981-10-8016-6_105",
                "abstract": (
                    "This book chapter evaluates the partitioning of heavy metals (Cd, Cr, Pb, Ni, Zn) across sediment, surface water, aquatic macrophytes "
                    "(Enhydra fluctuans), and fish in Buriganga River. Cr and Pb exceeded surface water criteria for aquatic life protection, and alarming "
                    "concentrations were recorded in sediment adjacent to historical tannery and industrial effluent channels in Dhaka."
                ),
                "featured": False,
            },
            {
                "doi": "10.2139/ssrn.7625014",
                "title": "From Conventional Sludge-Production Models to Population-Integrated Physics-Informed Neural Networks: A Technical Note on Proposed Conceptual Framework",
                "authors": "Asef Mohammad Redwan, Sakib Hossain Parvez, Puspita Das",
                "year": 2026,
                "venue": "SSRN Electronic Journal",
                "publication_type": Publication.PublicationType.PREPRINT,
                "publication_url": "https://doi.org/10.2139/ssrn.7625014",
                "abstract": (
                    "A conceptual technical note presenting a physics-informed neural network (PINN) architecture integrating biological population dynamics "
                    "with mass-balance constraints to enhance the predictive accuracy and optimization of wastewater sludge digestion and bioprocess control."
                ),
                "featured": False,
            },
        ]
        results = {}
        for pub in publication_records:
            existing = Publication.objects.filter(doi=pub["doi"]).first()
            if existing:
                if force_update and not dry_run:
                    for k, v in pub.items():
                        setattr(existing, k, v)
                    existing.status = Publication.Status.PUBLISHED
                    existing.save()
                    self.stdout.write(f"  [UPDATED] Pub: {pub['title'][:55]}...")
                else:
                    self.stdout.write(f"  [EXISTS]  Pub: {pub['title'][:55]}...")
                results[pub["doi"]] = existing
            else:
                if not dry_run:
                    obj = Publication.objects.create(
                        status=Publication.Status.PUBLISHED,
                        **pub,
                    )
                    results[pub["doi"]] = obj
                    self.stdout.write(self.style.SUCCESS(f"  [CREATED] Pub: {pub['title'][:55]}..."))
                else:
                    self.stdout.write(self.style.SUCCESS(f"  [WOULD CREATE] Pub: {pub['title'][:55]}..."))
        return results

    def import_research_projects(self, areas, pubs, dry_run, force_update):
        project_definitions = [
            {
                "slug": "ai-powered-waste-segregation-circular-bioeconomy",
                "title": "AI-Powered Waste Segregation and Circular Bioeconomy for NSU Green Campus",
                "area_key": "Waste valorization",
                "status": ResearchProject.Status.ACTIVE,
                "start_date": date(2026, 1, 1),
                "end_date": date(2026, 12, 31),
                "summary": "An intelligent waste classification and circular resource recovery initiative deploying computer-vision smart sorting bins and bioconversion of campus cafeteria organic waste into sustainable bio-fertilizer.",
                "collaborations": "North South University Department of Civil and Environmental Engineering, NSU Campus Operations.",
                "funding_notes": "Funded by North South University (NSU Research Grant, BDT 7 Lakh, 2026). Principal Investigator: Dr. Asef M. Redwan.",
                "monitoring_related": True,
                "external_url": "https://www.northsouth.edu/faculty-members/seps/cee/dr.-asef-mohammad-redwan.html",
                "description": (
                    "<p>Rapid urbanization and institutional campus operations produce complex solid waste streams with low baseline recycling rates. "
                    "This research develops and field-tests an automated multi-stream segregation infrastructure powered by edge computer-vision models. "
                    "Smart dustbin prototypes identify, classify, and sort compostable organic materials, recyclable plastics, and municipal refuse at the point of disposal.</p>"
                    "<p>Diverted organic fractions from campus cafeterias are subjected to controlled thermophilic composting and anaerobic fermentation, evaluating process kinetics, "
                    "pathogen inactivation, and nutrient recovery to formulate clean bio-fertilizers supporting sustainable campus landscape ecology.</p>"
                ),
                "methodology": (
                    "<p><strong>1. Computer Vision Sorting:</strong> Embedded deep learning classifiers (convolutional neural networks optimized via TensorRT) run on edge microcontrollers "
                    "paired with high-resolution optical and infrared sensors inside disposal chambers. Automated baffles mechanically route waste into compartmentalized bins.</p>"
                    "<p><strong>2. Bioeconomy Assay:</strong> Food waste is characterized for volatile solids (VS), chemical oxygen demand (COD), and C:N stoichiometry. "
                    "Bioreactor trials evaluate decomposition rates, volatile fatty acid generation, and humification indexes under varying aeration regimens.</p>"
                ),
                "pub_dois": ["10.2139/ssrn.7625014"],
            },
            {
                "slug": "textile-wastewater-treatment-zld",
                "title": "Immobilized Biomass Packed Bed Reactor for Textile Wastewater Treatment and Zero Liquid Discharge",
                "area_key": "Environmental engineering",
                "status": ResearchProject.Status.ACTIVE,
                "start_date": date(2025, 12, 1),
                "end_date": date(2026, 9, 30),
                "summary": "Continuous-flow biological reactor system utilizing immobilized microbial consortia for azo dye decolorization, toxic xenobiotic degradation, and process water recycling aiming for Zero Liquid Discharge in textile dyeing.",
                "collaborations": "ITN-BUET (International Training Network Centre, BUET), North South University.",
                "funding_notes": "Funded by ITN-BUET (BDT 14 Lakh, Dec 2025 – Sep 2026). Principal Investigator: Dr. Asef M. Redwan; Co-Investigators: S.R. Shuvo, N.M. Shuman, N. Nahar, S.E. Haque.",
                "monitoring_related": True,
                "external_url": "https://www.northsouth.edu/faculty-members/seps/cee/dr.-asef-mohammad-redwan.html",
                "description": (
                    "<p>The textile and garment sector is Bangladesh's primary industrial export engine but generates immense volumes of hypersaline, "
                    "highly colored wastewater loaded with refractory synthetic dyes, surfactants, and heavy metal mordants. Standalone chemical coagulation "
                    "produces massive toxic sludge volumes, while conventional activated sludge systems struggle with dye toxicity and shock loading.</p>"
                    "<p>This project develops an advanced Immobilized Biomass Packed Bed Reactor (IB-PBR). By encapsulating adapted microbial consortia "
                    "within high-surface-area porous carriers, the system achieves elevated biomass retention, robust resilience against chemical shock, "
                    "and sustained enzymatic cleavage of azo bonds, preparing high-quality treated water for in-plant reuse toward Zero Liquid Discharge (ZLD).</p>"
                ),
                "methodology": (
                    "<p><strong>1. Bioreactor Configuration:</strong> Vertical packed bed column with inert structured packing supporting acclimated biofilm cultures. "
                    "Continuous hydraulic testing evaluates empty bed contact time (EBCT), hydraulic retention time (HRT), and pollutant loading rates.</p>"
                    "<p><strong>2. Analytical Monitoring:</strong> Spectrophotometric color analysis, TOC/COD removal efficiencies, gas chromatography-mass spectrometry (GC-MS) "
                    "for dye metabolite pathway elucidation, and residual salinity testing for membrane-polishing compatibility.</p>"
                ),
                "pub_dois": ["10.1016/j.biortech.2021.125738", "10.1007/s11356-025-37256-9"],
            },
            {
                "slug": "climate-smart-sanitation-safety-planning",
                "title": "Climate-Smart Integrated Water-Sanitation Safety Planning for Coastal Bangladesh",
                "area_key": "Environmental sustainability",
                "status": ResearchProject.Status.ACTIVE,
                "start_date": date(2026, 2, 1),
                "end_date": date(2027, 3, 31),
                "summary": "Risk-based climate vulnerability framework and resilient technological interventions safeguarding drinking water resources and sanitation infrastructure against storm surges and salinity intrusion in coastal communities.",
                "collaborations": "United International University (UIU), ITN-BUET, North South University.",
                "funding_notes": "Funded by United International University Research Grant (BDT 12 Lakh, Feb 2026 – Mar 2027). Principal Investigator: Dr. Asef M. Redwan.",
                "monitoring_related": False,
                "external_url": "https://www.northsouth.edu/faculty-members/seps/cee/dr.-asef-mohammad-redwan.html",
                "description": (
                    "<p>Coastal districts in southern Bangladesh face intersecting climate hazards including cyclonic inundation, saline water intrusion, "
                    "and waterlogged ground conditions that compromise pit latrines and shallow tubewells. This contamination drives recurrent waterborne disease outbreaks.</p>"
                    "<p>This initiative formulates climate-smart Water Safety Plans (WSP) and Sanitation Safety Plans (SSP) adapted to coastal delta vulnerabilities. "
                    "Through field surveys and community monitoring, the study designs flood-resilient fecal sludge containment technologies and safe drinking water barriers.</p>"
                ),
                "methodology": (
                    "<p><strong>1. Vulnerability Mapping:</strong> Hydrogeological salinity transects, sanitary risk scoring, and spatial mapping of inundation vulnerability in coastal study sites.</p>"
                    "<p><strong>2. Barrier Engineering:</strong> Assessment of sealed elevated pit designs, sand-envelope filters, and microbiological barrier verification using fecal indicator bacteria (E. coli, coliform assays).</p>"
                ),
                "pub_dois": ["10.1504/ijgw.2019.104269"],
            },
            {
                "slug": "rare-earth-element-biorecovery",
                "title": "Proteomic Insights and Biorecovery of Critical Materials & Rare Earth Elements",
                "area_key": "Resource recovery",
                "status": ResearchProject.Status.COMPLETED,
                "start_date": date(2022, 10, 1),
                "end_date": date(2024, 9, 30),
                "summary": "Elucidating microbial stress response pathways and cellular interactions between anaerobic fermenters and technology-critical lanthanides to design bio-enrichment and recovery technologies.",
                "collaborations": "Idaho National Laboratory (INL), Idaho State University, Texas Tech University.",
                "funding_notes": "Supported by U.S. Department of Energy (DOE) / Idaho National Laboratory LDRD Program (USD 898,265, 2022–2024). Principal Investigator: Dr. Asef M. Redwan.",
                "monitoring_related": False,
                "external_url": "https://www.northsouth.edu/faculty-members/seps/cee/dr.-asef-mohammad-redwan.html",
                "description": (
                    "<p>Rare earth elements (REEs) are indispensable components of wind turbines, electric vehicle motors, and modern electronic systems, "
                    "yet conventional chemical extraction is environmentally intensive and geographically constrained. Biological enrichment through microbial "
                    "biosorption and biomineralization presents an environmentally friendly alternative.</p>"
                    "<p>Directed as Principal Investigator at Idaho National Laboratory, this project investigated anaerobic fermenting microorganisms "
                    "(Clostridium sporogenes and Sporacetigenium mesophilum) to uncover the biochemical mechanisms mediating lanthanide binding, transport, "
                    "and tolerance, establishing fundamental scientific foundations for biomining.</p>"
                ),
                "methodology": (
                    "<p><strong>1. Anaerobic Fermentation:</strong> Strict anaerobic culturing under europium and samarium exposure gradients (sub-micromolar to 600 µM).</p>"
                    "<p><strong>2. Omics Characterization:</strong> High-resolution LC-MS/MS proteomic profiling comparing REE exposure against essential divalent metals (Fe, Ca, Zn), "
                    "identifying ATP synthase modulation, electron transfer flavoproteins, and peptide candidates for engineered capture molecules.</p>"
                ),
                "pub_dois": ["10.1021/acsomega.5c09729", "10.1007/s11356-025-37256-9"],
            },
            {
                "slug": "urban-river-heavy-metal-dynamics",
                "title": "Heavy Metal Pollution Dynamics and Ecological Partitioning in Buriganga River",
                "area_key": "Environmental sustainability",
                "status": ResearchProject.Status.COMPLETED,
                "start_date": date(2018, 1, 1),
                "end_date": date(2021, 12, 31),
                "summary": "Multi-compartment spatial and temporal assessment of toxic heavy metal accumulation across sediment, surface water, aquatic plants, and fish species in Dhaka's primary urban river.",
                "collaborations": "University of Asia Pacific, North South University, Texas Tech University.",
                "funding_notes": "Academic institutional research project led by regional researchers and Dr. Asef M. Redwan.",
                "monitoring_related": True,
                "external_url": "https://doi.org/10.1007/s13762-021-03434-8",
                "description": (
                    "<p>Dhaka's Buriganga River represents one of the most chemically stressed urban river corridors in South Asia, receiving unsegregated effluent "
                    "from tanneries, textile wet processing, and urban runoff. This study quantified spatial metal distributions (Cr, Cd, Pb, Ni, Zn) "
                    "and biological accumulation factors across multiple ecological compartments.</p>"
                ),
                "methodology": (
                    "<p>Sampling across Basila Bridge, Hazaribagh, and Babu Bazar. Atomic Absorption Spectrophotometry (AAS) determination of metal concentrations, "
                    "calculating contamination factors (CF), plant concentration factors (PCF), and biomagnification factors across trophic levels.</p>"
                ),
                "pub_dois": ["10.1007/s13762-021-03434-8", "10.1007/978-981-10-8016-6_105"],
            },
        ]
        results = {}
        for pdata in project_definitions:
            slug = pdata["slug"]
            area = areas.get(pdata["area_key"])
            pub_dois = pdata.pop("pub_dois", [])
            area_key = pdata.pop("area_key")

            existing = ResearchProject.objects.filter(slug=slug).first()
            if existing:
                if force_update and not dry_run:
                    for k, v in pdata.items():
                        setattr(existing, k, v)
                    existing.area = area
                    existing.is_published = True
                    for doi in pub_dois:
                        if doi in pubs:
                            existing.publications.add(pubs[doi])
                    existing.save()
                    self.stdout.write(f"  [UPDATED] Project: {pdata['title'][:55]}...")
                else:
                    self.stdout.write(f"  [EXISTS]  Project: {pdata['title'][:55]}...")
                results[slug] = existing
            else:
                if not dry_run:
                    obj = ResearchProject.objects.create(
                        area=area,
                        is_published=True,
                        **pdata,
                    )
                    for doi in pub_dois:
                        if doi in pubs:
                            obj.publications.add(pubs[doi])
                    obj.save()
                    results[slug] = obj
                    self.stdout.write(self.style.SUCCESS(f"  [CREATED] Project: {pdata['title'][:55]}..."))
                else:
                    self.stdout.write(self.style.SUCCESS(f"  [WOULD CREATE] Project: {pdata['title'][:55]}..."))
        return results

    def import_grants(self, projects, dry_run, force_update):
        grant_definitions = [
            {
                "title": "Immobilized Biomass Packed Bed Reactor (IB-PBR) as a Combined Dye Removal and Zero Liquid Discharge (ZLD) Technology from Textile Wastewater of Yarn Dyeing Facility in Bangladesh",
                "funding_organization": "ITN-BUET, Bangladesh",
                "amount_display": "BDT 14 Lakh",
                "amount": 1400000.00,
                "currency": "BDT",
                "start_date": date(2025, 12, 1),
                "end_date": date(2026, 9, 30),
                "role": "Principal Investigator (PI)",
                "awarded_institution": "North South University",
                "category": Grant.Category.LAB,
                "project_slug": "textile-wastewater-treatment-zld",
                "public_source_url": "https://www.northsouth.edu/faculty-members/seps/cee/dr.-asef-mohammad-redwan.html",
                "summary": "Development of continuous packed-bed bio-reactors using immobilized microbial consortia for azo dye decolorization and water recycling in yarn dyeing facilities toward Zero Liquid Discharge.",
                "sort_order": 1,
            },
            {
                "title": "Smart Dustbin with AI-Powered Waste Segregation and Circular Bioeconomy from Canteen Food Waste for NSU Green Campus",
                "funding_organization": "North South University (CTRG Research Grant)",
                "amount_display": "BDT 7 Lakh",
                "amount": 700000.00,
                "currency": "BDT",
                "start_date": date(2026, 1, 1),
                "end_date": date(2026, 12, 31),
                "role": "Principal Investigator (PI)",
                "awarded_institution": "North South University",
                "category": Grant.Category.LAB,
                "project_slug": "ai-powered-waste-segregation-circular-bioeconomy",
                "public_source_url": "https://www.northsouth.edu/faculty-members/seps/cee/dr.-asef-mohammad-redwan.html",
                "summary": "Campus green sustainability initiative creating computer-vision smart dustbin stations for automated waste segregation and subsequent conversion of food waste into organic bio-fertilizer.",
                "sort_order": 2,
            },
            {
                "title": "Climate-smart Integrated Water-Sanitation Safety Plan for Coastal Bangladesh",
                "funding_organization": "United International University (UIU)",
                "amount_display": "BDT 12 Lakh",
                "amount": 1200000.00,
                "currency": "BDT",
                "start_date": date(2026, 2, 1),
                "end_date": date(2027, 3, 31),
                "role": "Principal Investigator (PI)",
                "awarded_institution": "North South University / United International University",
                "category": Grant.Category.DIRECTOR,
                "project_slug": "climate-smart-sanitation-safety-planning",
                "public_source_url": "https://www.northsouth.edu/faculty-members/seps/cee/dr.-asef-mohammad-redwan.html",
                "summary": "Formulation and testing of resilient sanitation safety plans and flood-protected water containment barriers for vulnerable coastal communities in Bangladesh.",
                "sort_order": 3,
            },
            {
                "title": "Proteomic Insights to Interaction Between Fermenters and Rare Earth Elements",
                "funding_organization": "U.S. Department of Energy (DOE) / Idaho National Laboratory (INL)",
                "amount_display": "USD 898,265",
                "amount": 898265.00,
                "currency": "USD",
                "start_date": date(2022, 10, 1),
                "end_date": date(2024, 9, 30),
                "role": "Principal Investigator (PI)",
                "awarded_institution": "Idaho National Laboratory (INL)",
                "category": Grant.Category.PREVIOUS,
                "project_slug": "rare-earth-element-biorecovery",
                "public_source_url": "https://www.northsouth.edu/faculty-members/seps/cee/dr.-asef-mohammad-redwan.html",
                "summary": "Foundational Laboratory Directed Research and Development (LDRD) award investigating molecular proteome responses and critical element recovery using anaerobic fermenters.",
                "sort_order": 4,
            },
            {
                "title": "Biological Reduction of Lanthanides and Critical Material Recovery",
                "funding_organization": "U.S. Department of Energy (DOE) / Idaho National Laboratory (INL)",
                "amount_display": "USD 70,000",
                "amount": 70000.00,
                "currency": "USD",
                "start_date": date(2021, 10, 1),
                "end_date": date(2022, 9, 30),
                "role": "Principal Investigator (PI)",
                "awarded_institution": "Idaho National Laboratory (INL)",
                "category": Grant.Category.PREVIOUS,
                "project_slug": "rare-earth-element-biorecovery",
                "public_source_url": "https://www.northsouth.edu/faculty-members/seps/cee/dr.-asef-mohammad-redwan.html",
                "summary": "Seed investigation exploring microbial reduction pathways and critical material biosorption in anaerobic systems.",
                "sort_order": 5,
            },
        ]
        results = []
        for gdata in grant_definitions:
            project_slug = gdata.pop("project_slug", None)
            related_proj = projects.get(project_slug) if project_slug else None

            existing = Grant.objects.filter(
                title=gdata["title"],
                funding_organization=gdata["funding_organization"],
            ).first()

            if existing:
                if force_update and not dry_run:
                    for k, v in gdata.items():
                        setattr(existing, k, v)
                    existing.related_project = related_proj
                    existing.is_published = True
                    existing.is_verified = True
                    existing.save()
                    self.stdout.write(f"  [UPDATED] Grant: {gdata['title'][:55]}...")
                else:
                    self.stdout.write(f"  [EXISTS]  Grant: {gdata['title'][:55]}...")
                results.append(existing)
            else:
                if not dry_run:
                    obj = Grant.objects.create(
                        related_project=related_proj,
                        is_published=True,
                        is_verified=True,
                        **gdata,
                    )
                    results.append(obj)
                    self.stdout.write(self.style.SUCCESS(f"  [CREATED] Grant: {gdata['title'][:55]}..."))
                else:
                    self.stdout.write(self.style.SUCCESS(f"  [WOULD CREATE] Grant: {gdata['title'][:55]}..."))
        return results

    def import_team_director(self, projects, dry_run, force_update):
        director_data = {
            "name": "Dr. Asef Mohammad Redwan",
            "role": "Laboratory Director & Assistant Professor",
            "category": TeamMember.Category.DIRECTOR,
            "affiliation": "Department of Civil and Environmental Engineering, North South University",
            "biography": (
                "Dr. Asef Mohammad Redwan is an environmental engineering scientist specializing in environmental biotechnology, "
                "the biogeochemistry of metal-bacteria interactions, engineered bioremediation of organic and inorganic pollutants, "
                "and critical material recovery.\n\n"
                "He holds a Ph.D. and M.S. in Environmental Engineering from Texas Tech University (USA) and a B.Sc. in Civil Engineering "
                "from the Bangladesh University of Engineering and Technology (BUET). Prior to founding Waste Mining Lab at North South University, "
                "he served as a Staff Scientist and Postdoctoral Researcher at the Idaho National Laboratory (INL) in the United States, "
                "directing multiple U.S. Department of Energy (DOE) research initiatives. He maintains an active joint appointment as Affiliate Faculty "
                "at Idaho State University and collaborates extensively with ITN-BUET on climate-resilient water and sanitation engineering."
            ),
            "research_interests": (
                "Environmental biotechnology; metal-microbe biogeochemistry; rare earth element and critical material recovery; "
                "textile wastewater treatment & Zero Liquid Discharge (ZLD); AI-driven waste segregation; circular bioeconomy; "
                "climate-resilient water and sanitation safety planning."
            ),
            "email": "asef.redwan@northsouth.edu",
            "profile_url": "https://www.northsouth.edu/faculty-members/seps/cee/dr.-asef-mohammad-redwan.html",
            "sort_order": 1,
            "is_published": True,
        }

        existing = TeamMember.objects.filter(
            name=director_data["name"],
            category=TeamMember.Category.DIRECTOR,
        ).first()

        if existing:
            if force_update and not dry_run:
                for k, v in director_data.items():
                    setattr(existing, k, v)
                existing.save()
                for proj in projects.values():
                    existing.projects.add(proj)
                self.stdout.write(f"  [UPDATED] Director: {director_data['name']}")
            else:
                self.stdout.write(f"  [EXISTS]  Director: {director_data['name']}")
            return existing
        else:
            if not dry_run:
                obj = TeamMember.objects.create(**director_data)
                for proj in projects.values():
                    obj.projects.add(proj)
                self.stdout.write(self.style.SUCCESS(f"  [CREATED] Director: {director_data['name']}"))
                return obj
            else:
                self.stdout.write(self.style.SUCCESS(f"  [WOULD CREATE] Director: {director_data['name']}"))
                return None

    def import_news(self, projects, pubs, dry_run, force_update):
        news_section = SectionPage.objects.filter(slug="news").first()
        if not news_section:
            self.stdout.write(self.style.WARNING("  [SKIP] News SectionPage not found."))
            return []

        news_articles = [
            {
                "title": "Waste Mining Lab Awarded NSU Research Grant for AI-Powered Campus Bioeconomy",
                "slug": "nsu-grant-ai-waste-segregation-bioeconomy",
                "date": date(2026, 1, 15),
                "category": NewsArticlePage.Category.LAB,
                "featured": True,
                "excerpt": (
                    "North South University has awarded competitive research grant funding to Waste Mining Lab to develop and pilot "
                    "smart dustbin units equipped with computer-vision sorting, converting campus cafeteria food waste into bio-fertilizer."
                ),
                "body": (
                    "<p>Waste Mining Lab has commenced work on an innovative applied sustainability initiative funded by North South University. "
                    "Led by Dr. Asef Mohammad Redwan as Principal Investigator, the project combines edge artificial intelligence with circular bioeconomy processes.</p>"
                    "<p>The research team is engineering smart receptacle stations with real-time optical image classification to automate solid waste segregation "
                    "at the point of disposal. Collected cafeteria organic waste will be processed through thermophilic digestion and aerobic composting, "
                    "generating verified bio-fertilizers for campus landscaping and establishing a measurable model for institutional circular bioeconomies.</p>"
                ),
                "project_slug": "ai-powered-waste-segregation-circular-bioeconomy",
                "pub_doi": "10.2139/ssrn.7625014",
            },
            {
                "title": "New Peer-Reviewed Studies on Rare Earth Element Microbial Interactions Published in ACS Omega and ESPR",
                "slug": "rare-earth-element-microbial-studies-published",
                "date": date(2026, 2, 10),
                "category": NewsArticlePage.Category.RESEARCH,
                "featured": False,
                "excerpt": (
                    "Dr. Asef M. Redwan and international collaborators from Idaho National Laboratory report significant proteomic and metabolic "
                    "findings on anaerobic bacterial responses to europium and samarium in ACS Omega and Environmental Science and Pollution Research."
                ),
                "body": (
                    "<p>Two peer-reviewed research papers exploring the interaction of microorganisms with technology-critical rare earth elements (REEs) "
                    "have been published in leading international environmental journals.</p>"
                    "<p>The first paper, appearing in <em>ACS Omega</em>, resolves quantitative proteomic shifts in <em>Clostridium sporogenes</em> exposed to "
                    "europium and samarium, revealing distinct ATP synthase and electron transfer flavoprotein expression patterns. The companion paper in "
                    "<em>Environmental Science and Pollution Research</em> documents concentration-dependent physiological impacts on <em>Sporacetigenium mesophilum</em>, "
                    "providing molecular groundwork for biomining and critical material recovery.</p>"
                ),
                "project_slug": "rare-earth-element-biorecovery",
                "pub_doi": "10.1021/acsomega.5c09729",
            },
            {
                "title": "ITN-BUET Grants Award for Immobilized Biomass Reactor Research on Textile Dye Removal & ZLD",
                "slug": "itn-buet-textile-wastewater-zld-award",
                "date": date(2025, 12, 5),
                "category": NewsArticlePage.Category.ANNOUNCEMENT,
                "featured": False,
                "excerpt": (
                    "ITN-BUET announces research grant award to North South University researchers led by Dr. Asef M. Redwan to pioneer "
                    "Immobilized Biomass Packed Bed Reactors for industrial textile dye removal and Zero Liquid Discharge."
                ),
                "body": (
                    "<p>ITN-BUET has officially approved funding for a 10-month research project titled <em>'Immobilized Biomass Packed Bed Reactor (IB-PBR) "
                    "as a Combined Dye Removal and Zero Liquid Discharge (ZLD) Technology from Textile Wastewater of Yarn Dyeing Facility in Bangladesh'</em>.</p>"
                    "<p>Directed by Dr. Asef Mohammad Redwan as Principal Investigator alongside co-investigators from NSU CEE, the project addresses one of Bangladesh's "
                    "most pressing industrial environmental challenges: treating hypersaline, recalcitrant dye effluents to effluent reuse standards.</p>"
                ),
                "project_slug": "textile-wastewater-treatment-zld",
                "pub_doi": "10.1016/j.biortech.2021.125738",
            },
        ]
        results = []
        for article in news_articles:
            slug = article.pop("slug")
            project_slug = article.pop("project_slug", None)
            pub_doi = article.pop("pub_doi", None)
            related_proj = projects.get(project_slug) if project_slug else None
            related_pub = pubs.get(pub_doi) if pub_doi else None

            existing = NewsArticlePage.objects.child_of(news_section).filter(slug=slug).first()
            if existing:
                if force_update and not dry_run:
                    for k, v in article.items():
                        setattr(existing, k, v)
                    existing.related_project = related_proj
                    existing.related_publication = related_pub
                    existing.save()
                    self.stdout.write(f"  [UPDATED] News: {article['title'][:55]}...")
                else:
                    self.stdout.write(f"  [EXISTS]  News: {article['title'][:55]}...")
                results.append(existing)
            else:
                if not dry_run:
                    page = NewsArticlePage(
                        slug=slug,
                        live=True,
                        has_unpublished_changes=False,
                        related_project=related_proj,
                        related_publication=related_pub,
                        **article,
                    )
                    news_section.add_child(instance=page)
                    results.append(page)
                    self.stdout.write(self.style.SUCCESS(f"  [CREATED] News: {article['title'][:55]}..."))
                else:
                    self.stdout.write(self.style.SUCCESS(f"  [WOULD CREATE] News: {article['title'][:55]}..."))
        return results

    def sync_homepage(self, dry_run):
        home = HomePage.objects.first()
        if not home:
            return

        if not dry_run:
            if not home.hero_headline:
                home.hero_headline = "Waste Mining Lab"
            if not home.hero_subtitle:
                home.hero_subtitle = (
                    "At Waste Mining Lab, we explore how discarded materials, environmental biotechnology, "
                    "and resource recovery can transform environmental challenges into sustainable solutions. "
                    "Our research at North South University investigates what waste can teach us about a circular, resilient future."
                )
            if not home.lab_introduction:
                home.lab_introduction = (
                    "<p>Waste Mining Lab is based in the Department of Civil and Environmental Engineering at North South University. "
                    "Led by Dr. Asef Mohammad Redwan, our group advances environmental sustainability, waste valorization, "
                    "resource recovery, and industrial wastewater treatment through rigorous academic research and practical technology development.</p>"
                )
            home.save()
            self.stdout.write(self.style.SUCCESS("  [SYNCHRONIZED] Homepage hero copy and lab introduction."))
        else:
            self.stdout.write(self.style.SUCCESS("  [WOULD SYNC] Homepage hero copy and lab introduction."))
