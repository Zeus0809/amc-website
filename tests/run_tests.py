"""
Test Runner for AMC Website
Runs all test suites and provides summary
"""
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run_all_tests():
    """Run all test suites"""
    print('🧪 AMC Website - Complete Test Suite\n')
    print('=' * 70)
    
    # Import test modules
    from test_basic_entities import run_all_tests as run_basic_tests
    from test_admin_approval import run_approval_tests
    
    test_suites = [
        ('Basic Entity Tests', run_basic_tests),
        ('Admin Approval Tests', run_approval_tests)
    ]
    
    suite_results = []
    
    for suite_name, test_function in test_suites:
        print(f'\n🏃 Running {suite_name}...')
        print('=' * 70)
        
        try:
            result = test_function()
            suite_results.append((suite_name, result))
        except Exception as e:
            print(f'❌ {suite_name} failed with exception: {e}')
            suite_results.append((suite_name, False))
        
        print('\n' + '=' * 70)
    
    # Final summary
    print('\n🎯 FINAL TEST SUMMARY')
    print('=' * 70)
    
    passed_suites = 0
    failed_suites = 0
    
    for suite_name, passed in suite_results:
        if passed:
            print(f'✅ {suite_name}: PASSED')
            passed_suites += 1
        else:
            print(f'❌ {suite_name}: FAILED')
            failed_suites += 1
    
    print(f'\n📊 Suite Results: {passed_suites} passed, {failed_suites} failed')
    
    if failed_suites == 0:
        print('\n🎉 ALL TEST SUITES PASSED!')
        print('✅ Chunk 1B: Database Models - FULLY VALIDATED')
        print('🚀 Ready to proceed to Chunk 2A: Authentication System')
        return True
    else:
        print('\n❌ SOME TEST SUITES FAILED!')
        print('🔧 Please review and fix failing tests before proceeding')
        return False

if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
