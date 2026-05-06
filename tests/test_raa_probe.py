import pytest
from typing import Dict, Any
from primerlab.workflows.raa.probe import find_exo_probe, annotate_probe, create_amplicon_map
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
    probe = Primer(id="p1", sequence="A" * 10, tm=60.0, gc=0.0, length=10)
    ann = annotate_probe(probe, mock_config)
    
    assert ann["type"] == "fpg"
    assert "[dR-Biotin]" in ann["annotated_sequence"]

def test_amplicon_map():
    fwd = Primer(id="f", sequence="AAA", tm=60.0, gc=0.0, length=3)
    rev = Primer(id="r", sequence="TTT", tm=60.0, gc=0.0, length=3)
    probe = Primer(id="p", sequence="GGG", tm=60.0, gc=0.0, length=3)
    amp_seq = "AAACCCGGGCCCTTT"
    
    # Map should look like: >>>---===---<<<
    viz = create_amplicon_map(amp_seq, fwd, rev, probe)
    assert viz == ">>>---===---<<<"
