from typing import List, Dict, Optional, Tuple
from datetime import datetime
import difflib
import logging

logger = logging.getLogger(__name__)


def is_duplicate(posting1: Dict, posting2: Dict, threshold: float = 0.85) -> bool:
    """
    Check if two job postings are duplicates using fuzzy matching.
    
    Uses token-set ratio to compare:
        - Title
        - Company
        - Location
    
    Args:
        posting1: First posting dict with title, company, location
        posting2: Second posting dict
        threshold: Similarity threshold (0.0-1.0), default 0.85
    
    Returns:
        True if likely duplicate
    """
    try:
        # Compare title
        title1 = (posting1.get('title') or '').lower().strip()
        title2 = (posting2.get('title') or '').lower().strip()
        title_similarity = difflib.SequenceMatcher(None, title1, title2).ratio()
        
        # Compare company
        company1 = (posting1.get('company') or '').lower().strip()
        company2 = (posting2.get('company') or '').lower().strip()
        company_similarity = difflib.SequenceMatcher(None, company1, company2).ratio()
        
        # Compare location (more lenient)
        location1 = (posting1.get('location') or '').lower().strip()
        location2 = (posting2.get('location') or '').lower().strip()
        location_similarity = difflib.SequenceMatcher(None, location1, location2).ratio()
        
        # Weighted score: title and company are most important
        score = (
            title_similarity * 0.5 +
            company_similarity * 0.4 +
            location_similarity * 0.1
        )
        
        is_dup = score >= threshold
        
        if is_dup:
            logger.debug(f"Duplicate detected: '{title1}' at '{company1}' "
                        f"(score={score:.2f})")
        
        return is_dup
        
    except Exception as e:
        logger.error(f"Error checking duplicate: {e}")
        return False


def token_set_similarity(text1: str, text2: str) -> float:
    """
    Token-set ratio: compare unique words (order-independent).
    More robust than simple sequence matching.
    
    Returns:
        Similarity score 0.0-1.0
    """
    if not text1 or not text2:
        return 0.0
    
    # Tokenize and get unique words
    tokens1 = set(text1.lower().split())
    tokens2 = set(text2.lower().split())
    
    # Calculate Jaccard similarity
    intersection = tokens1 & tokens2
    union = tokens1 | tokens2
    
    if not union:
        return 0.0
    
    return len(intersection) / len(union)


def find_duplicates_in_batch(
    new_posting: Dict,
    existing_postings: List[Dict],
    threshold: float = 0.85
) -> List[Tuple[Dict, float]]:
    """
    Find all duplicates of new_posting in existing batch.
    
    Args:
        new_posting: Posting to check
        existing_postings: List of existing postings
        threshold: Similarity threshold
    
    Returns:
        List of (posting, score) tuples for duplicates
    """
    duplicates = []
    
    for existing in existing_postings:
        # First check fingerprints (fast exact match)
        if new_posting.get('fingerprint') == existing.get('fingerprint'):
            duplicates.append((existing, 1.0))
            continue
        
        # Fuzzy match
        if is_duplicate(new_posting, existing, threshold):
            # Calculate actual score for ranking
            title_sim = token_set_similarity(
                new_posting.get('title', ''),
                existing.get('title', '')
            )
            company_sim = token_set_similarity(
                new_posting.get('company', ''),
                existing.get('company', '')
            )
            score = (title_sim * 0.6 + company_sim * 0.4)
            duplicates.append((existing, score))
    
    # Sort by score descending
    duplicates.sort(key=lambda x: x[1], reverse=True)
    
    return duplicates


def merge_postings(primary: Dict, secondary: Dict) -> Dict:
    """
    Merge two duplicate postings, taking best data from each.
    
    Strategy:
        - Use primary as base
        - Merge source_references
        - Take longest description
        - Take best salary data
        - Union of skills
    
    Args:
        primary: Primary posting (usually existing)
        secondary: Secondary posting (usually new)
    
    Returns:
        Merged posting dict
    """
    merged = primary.copy()
    
    # Merge source references
    primary_refs = primary.get('source_references', [])
    secondary_refs = secondary.get('source_references', [])
    
    if isinstance(primary_refs, str):
        import json
        primary_refs = json.loads(primary_refs) if primary_refs else []
    if isinstance(secondary_refs, str):
        import json
        secondary_refs = json.loads(secondary_refs) if secondary_refs else []
    
    merged_refs = primary_refs + [
        ref for ref in secondary_refs
        if ref not in primary_refs
    ]
    merged['source_references'] = merged_refs
    
    # Take longest description
    if secondary.get('description') and (
        not primary.get('description') or
        len(secondary['description']) > len(primary.get('description', ''))
    ):
        merged['description'] = secondary['description']
    
    # Take best salary (highest max)
    if secondary.get('salary_max_cents'):
        if not primary.get('salary_max_cents') or \
           secondary['salary_max_cents'] > primary['salary_max_cents']:
            merged['salary_min_cents'] = secondary.get('salary_min_cents')
            merged['salary_max_cents'] = secondary['salary_max_cents']
            merged['salary_currency'] = secondary.get('salary_currency', 'USD')
    
    # Union of skills
    primary_skills = set(primary.get('skills', []) or [])
    secondary_skills = set(secondary.get('skills', []) or [])
    merged['skills'] = list(primary_skills | secondary_skills)
    
    # Update timestamps
    merged['updated_at'] = datetime.utcnow()
    merged['last_seen_at'] = datetime.utcnow()
    
    return merged


def deduplicate_batch(postings: List[Dict], threshold: float = 0.85) -> List[Dict]:
    """
    Deduplicate a batch of postings in-memory.
    
    Args:
        postings: List of posting dicts
        threshold: Similarity threshold
    
    Returns:
        Deduplicated list of postings
    """
    if not postings:
        return []
    
    unique_postings = []
    fingerprints_seen = set()
    
    for posting in postings:
        fingerprint = posting.get('fingerprint')
        
        # Check exact fingerprint match first
        if fingerprint and fingerprint in fingerprints_seen:
            logger.debug(f"Skipping duplicate by fingerprint: {posting.get('title')}")
            continue
        
        # Check fuzzy duplicates
        duplicates = find_duplicates_in_batch(posting, unique_postings, threshold)
        
        if duplicates:
            # Merge with best match
            best_match, score = duplicates[0]
            logger.info(f"Merging duplicate: '{posting.get('title')}' with "
                       f"'{best_match.get('title')}' (score={score:.2f})")
            
            # Update the existing posting in place
            merged = merge_postings(best_match, posting)
            # Replace in list
            idx = unique_postings.index(best_match)
            unique_postings[idx] = merged
        else:
            # No duplicate found - add as new
            unique_postings.append(posting)
            if fingerprint:
                fingerprints_seen.add(fingerprint)
    
    logger.info(f"Deduplicated {len(postings)} -> {len(unique_postings)} postings")
    
    return unique_postings


def calculate_similarity_score(posting1: Dict, posting2: Dict) -> float:
    """
    Calculate detailed similarity score between two postings.
    
    Returns:
        Score 0.0-1.0
    """
    title_sim = token_set_similarity(
        posting1.get('title', ''),
        posting2.get('title', '')
    )
    
    company_sim = token_set_similarity(
        posting1.get('company', ''),
        posting2.get('company', '')
    )
    
    location_sim = token_set_similarity(
        posting1.get('location', ''),
        posting2.get('location', '')
    )
    
    # Weighted score
    score = (
        title_sim * 0.5 +
        company_sim * 0.35 +
        location_sim * 0.15
    )
    
    return score
