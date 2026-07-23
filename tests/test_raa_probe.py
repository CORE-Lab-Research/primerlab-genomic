import pytest
from typing import Dict, Any
from primerlab.workflows.raa.probe import (
    find_exo_probe, annotate_probe, create_amplicon_map, apply_annotation,
    find_thf_site,
)
from primerlab.core.models import Primer

@pytest.fixture
def mock_config():
    return {
        "parameters": {
            "probe": {
                "enabled": True,
                "type": "exo",
                "size": {"min": 46, "opt": 48, "max": 52},
                "tm": {"min": 54.0, "opt": 65.0, "max": 85.0},
                "thf_upstream_min": 30,
                "thf_downstream_min": 15,
                "labels": {
                    "fluorophore": "FAM",
                    "quencher": "BHQ1",
                    "blocker": "C3-spacer",
                    "abasic": "THF"
                }
            },
            "thermodynamics": {
                "salt_monovalent": 50.0,
                "salt_divalent": 1.5,
                "dntp_conc": 0.6,
                "dna_conc": 50.0
            }
        }
    }

def test_find_exo_probe_valid(mock_config):
    # Amplicon 150bp, inner gap ~80bp
    # FWD (30nt) + GAP (90nt) + REV (30nt)
    fwd_seq = "A" * 30
    gap_seq = "GATC" * 22 + "GG"
    rev_seq = "T" * 30
    amp_seq = fwd_seq + gap_seq + rev_seq
    
    probe = find_exo_probe(amp_seq, 30, 30, mock_config)
    assert probe is not None
    assert 46 <= len(probe.sequence) <= 52
    assert probe.sequence in gap_seq

def test_find_exo_probe_too_short(mock_config):
    # Amplicon 80bp, inner gap 20bp (too small for 46nt probe)
    amp_seq = "A" * 30 + "G" * 20 + "T" * 30
    probe = find_exo_probe(amp_seq, 30, 30, mock_config)
    assert probe is None

def test_annotate_probe_exo(mock_config):
    probe = Primer(id="p1", sequence="T" * 50, tm=60.0, gc=0.0, length=50)
    ann = annotate_probe(probe, mock_config)
    
    assert ann["type"] == "exo"
    assert "[FAM-dT][THF][BHQ1-dT]" in ann["annotated_sequence"]
    assert ann["annotated_sequence"].endswith("[C3-spacer]")

def test_annotate_probe_taqman(mock_config):
    mock_config["parameters"]["probe"]["type"] = "taqman"
    probe = Primer(id="p1", sequence="ATGCT", tm=60.0, gc=0.0, length=5)
    ann = annotate_probe(probe, mock_config)
    
    assert ann["type"] == "taqman"
    assert ann["annotated_sequence"] == "[FAM]ATGCT[BHQ1]"

def test_annotate_probe_fpg(mock_config):
    mock_config["parameters"]["probe"]["type"] = "fpg"
    mock_config["parameters"]["probe"]["labels"]["abasic"] = "dR-Biotin"
    probe = Primer(id="p1", sequence="A" * 50, tm=60.0, gc=0.0, length=50)
    ann = annotate_probe(probe, mock_config)
    
    assert ann["type"] == "fpg"
    assert "[dR-Biotin]" in ann["annotated_sequence"]

def test_thf_index_survives_to_dict(mock_config):
    """The cleavage-site position must reach the exported JSON.

    annotate_probe() has always computed thf_index, but it was dropped when the
    annotation was copied onto the Primer, so every downstream consumer saw only
    the bracket markup in labeled_sequence. Anything validating the probe against
    real target variants needs the numeric position.
    """
    probe = Primer(id="p1", sequence="T" * 50, tm=60.0, gc=0.0, length=50)
    ann = annotate_probe(probe, mock_config)
    apply_annotation(probe, ann)

    assert probe.thf_index == ann["thf_index"]
    d = probe.to_dict()
    assert d["thf_index"] == ann["thf_index"]
    assert d["probe_type"] == "exo"

    # The index must actually point at the residue the markup replaced, i.e. the
    # sandwich occupies sequence[thf_index-1 : thf_index+2].
    left = probe.sequence[: probe.thf_index - 1]
    assert d["labeled_sequence"].startswith(left + "[FAM-dT][THF][BHQ1-dT]")


def test_find_exo_probe_exports_thf_index(mock_config):
    """The manual-probe path must populate the same fields as the primer3 path."""
    amp_seq = "A" * 30 + ("GATC" * 22 + "GG") + "T" * 30
    probe = find_exo_probe(amp_seq, 30, 30, mock_config)
    assert probe is not None
    assert probe.probe_type == "exo"
    assert probe.thf_index is not None
    assert 0 < probe.thf_index < len(probe.sequence) - 1


def test_taqman_has_no_thf_index(mock_config):
    """A hydrolysis probe has no abasic site; the field must stay None rather
    than defaulting to 0, which would read as 'THF at the first base'."""
    mock_config["parameters"]["probe"]["type"] = "taqman"
    probe = Primer(id="p1", sequence="ATGCT", tm=60.0, gc=0.0, length=5)
    apply_annotation(probe, annotate_probe(probe, mock_config))
    assert probe.thf_index is None
    assert probe.probe_type == "taqman"


# --- THF placement rules (TwistAmp Assay Design Manual §3.1.1-3.1.2) ----------

# The manual's own worked example. Target has T at index 28 and 32; the abasic
# residue replaces the A at index 30, giving exactly 30 bases 5' and 15 bases 3'.
MANUAL_EXAMPLE = "GAATTTCAGAGGCTATAGCGATCTCAGGTCAATCGATAGATCGCTA"


def test_reproduces_manual_worked_example(mock_config):
    probe = Primer(id="p", sequence=MANUAL_EXAMPLE, tm=60.0, gc=45.0,
                   length=len(MANUAL_EXAMPLE))
    ann = annotate_probe(probe, mock_config)

    assert ann["bases_upstream"] == 30      # manual: ">=30 bases 5' of THF"
    assert ann["bases_downstream"] == 15    # manual: ">=15 bases 3' of THF"
    assert ann["fluor_index"] == 28
    assert ann["quencher_index"] == 32
    assert ann["mismatched_labels"] == 0
    assert ann["compliant"] is True


def test_labels_land_on_thymines_not_the_abasic_site(mock_config):
    """The dT-fluorophore and dT-quencher reagents only exist as T couplings, so
    the FLANKS must be T. The abasic residue has no sequence requirement.

    The previous implementation had this inverted: it anchored the abasic residue
    onto the nearest T and let the two labels fall on whatever bases happened to
    be adjacent, so every probe could carry two unnecessary mismatches.
    """
    seq = MANUAL_EXAMPLE
    ann = annotate_probe(
        Primer(id="p", sequence=seq, tm=60.0, gc=45.0, length=len(seq)), mock_config)
    assert seq[ann["fluor_index"]] == "T"
    assert seq[ann["quencher_index"]] == "T"


def test_abasic_never_placed_closer_than_30_bases_from_the_5_prime_end(mock_config):
    """A lone T just before the target position used to drag the abasic residue to
    index 28, which the manual lists verbatim as a "Poor probe design"."""
    seq = "GC" * 14 + "T" + "GC" * 11          # single T at index 28, 51 nt total
    ann = annotate_probe(
        Primer(id="p", sequence=seq, tm=60.0, gc=70.0, length=len(seq)), mock_config)
    assert ann["bases_upstream"] >= 30
    assert ann["bases_downstream"] >= 15


def test_single_label_mismatch_preferred_over_two(mock_config):
    """The manual sanctions ignoring "the mismatch of ONE of the thymines"; a site
    needing one mismatch must therefore beat one needing two."""
    seq = "GC" * 14 + "T" + "GC" * 11          # exactly one usable T
    ann = annotate_probe(
        Primer(id="p", sequence=seq, tm=60.0, gc=70.0, length=len(seq)), mock_config)
    assert ann["mismatched_labels"] == 1
    assert ann["compliant"] is False
    assert ann["warnings"], "a deliberate label mismatch must be reported, not silent"


def test_label_mismatches_are_reported_so_downstream_can_discount_them(mock_config):
    """Nothing validating the probe against target variants may count a label
    mismatch as target variation — it is a property of the design."""
    seq = "GC" * 25                             # no T anywhere
    probe = Primer(id="p", sequence=seq, tm=60.0, gc=100.0, length=len(seq))
    apply_annotation(probe, annotate_probe(probe, mock_config))
    assert probe.probe_label_mismatches == 2
    assert probe.probe_compliant is False
    assert probe.to_dict()["probe_label_mismatches"] == 2
    assert any("mismatch" in w for w in probe.warnings)


def test_find_thf_site_rejects_when_geometry_impossible():
    assert find_thf_site("ACGT" * 10) is None   # 40 nt: cannot fit 30 + 1 + 15


def test_gap_between_label_and_abasic_never_exceeds_two(mock_config):
    """Manual: the number of nucleotides between a dT label and the THF "can be
    0, 1 or 2" — which also keeps fluorophore/quencher separation within 5."""
    seq = "GAATTTCAGAGGCTATAGCGATCTCAGGTCAATCGATAGATCGCTAGGCC"
    ann = annotate_probe(
        Primer(id="p", sequence=seq, tm=60.0, gc=45.0, length=len(seq)), mock_config)
    assert 0 <= ann["thf_index"] - ann["fluor_index"] - 1 <= 2
    assert 0 <= ann["quencher_index"] - ann["thf_index"] - 1 <= 2
    assert ann["quencher_index"] - ann["fluor_index"] <= 5


def test_amplicon_map():
    fwd = Primer(id="f", sequence="AAA", tm=60.0, gc=0.0, length=3)
    rev = Primer(id="r", sequence="TTT", tm=60.0, gc=0.0, length=3)
    probe = Primer(id="p", sequence="GGG", tm=60.0, gc=0.0, length=3)
    amp_seq = "AAACCCGGGCCCTTT"
    
    # Map should look like: >>>---===---<<<
    viz = create_amplicon_map(amp_seq, fwd, rev, probe)
    assert viz == ">>>---===---<<<"
