"""
Test Language Service
"""
from services.language_service import language_service

print("=" * 60)
print("TESTING LANGUAGE DETECTION SERVICE")
print("=" * 60)

# Test 1: Language detection
print("\n1️⃣  Testing language detection...")
test_texts = {
    'Questo è un testo in italiano sulla politica italiana': 'it',
    'This is an English text about technology': 'en',
    'Das ist ein deutscher Text über Wirtschaft': 'de',
    'C\'est un texte français sur la culture': 'fr'
}

for text, expected in test_texts.items():
    detected = language_service.detect_language(text)
    status = "✅" if detected == expected else "❌"
    print(f"{status} '{text[:40]}...' => {detected} (expected: {expected})")

# Test 2: Country detection
print("\n2️⃣  Testing country detection...")
test_cases = [
    {
        'title': 'Breaking news from Washington DC',
        'text': 'President announces new policy in America',
        'expected': 'USA'
    },
    {
        'title': 'Governo italiano approva riforma',
        'text': 'A Roma si discute della nuova legge italiana',
        'expected': 'ITA'
    },
    {
        'title': 'Tech startup raises funds',
        'text': 'Silicon Valley company secures investment',
        'expected': 'USA'
    }
]

for case in test_cases:
    detected = language_service.detect_country(
        case['text'], 
        case['title']
    )
    status = "✅" if detected == case['expected'] else "⚠️"
    print(f"{status} '{case['title']}' => {detected} (expected: {case['expected']})")

# Test 3: Entity extraction
print("\n3️⃣  Testing entity extraction...")
entity_text = """
Breaking News from New York City: Apple Inc and Microsoft Corporation 
announced a partnership. The White House confirmed the deal.
"""

entities = language_service.extract_entities(entity_text)
print(f"Locations: {entities['locations']}")
print(f"Organizations: {entities['organizations']}")

# Test 4: Full article enrichment
print("\n4️⃣  Testing full article enrichment...")
article = {
    'title': 'Amazon expands in Europe',
    'content': 'Amazon announced new offices in London and Paris. The company plans to hire 5000 employees across European markets.',
    'source': 'test'
}

enriched = language_service.enrich_article(article.copy())
print(f"Language: {enriched.get('language')}")
print(f"Country: {enriched.get('country')}")
print(f"Entities: {enriched.get('entities')}")

print("\n" + "=" * 60)
print("✅ LANGUAGE SERVICE TESTS COMPLETED")
print("=" * 60)
