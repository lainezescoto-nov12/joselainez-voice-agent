"""Static demo data for check_vehicle_status and dealership_faq_lookup.

Stand-ins for what would be a DMS/inventory API integration and a real
vector-indexed KB, respectively — out of scope for the v2 single-tenant
build. Swappable behind the same function signatures later.
"""

VEHICLES_BY_VIN = {
    "1HGCM82633A004352": {
        "vin": "1HGCM82633A004352",
        "year": 2023,
        "make": "Honda",
        "model": "Accord",
        "status": "in_service",
        "service_notes": "Awaiting brake pad replacement, part on backorder until Thu.",
        "open_recall": False,
    },
    "5YJ3E1EA7KF317000": {
        "vin": "5YJ3E1EA7KF317000",
        "year": 2022,
        "make": "Tesla",
        "model": "Model 3",
        "status": "ready_for_pickup",
        "service_notes": "Software update + tire rotation complete.",
        "open_recall": False,
    },
    "1FTFW1ET1EFA00001": {
        "vin": "1FTFW1ET1EFA00001",
        "year": 2021,
        "make": "Ford",
        "model": "F-150",
        "status": "in_service",
        "service_notes": "Diagnosing check-engine light.",
        "open_recall": True,
        "recall_description": "Fuel pump recall NHTSA #21V-912 — replacement covered under warranty.",
    },
    "5NPE24AF9FH000001": {
        "vin": "5NPE24AF9FH000001",
        "year": 2019,
        "make": "Hyundai",
        "model": "Sonata",
        "status": "ready_for_pickup",
        "service_notes": "Oil change and multi-point inspection complete.",
        "open_recall": False,
    },
    "KM8J3CA46LU000001": {
        "vin": "KM8J3CA46LU000001",
        "year": 2020,
        "make": "Hyundai",
        "model": "Tucson",
        "status": "in_service",
        "service_notes": "Replacing rear brake pads and rotors.",
        "open_recall": True,
        "recall_description": "Theta II engine recall NHTSA #20V-473 — inspection and possible engine replacement covered under warranty.",
    },
    "4T1BF1FK5HU000001": {
        "vin": "4T1BF1FK5HU000001",
        "year": 2017,
        "make": "Toyota",
        "model": "Camry",
        "status": "ready_for_pickup",
        "service_notes": "Brake pad replacement complete, four-wheel alignment performed.",
        "open_recall": False,
    },
    "5TFEY5F1XLX000001": {
        "vin": "5TFEY5F1XLX000001",
        "year": 2020,
        "make": "Toyota",
        "model": "Tundra",
        "status": "in_service",
        "service_notes": "Awaiting parts for a scheduled 30,000-mile service.",
        "open_recall": False,
    },
}

FAQ_KB = [
    {
        "question": "What are your service department hours?",
        "answer": "Service is open Monday through Saturday, 9am to 6pm. Closed Sundays.",
    },
    {
        "question": "Do you offer loaner vehicles during service?",
        "answer": "Loaners are available for repairs expected to take more than a day, subject to availability. Ask your service advisor to reserve one.",
    },
    {
        "question": "What's included in a trade-in appraisal?",
        "answer": "A trade-in appraisal covers a vehicle history check, a mechanical inspection, and a market-comparable valuation. It takes about 20 minutes on-site.",
    },
    {
        "question": "Can I finance a used vehicle?",
        "answer": "Yes, we offer financing on all certified pre-owned and used inventory through our lending partners.",
    },
    {
        "question": "How do I check if my vehicle has an open recall?",
        "answer": "Ask for a vehicle status check with your VIN, or look it up at nhtsa.gov/recalls.",
    },
    {
        "question": "What brands do you sell and service?",
        "answer": "We're a Hyundai and Toyota dealership — sales, service, and parts for both brands. We can also service other makes, but factory parts and warranty work are strongest for Hyundai and Toyota.",
    },
    {
        "question": "What's your address and how do I get there?",
        "answer": "We're happy to text or email you directions — ask your service advisor or sales rep for the exact address when you call.",
    },
    {
        "question": "Do you buy cars even if I'm not trading one in?",
        "answer": "Yes, we buy vehicles outright, no trade-in or purchase required. Ask for a trade-in appraisal to get a ballpark value.",
    },
    {
        "question": "What payment methods do you accept for service?",
        "answer": "We accept all major credit cards, debit, and financing through our lending partners for larger repairs.",
    },
]
