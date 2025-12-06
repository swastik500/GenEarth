"""
Database initialization script
Run this to set up the database with sample data and initialize ChromaDB
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.database import engine, SessionLocal
from backend.models import Base, NGO, GovernmentScheme, User
from backend.ai.knowledge_loader import initialize_vector_store, add_scheme_to_vector_store


def create_tables():
    """Create all database tables"""
    print("📊 Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created")


def seed_ngos(db):
    """Seed NGO data"""
    print("🌱 Seeding NGO data...")
    
    ngos_data = [
        {
            "name": "Swachh Mumbai",
            "state": "Maharashtra",
            "city": "Mumbai",
            "category": "Waste Management",
            "website": "https://swachhmumbai.org",
            "contact_email": "contact@swachhmumbai.org",
            "contact_phone": "+91-22-1234-5678",
            "description": "Working towards making Mumbai cleaner through waste segregation and recycling initiatives."
        },
        {
            "name": "Green Pune Foundation",
            "state": "Maharashtra",
            "city": "Pune",
            "category": "Environmental Conservation",
            "website": "https://greenpune.org",
            "contact_email": "info@greenpune.org",
            "contact_phone": "+91-20-9876-5432",
            "description": "Focused on tree plantation, water conservation, and sustainable urban development."
        },
        {
            "name": "Delhi Energy Savers",
            "state": "Delhi",
            "city": "Delhi",
            "category": "Energy Conservation",
            "website": "https://delhienergysavers.in",
            "contact_email": "hello@delhienergysavers.in",
            "contact_phone": "+91-11-5555-6666",
            "description": "Promoting renewable energy adoption and energy-efficient practices in Delhi NCR."
        },
        {
            "name": "Bangalore Green Brigade",
            "state": "Karnataka",
            "city": "Bangalore",
            "category": "Waste Management",
            "website": "https://bgbrigade.com",
            "contact_email": "support@bgbrigade.com",
            "contact_phone": "+91-80-7777-8888",
            "description": "Community-driven waste management and composting programs across Bangalore."
        },
        {
            "name": "Clean Air Chennai",
            "state": "Tamil Nadu",
            "city": "Chennai",
            "category": "Air Quality",
            "contact_email": "team@cleanairchennai.org",
            "contact_phone": "+91-44-3333-4444",
            "description": "Fighting air pollution through awareness campaigns and pollution monitoring."
        },
        {
            "name": "Hyderabad Water Warriors",
            "state": "Telangana",
            "city": "Hyderabad",
            "category": "Water Conservation",
            "website": "https://waterwarriors.in",
            "contact_email": "contact@waterwarriors.in",
            "contact_phone": "+91-40-2222-3333",
            "description": "Rainwater harvesting and lake restoration projects in Hyderabad."
        },
        {
            "name": "Ahmedabad Solar Initiative",
            "state": "Gujarat",
            "city": "Ahmedabad",
            "category": "Renewable Energy",
            "website": "https://ahmedabadsolar.org",
            "contact_email": "info@ahmedabadsolar.org",
            "contact_phone": "+91-79-6666-7777",
            "description": "Helping communities adopt solar energy through subsidies and awareness."
        },
        {
            "name": "Kolkata Recycle Hub",
            "state": "West Bengal",
            "city": "Kolkata",
            "category": "Waste Management",
            "contact_email": "hello@kolkatarecycle.org",
            "contact_phone": "+91-33-8888-9999",
            "description": "E-waste collection and recycling center serving Kolkata metropolitan area."
        },
        {
            "name": "Jaipur Green City Project",
            "state": "Rajasthan",
            "city": "Jaipur",
            "category": "Environmental Conservation",
            "website": "https://jaipurgreen.in",
            "contact_email": "team@jaipurgreen.in",
            "contact_phone": "+91-141-4444-5555",
            "description": "Urban greening initiatives including rooftop gardens and community parks."
        },
        {
            "name": "Chandigarh Clean Energy",
            "state": "Chandigarh",
            "city": "Chandigarh",
            "category": "Energy Conservation",
            "website": "https://chandigarhcleanenergy.org",
            "contact_email": "info@chandigarhcleanenergy.org",
            "contact_phone": "+91-172-1111-2222",
            "description": "Promoting electric vehicles and renewable energy in Chandigarh and surrounding areas."
        }
    ]
    
    for ngo_data in ngos_data:
        ngo = NGO(**ngo_data)
        db.add(ngo)
    
    db.commit()
    print(f"✅ Added {len(ngos_data)} NGOs")


def seed_users(db):
    """Seed sample users for gamification leaderboard"""
    print("🌱 Seeding sample users for gamification...")
    
    from datetime import datetime, timedelta
    import random
    
    sample_users = [
        {"username": "eco_warrior", "email": "warrior@ecomitra.com", "ecoscore": 250},
        {"username": "green_hero", "email": "hero@ecomitra.com", "ecoscore": 180},
        {"username": "planet_saver", "email": "saver@ecomitra.com", "ecoscore": 150},
        {"username": "earth_friend", "email": "friend@ecomitra.com", "ecoscore": 120},
        {"username": "nature_lover", "email": "lover@ecomitra.com", "ecoscore": 100},
        {"username": "eco_champion", "email": "champion@ecomitra.com", "ecoscore": 85},
        {"username": "green_thumb", "email": "thumb@ecomitra.com", "ecoscore": 70},
        {"username": "recycler_pro", "email": "pro@ecomitra.com", "ecoscore": 55},
        {"username": "solar_fan", "email": "solar@ecomitra.com", "ecoscore": 40},
        {"username": "water_saver", "email": "water@ecomitra.com", "ecoscore": 25},
    ]
    
    for user_data in sample_users:
        user = User(
            username=user_data["username"],
            email=user_data["email"],
            ecoscore=user_data["ecoscore"],
            current_streak=random.randint(0, 7),
            longest_streak=random.randint(3, 15),
            last_active_date=datetime.utcnow() - timedelta(days=random.randint(0, 3)),
            badges=random.sample(
                ["waste_warrior", "energy_saver", "scheme_explorer", "ngo_connector"],
                k=random.randint(1, 3)
            ),
            quiz_completed=random.randint(0, 5),
            images_analyzed=random.randint(2, 10),
            chat_questions=random.randint(5, 20),
            ngos_viewed=random.randint(1, 8),
            schemes_viewed=random.randint(1, 8)
        )
        db.add(user)
    
    db.commit()
    print(f"✅ {len(sample_users)} sample users added")


def seed_schemes(db):
    """Seed government scheme data"""
    print("🏛️ Seeding government scheme data...")
    
    schemes_data = [
        {
            "name": "PM-KUSUM (Pradhan Mantri Kisan Urja Suraksha evam Utthaan Mahabhiyan)",
            "state": "National",
            "category": "Solar Energy",
            "summary": "Scheme to provide financial support for installation of solar pumps and grid-connected solar power plants for farmers.",
            "eligibility": "Individual farmers, groups of farmers, cooperatives, panchayats, and Farmer Producer Organizations (FPOs).",
            "how_to_apply": "Apply through state nodal agencies or DISCOM offices. Visit official MNRE website for application forms and guidelines.",
            "official_url": "https://mnre.gov.in/solar/schemes"
        },
        {
            "name": "FAME India Scheme (Faster Adoption and Manufacturing of Electric Vehicles)",
            "state": "National",
            "category": "Electric Vehicles",
            "summary": "Incentives and subsidies for purchasing electric and hybrid vehicles to reduce vehicular pollution.",
            "eligibility": "All Indian citizens purchasing eligible electric 2-wheelers, 3-wheelers, 4-wheelers, and e-buses.",
            "how_to_apply": "Incentive is automatically applied at the dealership during vehicle purchase. No separate application needed.",
            "official_url": "https://fame2.heavyindustries.gov.in"
        },
        {
            "name": "National Clean Air Programme (NCAP)",
            "state": "National",
            "category": "Air Quality",
            "summary": "Comprehensive plan to reduce air pollution across India with a target of 20-30% reduction in PM2.5 and PM10 by 2024.",
            "eligibility": "State governments, urban local bodies, and pollution control boards can apply for funding.",
            "how_to_apply": "State governments submit city-specific action plans to MoEFCC for approval and funding.",
            "official_url": "https://moef.gov.in/ncap"
        },
        {
            "name": "Swachh Bharat Mission - Urban 2.0",
            "state": "National",
            "category": "Waste Management",
            "summary": "Focus on complete sanitation, waste management, and making cities garbage-free through source segregation and scientific processing.",
            "eligibility": "Urban local bodies, community groups, and waste management service providers.",
            "how_to_apply": "Contact your municipal corporation or urban local body for participation in waste segregation programs.",
            "official_url": "https://swachhbharaturban.gov.in"
        },
        {
            "name": "Maharashtra Solar Rooftop Subsidy",
            "state": "Maharashtra",
            "category": "Solar Energy",
            "summary": "30-40% subsidy on solar rooftop installation for residential consumers in Maharashtra.",
            "eligibility": "Residential electricity consumers in Maharashtra with their own rooftop space.",
            "how_to_apply": "Apply online through MSEDCL portal or registered solar vendors. Subsidy is credited after installation and inspection.",
            "official_url": "https://www.mahadiscom.in/solar"
        },
        {
            "name": "Delhi Electric Vehicle Policy",
            "state": "Delhi",
            "category": "Electric Vehicles",
            "summary": "Purchase incentives up to ₹1.5 lakh for electric cars and ₹30,000 for e-scooters, plus road tax exemption.",
            "eligibility": "Delhi residents purchasing new electric vehicles registered in Delhi.",
            "how_to_apply": "Incentive is processed through dealership at time of purchase. Upload documents on Delhi EV portal for reimbursement.",
            "official_url": "https://ev.delhi.gov.in"
        },
        {
            "name": "Karnataka Solar Water Pump Scheme",
            "state": "Karnataka",
            "category": "Solar Energy",
            "summary": "90% subsidy for small and marginal farmers for installation of solar water pumps up to 5 HP.",
            "eligibility": "Small and marginal farmers in Karnataka with agricultural land and electricity connection.",
            "how_to_apply": "Apply through Karnataka Renewable Energy Development Limited (KREDL) or agriculture department offices.",
            "official_url": "https://kredl.karnataka.gov.in"
        },
        {
            "name": "Tamil Nadu Green Building Incentive",
            "state": "Tamil Nadu",
            "category": "Green Building",
            "summary": "Rebates on property tax and fast-track approvals for buildings certified under green building standards.",
            "eligibility": "Builders and property owners constructing new buildings or renovating existing ones in Tamil Nadu.",
            "how_to_apply": "Submit green building certification along with building plan approval to respective municipal corporation.",
            "official_url": "https://www.tn.gov.in/green-building"
        }
    ]
    
    for scheme_data in schemes_data:
        scheme = GovernmentScheme(**scheme_data)
        db.add(scheme)
    
    db.commit()
    print(f"✅ Added {len(schemes_data)} government schemes")
    
    # Also add schemes to vector store
    print("🔄 Adding schemes to vector store...")
    for scheme_data in schemes_data:
        try:
            add_scheme_to_vector_store(scheme_data)
        except Exception as e:
            print(f"⚠️ Warning: Could not add scheme to vector store: {e}")


def init_vector_store():
    """Initialize ChromaDB vector store"""
    print("🧠 Initializing vector store...")
    try:
        initialize_vector_store(force_reload=True)
        print("✅ Vector store initialized")
    except Exception as e:
        print(f"⚠️ Warning: Vector store initialization failed: {e}")
        print("   Make sure knowledge base files exist in the data/ directory")


def main():
    """Main initialization function"""
    print("=" * 60)
    print("EcoMitra Database Initialization")
    print("=" * 60)
    
    # Create tables
    create_tables()
    
    # Get database session
    db = SessionLocal()
    
    try:
        # Check if already seeded
        existing_ngos = db.query(NGO).count()
        existing_schemes = db.query(GovernmentScheme).count()
        existing_users = db.query(User).count()
        
        if existing_ngos > 0 or existing_schemes > 0:
            print(f"\n⚠️ Database already contains data:")
            print(f"   - NGOs: {existing_ngos}")
            print(f"   - Schemes: {existing_schemes}")
            print(f"   - Users: {existing_users}")
            response = input("\nDo you want to reset and reseed? (yes/no): ")
            
            if response.lower() in ['yes', 'y']:
                print("\n🔄 Clearing existing data...")
                db.query(NGO).delete()
                db.query(GovernmentScheme).delete()
                db.query(User).delete()
                db.commit()
            else:
                print("\n✅ Keeping existing data")
                db.close()
                
                # Still initialize vector store
                init_vector_store()
                
                print("\n" + "=" * 60)
                print("✅ Initialization complete!")
                print("=" * 60)
                return
        
        # Seed data
        seed_ngos(db)
        seed_schemes(db)
        seed_users(db)
        
    finally:
        db.close()
    
    # Initialize vector store
    init_vector_store()
    
    print("\n" + "=" * 60)
    print("✅ Initialization complete!")
    print("=" * 60)
    print("\n📝 Next steps:")
    print("   1. Make sure .env file has your GOOGLE_API_KEY")
    print("   2. Run: uvicorn backend.main:app --reload")
    print("   3. Open: http://localhost:8000/")
    print("\n")


if __name__ == "__main__":
    main()
