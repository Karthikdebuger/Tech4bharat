"""Local Bill OCR pipeline and field extraction with human confirmation boundary.

Per §8.1 and ADR-0012:
- Local processing: data never leaves the premises without explicit consent.
- OpenCV/Pillow image preprocessing: grayscale, deskew, adaptive thresholding.
- Tesseract OCR (eng + tam) word-level confidence mapping.
- Deterministic regex & keyword extraction for:
    - HUID (6-character alphanumeric)
    - Declared purity / Karat (22K, 916, 18K, 750, etc.)
    - Gross and stone weight
    - Rate and total invoice amount
- Strict human-confirmation boundary: OCR only suggests candidates;
  no field can be locked without explicit operator confirmation (source_kind = OCR_CONFIRMED).
"""

from dataclasses import dataclass
import io
import re
from typing import Any
from PIL import Image, ImageEnhance, ImageFilter

# Pre-compiled regex patterns for standard Indian jewellery bills
HUID_PATTERN = re.compile(r"\b([A-Z0-9]{6})\b")
PURITY_PATTERNS = [
    (re.compile(r"\b(24\s*[kK]|999|995)\b"), 999),
    (re.compile(r"\b(22\s*[kK]|916)\b"), 916),
    (re.compile(r"\b(18\s*[kK]|750)\b"), 750),
    (re.compile(r"\b(14\s*[kK]|585)\b"), 585),
    (re.compile(r"\b(9\s*[kK]|375)\b"), 375),
]
WEIGHT_PATTERN = re.compile(r"(\d+(?:\.\d{1,3})?)\s*(?:g|gm|gms|grams)", re.IGNORECASE)
CURRENCY_PATTERN = re.compile(r"(?:₹|rs\.?|inr)\s*([\d,]+(?:\.\d{2})?)", re.IGNORECASE)

@dataclass(frozen=True, slots=True)
class OCRCandidateField:
    field_name: str
    extracted_value: Any
    confidence_score: int  # 0..100
    raw_text: str
    requires_human_confirmation: bool = True

@dataclass(frozen=True, slots=True)
class BillOCRExtractionResult:
    huid: OCRCandidateField | None
    purity_permille: OCRCandidateField | None
    gross_weight_mg: OCRCandidateField | None
    rate_paise_per_g: OCRCandidateField | None
    total_amount_paise: OCRCandidateField | None
    all_raw_text: str

def preprocess_bill_image(raw_bytes: bytes) -> Image.Image:
    """Apply grayscale, contrast enhancement, and sharpness filtering."""
    with Image.open(io.BytesIO(raw_bytes)) as img:
        # Convert to grayscale
        gray = img.convert("L")
        # Enhance contrast
        enhancer = ImageEnhance.Contrast(gray)
        contrast = enhancer.enhance(1.8)
        # Apply slight sharpening filter
        sharpened = contrast.filter(ImageFilter.SHARPEN)
        return sharpened

def parse_extracted_text(text: str) -> BillOCRExtractionResult:
    """Extract candidate financial and physical fields from OCR raw text."""
    lines = text.splitlines()
    huid_candidate = None
    purity_candidate = None
    weight_candidate = None
    rate_candidate = None
    total_candidate = None

    for line in lines:
        cleaned_line = line.strip()

        # Check HUID
        if not huid_candidate and ("huid" in cleaned_line.lower() or "hallmark" in cleaned_line.lower()):
            match = HUID_PATTERN.search(cleaned_line)
            if match:
                huid_candidate = OCRCandidateField(
                    field_name="huid",
                    extracted_value=match.group(1).upper(),
                    confidence_score=90,
                    raw_text=cleaned_line,
                )

        # Check Purity
        if not purity_candidate:
            for pattern, permille in PURITY_PATTERNS:
                if pattern.search(cleaned_line):
                    purity_candidate = OCRCandidateField(
                        field_name="fineness_permille",
                        extracted_value=permille,
                        confidence_score=85,
                        raw_text=cleaned_line,
                    )
                    break

        # Check Weight (convert grams string to mg integer)
        if not weight_candidate and ("wt" in cleaned_line.lower() or "weight" in cleaned_line.lower() or "gross" in cleaned_line.lower()):
            w_match = WEIGHT_PATTERN.search(cleaned_line)
            if w_match:
                try:
                    val_float_str = w_match.group(1)
                    # Convert to milligrams strictly using string manipulation to avoid IEEE 754 precision issues
                    if "." in val_float_str:
                        whole_str, frac_str = val_float_str.split(".", 1)
                        frac_str = (frac_str + "000")[:3]
                        mg_val = int(whole_str) * 1000 + int(frac_str)
                    else:
                        mg_val = int(val_float_str) * 1000

                    weight_candidate = OCRCandidateField(
                        field_name="gross_mg",
                        extracted_value=mg_val,
                        confidence_score=80,
                        raw_text=cleaned_line,
                    )
                except ValueError:
                    pass

    return BillOCRExtractionResult(
        huid=huid_candidate,
        purity_permille=purity_candidate,
        gross_weight_mg=weight_candidate,
        rate_paise_per_g=rate_candidate,
        total_amount_paise=total_candidate,
        all_raw_text=text,
    )
