import pytest
import os
import tempfile
from primerlab.core.tools.primer3_wrapper import Primer3Wrapper
from primerlab.core.exceptions import PrimerLabException

class TestPrimer3PickOnly:
    def test_pick_left_only(self):
        wrapper = Primer3Wrapper()
        params = {"pick_only": "left"}
        p3_settings = wrapper._build_p3_settings(params, "pcr")
        
        assert p3_settings["PRIMER_PICK_LEFT_PRIMER"] == 1
        assert p3_settings["PRIMER_PICK_RIGHT_PRIMER"] == 0
        assert p3_settings["PRIMER_PICK_INTERNAL_OLIGO"] == 0

    def test_pick_right_only(self):
        wrapper = Primer3Wrapper()
        params = {"pick_only": "right"}
        p3_settings = wrapper._build_p3_settings(params, "pcr")
        
        assert p3_settings["PRIMER_PICK_LEFT_PRIMER"] == 0
        assert p3_settings["PRIMER_PICK_RIGHT_PRIMER"] == 1
        assert p3_settings["PRIMER_PICK_INTERNAL_OLIGO"] == 0

    def test_pick_probe_only(self):
        wrapper = Primer3Wrapper()
        params = {"pick_only": "probe"}
        p3_settings = wrapper._build_p3_settings(params, "qpcr")
        
        assert p3_settings["PRIMER_PICK_LEFT_PRIMER"] == 0
        assert p3_settings["PRIMER_PICK_RIGHT_PRIMER"] == 0
        assert p3_settings["PRIMER_PICK_INTERNAL_OLIGO"] == 1

class TestProbeMishybLibrary:
    def test_probe_mishyb_library_valid(self):
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(b">seq1\nATGC\n")
            tmp_name = tmp.name
            
        try:
            wrapper = Primer3Wrapper()
            config = {
                "workflow": "qpcr",
                "parameters": {
                    "probe": {
                        "mishyb_library_path": tmp_name
                    }
                }
            }
            with pytest.MonkeyPatch.context() as m:
                import primer3.bindings
                
                def mock_design_primers(seq_args, p3_settings):
                    wrapper.captured_settings = p3_settings
                    return {"PRIMER_PAIR_NUM_RETURNED": 0}
                
                m.setattr(primer3.bindings, "design_primers", mock_design_primers)
                try:
                    wrapper.design_primers("ATGC" * 50, config)
                except Exception:
                    pass
                
            p3_settings = wrapper.captured_settings
            assert "PRIMER_INTERNAL_MISHYB_LIBRARY" in p3_settings
            assert p3_settings["PRIMER_INTERNAL_MISHYB_LIBRARY"] == tmp_name
        finally:
            os.unlink(tmp_name)

    def test_probe_mishyb_library_not_found(self):
        wrapper = Primer3Wrapper()
        config = {
            "workflow": "qpcr",
            "parameters": {
                "probe": {
                    "mishyb_library_path": "/path/that/does/not/exist.fasta"
                }
            }
        }
        with pytest.raises(PrimerLabException) as excinfo:
            wrapper.design_primers("ATGC", config)
            
        assert "ERR_P3_LIB_NOT_FOUND" in str(excinfo.value.error_code)
