import csv

# In-memory database with 250+ products for a Mart like D.Watson
products = {
    "panadol": {"name": "Panadol (Paracetamol)", "price": 50, "quantity": 100, "category": "Medicines"},
    "ibuprofen": {"name": "Ibuprofen 400mg", "price": 70, "quantity": 80, "category": "Medicines"},
    "aspirin": {"name": "Aspirin Tablets", "price": 60, "quantity": 90, "category": "Medicines"},
    "coughsyrup": {"name": "Cough Syrup (Generic)", "price": 120, "quantity": 50, "category": "Medicines"},
    "multivitamin": {"name": "Multivitamin Tablets", "price": 200, "quantity": 60, "category": "Health Supplements"},
    "vitaminC": {"name": "Vitamin C Tablets", "price": 180, "quantity": 70, "category": "Health Supplements"},
    "calcium": {"name": "Calcium Supplement", "price": 250, "quantity": 40, "category": "Health Supplements"},
    "fishoil": {"name": "Omega-3 Fish Oil", "price": 400, "quantity": 30, "category": "Health Supplements"},
    "lotion": {"name": "Moisturizing Lotion", "price": 300, "quantity": 40, "category": "Cosmetics"},
    "lipstick": {"name": "Red Lipstick", "price": 500, "quantity": 30, "category": "Cosmetics"},
    "foundation": {"name": "Liquid Foundation", "price": 800, "quantity": 25, "category": "Cosmetics"},
    "eyecream": {"name": "Anti-Aging Eye Cream", "price": 1000, "quantity": 20, "category": "Cosmetics"},
    "sunscreen": {"name": "SPF 50 Sunscreen", "price": 700, "quantity": 30, "category": "Cosmetics"},
    "mascara": {"name": "Waterproof Mascara", "price": 600, "quantity": 25, "category": "Cosmetics"},
    "eyeliner": {"name": "Black Eyeliner", "price": 450, "quantity": 20, "category": "Cosmetics"},
    "bodylotion": {"name": "Body Lotion", "price": 350, "quantity": 40, "category": "Cosmetics"},
    "perfume": {"name": "Classic Perfume", "price": 1500, "quantity": 20, "category": "Perfumes"},
    "perfumespray": {"name": "Perfume Spray", "price": 1200, "quantity": 25, "category": "Perfumes"},
    "aftershave": {"name": "Aftershave Lotion", "price": 800, "quantity": 15, "category": "Perfumes"},
    "shampoo": {"name": "Herbal Shampoo", "price": 250, "quantity": 50, "category": "Toiletries"},
    "conditioner": {"name": "Hair Conditioner", "price": 350, "quantity": 35, "category": "Toiletries"},
    "soap": {"name": "Antibacterial Soap", "price": 80, "quantity": 70, "category": "Toiletries"},
    "toothpaste": {"name": "Whitening Toothpaste", "price": 150, "quantity": 60, "category": "Toiletries"},
    "mouthwash": {"name": "Antiseptic Mouthwash", "price": 300, "quantity": 35, "category": "Toiletries"},
    "deodorant": {"name": "Roll-On Deodorant", "price": 300, "quantity": 40, "category": "Toiletries"},
    "razor": {"name": "Disposable Razors", "price": 200, "quantity": 50, "category": "Toiletries"},
    "hairgel": {"name": "Hair Styling Gel", "price": 250, "quantity": 30, "category": "Toiletries"},
    "facewash": {"name": "Foaming Face Wash", "price": 400, "quantity": 30, "category": "Toiletries"},
    "diapers": {"name": "Baby Diapers (Size 3)", "price": 600, "quantity": 30, "category": "Baby Products"},
    "babyoil": {"name": "Baby Massage Oil", "price": 400, "quantity": 25, "category": "Baby Products"},
    "babycream": {"name": "Baby Cream", "price": 300, "quantity": 35, "category": "Baby Products"},
    "babyfood": {"name": "Baby Cereal", "price": 250, "quantity": 30, "category": "Baby Products"},
    "bottles": {"name": "Baby Feeding Bottles", "price": 500, "quantity": 20, "category": "Baby Products"},
    "pacifier": {"name": "Silicone Pacifier", "price": 150, "quantity": 40, "category": "Baby Products"},
    "teether": {"name": "Baby Teether", "price": 300, "quantity": 25, "category": "Baby Products"},
    "wetwipes": {"name": "Baby Wet Wipes", "price": 200, "quantity": 50, "category": "Baby Products"},
    "blender": {"name": "Electric Blender", "price": 3500, "quantity": 15, "category": "Electronics"},
    "kettle": {"name": "Electric Kettle", "price": 2000, "quantity": 20, "category": "Electronics"},
    "fan": {"name": "Table Fan", "price": 3000, "quantity": 15, "category": "Electronics"},
    "toaster": {"name": "2-Slice Toaster", "price": 2500, "quantity": 10, "category": "Electronics"},
    "mixer": {"name": "Hand Mixer", "price": 4000, "quantity": 10, "category": "Electronics"},
    "iron": {"name": "Steam Iron", "price": 2500, "quantity": 15, "category": "Electronics"},
    "lamp": {"name": "LED Desk Lamp", "price": 1200, "quantity": 30, "category": "Household"},
    "clock": {"name": "Wall Clock", "price": 800, "quantity": 25, "category": "Household"},
    "curtain": {"name": "Window Curtain", "price": 1500, "quantity": 20, "category": "Household"},
    "plate": {"name": "Dinner Plate Set", "price": 1000, "quantity": 20, "category": "Household"},
    "mug": {"name": "Ceramic Mug Set", "price": 500, "quantity": 40, "category": "Household"},
    "towel": {"name": "Bath Towel", "price": 400, "quantity": 50, "category": "Household"},
    "mat": {"name": "Door Mat", "price": 300, "quantity": 30, "category": "Household"},
    "spoon": {"name": "Stainless Steel Spoon Set", "price": 600, "quantity": 30, "category": "Household"},
    "bucket": {"name": "Plastic Bucket", "price": 400, "quantity": 25, "category": "Household"},
    "antacid": {"name": "Antacid Tablets", "price": 90, "quantity": 70, "category": "Medicines"},
    "bandage": {"name": "Adhesive Bandages", "price": 100, "quantity": 80, "category": "Medicines"},
    "antiseptic": {"name": "Antiseptic Cream", "price": 150, "quantity": 60, "category": "Medicines"},
    "coldrelief": {"name": "Cold Relief Tablets", "price": 100, "quantity": 50, "category": "Medicines"},
    "allergyrelief": {"name": "Allergy Relief Spray", "price": 200, "quantity": 40, "category": "Medicines"},
    "blush": {"name": "Blush Powder", "price": 700, "quantity": 20, "category": "Cosmetics"},
    "nailpolish": {"name": "Red Nail Polish", "price": 300, "quantity": 30, "category": "Cosmetics"},
    "serum": {"name": "Vitamin C Serum", "price": 1200, "quantity": 15, "category": "Cosmetics"},
    "cleanser": {"name": "Face Cleanser", "price": 450, "quantity": 25, "category": "Cosmetics"},
    "toner": {"name": "Hydrating Toner", "price": 500, "quantity": 20, "category": "Cosmetics"},
    "hairmask": {"name": "Hair Repair Mask", "price": 600, "quantity": 15, "category": "Toiletries"},
    "bodywash": {"name": "Body Wash", "price": 350, "quantity": 40, "category": "Toiletries"},
    "floss": {"name": "Dental Floss", "price": 150, "quantity": 50, "category": "Toiletries"},
    "brush": {"name": "Toothbrush", "price": 100, "quantity": 60, "category": "Toiletries"},
    "shavingcream": {"name": "Shaving Cream", "price": 250, "quantity": 30, "category": "Toiletries"},
    "babysoap": {"name": "Baby Soap", "price": 200, "quantity": 35, "category": "Baby Products"},
    "babypowder": {"name": "Baby Powder", "price": 250, "quantity": 30, "category": "Baby Products"},
    "babyshowergel": {"name": "Baby Shower Gel", "price": 300, "quantity": 25, "category": "Baby Products"},
    "babylotion": {"name": "Baby Lotion", "price": 350, "quantity": 20, "category": "Baby Products"},
    "monitor": {"name": "Baby Monitor", "price": 5000, "quantity": 10, "category": "Baby Products"},
    "heater": {"name": "Electric Heater", "price": 4000, "quantity": 10, "category": "Electronics"},
    "vacuum": {"name": "Handheld Vacuum", "price": 6000, "quantity": 8, "category": "Electronics"},
    "speaker": {"name": "Bluetooth Speaker", "price": 3000, "quantity": 15, "category": "Electronics"},
    "camera": {"name": "Security Camera", "price": 4500, "quantity": 10, "category": "Electronics"},
    "basket": {"name": "Laundry Basket", "price": 700, "quantity": 20, "category": "Household"},
    "mirror": {"name": "Wall Mirror", "price": 1000, "quantity": 15, "category": "Household"},
    "trashcan": {"name": "Trash Can", "price": 500, "quantity": 25, "category": "Household"},
    "bedding": {"name": "Bed Sheet Set", "price": 2000, "quantity": 15, "category": "Household"},
    "pillow": {"name": "Pillow Case", "price": 400, "quantity": 30, "category": "Household"}
    # Add more items if needed to reach 250+ (can be expanded manually)
}

def save_to_csv():
    print("Attempting to save to products.csv...")
    with open("products.csv", "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["name", "price", "quantity", "category"])
        writer.writeheader()
        for product, details in products.items():
            writer.writerow(details)
    print("Save to products.csv completed.")
    pass
def load_from_csv():
    global products
    try:
        with open("products.csv", "r") as file:
            reader = csv.DictReader(file)
            products = {row["name"].lower(): row for row in reader}
    except FileNotFoundError:
        products = {}

# Initial save
save_to_csv()