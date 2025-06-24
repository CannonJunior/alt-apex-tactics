#!/usr/bin/env python3
"""
Comprehensive Test Runner for Phase 1 Foundation

Runs all tests in proper order: unit → integration → performance → demo
Provides comprehensive validation of Phase 1 implementation.
"""

import sys
import os
import subprocess
import time
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))


class TestRunner:
    """Comprehensive test runner for Phase 1 systems"""
    
    def __init__(self, verbose: bool = False, stop_on_failure: bool = False):
        self.verbose = verbose
        self.stop_on_failure = stop_on_failure
        self.results = {}
        self.start_time = time.time()
        
        # Test categories and their files
        self.test_categories = {
            'unit': [
                'tests/unit/test_ecs_core.py',
                'tests/unit/test_stat_system.py',
                'tests/unit/test_grid_pathfinding.py'
            ],
            'integration': [
                'tests/integration/test_full_system.py'
            ],
            'mcp': [
                'tests/mcp/test_tactical_server.py'
            ],
            'performance': [
                'tests/performance/performance_suite.py'
            ],
            'functional': [
                'tests/functional/demo_phase1.py'
            ]
        }
    
    def print_header(self, title: str):
        """Print formatted header"""
        print("\n" + "="*60)
        print(f" {title}")
        print("="*60)
    
    def print_section(self, title: str):
        """Print formatted section header"""
        print(f"\n{'-'*40}")
        print(f" {title}")
        print(f"{'-'*40}")
    
    def run_pytest_tests(self, test_files: list, category: str) -> bool:
        """Run pytest on specified test files"""
        self.print_section(f"Running {category.upper()} Tests")
        
        all_passed = True
        category_results = []
        
        for test_file in test_files:
            if not os.path.exists(test_file):
                print(f"⚠️  Test file not found: {test_file}")
                continue
            
            print(f"\n📁 {test_file}")
            
            # Run pytest with appropriate flags
            cmd = [
                sys.executable, '-m', 'pytest',
                test_file,
                '-v' if self.verbose else '-q',
                '--tb=short',
                '--no-header'
            ]
            
            try:
                start_time = time.time()
                result = subprocess.run(cmd, capture_output=True, text=True, cwd='.')
                elapsed = time.time() - start_time
                
                if result.returncode == 0:
                    print(f"✅ PASSED ({elapsed:.2f}s)")
                    if self.verbose and result.stdout:
                        print(result.stdout)
                else:
                    print(f"❌ FAILED ({elapsed:.2f}s)")
                    print(result.stdout)
                    if result.stderr:
                        print("STDERR:", result.stderr)
                    all_passed = False
                
                category_results.append({
                    'file': test_file,
                    'passed': result.returncode == 0,
                    'time': elapsed,
                    'output': result.stdout,
                    'errors': result.stderr
                })
                
                if not all_passed and self.stop_on_failure:
                    break
                    
            except Exception as e:
                print(f"❌ ERROR running {test_file}: {e}")
                all_passed = False
                category_results.append({
                    'file': test_file,
                    'passed': False,
                    'time': 0,
                    'output': '',
                    'errors': str(e)
                })
        
        self.results[category] = {
            'passed': all_passed,
            'results': category_results,
            'total_files': len(test_files),
            'passed_files': sum(1 for r in category_results if r['passed'])
        }
        
        # Print category summary
        passed_count = self.results[category]['passed_files']
        total_count = self.results[category]['total_files']
        status = "✅ PASSED" if all_passed else "❌ FAILED"
        print(f"\n{category.upper()} Tests: {status} ({passed_count}/{total_count})")
        
        return all_passed
    
    def run_performance_suite(self) -> bool:
        """Run the performance validation suite"""
        self.print_section("Performance Validation")
        
        try:
            # Import and run performance suite
            sys.path.insert(0, 'tests/performance')
            from performance_suite import run_performance_suite
            
            print("🔄 Running comprehensive performance validation...")
            start_time = time.time()
            results = run_performance_suite()
            elapsed = time.time() - start_time
            
            passed = results['summary']['overall_pass']
            status = "✅ PASSED" if passed else "❌ FAILED"
            
            print(f"\nPerformance Validation: {status} ({elapsed:.2f}s)")
            
            if not passed:
                print("❌ Performance targets not met:")
                for test in results['summary']['failed_tests']:
                    print(f"   • {test}")
            
            self.results['performance'] = {
                'passed': passed,
                'time': elapsed,
                'details': results
            }
            
            return passed
            
        except Exception as e:
            print(f"❌ ERROR running performance suite: {e}")
            self.results['performance'] = {'passed': False, 'error': str(e)}
            return False
    
    def run_functional_demo(self) -> bool:
        """Run the functional demonstration"""
        self.print_section("Functional Demonstration")
        
        try:
            print("🎮 Running Phase 1 functional demonstration...")
            print("   (Demo will run in console mode for automated testing)")
            
            # Run demo in non-interactive mode
            cmd = [sys.executable, 'tests/functional/demo_phase1.py']
            
            # Set environment to disable interactive features
            env = os.environ.copy()
            env['DEMO_NON_INTERACTIVE'] = '1'
            
            start_time = time.time()
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=30,  # 30 second timeout
                env=env
            )
            elapsed = time.time() - start_time
            
            passed = result.returncode == 0
            status = "✅ PASSED" if passed else "❌ FAILED"
            
            print(f"Functional Demo: {status} ({elapsed:.2f}s)")
            
            if self.verbose or not passed:
                if result.stdout:
                    print("STDOUT:", result.stdout[-500:])  # Last 500 chars
                if result.stderr:
                    print("STDERR:", result.stderr[-500:])
            
            self.results['functional'] = {
                'passed': passed,
                'time': elapsed,
                'output': result.stdout,
                'errors': result.stderr
            }
            
            return passed
            
        except subprocess.TimeoutExpired:
            print("❌ TIMEOUT: Demo took too long to complete")
            self.results['functional'] = {'passed': False, 'error': 'Timeout'}
            return False
        except Exception as e:
            print(f"❌ ERROR running functional demo: {e}")
            self.results['functional'] = {'passed': False, 'error': str(e)}
            return False
    
    def generate_test_report(self):
        """Generate comprehensive test report"""
        self.print_header("PHASE 1 FOUNDATION TEST REPORT")
        
        total_time = time.time() - self.start_time
        
        # Summary statistics
        total_categories = len(self.results)
        passed_categories = sum(1 for r in self.results.values() if r.get('passed', False))
        
        print(f"Test Execution Time: {total_time:.2f}s")
        print(f"Categories Tested: {total_categories}")
        print(f"Categories Passed: {passed_categories}")
        
        # Detailed results
        for category, results in self.results.items():
            print(f"\n📊 {category.upper()} Results:")
            
            if 'total_files' in results:
                # Test file category
                print(f"   Files: {results['passed_files']}/{results['total_files']} passed")
                
                for test_result in results['results']:
                    status = "✅" if test_result['passed'] else "❌"
                    print(f"   {status} {test_result['file']} ({test_result['time']:.2f}s)")
            else:
                # Special category (performance, functional)
                status = "✅ PASSED" if results['passed'] else "❌ FAILED"
                time_info = f" ({results.get('time', 0):.2f}s)" if 'time' in results else ""
                print(f"   {status}{time_info}")
                
                if not results['passed'] and 'error' in results:
                    print(f"   Error: {results['error']}")
        
        # Overall result
        overall_passed = all(r.get('passed', False) for r in self.results.values())
        overall_status = "🎉 ALL TESTS PASSED" if overall_passed else "⚠️  SOME TESTS FAILED"
        
        print(f"\n{'-'*60}")
        print(f"OVERALL RESULT: {overall_status}")
        print(f"{'-'*60}")
        
        if overall_passed:
            print("\n✅ Phase 1 foundation is ready for Phase 2 development!")
        else:
            print("\n❌ Phase 1 foundation requires fixes before Phase 2.")
            print("   Review failed tests and address issues.")
        
        return overall_passed
    
    def run_all_tests(self) -> bool:
        """Run complete test suite"""
        self.print_header("PHASE 1 FOUNDATION - COMPREHENSIVE TEST SUITE")
        
        print("🚀 Starting comprehensive validation of Phase 1 systems...")
        print("📋 Test Plan: Unit → Integration → MCP → Performance → Functional")
        
        overall_success = True
        
        # Run test categories in order
        test_order = ['unit', 'integration', 'mcp']
        
        for category in test_order:
            if category in self.test_categories:
                success = self.run_pytest_tests(self.test_categories[category], category)
                if not success:
                    overall_success = False
                    if self.stop_on_failure:
                        print(f"\n❌ Stopping due to {category} test failures")
                        break
        
        # Run performance validation
        if overall_success or not self.stop_on_failure:
            performance_success = self.run_performance_suite()
            if not performance_success:
                overall_success = False
        
        # Run functional demonstration
        if overall_success or not self.stop_on_failure:
            functional_success = self.run_functional_demo()
            if not functional_success:
                overall_success = False
        
        # Generate final report
        self.generate_test_report()
        
        return overall_success


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Run Phase 1 Foundation Test Suite')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Verbose output with detailed test results')
    parser.add_argument('-f', '--fail-fast', action='store_true',
                       help='Stop on first test failure')
    parser.add_argument('--category', choices=['unit', 'integration', 'mcp', 'performance', 'functional'],
                       help='Run only specified test category')
    
    args = parser.parse_args()
    
    runner = TestRunner(verbose=args.verbose, stop_on_failure=args.fail_fast)
    
    if args.category:
        # Run specific category
        if args.category == 'performance':
            success = runner.run_performance_suite()
        elif args.category == 'functional':
            success = runner.run_functional_demo()
        else:
            success = runner.run_pytest_tests(runner.test_categories[args.category], args.category)
    else:
        # Run all tests
        success = runner.run_all_tests()
    
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())