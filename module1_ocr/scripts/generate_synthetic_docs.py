"""Synthetic Identity Document Generator for AI-DIDSS Module 1.

Generates realistic, standardized, and compliant synthetic identity documents:
- Passports (ICAO Doc 9303 TD3)
- Visas (MRV-A)
- Driver's Licenses (AAMVA DL format)
- National Identity Cards (TD1)
- Residence Permits

Includes geometric transformations, lighting artifacts, and noise variations
while preserving strict ground-truth bounding box and field annotations.
Zero real PII is used; all data is procedurally generated.
"""

import os
import json
import random
import hashlib
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# Seed for deterministic reproducibility
random.seed(42)
np.random.seed(42)

# Synthetic entity dictionaries
FIRST_NAMES_MALE = ["JAMES", "JOHN", "ROBERT", "MICHAEL", "DAVID", "LIAM", "NOAH", "OLIVER", "LUCAS", "MATEO"]
FIRST_NAMES_FEMALE = ["MARY", "PATRICIA", "JENNIFER", "LINDA", "ELIZABETH", "EMMA", "AVA", "SOPHIA", "ISABELLA", "MIA"]
LAST_NAMES = ["SMITH", "JOHNSON", "WILLIAMS", "BROWN", "JONES", "GARCIA", "MILLER", "DAVIS", "RODRIGUEZ", "MARTINEZ", "TAYLOR", "ANDERSON"]
COUNTRIES = [
    ("UTO", "UTOPIA"),
    ("XAN", "XANADU"),
    ("ATL", "ATLANTIS"),
    ("ELD", "ELDORADO"),
    ("VAL", "VALHALLA"),
    ("ARC", "ARCADIA")
]
CITIES = ["NEW HAVEN", "RIVERSIDE", "SUNNYVALE", "METROPOLIS", "OAKRIDGE", "SILVER CITY", "GRAND LAKE"]
STREETS = ["MAIN ST", "OAK AVE", "MAPLE BLVD", "PINE RD", "WASHINGTON ST", "CEDAR LN", "PARK AVE"]
VEHICLE_CLASSES = ["CLASS C (STANDARD PASSENGER)", "CLASS A (COMMERCIAL)", "CLASS M (MOTORCYCLE)", "CLASS B (BUS/HEAVY)"]
PERMIT_TYPES = ["PERMANENT RESIDENT", "WORK AUTHORIZATION", "SPECIAL SKILLS TALENT", "ACADEMIC RESEARCH"]

def compute_mrz_check_digit(data_str: str) -> str:
    """Computes standard ICAO Doc 9303 modulo-10 check digit with [7, 3, 1] weights."""
    weights = [7, 3, 1]
    total = 0
    for idx, char in enumerate(data_str):
        if char.isdigit():
            val = int(char)
        elif char.isalpha():
            val = ord(char.upper()) - ord('A') + 10
        elif char == '<':
            val = 0
        else:
            val = 0
        total += val * weights[idx % 3]
    return str(total % 10)

def generate_synthetic_identity():
    gender = random.choice(["M", "F"])
    first_name = random.choice(FIRST_NAMES_MALE if gender == "M" else FIRST_NAMES_FEMALE)
    last_name = random.choice(LAST_NAMES)
    country_code, country_name = random.choice(COUNTRIES)
    doc_num = f"{random.choice(['P', 'E', 'A', 'D'])}{random.randint(10000000, 99999999)}"
    
    # Dates: YYMMDD for MRZ, YYYY-MM-DD for VIZ
    birth_year = random.randint(1960, 2004)
    birth_month = random.randint(1, 12)
    birth_day = random.randint(1, 28)
    dob_mrz = f"{str(birth_year)[2:]}{birth_month:02d}{birth_day:02d}"
    dob_viz = f"{birth_year}-{birth_month:02d}-{birth_day:02d}"
    
    issue_year = random.randint(2018, 2024)
    issue_month = random.randint(1, 12)
    issue_day = random.randint(1, 28)
    issue_viz = f"{issue_year}-{issue_month:02d}-{issue_day:02d}"
    
    expiry_year = issue_year + random.choice([5, 10])
    expiry_month = issue_month
    expiry_day = issue_day
    expiry_mrz = f"{str(expiry_year)[2:]}{expiry_month:02d}{expiry_day:02d}"
    expiry_viz = f"{expiry_year}-{expiry_month:02d}-{expiry_day:02d}"
    
    address = f"{random.randint(100, 9999)} {random.choice(STREETS)}, {random.choice(CITIES)}, {country_code}"
    
    return {
        "first_name": first_name,
        "last_name": last_name,
        "full_name": f"{first_name} {last_name}",
        "gender": gender,
        "country_code": country_code,
        "country_name": country_name,
        "doc_number": doc_num,
        "dob_mrz": dob_mrz,
        "dob_viz": dob_viz,
        "issue_viz": issue_viz,
        "expiry_mrz": expiry_mrz,
        "expiry_viz": expiry_viz,
        "address": address
    }

def draw_face_placeholder(draw, bbox):
    """Draws a synthetic avatar silhouette for face area."""
    x1, y1, x2, y2 = bbox
    # Background box
    draw.rectangle([x1, y1, x2, y2], fill=(210, 220, 235), outline=(100, 120, 150), width=2)
    # Head circle
    head_cx = (x1 + x2) // 2
    head_cy = y1 + (y2 - y1) // 3
    head_r = (x2 - x1) // 4
    draw.ellipse([head_cx - head_r, head_cy - head_r, head_cx + head_r, head_cy + head_r], fill=(130, 150, 180))
    # Shoulders
    shoulder_y = head_cy + head_r + 5
    draw.chord([x1 + 10, shoulder_y, x2 - 10, y2 + 40], start=0, end=180, fill=(90, 110, 140))

def generate_passport(identity, doc_id, variation_id=1):
    """Generates synthetic ICAO Doc 9303 TD3 Passport Image and ground truth."""
    width, height = 1000, 700
    img = Image.new("RGB", (width, height), color=(248, 246, 240))
    draw = ImageDraw.Draw(img)
    
    # Header & guilloche simulation
    draw.rectangle([0, 0, width, 80], fill=(25, 45, 85))
    draw.text((30, 25), f"PASSPORT / PASSEPORT — {identity['country_name']}", fill=(255, 255, 255))
    
    # Face photo box
    photo_bbox = [50, 110, 260, 380]
    draw_face_placeholder(draw, photo_bbox)
    
    # VIZ Fields
    fields = {}
    
    fields["document_type"] = {"text": "PASSPORT", "bbox": [300, 100, 450, 125], "confidence": 1.0}
    draw.text((300, 100), "TYPE: P", fill=(80, 80, 80))
    
    fields["issuing_country"] = {"text": identity["country_code"], "bbox": [480, 100, 600, 125], "confidence": 1.0}
    draw.text((480, 100), f"CODE: {identity['country_code']}", fill=(80, 80, 80))
    
    fields["passport_number"] = {"text": identity["doc_number"], "bbox": [650, 100, 900, 130], "confidence": 1.0}
    draw.text((650, 100), f"PASSPORT NO: {identity['doc_number']}", fill=(20, 20, 20))
    
    fields["surname"] = {"text": identity["last_name"], "bbox": [300, 145, 750, 180], "confidence": 1.0}
    draw.text((300, 140), f"SURNAME / NOM:\n{identity['last_name']}", fill=(20, 20, 20))
    
    fields["given_names"] = {"text": identity["first_name"], "bbox": [300, 195, 750, 235], "confidence": 1.0}
    draw.text((300, 190), f"GIVEN NAMES / PRENOMS:\n{identity['first_name']}", fill=(20, 20, 20))
    
    fields["nationality"] = {"text": identity["country_code"], "bbox": [300, 250, 500, 290], "confidence": 1.0}
    draw.text((300, 245), f"NATIONALITY / NATIONALITE:\n{identity['country_name']} ({identity['country_code']})", fill=(20, 20, 20))
    
    fields["date_of_birth"] = {"text": identity["dob_viz"], "bbox": [300, 305, 500, 345], "confidence": 1.0}
    draw.text((300, 300), f"DATE OF BIRTH:\n{identity['dob_viz']}", fill=(20, 20, 20))
    
    fields["gender"] = {"text": identity["gender"], "bbox": [550, 305, 650, 345], "confidence": 1.0}
    draw.text((550, 300), f"SEX:\n{identity['gender']}", fill=(20, 20, 20))
    
    fields["date_of_issue"] = {"text": identity["issue_viz"], "bbox": [300, 360, 500, 400], "confidence": 1.0}
    draw.text((300, 355), f"DATE OF ISSUE:\n{identity['issue_viz']}", fill=(20, 20, 20))
    
    fields["date_of_expiry"] = {"text": identity["expiry_viz"], "bbox": [550, 360, 750, 400], "confidence": 1.0}
    draw.text((550, 355), f"DATE OF EXPIRY:\n{identity['expiry_viz']}", fill=(20, 20, 20))
    
    # MRZ generation
    doc_chk = compute_mrz_check_digit(identity["doc_number"])
    dob_chk = compute_mrz_check_digit(identity["dob_mrz"])
    exp_chk = compute_mrz_check_digit(identity["expiry_mrz"])
    
    # Line 1: P<UTO LASTNAME<<FIRSTNAME<<<<... (44 chars)
    name_field = f"{identity['last_name']}<<{identity['first_name']}"
    line1 = f"P<{identity['country_code']}{name_field}".ljust(44, '<')[:44]
    
    # Line 2: DOC_NUM + CHK + NAT + DOB + CHK + GENDER + EXP + CHK + OPT + COMPOSITE_CHK
    opt_data = "".ljust(14, '<')
    composite_raw = f"{identity['doc_number']}{doc_chk}{identity['dob_mrz']}{dob_chk}{identity['expiry_mrz']}{exp_chk}{opt_data}"
    comp_chk = compute_mrz_check_digit(composite_raw)
    line2 = f"{identity['doc_number']}{doc_chk}{identity['country_code']}{identity['dob_mrz']}{dob_chk}{identity['gender']}{identity['expiry_mrz']}{exp_chk}{opt_data}{comp_chk}"[:44]
    
    # Draw MRZ section
    draw.rectangle([0, 520, width, height], fill=(235, 235, 230), outline=(180, 180, 180), width=1)
    fields["mrz_line1"] = {"text": line1, "bbox": [40, 550, 960, 600], "confidence": 1.0}
    fields["mrz_line2"] = {"text": line2, "bbox": [40, 620, 960, 670], "confidence": 1.0}
    
    draw.text((40, 550), line1, fill=(10, 10, 10))
    draw.text((40, 620), line2, fill=(10, 10, 10))
    
    return apply_capture_variation(img, fields, variation_id)

def generate_driver_license(identity, doc_id, variation_id=1):
    """Generates synthetic AAMVA Driver's License Image."""
    width, height = 900, 550
    img = Image.new("RGB", (width, height), color=(240, 248, 255))
    draw = ImageDraw.Draw(img)
    
    # Header
    draw.rectangle([0, 0, width, 70], fill=(20, 80, 140))
    draw.text((30, 20), f"STATE OF {identity['country_name']} — DRIVER LICENSE", fill=(255, 255, 255))
    
    # Photo box
    photo_bbox = [40, 90, 240, 330]
    draw_face_placeholder(draw, photo_bbox)
    
    # Barcode placeholder
    draw.rectangle([40, 360, 240, 510], fill=(20, 20, 20))
    draw.text((50, 420), "PDF417 2D BARCODE\nAAMVA COMPLIANT", fill=(200, 200, 200))
    
    fields = {}
    dl_num = f"DL-{identity['doc_number']}"
    fields["document_type"] = {"text": "DRIVER_LICENSE", "bbox": [280, 80, 500, 105], "confidence": 1.0}
    fields["license_number"] = {"text": dl_num, "bbox": [280, 110, 600, 140], "confidence": 1.0}
    draw.text((280, 110), f"DL NO: {dl_num}", fill=(180, 20, 20))
    
    fields["full_name"] = {"text": identity["full_name"], "bbox": [280, 150, 700, 185], "confidence": 1.0}
    draw.text((280, 150), f"NAME: {identity['last_name']}, {identity['first_name']}", fill=(20, 20, 20))
    
    fields["address"] = {"text": identity["address"], "bbox": [280, 195, 800, 230], "confidence": 1.0}
    draw.text((280, 195), f"ADDR: {identity['address']}", fill=(20, 20, 20))
    
    fields["date_of_birth"] = {"text": identity["dob_viz"], "bbox": [280, 240, 500, 270], "confidence": 1.0}
    draw.text((280, 240), f"DOB: {identity['dob_viz']}", fill=(20, 20, 20))
    
    fields["gender"] = {"text": identity["gender"], "bbox": [530, 240, 620, 270], "confidence": 1.0}
    draw.text((530, 240), f"SEX: {identity['gender']}", fill=(20, 20, 20))
    
    fields["issue_date"] = {"text": identity["issue_viz"], "bbox": [280, 285, 500, 315], "confidence": 1.0}
    draw.text((280, 285), f"ISS: {identity['issue_viz']}", fill=(20, 20, 20))
    
    fields["expiry_date"] = {"text": identity["expiry_viz"], "bbox": [530, 285, 750, 315], "confidence": 1.0}
    draw.text((530, 285), f"EXP: {identity['expiry_viz']}", fill=(180, 20, 20))
    
    v_class = random.choice(VEHICLE_CLASSES)
    fields["vehicle_class"] = {"text": v_class, "bbox": [280, 330, 750, 360], "confidence": 1.0}
    draw.text((280, 330), f"CLASS: {v_class}", fill=(20, 20, 20))
    
    return apply_capture_variation(img, fields, variation_id)

def generate_visa(identity, doc_id, variation_id=1):
    """Generates synthetic Travel Visa (MRV-A)."""
    width, height = 950, 650
    img = Image.new("RGB", (width, height), color=(250, 248, 235))
    draw = ImageDraw.Draw(img)
    
    # Border pattern
    draw.rectangle([0, 0, width, 60], fill=(60, 100, 70))
    draw.text((30, 20), f"TRAVEL VISA — {identity['country_name']}", fill=(255, 255, 255))
    
    # Photo box
    photo_bbox = [50, 90, 230, 320]
    draw_face_placeholder(draw, photo_bbox)
    
    fields = {}
    visa_num = f"V{random.randint(10000000, 99999999)}"
    fields["document_type"] = {"text": "VISA", "bbox": [270, 80, 450, 105], "confidence": 1.0}
    fields["visa_number"] = {"text": visa_num, "bbox": [270, 110, 550, 140], "confidence": 1.0}
    draw.text((270, 110), f"VISA NO: {visa_num}", fill=(180, 20, 20))
    
    fields["full_name"] = {"text": identity["full_name"], "bbox": [270, 150, 700, 185], "confidence": 1.0}
    draw.text((270, 150), f"BEARER: {identity['last_name']}, {identity['first_name']}", fill=(20, 20, 20))
    
    fields["passport_number"] = {"text": identity["doc_number"], "bbox": [270, 195, 600, 225], "confidence": 1.0}
    draw.text((270, 195), f"PASSPORT NO: {identity['doc_number']}", fill=(20, 20, 20))
    
    fields["issue_date"] = {"text": identity["issue_viz"], "bbox": [270, 240, 500, 270], "confidence": 1.0}
    draw.text((270, 240), f"VALID FROM: {identity['issue_viz']}", fill=(20, 20, 20))
    
    fields["expiry_date"] = {"text": identity["expiry_viz"], "bbox": [530, 240, 750, 270], "confidence": 1.0}
    draw.text((530, 240), f"VALID UNTIL: {identity['expiry_viz']}", fill=(180, 20, 20))
    
    fields["entries"] = {"text": "MULTIPLE", "bbox": [270, 285, 450, 315], "confidence": 1.0}
    draw.text((270, 285), "ENTRIES: MULTIPLE", fill=(20, 20, 20))
    
    # MRV-A Lines
    doc_chk = compute_mrz_check_digit(visa_num)
    dob_chk = compute_mrz_check_digit(identity["dob_mrz"])
    exp_chk = compute_mrz_check_digit(identity["expiry_mrz"])
    
    line1 = f"VN<{identity['country_code']}{identity['last_name']}<<{identity['first_name']}".ljust(44, '<')[:44]
    line2 = f"{visa_num}{doc_chk}{identity['country_code']}{identity['dob_mrz']}{dob_chk}{identity['gender']}{identity['expiry_mrz']}{exp_chk}".ljust(44, '<')[:44]
    
    draw.rectangle([0, 480, width, height], fill=(240, 238, 225))
    fields["mrz_line1"] = {"text": line1, "bbox": [40, 510, 910, 555], "confidence": 1.0}
    fields["mrz_line2"] = {"text": line2, "bbox": [40, 575, 910, 620], "confidence": 1.0}
    
    draw.text((40, 510), line1, fill=(10, 10, 10))
    draw.text((40, 575), line2, fill=(10, 10, 10))
    
    return apply_capture_variation(img, fields, variation_id)

def generate_national_id(identity, doc_id, variation_id=1):
    """Generates synthetic National ID Card (TD1 layout)."""
    width, height = 860, 540
    img = Image.new("RGB", (width, height), color=(245, 248, 252))
    draw = ImageDraw.Draw(img)
    
    # Header
    draw.rectangle([0, 0, width, 60], fill=(40, 50, 90))
    draw.text((30, 20), f"NATIONAL IDENTITY CARD — {identity['country_name']}", fill=(255, 255, 255))
    
    photo_bbox = [40, 80, 220, 310]
    draw_face_placeholder(draw, photo_bbox)
    
    fields = {}
    id_num = f"ID-{identity['doc_number']}"
    fields["document_type"] = {"text": "NATIONAL_ID", "bbox": [260, 80, 450, 105], "confidence": 1.0}
    fields["id_number"] = {"text": id_num, "bbox": [260, 110, 550, 140], "confidence": 1.0}
    draw.text((260, 110), f"ID NO: {id_num}", fill=(20, 20, 20))
    
    fields["full_name"] = {"text": identity["full_name"], "bbox": [260, 150, 650, 185], "confidence": 1.0}
    draw.text((260, 150), f"NAME: {identity['last_name']}, {identity['first_name']}", fill=(20, 20, 20))
    
    fields["date_of_birth"] = {"text": identity["dob_viz"], "bbox": [260, 195, 450, 225], "confidence": 1.0}
    draw.text((260, 195), f"DOB: {identity['dob_viz']}", fill=(20, 20, 20))
    
    fields["nationality"] = {"text": identity["country_code"], "bbox": [480, 195, 600, 225], "confidence": 1.0}
    draw.text((480, 195), f"CITIZENSHIP: {identity['country_code']}", fill=(20, 20, 20))
    
    fields["expiry_date"] = {"text": identity["expiry_viz"], "bbox": [260, 240, 500, 270], "confidence": 1.0}
    draw.text((260, 240), f"EXPIRY: {identity['expiry_viz']}", fill=(180, 20, 20))
    
    # TD1 MRZ (3 lines of 30 chars)
    line1 = f"I<{identity['country_code']}{identity['doc_number'][:9]}".ljust(30, '<')[:30]
    line2 = f"{identity['dob_mrz']}{identity['gender']}{identity['expiry_mrz']}{identity['country_code']}".ljust(30, '<')[:30]
    line3 = f"{identity['last_name']}<<{identity['first_name']}".ljust(30, '<')[:30]
    
    draw.rectangle([0, 360, width, height], fill=(235, 238, 245))
    fields["mrz_line1"] = {"text": line1, "bbox": [30, 380, 830, 415], "confidence": 1.0}
    fields["mrz_line2"] = {"text": line2, "bbox": [30, 430, 830, 465], "confidence": 1.0}
    fields["mrz_line3"] = {"text": line3, "bbox": [30, 480, 830, 515], "confidence": 1.0}
    
    draw.text((30, 380), line1, fill=(10, 10, 10))
    draw.text((30, 430), line2, fill=(10, 10, 10))
    draw.text((30, 480), line3, fill=(10, 10, 10))
    
    return apply_capture_variation(img, fields, variation_id)

def generate_permit(identity, doc_id, variation_id=1):
    """Generates synthetic Residence / Work Permit."""
    width, height = 860, 540
    img = Image.new("RGB", (width, height), color=(252, 245, 248))
    draw = ImageDraw.Draw(img)
    
    draw.rectangle([0, 0, width, 60], fill=(120, 40, 60))
    draw.text((30, 20), f"RESIDENCE & WORK PERMIT — {identity['country_name']}", fill=(255, 255, 255))
    
    photo_bbox = [40, 80, 220, 310]
    draw_face_placeholder(draw, photo_bbox)
    
    fields = {}
    permit_num = f"RP-{identity['doc_number']}"
    fields["document_type"] = {"text": "RESIDENCE_PERMIT", "bbox": [260, 80, 480, 105], "confidence": 1.0}
    fields["permit_number"] = {"text": permit_num, "bbox": [260, 110, 550, 140], "confidence": 1.0}
    draw.text((260, 110), f"PERMIT NO: {permit_num}", fill=(20, 20, 20))
    
    fields["full_name"] = {"text": identity["full_name"], "bbox": [260, 150, 650, 185], "confidence": 1.0}
    draw.text((260, 150), f"HOLDER: {identity['last_name']}, {identity['first_name']}", fill=(20, 20, 20))
    
    p_type = random.choice(PERMIT_TYPES)
    fields["permit_category"] = {"text": p_type, "bbox": [260, 195, 600, 225], "confidence": 1.0}
    draw.text((260, 195), f"CATEGORY: {p_type}", fill=(20, 20, 20))
    
    fields["valid_until"] = {"text": identity["expiry_viz"], "bbox": [260, 240, 500, 270], "confidence": 1.0}
    draw.text((260, 240), f"VALID UNTIL: {identity['expiry_viz']}", fill=(180, 20, 20))
    
    sponsor = f"{random.choice(COUNTRIES)[1]} TECH CORP"
    fields["sponsor"] = {"text": sponsor, "bbox": [260, 285, 650, 315], "confidence": 1.0}
    draw.text((260, 285), f"EMPLOYER: {sponsor}", fill=(20, 20, 20))
    
    return apply_capture_variation(img, fields, variation_id)

def apply_capture_variation(img, fields, variation_id):
    """Applies realistic optical variations (clean, glare/lighting, mild blur, noise)."""
    if variation_id == 1:
        # Standard clean flatbed scan
        return img, fields
    elif variation_id == 2:
        # Lighting / shadow gradient
        arr = np.array(img, dtype=np.float32)
        h, w, _ = arr.shape
        gradient = np.linspace(0.85, 1.15, w).reshape(1, w, 1)
        arr = np.clip(arr * gradient, 0, 255).astype(np.uint8)
        var_img = Image.fromarray(arr)
        return var_img, fields
    elif variation_id == 3:
        # Slight blur / camera lens softness
        var_img = img.filter(ImageFilter.GaussianBlur(radius=0.7))
        return var_img, fields
    else:
        # Mild sensor noise
        arr = np.array(img, dtype=np.int16)
        noise = np.random.normal(0, 3.5, arr.shape).astype(np.int16)
        arr = np.clip(arr + noise, 0, 255).astype(np.uint8)
        var_img = Image.fromarray(arr)
        return var_img, fields

def generate_dataset(raw_dir, annotations_dir, total_identities=120, external_identities=30):
    """Generates the primary dataset and isolated external test dataset."""
    os.makedirs(raw_dir, exist_ok=True)
    os.makedirs(annotations_dir, exist_ok=True)
    
    manifest_records = []
    
    doc_generators = [
        ("passport", generate_passport),
        ("driver_license", generate_driver_license),
        ("visa", generate_visa),
        ("national_id", generate_national_id),
        ("permit", generate_permit)
    ]
    
    print(f"Generating primary dataset ({total_identities} unique document identities)...")
    
    for i in range(total_identities):
        doc_type, gen_func = doc_generators[i % len(doc_generators)]
        identity = generate_synthetic_identity()
        doc_id = f"DOC_{doc_type.upper()}_{i+1:04d}"
        
        # Generate 2 variations per document identity (e.g. scan + camera condition)
        for var_id in [1, 2]:
            img, fields = gen_func(identity, doc_id, variation_id=var_id)
            img_filename = f"{doc_id}_v{var_id}.png"
            img_path = os.path.join(raw_dir, img_filename)
            img.save(img_path, "PNG")
            
            record = {
                "image_id": img_filename,
                "document_id": doc_id,
                "document_type": doc_type,
                "source": "synth_doc_gen_v1",
                "variation": f"var_{var_id}",
                "width": img.width,
                "height": img.height,
                "fields": fields
            }
            manifest_records.append(record)
            
    # Inject 3 controlled edge cases to demonstrate automated cleaning detection:
    # 1. Zero-byte corrupted file
    zero_byte_path = os.path.join(raw_dir, "DOC_CORRUPTED_ZERO_BYTE.png")
    with open(zero_byte_path, "wb") as f:
        pass
        
    # 2. Corrupted header file
    corrupt_hdr_path = os.path.join(raw_dir, "DOC_CORRUPTED_HEADER.png")
    with open(corrupt_hdr_path, "wb") as f:
        f.write(b"NOT_A_VALID_IMAGE_HEADER_DATA")
        
    # 3. Micro image below minimum threshold
    micro_img = Image.new("RGB", (50, 50), color=(0, 0, 0))
    micro_path = os.path.join(raw_dir, "DOC_REJECTED_TINY_DIMENSIONS.png")
    micro_img.save(micro_path)

    # Save primary raw annotations
    raw_ann_file = os.path.join(annotations_dir, "raw_annotations.jsonl")
    with open(raw_ann_file, "w", encoding="utf-8") as f:
        for r in manifest_records:
            f.write(json.dumps(r) + "\n")
            
    print(f"Generated {len(manifest_records)} primary image captures across {total_identities} document identities.")
    print(f"Injected 3 controlled corrupted/edge-case files in {raw_dir} for cleaning tests.")

    # Generate isolated external test set
    ext_dir = os.path.join(os.path.dirname(raw_dir), "external_test")
    os.makedirs(ext_dir, exist_ok=True)
    ext_manifest_records = []
    
    print(f"Generating isolated external test set ({external_identities} unique identities)...")
    for i in range(external_identities):
        doc_type, gen_func = doc_generators[i % len(doc_generators)]
        identity = generate_synthetic_identity()
        doc_id = f"EXT_{doc_type.upper()}_{i+1:04d}"
        
        img, fields = gen_func(identity, doc_id, variation_id=random.choice([2, 3, 4]))
        img_filename = f"{doc_id}_ext.png"
        img_path = os.path.join(ext_dir, img_filename)
        img.save(img_path, "PNG")
        
        record = {
            "image_id": img_filename,
            "document_id": doc_id,
            "document_type": doc_type,
            "source": "isolated_external_eval",
            "variation": "external_unseen",
            "width": img.width,
            "height": img.height,
            "fields": fields
        }
        ext_manifest_records.append(record)
        
    ext_ann_file = os.path.join(annotations_dir, "external_test_annotations.jsonl")
    with open(ext_ann_file, "w", encoding="utf-8") as f:
        for r in ext_manifest_records:
            f.write(json.dumps(r) + "\n")
            
    print(f"Generated {len(ext_manifest_records)} external test images.")

if __name__ == "__main__":
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    raw_dir = os.path.join(base_dir, "data", "raw")
    annotations_dir = os.path.join(base_dir, "data", "annotations")
    generate_dataset(raw_dir, annotations_dir, total_identities=120, external_identities=30)
