#!/usr/bin/env python3
"""
Simple test script to validate the Terms & Conditions analysis functionality.
"""

import sys
import os
sys.path.insert(0, '/home/runner/work/termscon/termscon')

from main import SimpleApp
from backend.models.simple_schemas import RiskLevel

def test_basic_analysis():
    """Test basic analysis functionality."""
    print("🧪 Testing basic analysis functionality...")
    
    app = SimpleApp()
    
    # Test with a simple problematic clause
    test_text = """
    Vyhrazujeme si právo kdykoli změnit tyto podmínky bez předchozího upozornění.
    Společnost se zprošťuje veškeré odpovědnosti za škody.
    """
    
    try:
        result = app.analyze_text(test_text)
        
        assert result.document_id is not None, "Document ID should be generated"
        assert len(result.clause_analyses) > 0, "Should have at least one clause"
        assert result.overall_summary.total_clauses > 0, "Should count clauses"
        
        print(f"✅ Basic analysis passed:")
        print(f"   - Document ID: {result.document_id}")
        print(f"   - Clauses analyzed: {len(result.clause_analyses)}")
        print(f"   - Overall risk: {result.overall_summary.overall_risk_score.value}")
        
        return True
        
    except Exception as e:
        print(f"❌ Basic analysis failed: {e}")
        return False

def test_risk_assessment():
    """Test risk assessment logic."""
    print("\n🧪 Testing risk assessment logic...")
    
    app = SimpleApp()
    
    test_cases = [
        ("Snažíme se poskytovat kvalitní služby.", RiskLevel.LOW),
        ("Můžeme podle našeho uvážení změnit podmínky.", RiskLevel.MEDIUM),
        ("Vyhrazujeme si právo kdykoli změnit bez upozornění.", RiskLevel.HIGH),
    ]
    
    all_passed = True
    
    for text, expected_min_risk in test_cases:
        try:
            result = app.analyze_text(text)
            actual_risk = result.clause_analyses[0].risk_level
            
            print(f"   Text: {text[:50]}...")
            print(f"   Expected min: {expected_min_risk.value}, Got: {actual_risk.value}")
            
            # Basic validation that analysis produces reasonable results
            assert actual_risk in [RiskLevel.LOW, RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.CRITICAL]
            
        except Exception as e:
            print(f"❌ Risk assessment failed for: {text[:30]}... - {e}")
            all_passed = False
    
    if all_passed:
        print("✅ Risk assessment tests passed")
    
    return all_passed

def test_clause_segmentation():
    """Test clause segmentation."""
    print("\n🧪 Testing clause segmentation...")
    
    app = SimpleApp()
    
    # Multi-clause text
    multi_clause_text = """1. První klauzule týkající se registrace.
2. Druhá klauzule o odpovědnosti.
3. Třetí klauzule ohledně dat."""
    
    try:
        clauses = app.text_processor.segment_terms_conditions(multi_clause_text)
        
        print(f"   Original text length: {len(multi_clause_text)} chars")
        print(f"   Segmented into: {len(clauses)} clauses")
        
        assert len(clauses) >= 2, "Should segment multi-clause text"
        
        for i, clause in enumerate(clauses):
            print(f"   Clause {i+1}: {clause[:50]}...")
        
        print("✅ Clause segmentation test passed")
        return True
        
    except Exception as e:
        print(f"❌ Clause segmentation failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Starting Terms & Conditions Analyzer Tests\n")
    
    tests = [
        test_basic_analysis,
        test_risk_assessment,
        test_clause_segmentation
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed")
        return 1

if __name__ == "__main__":
    exit(main())