"""Tests for Bill OCR extraction and parsing."""

from app.services.ocr import parse_extracted_text

def test_parse_sample_jewellery_bill() -> None:
    sample_ocr_text = """
    SRI MEENAKSHI JEWELLERS
    Madurai, Tamil Nadu
    Invoice Date: 15-Nov-2026
    Item: 22K Gold Bangle
    HUID: AH8972
    Gross Weight: 30.800 gms
    Net Weight: 30.800 g
    Rate / gm: Rs 13000.00
    Total: Rs 400400.00
    """

    res = parse_extracted_text(sample_ocr_text)

    # 1. HUID
    assert res.huid is not None
    assert res.huid.extracted_value == "AH8972"
    assert res.huid.requires_human_confirmation is True

    # 2. Purity (22K -> 916‰)
    assert res.purity_permille is not None
    assert res.purity_permille.extracted_value == 916

    # 3. Gross Weight (30.800 gms -> 30,800 mg)
    assert res.gross_weight_mg is not None
    assert res.gross_weight_mg.extracted_value == 30800

def test_ocr_missing_fields_graceful() -> None:
    unrelated_text = "Coffee Shop Receipt\nTotal: 150"
    res = parse_extracted_text(unrelated_text)
    assert res.huid is None
    assert res.purity_permille is None
    assert res.gross_weight_mg is None
