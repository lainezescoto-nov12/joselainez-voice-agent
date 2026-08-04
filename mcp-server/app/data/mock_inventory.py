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
]
