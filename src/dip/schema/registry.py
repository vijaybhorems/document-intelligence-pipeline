"""The field registry: every extracted field is defined exactly once, here.

Prompts, the LLM and domain schemas, the gold-label builder, eval matchers
and report groupings are all driven from ``FIELDS`` (SPEC §4.2).

Definitions are adapted from the CUAD v1 README (CC BY 4.0, The Atticus Project).
``cuad_category`` is the exact spelling used in ``master_clauses.csv`` and
``CUAD_v1.json``, which differs from the README's display names in places.
"""

from dataclasses import dataclass, replace
from enum import StrEnum


class FieldType(StrEnum):
    ENTITY_LIST = "entity_list"
    TEXT = "text"
    DATE = "date"
    DURATION = "duration"
    JURISDICTION = "jurisdiction"
    CLAUSE = "clause"


class FieldGroup(StrEnum):
    """Related fields extracted together in one LLM call (decision D4).

    For clause fields the group doubles as the clause family used in reports.
    """

    GENERAL = "general"
    TERM = "term_and_termination"
    RESTRICTIVE = "restrictive_covenants"
    COMMERCIAL = "commercial_terms"
    IP_LICENSING = "ip_and_licensing"
    LIABILITY = "liability_and_risk"


@dataclass(frozen=True)
class FieldSpec:
    name: str
    cuad_category: str
    field_type: FieldType
    group: FieldGroup
    definition: str
    # Filled in Phase 2 (phrasing slice, SPEC §10.6) and Phase 5 (prompting, §7.2).
    canonical_cues: tuple[str, ...] = ()
    phrasing_variants: tuple[str, ...] = ()

    @property
    def csv_answer_column(self) -> str:
        if self.cuad_category == "Notice Period To Terminate Renewal":
            return "Notice Period To Terminate Renewal- Answer"  # sic: CUAD's header has a typo
        return f"{self.cuad_category}-Answer"

    @property
    def clause_family(self) -> FieldGroup | None:
        return self.group if self.field_type is FieldType.CLAUSE else None


_T, _G = FieldType, FieldGroup

_FIELDS: tuple[FieldSpec, ...] = (
    # ── Typed fields (8) ────────────────────────────────────────────────────
    FieldSpec("document_name", "Document Name", _T.TEXT, _G.GENERAL, "The name of the contract."),
    FieldSpec(
        "parties",
        "Parties",
        _T.ENTITY_LIST,
        _G.GENERAL,
        "The two or more parties who signed the contract.",
    ),
    FieldSpec("agreement_date", "Agreement Date", _T.DATE, _G.GENERAL, "The date of the contract."),
    FieldSpec(
        "effective_date",
        "Effective Date",
        _T.DATE,
        _G.GENERAL,
        "The date when the contract is effective.",
    ),
    FieldSpec(
        "governing_law",
        "Governing Law",
        _T.JURISDICTION,
        _G.GENERAL,
        "Which state/country's law governs the interpretation of the contract?",
    ),
    FieldSpec(
        "expiration_date",
        "Expiration Date",
        _T.DATE,
        _G.TERM,
        "On what date will the contract's initial term expire?",
    ),
    FieldSpec(
        "renewal_term",
        "Renewal Term",
        _T.DURATION,
        _G.TERM,
        "What is the renewal term after the initial term expires? This includes automatic "
        "extensions and unilateral extensions with prior notice.",
    ),
    FieldSpec(
        "notice_period_to_terminate_renewal",
        "Notice Period To Terminate Renewal",
        _T.DURATION,
        _G.TERM,
        "What is the notice period required to terminate renewal?",
    ),
    # ── Clause fields (33) ──────────────────────────────────────────────────
    FieldSpec(
        "termination_for_convenience",
        "Termination For Convenience",
        _T.CLAUSE,
        _G.TERM,
        "Can a party terminate this contract without cause (solely by giving a notice and "
        "allowing a waiting period to expire)?",
    ),
    FieldSpec(
        "change_of_control",
        "Change Of Control",
        _T.CLAUSE,
        _G.TERM,
        "Does one party have the right to terminate or is consent or notice required of the "
        "counterparty if such party undergoes a change of control, such as a merger, stock "
        "sale, transfer of all or substantially all of its assets or business, or assignment "
        "by operation of law?",
    ),
    FieldSpec(
        "anti_assignment",
        "Anti-Assignment",
        _T.CLAUSE,
        _G.TERM,
        "Is consent or notice required of a party if the contract is assigned to a third party?",
    ),
    FieldSpec(
        "post_termination_services",
        "Post-Termination Services",
        _T.CLAUSE,
        _G.TERM,
        "Is a party subject to obligations after the termination or expiration of a "
        "contract, including any post-termination transition, payment, transfer of IP, "
        "wind-down, last-buy, or similar commitments?",
    ),
    FieldSpec(
        "non_compete",
        "Non-Compete",
        _T.CLAUSE,
        _G.RESTRICTIVE,
        "Is there a restriction on the ability of a party to compete with the counterparty "
        "or operate in a certain geography or business or technology sector?",
    ),
    FieldSpec(
        "exclusivity",
        "Exclusivity",
        _T.CLAUSE,
        _G.RESTRICTIVE,
        "Is there an exclusive dealing commitment with the counterparty? This includes a "
        "commitment to procure all 'requirements' from one party of certain technology, "
        "goods, or services or a prohibition on licensing or selling technology, goods or "
        "services to third parties, or a prohibition on collaborating or working with other "
        "parties, whether during the contract or after the contract ends (or both).",
    ),
    FieldSpec(
        "no_solicit_of_customers",
        "No-Solicit Of Customers",
        _T.CLAUSE,
        _G.RESTRICTIVE,
        "Is a party restricted from contracting or soliciting customers or partners of the "
        "counterparty, whether during the contract or after the contract ends (or both)?",
    ),
    FieldSpec(
        "competitive_restriction_exception",
        "Competitive Restriction Exception",
        _T.CLAUSE,
        _G.RESTRICTIVE,
        "The exceptions or carveouts to Non-Compete, Exclusivity and No-Solicit of Customers.",
    ),
    FieldSpec(
        "no_solicit_of_employees",
        "No-Solicit Of Employees",
        _T.CLAUSE,
        _G.RESTRICTIVE,
        "Is there a restriction on a party's soliciting or hiring employees and/or "
        "contractors from the counterparty, whether during the contract or after the "
        "contract ends (or both)?",
    ),
    FieldSpec(
        "non_disparagement",
        "Non-Disparagement",
        _T.CLAUSE,
        _G.RESTRICTIVE,
        "Is there a requirement on a party not to disparage the counterparty?",
    ),
    FieldSpec(
        "most_favored_nation",
        "Most Favored Nation",
        _T.CLAUSE,
        _G.COMMERCIAL,
        "Is there a clause that if a third party gets better terms on the licensing or sale "
        "of technology/goods/services described in the contract, the buyer of such "
        "technology/goods/services under the contract shall be entitled to those better "
        "terms?",
    ),
    FieldSpec(
        "rofr_rofo_rofn",
        "Rofr/Rofo/Rofn",
        _T.CLAUSE,
        _G.COMMERCIAL,
        "Is there a clause granting one party a right of first refusal, right of first offer "
        "or right of first negotiation to purchase, license, market, or distribute equity "
        "interest, technology, assets, products or services?",
    ),
    FieldSpec(
        "revenue_profit_sharing",
        "Revenue/Profit Sharing",
        _T.CLAUSE,
        _G.COMMERCIAL,
        "Is one party required to share revenue or profit with the counterparty for any "
        "technology, goods, or services?",
    ),
    FieldSpec(
        "price_restrictions",
        "Price Restrictions",
        _T.CLAUSE,
        _G.COMMERCIAL,
        "Is there a restriction on the ability of a party to raise or reduce prices of "
        "technology, goods, or services provided?",
    ),
    FieldSpec(
        "minimum_commitment",
        "Minimum Commitment",
        _T.CLAUSE,
        _G.COMMERCIAL,
        "Is there a minimum order size or minimum amount or units per-time period that one "
        "party must buy from the counterparty under the contract?",
    ),
    FieldSpec(
        "volume_restriction",
        "Volume Restriction",
        _T.CLAUSE,
        _G.COMMERCIAL,
        "Is there a fee increase or consent requirement, etc. if one party's use of the "
        "product/services exceeds certain threshold?",
    ),
    FieldSpec(
        "audit_rights",
        "Audit Rights",
        _T.CLAUSE,
        _G.COMMERCIAL,
        "Does a party have the right to audit the books, records, or physical locations of "
        "the counterparty to ensure compliance with the contract?",
    ),
    FieldSpec(
        "insurance",
        "Insurance",
        _T.CLAUSE,
        _G.COMMERCIAL,
        "Is there a requirement for insurance that must be maintained by one party for the "
        "benefit of the counterparty?",
    ),
    FieldSpec(
        "ip_ownership_assignment",
        "Ip Ownership Assignment",
        _T.CLAUSE,
        _G.IP_LICENSING,
        "Does intellectual property created by one party become the property of the "
        "counterparty, either per the terms of the contract or upon the occurrence of "
        "certain events?",
    ),
    FieldSpec(
        "joint_ip_ownership",
        "Joint Ip Ownership",
        _T.CLAUSE,
        _G.IP_LICENSING,
        "Is there any clause providing for joint or shared ownership of intellectual "
        "property between the parties to the contract?",
    ),
    FieldSpec(
        "license_grant",
        "License Grant",
        _T.CLAUSE,
        _G.IP_LICENSING,
        "Does the contract contain a license granted by one party to its counterparty?",
    ),
    FieldSpec(
        "non_transferable_license",
        "Non-Transferable License",
        _T.CLAUSE,
        _G.IP_LICENSING,
        "Does the contract limit the ability of a party to transfer the license being "
        "granted to a third party?",
    ),
    FieldSpec(
        "affiliate_license_licensor",
        "Affiliate License-Licensor",
        _T.CLAUSE,
        _G.IP_LICENSING,
        "Does the contract contain a license grant by affiliates of the licensor or that "
        "includes intellectual property of affiliates of the licensor?",
    ),
    FieldSpec(
        "affiliate_license_licensee",
        "Affiliate License-Licensee",
        _T.CLAUSE,
        _G.IP_LICENSING,
        "Does the contract contain a license grant to a licensee (incl. sublicensor) and the "
        "affiliates of such licensee/sublicensor?",
    ),
    FieldSpec(
        "unlimited_all_you_can_eat_license",
        "Unlimited/All-You-Can-Eat-License",
        _T.CLAUSE,
        _G.IP_LICENSING,
        "Is there a clause granting one party an 'enterprise', 'all you can eat' or "
        "unlimited usage license?",
    ),
    FieldSpec(
        "irrevocable_or_perpetual_license",
        "Irrevocable Or Perpetual License",
        _T.CLAUSE,
        _G.IP_LICENSING,
        "Does the contract contain a license grant that is irrevocable or perpetual?",
    ),
    FieldSpec(
        "source_code_escrow",
        "Source Code Escrow",
        _T.CLAUSE,
        _G.IP_LICENSING,
        "Is one party required to deposit its source code into escrow with a third party, "
        "which can be released to the counterparty upon the occurrence of certain events "
        "(bankruptcy, insolvency, etc.)?",
    ),
    FieldSpec(
        "covenant_not_to_sue",
        "Covenant Not To Sue",
        _T.CLAUSE,
        _G.IP_LICENSING,
        "Is a party restricted from contesting the validity of the counterparty's ownership "
        "of intellectual property or otherwise bringing a claim against the counterparty "
        "for matters unrelated to the contract?",
    ),
    FieldSpec(
        "uncapped_liability",
        "Uncapped Liability",
        _T.CLAUSE,
        _G.LIABILITY,
        "Is a party's liability uncapped upon the breach of its obligation in the contract? "
        "This also includes uncapped liability for a particular type of breach such as IP "
        "infringement or breach of confidentiality obligation.",
    ),
    FieldSpec(
        "cap_on_liability",
        "Cap On Liability",
        _T.CLAUSE,
        _G.LIABILITY,
        "Does the contract include a cap on liability upon the breach of a party's "
        "obligation? This includes time limitation for the counterparty to bring claims or "
        "maximum amount for recovery.",
    ),
    FieldSpec(
        "liquidated_damages",
        "Liquidated Damages",
        _T.CLAUSE,
        _G.LIABILITY,
        "Does the contract contain a clause that would award either party liquidated "
        "damages for breach or a fee upon the termination of a contract (termination fee)?",
    ),
    # CUAD's README gives a duration answer format, but master_clauses.csv only
    # records Yes/No for this category, so it is scored as a clause.
    FieldSpec(
        "warranty_duration",
        "Warranty Duration",
        _T.CLAUSE,
        _G.LIABILITY,
        "What is the duration of any warranty against defects or errors in technology, "
        "products, or services provided under the contract?",
    ),
    FieldSpec(
        "third_party_beneficiary",
        "Third Party Beneficiary",
        _T.CLAUSE,
        _G.LIABILITY,
        "Is there a non-contracting party who is a beneficiary to some or all of the clauses "
        "in the contract and therefore can enforce its rights against a contracting party?",
    ),
)

# The obvious wording for each field, matched as word prefixes ("own" matches
# "ownership", not "known"). A gold span containing a cue is "canonical"; the
# phrasing slice (SPEC §10.6) compares recall on canonical vs non-canonical spans.
# Parties and agreement/effective dates have no cues: their spans are names or
# date strings, not phrasing.
CANONICAL_CUES: dict[str, tuple[str, ...]] = {
    "document_name": ("agreement",),
    "governing_law": ("governed by", "governing law", "laws of"),
    "expiration_date": ("expir", "initial term", "term of this agreement"),
    "renewal_term": ("renew",),
    "notice_period_to_terminate_renewal": ("non-renewal", "not to renew", "prior written notice"),
    "termination_for_convenience": ("for convenience", "without cause", "for any reason"),
    "change_of_control": ("change of control", "change in control"),
    "anti_assignment": ("assign",),
    "post_termination_services": ("after termination", "upon termination", "post-termination",
                                  "following termination", "surviv"),
    "non_compete": ("compet",),
    "exclusivity": ("exclusiv",),
    "no_solicit_of_customers": ("solicit",),
    "competitive_restriction_exception": ("notwithstanding", "except", "nothing in this"),
    "no_solicit_of_employees": ("solicit",),
    "non_disparagement": ("disparag",),
    "most_favored_nation": ("most favo", "no less favo", "more favo"),
    "rofr_rofo_rofn": ("right of first", "first refusal", "first offer", "first negotiation"),
    "revenue_profit_sharing": ("royalt", "revenue", "profit", "commission"),
    "price_restrictions": ("price", "pricing"),
    "minimum_commitment": ("minimum",),
    "volume_restriction": ("exceed", "in excess of"),
    "audit_rights": ("audit", "inspect", "books and records"),
    "insurance": ("insur",),
    "ip_ownership_assignment": ("ownership", "hereby assign", "sole property"),
    "joint_ip_ownership": ("joint", "co-own", "shared"),
    "license_grant": ("licens", "licenc"),
    "non_transferable_license": ("non-transferable", "nontransferable", "not transferable",
                                 "non-assignable", "non-sublicensable"),
    "affiliate_license_licensor": ("affiliate",),
    "affiliate_license_licensee": ("affiliate",),
    "unlimited_all_you_can_eat_license": ("unlimited", "enterprise", "all you can eat"),
    "irrevocable_or_perpetual_license": ("irrevocabl", "perpetual"),
    "source_code_escrow": ("escrow",),
    "covenant_not_to_sue": ("not to sue", "contest", "challenge"),
    "uncapped_liability": ("shall not apply", "not be limited", "unlimited", "except"),
    "cap_on_liability": ("in no event", "shall not exceed", "limitation of liability", "maximum"),
    "liquidated_damages": ("liquidated damages", "termination fee", "penalt"),
    "warranty_duration": ("warrant",),
    "third_party_beneficiary": ("third party beneficiar", "third-party beneficiar", "beneficiar"),
}  # fmt: skip

FIELDS: tuple[FieldSpec, ...] = tuple(
    replace(f, canonical_cues=CANONICAL_CUES.get(f.name, ())) for f in _FIELDS
)

FIELDS_BY_NAME: dict[str, FieldSpec] = {f.name: f for f in FIELDS}
FIELDS_BY_CATEGORY: dict[str, FieldSpec] = {f.cuad_category: f for f in FIELDS}


def fields_of_type(field_type: FieldType) -> tuple[FieldSpec, ...]:
    return tuple(f for f in FIELDS if f.field_type is field_type)
