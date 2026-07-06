import pytest
from primerlab.workflows.raa.workflow import run_raa_workflow
from primerlab.core.models import Primer, Amplicon, WorkflowResult
from unittest.mock import MagicMock, patch

def test_two_stage_ranking_logic():
    # We will test the sorting and ranking logic inside run_raa_workflow by mocking
    # the Primer3Wrapper output and the QC engine results.
    
    # 1. Create Mock Config
    config = {
        "input": {
            "sequence": "ATGC" * 100
        },
        "parameters": {
            "probe": {
                "enabled": False
            }
        },
        "qc": {
            "vienna_ranking_limit": 5
        },
        "output": {
            "num_results_to_export": 5
        }
    }

    # 2. Mock Sequence Loader
    mock_seq = "ATGC" * 100

    # 3. Mock Primer3Wrapper.design_primers to return some candidates
    # We want 3 candidates to test the different Tiers:
    # Candidate A: 0 warnings, P3 penalty = 10.0 (Tier 1, Rank 2)
    # Candidate B: 0 warnings, P3 penalty = 5.0  (Tier 1, Rank 1)
    # Candidate C: 1 warning,  P3 penalty = 2.0  (Tier 2, Rank 3)
    # Candidate D: 3 warnings, P3 penalty = 1.0  (Tier 3, Rank 4)
    
    fwd_a = Primer(id="forward_0", sequence="A"*30, tm=60.0, gc=40.0, length=30, start=0, end=29)
    rev_a = Primer(id="reverse_0", sequence="T"*30, tm=60.0, gc=40.0, length=30, start=100, end=129)
    
    fwd_b = Primer(id="forward_1", sequence="A"*30, tm=60.0, gc=40.0, length=30, start=10, end=39)
    rev_b = Primer(id="reverse_1", sequence="T"*30, tm=60.0, gc=40.0, length=30, start=110, end=139)
    
    fwd_c = Primer(id="forward_2", sequence="A"*30, tm=60.0, gc=40.0, length=30, start=20, end=49)
    rev_c = Primer(id="reverse_2", sequence="T"*30, tm=60.0, gc=40.0, length=30, start=120, end=149)
    
    fwd_d = Primer(id="forward_3", sequence="A"*30, tm=60.0, gc=40.0, length=30, start=30, end=59)
    rev_d = Primer(id="reverse_3", sequence="T"*30, tm=60.0, gc=40.0, length=30, start=130, end=159)

    mock_raw_results = {
        "PRIMER_PAIR_NUM_RETURNED": 4,
        "PRIMER_LEFT_NUM_RETURNED": 4,
        "PRIMER_LEFT_0": (0, 30),
        "PRIMER_RIGHT_0": (129, 30),
        "PRIMER_LEFT_0_SEQUENCE": "A"*30,
        "PRIMER_RIGHT_0_SEQUENCE": "T"*30,
        "PRIMER_PAIR_0_PRODUCT_SIZE": 130,
        "PRIMER_PAIR_0_PENALTY": 10.0,
        
        "PRIMER_LEFT_1": (10, 30),
        "PRIMER_RIGHT_1": (139, 30),
        "PRIMER_LEFT_1_SEQUENCE": "G"*30,
        "PRIMER_RIGHT_1_SEQUENCE": "C"*30,
        "PRIMER_PAIR_1_PRODUCT_SIZE": 130,
        "PRIMER_PAIR_1_PENALTY": 5.0,
        
        "PRIMER_LEFT_2": (20, 30),
        "PRIMER_RIGHT_2": (149, 30),
        "PRIMER_LEFT_2_SEQUENCE": "AT"*15,
        "PRIMER_RIGHT_2_SEQUENCE": "GC"*15,
        "PRIMER_PAIR_2_PRODUCT_SIZE": 130,
        "PRIMER_PAIR_2_PENALTY": 2.0,
        
        "PRIMER_LEFT_3": (30, 30),
        "PRIMER_RIGHT_3": (159, 30),
        "PRIMER_LEFT_3_SEQUENCE": "TA"*15,
        "PRIMER_RIGHT_3_SEQUENCE": "CG"*15,
        "PRIMER_PAIR_3_PRODUCT_SIZE": 130,
        "PRIMER_PAIR_3_PENALTY": 1.0,
    }

    # 4. Mock the QC Result evaluation
    from primerlab.core.models.qc import QCResult
    qc_a = QCResult(
        hairpin_ok=True, homodimer_ok=True, heterodimer_ok=True, end_stability_ok=True, tm_balance_ok=True,
        hairpin_dg=0.0, homodimer_dg=0.0, heterodimer_dg=0.0, end_stability_dg=0.0, tm_diff=0.0,
        warnings=[], errors=[]
    )
    qc_b = QCResult(
        hairpin_ok=True, homodimer_ok=True, heterodimer_ok=True, end_stability_ok=True, tm_balance_ok=True,
        hairpin_dg=0.0, homodimer_dg=0.0, heterodimer_dg=0.0, end_stability_dg=0.0, tm_diff=0.0,
        warnings=[], errors=[]
    )
    qc_c = QCResult(
        hairpin_ok=True, homodimer_ok=True, heterodimer_ok=True, end_stability_ok=True, tm_balance_ok=True,
        hairpin_dg=0.0, homodimer_dg=0.0, heterodimer_dg=0.0, end_stability_dg=0.0, tm_diff=0.0,
        warnings=["One minor issue"], errors=[]
    )
    qc_d = QCResult(
        hairpin_ok=True, homodimer_ok=True, heterodimer_ok=True, end_stability_ok=True, tm_balance_ok=True,
        hairpin_dg=0.0, homodimer_dg=0.0, heterodimer_dg=0.0, end_stability_dg=0.0, tm_diff=0.0,
        warnings=["Issue 1", "Issue 2", "Issue 3"], errors=[]
    )

    # 5. Patch RAAQC, Primer3Wrapper and SequenceLoader
    with patch("primerlab.workflows.raa.workflow.SequenceLoader.load", return_value=mock_seq), \
         patch("primerlab.workflows.raa.workflow.Primer3Wrapper") as mock_p3_class, \
         patch("primerlab.workflows.raa.workflow.RAAQC") as mock_qc_class:
         
         # Mock Primer3Wrapper instance methods
         mock_p3_inst = MagicMock()
         mock_p3_inst.design_primers.return_value = mock_raw_results
         mock_p3_class.return_value = mock_p3_inst
         
         # Mock parse_primer3_output
         def mock_parse_p3(mini_res, *args, **kwargs):
             fwd_seq = mini_res.get("PRIMER_LEFT_0_SEQUENCE")
             if fwd_seq == "A"*30:
                 return [{"forward": fwd_a, "reverse": rev_a}]
             elif fwd_seq == "G"*30:
                 return [{"forward": fwd_b, "reverse": rev_b}]
             elif fwd_seq == "AT"*15:
                 return [{"forward": fwd_c, "reverse": rev_c}]
             elif fwd_seq == "TA"*15:
                 return [{"forward": fwd_d, "reverse": rev_d}]
             return []
         with patch("primerlab.workflows.raa.workflow.parse_primer3_output", side_effect=mock_parse_p3):
             
             # Mock RAAQC instance methods
             mock_qc_inst = MagicMock()
             mock_qc_inst.vienna.is_available = True
             
             # evaluate_pair_extended side effects:
             # index 0 (Candidate A): qc_a
             # index 1 (Candidate B): qc_b
             # index 2 (Candidate C): qc_c
             # index 3 (Candidate D): qc_d
             mock_qc_inst.evaluate_pair_extended.side_effect = [qc_a, qc_b, qc_c, qc_d]
             
             # Mock evaluate_target_structure (ViennaRNA)
             # Let's say Candidate B (which is currently Rank 1) has a highly stable structure and is not accessible:
             # normalized_dg = -4.0, which means vienna_penalty = 4.0 * 1.5 = 6.0 ranks penalty!
             # Candidate A (Rank 2) is perfectly accessible: vienna_penalty = 0.0.
             # Candidate C (Rank 3) is perfectly accessible: vienna_penalty = 0.0.
             # This should make Candidate A re-rank as the ultimate winner!
             def mock_evaluate_target_structure(amp_seq):
                  if amp_seq == mock_seq:
                      return {"dg": -1.0, "normalized_dg": -0.3, "accessible": True, "warnings": []}
                  if len(amp_seq) == 130 and amp_seq.startswith("G"):
                      # Candidate B starts with 'G' (index 10 in mock_seq)
                      return {"dg": -12.0, "normalized_dg": -4.0, "accessible": False, "warnings": ["Stable structure"]}
                  return {"dg": -1.0, "normalized_dg": -0.3, "accessible": True, "warnings": []}
                 
             mock_qc_inst.evaluate_target_structure.side_effect = mock_evaluate_target_structure
             mock_qc_class.return_value = mock_qc_inst
             
             # Run workflow
             res = run_raa_workflow(config)
             
             print("\nDEBUG RANKS:")
             for alt in res.alternatives:
                 print(f"ID: {alt['primers']['forward']['id']}, Stage 1 Rank: {alt['stage1_rank']}, Final Rank: {alt['final_rank']}, Tier: {alt['tier']}, P3 Penalty: {alt['p3_penalty']}, Final Score: {alt['final_score']}")
             
             # Assertions
             assert isinstance(res, WorkflowResult)
             assert len(res.alternatives) == 4
             
             # Verify Stage 1 ranking details before Stage 2
             # Candidate B (penalty 5, Tier 1) should be stage1_rank = 1
             # Candidate A (penalty 10, Tier 1) should be stage1_rank = 2
             # Candidate C (penalty 2, Tier 2) should be stage1_rank = 3
             # Candidate D (penalty 1, Tier 3) should be stage1_rank = 4
             
             # Let's find alternatives by their ID to check ranks
             alt_b = next(a for a in res.alternatives if a["primers"]["forward"]["id"] == "forward_1")
             alt_a = next(a for a in res.alternatives if a["primers"]["forward"]["id"] == "forward_0")
             alt_c = next(a for a in res.alternatives if a["primers"]["forward"]["id"] == "forward_2")
             alt_d = next(a for a in res.alternatives if a["primers"]["forward"]["id"] == "forward_3")
             
             assert alt_b["stage1_rank"] == 1
             assert alt_a["stage1_rank"] == 2
             assert alt_c["stage1_rank"] == 3
             assert alt_d["stage1_rank"] == 4
             
             # Verify Stage 2 ViennaRNA Re-ranking
             # Candidate B had stable structure -> penalty = 4.0 * 1.5 = 6.0
             # final_score of B = 1 (stage1_rank) + 6.0 = 7.0
             # Candidate A had accessible structure -> penalty = 0.0
             # final_score of A = 2 (stage1_rank) + 0.0 = 2.0
             # Candidate C had accessible structure -> penalty = 0.0
             # final_score of C = 3 (stage1_rank) + 0.0 = 3.0
             # Candidate D had accessible structure -> penalty = 0.0 (and was evaluated if within vienna_limit of 5)
             # final_score of D = 4 (stage1_rank) + 0.0 = 4.0
             
             # So the final sorted order should be:
             # Final Rank 1: Candidate A (score 2.0)
             # Final Rank 2: Candidate C (score 3.0)
             # Final Rank 3: Candidate B (score 7.0)
             # Final Rank 4: Candidate D (score 10.0)
              
             assert alt_a["final_rank"] == 1
             assert alt_c["final_rank"] == 2
             assert alt_b["final_rank"] == 3
             assert alt_d["final_rank"] == 4
             
             # Top selected candidate must be Candidate A
             assert res.primers["forward"].id == "forward_0"
             assert res.score == 10.0 # top_res original Primer3 penalty
