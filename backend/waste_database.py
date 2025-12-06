"""
Waste items database with disposal instructions
"""
from typing import Dict, List, Optional

WASTE_ITEMS_DB = {
    # Organic/Wet Waste
    "food_scraps": {
        "category": "organic",
        "names": ["food scraps", "food waste", "kitchen waste", "vegetable peels", "fruit peels"],
        "disposal": "Compost at home or use municipal organic waste bins",
        "impact": "Produces methane in landfills; composting converts it to useful fertilizer",
        "recyclable": False
    },
    "banana_peel": {
        "category": "organic",
        "names": ["banana peel", "banana skin"],
        "disposal": "Compost or organic waste bin",
        "impact": "Biodegradable, excellent for composting",
        "recyclable": False
    },
    "leaves": {
        "category": "organic",
        "names": ["leaves", "dried leaves", "garden waste"],
        "disposal": "Compost or municipal green waste collection",
        "impact": "Natural fertilizer when composted",
        "recyclable": False
    },
    
    # Dry Recyclables - Plastic
    "plastic_bottle": {
        "category": "dry_recyclables",
        "names": ["plastic bottle", "pet bottle", "water bottle", "soda bottle"],
        "disposal": "Rinse and place in recycling bin. Check for #1 or #2 symbol",
        "impact": "Takes 450+ years to decompose; recycling saves petroleum resources",
        "recyclable": True,
        "recycling_code": "PET #1 or HDPE #2"
    },
    "plastic_bag": {
        "category": "dry_recyclables",
        "names": ["plastic bag", "shopping bag", "polythene bag"],
        "disposal": "Reuse or take to plastic bag collection centers",
        "impact": "Clogs drains, harms marine life; very difficult to recycle",
        "recyclable": False
    },
    "plastic_container": {
        "category": "dry_recyclables",
        "names": ["plastic container", "food container", "takeout container"],
        "disposal": "Clean and check recycling code; #1, #2, #5 usually recyclable",
        "impact": "Can be recycled if clean; contamination ruins entire batches",
        "recyclable": True,
        "recycling_code": "Check bottom for #1-7"
    },
    
    # Dry Recyclables - Paper/Cardboard
    "cardboard": {
        "category": "dry_recyclables",
        "names": ["cardboard", "cardboard box", "corrugated box"],
        "disposal": "Flatten and place in recycling bin; remove tape/staples",
        "impact": "Highly recyclable; saves trees and energy",
        "recyclable": True
    },
    "paper": {
        "category": "dry_recyclables",
        "names": ["paper", "newspaper", "magazine", "office paper"],
        "disposal": "Dry paper in recycling bin; wet/soiled paper goes to compost",
        "impact": "5 times recyclable before fibers degrade",
        "recyclable": True
    },
    
    # Dry Recyclables - Metal
    "aluminum_can": {
        "category": "dry_recyclables",
        "names": ["aluminum can", "soda can", "beer can", "tin can"],
        "disposal": "Rinse and recycle; infinitely recyclable",
        "impact": "Recycling saves 95% of energy vs. new production",
        "recyclable": True
    },
    "metal_scrap": {
        "category": "dry_recyclables",
        "names": ["metal", "scrap metal", "steel", "iron"],
        "disposal": "Take to scrap metal dealer or recycling center",
        "impact": "Highly valuable; metal recycling is very profitable",
        "recyclable": True
    },
    
    # Dry Recyclables - Glass
    "glass_bottle": {
        "category": "dry_recyclables",
        "names": ["glass bottle", "glass jar", "wine bottle"],
        "disposal": "Rinse and recycle; remove caps",
        "impact": "100% recyclable without quality loss",
        "recyclable": True
    },
    
    # E-Waste
    "battery": {
        "category": "e_waste",
        "names": ["battery", "batteries", "aa battery", "lithium battery"],
        "disposal": "Never trash! Take to e-waste collection center or battery drop-off",
        "impact": "Contains toxic heavy metals; must be specially recycled",
        "recyclable": True,
        "hazard_level": "high"
    },
    "phone": {
        "category": "e_waste",
        "names": ["mobile phone", "smartphone", "cell phone", "old phone"],
        "disposal": "E-waste collection center or manufacturer take-back program",
        "impact": "Contains valuable metals and toxic substances",
        "recyclable": True
    },
    "laptop": {
        "category": "e_waste",
        "names": ["laptop", "computer", "notebook"],
        "disposal": "E-waste recycling facility; wipe data first",
        "impact": "Contains precious metals and hazardous materials",
        "recyclable": True
    },
    "charger": {
        "category": "e_waste",
        "names": ["charger", "cable", "usb cable", "power cord"],
        "disposal": "E-waste bin or electronics store take-back",
        "impact": "Copper wire is valuable; plastic coating is not",
        "recyclable": True
    },
    
    # Hazardous
    "paint": {
        "category": "hazardous",
        "names": ["paint", "paint can", "spray paint"],
        "disposal": "Hazardous waste collection day or facility",
        "impact": "Contains toxic chemicals; never pour down drain",
        "recyclable": False,
        "hazard_level": "high"
    },
    "medicine": {
        "category": "hazardous",
        "names": ["medicine", "pills", "medication", "expired medicine"],
        "disposal": "Pharmacy take-back program or hazardous waste facility",
        "impact": "Contaminates water supply if flushed or trashed",
        "recyclable": False,
        "hazard_level": "high"
    },
    "light_bulb": {
        "category": "hazardous",
        "names": ["light bulb", "cfl bulb", "fluorescent tube"],
        "disposal": "Hazardous waste or hardware store recycling; contains mercury",
        "impact": "CFL/fluorescent contain mercury; LED safer but still e-waste",
        "recyclable": True,
        "hazard_level": "medium"
    }
}


def search_waste_item(query: str) -> Optional[Dict]:
    """Search for a waste item by name"""
    query_lower = query.lower().strip()
    
    for item_id, item_data in WASTE_ITEMS_DB.items():
        if any(name in query_lower or query_lower in name for name in item_data["names"]):
            return {
                "item_id": item_id,
                **item_data
            }
    
    return None


def get_disposal_info(category: str) -> Dict:
    """Get general disposal guidelines by category"""
    guidelines = {
        "organic": {
            "disposal": "Compost at home or use municipal organic waste bins",
            "do": ["Separate wet from dry waste", "Use for composting", "Avoid plastic contamination"],
            "dont": ["Mix with dry recyclables", "Add meat/dairy to home compost", "Use plastic bags"]
        },
        "dry_recyclables": {
            "disposal": "Rinse, dry, and place in recycling bin",
            "do": ["Clean containers before recycling", "Remove labels if possible", "Flatten cardboard"],
            "dont": ["Recycle greasy pizza boxes", "Mix different materials", "Include wet/contaminated items"]
        },
        "e_waste": {
            "disposal": "Take to authorized e-waste collection center",
            "do": ["Wipe personal data", "Keep components together", "Use manufacturer take-back"],
            "dont": ["Throw in regular trash", "Burn electronics", "Dump in landfills"]
        },
        "hazardous": {
            "disposal": "Special hazardous waste collection only",
            "do": ["Keep in original container", "Use designated drop-off", "Check local collection days"],
            "dont": ["Pour down drain", "Mix chemicals", "Put in regular trash"]
        }
    }
    
    return guidelines.get(category, {
        "disposal": "Check with local waste management authority",
        "do": ["Research proper disposal", "Consult municipal guidelines"],
        "dont": ["Assume it's recyclable", "Mix with other waste"]
    })


def get_all_categories() -> List[str]:
    """Get list of all waste categories"""
    return ["organic", "dry_recyclables", "e_waste", "hazardous", "unknown"]
