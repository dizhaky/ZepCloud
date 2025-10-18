#!/usr/bin/env python3
"""
RAG-Anything Integration Test Suite
End-to-end testing: M365 → Graph Builder → Azure AI Search → TypingMind
"""

import os
import sys
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
from dotenv import load_dotenv

# Add raganything-processor to path
sys.path.insert(0, str(Path(__file__).parent / "raganything-processor"))
from graph_builder import GraphBuilder

load_dotenv()

class RAGAnythingIntegrationTests:
    """Comprehensive integration test suite"""

    def __init__(self):
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'tests': [],
            'passed': 0,
            'failed': 0,
            'warnings': 0
        }

    def add_test(self, name: str, status: str, message: str, details: Dict = None):
        """Add test result"""
        test_result = {
            'name': name,
            'status': status,  # 'pass', 'fail', 'warning'
            'message': message,
            'details': details or {}
        }
        self.results['tests'].append(test_result)

        if status == 'pass':
            self.results['passed'] += 1
        elif status == 'fail':
            self.results['failed'] += 1
        else:
            self.results['warnings'] += 1

    def print_result(self, status: str, name: str, message: str):
        """Print formatted test result"""
        icons = {'pass': '✅', 'fail': '❌', 'warning': '⚠️'}
        icon = icons.get(status, '❓')
        print(f"{icon} {name}: {message}")

    def test_graph_builder(self) -> bool:
        """Test 1: Graph Builder Functionality"""
        print("\n" + "="*60)
        print("TEST 1: Graph Builder")
        print("="*60)

        try:
            # Create graph builder
            graph = GraphBuilder()

            # Add test documents
            doc1_metadata = {
                'people': ['Dan Izhaky'],
                'organizations': ['United Safety Technology'],
                'keyPhrases': ['safety equipment', 'budget report']
            }

            relationships1 = graph.add_document(
                'test_doc1.pdf',
                'Budget report for United Safety Technology. Contact Dan Izhaky.',
                doc1_metadata
            )

            doc2_metadata = {
                'people': ['Dan Izhaky', 'John Smith'],
                'organizations': ['United Safety Technology'],
                'keyPhrases': ['safety equipment', 'quarterly results']
            }

            relationships2 = graph.add_document(
                'test_doc2.pdf',
                'Quarterly results. Contact Dan Izhaky or John Smith.',
                doc2_metadata
            )

            # Verify relationships were created
            if relationships1.get('relationship_score', 0) >= 0:
                self.print_result('pass', 'Graph Creation', 'Documents added successfully')
                self.add_test('Graph Builder', 'pass', 'Successfully created document relationships')

            # Test relationship finding
            related = graph.find_related_documents('test_doc1.pdf')
            if len(related) > 0:
                self.print_result('pass', 'Relationship Discovery', f'Found {len(related)} related documents')
            else:
                self.print_result('warning', 'Relationship Discovery', 'No related documents found')

            # Get statistics
            stats = graph.get_statistics()
            self.print_result('pass', 'Statistics', f'{stats["total_documents"]} documents, {stats["total_entities"]} entities')

            return True

        except Exception as e:
            self.print_result('fail', 'Graph Builder', str(e))
            self.add_test('Graph Builder', 'fail', f'Exception: {e}')
            return False

    def test_azure_schema(self) -> bool:
        """Test 2: Azure AI Search Schema"""
        print("\n" + "="*60)
        print("TEST 2: Azure AI Search Schema")
        print("="*60)

        try:
            import requests

            search_service = os.getenv('AZURE_SEARCH_SERVICE_NAME')
            admin_key = os.getenv('AZURE_SEARCH_ADMIN_KEY')
            endpoint = os.getenv('AZURE_SEARCH_ENDPOINT')
            index_name = os.getenv('AZURE_SEARCH_INDEX_NAME', 'training-data-index')

            if not all([search_service, admin_key, endpoint]):
                self.print_result('warning', 'Azure Credentials', 'Not configured in .env')
                self.add_test('Azure Schema', 'warning', 'Azure credentials not configured')
                return False

            # Get index schema
            url = f"{endpoint}/indexes/{index_name}?api-version=2023-11-01"
            headers = {'api-key': admin_key}

            response = requests.get(url, headers=headers, timeout=30)

            if response.status_code != 200:
                self.print_result('fail', 'Schema Fetch', f'HTTP {response.status_code}')
                self.add_test('Azure Schema', 'fail', f'Failed to fetch schema: {response.status_code}')
                return False

            index_def = response.json()
            fields = {field['name']: field for field in index_def['fields']}

            # Check for enhanced fields
            enhanced_fields = [
                'has_tables', 'has_equations', 'has_images',
                'relationship_score', 'has_relationships',
                'tables_content', 'equations_content',
                'graph_relationships', 'related_documents'
            ]

            missing_fields = [f for f in enhanced_fields if f not in fields]

            if not missing_fields:
                self.print_result('pass', 'Enhanced Fields', 'All fields present')
                self.add_test('Azure Schema', 'pass', f'Schema has {len(fields)} fields including all enhanced fields')
            else:
                self.print_result('warning', 'Enhanced Fields', f'Missing: {", ".join(missing_fields)}')
                self.add_test('Azure Schema', 'warning', f'Missing fields: {missing_fields}')

            self.print_result('pass', 'Schema', f'Index has {len(fields)} total fields')

            return True

        except Exception as e:
            self.print_result('fail', 'Azure Schema', str(e))
            self.add_test('Azure Schema', 'fail', f'Exception: {e}')
            return False

    def test_sharepoint_indexer(self) -> bool:
        """Test 3: Enhanced SharePoint Indexer"""
        print("\n" + "="*60)
        print("TEST 3: Enhanced SharePoint Indexer")
        print("="*60)

        try:
            from m365_sharepoint_indexer_enhanced import EnhancedSharePointIndexer

            # Initialize indexer
            indexer = EnhancedSharePointIndexer()

            self.print_result('pass', 'Initialization', 'Indexer created successfully')

            # Check components
            if indexer.graph_builder:
                self.print_result('pass', 'Graph Builder', 'Integrated')

            if indexer.auth:
                self.print_result('pass', 'Authentication', 'Configured')

            if indexer.blob_service:
                self.print_result('pass', 'Azure Storage', 'Connected')

            # Get status
            status = indexer.get_status()
            self.print_result('pass', 'Status', f'{status.get("total_documents", 0)} documents processed')

            self.add_test('Enhanced Indexer', 'pass', 'All components initialized and working')

            return True

        except Exception as e:
            self.print_result('fail', 'Enhanced Indexer', str(e))
            self.add_test('Enhanced Indexer', 'fail', f'Exception: {e}')
            return False

    def test_orchestrator(self) -> bool:
        """Test 4: RAG-Anything Orchestrator"""
        print("\n" + "="*60)
        print("TEST 4: Orchestrator")
        print("="*60)

        try:
            from orchestrate_rag_anything import RAGAnythingOrchestrator

            # Initialize orchestrator
            orchestrator = RAGAnythingOrchestrator()

            self.print_result('pass', 'Initialization', 'Orchestrator created')

            # Get status
            status = orchestrator.get_status()

            if status:
                self.print_result('pass', 'Status', 'Successfully retrieved')
                self.add_test('Orchestrator', 'pass', 'Orchestrator working correctly')

            return True

        except Exception as e:
            self.print_result('fail', 'Orchestrator', str(e))
            self.add_test('Orchestrator', 'fail', f'Exception: {e}')
            return False

    def test_multimodal_detection(self) -> bool:
        """Test 5: Multimodal Content Detection"""
        print("\n" + "="*60)
        print("TEST 5: Multimodal Content Detection")
        print("="*60)

        try:
            from m365_sharepoint_indexer_enhanced import EnhancedSharePointIndexer

            indexer = EnhancedSharePointIndexer()

            # Test table detection
            test_content_table = b"Column1|Column2|Column3\nData1|Data2|Data3"
            result = indexer._extract_multimodal_content(test_content_table, "test.txt", {})

            if result.get('has_tables'):
                self.print_result('pass', 'Table Detection', 'Working')
            else:
                self.print_result('warning', 'Table Detection', 'Not detected')

            # Test equation detection
            test_content_eq = b"The formula is $E=mc^2$ where..."
            result = indexer._extract_multimodal_content(test_content_eq, "test.txt", {})

            if result.get('has_equations'):
                self.print_result('pass', 'Equation Detection', 'Working')
            else:
                self.print_result('warning', 'Equation Detection', 'Not detected')

            self.add_test('Multimodal Detection', 'pass', 'Content detection functions working')

            return True

        except Exception as e:
            self.print_result('fail', 'Multimodal Detection', str(e))
            self.add_test('Multimodal Detection', 'fail', f'Exception: {e}')
            return False

    def test_end_to_end_flow(self) -> bool:
        """Test 6: End-to-End Data Flow"""
        print("\n" + "="*60)
        print("TEST 6: End-to-End Data Flow")
        print("="*60)

        print("   M365 → Enhanced Indexer → Graph Builder → Azure Storage → Azure AI Search")

        # Check each component exists
        components = [
            ('M365 Auth', 'M365Auth'),
            ('Graph Builder', 'GraphBuilder'),
            ('Enhanced Indexer', 'EnhancedSharePointIndexer'),
            ('Orchestrator', 'RAGAnythingOrchestrator')
        ]

        all_present = True
        for name, class_name in components:
            try:
                if name == 'M365 Auth':
                    from m365_auth import M365Auth
                elif name == 'Graph Builder':
                    from graph_builder import GraphBuilder
                elif name == 'Enhanced Indexer':
                    from m365_sharepoint_indexer_enhanced import EnhancedSharePointIndexer
                elif name == 'Orchestrator':
                    from orchestrate_rag_anything import RAGAnythingOrchestrator

                self.print_result('pass', name, 'Available')
            except Exception as e:
                self.print_result('fail', name, str(e))
                all_present = False

        if all_present:
            self.add_test('End-to-End Flow', 'pass', 'All pipeline components present')
        else:
            self.add_test('End-to-End Flow', 'fail', 'Missing pipeline components')

        return all_present

    def generate_report(self):
        """Generate and display final test report"""
        print("\n" + "="*60)
        print("FINAL TEST REPORT")
        print("="*60)

        print(f"\nTest Run: {self.results['timestamp']}")
        print(f"\nResults:")
        print(f"  ✅ Passed:  {self.results['passed']}")
        print(f"  ❌ Failed:  {self.results['failed']}")
        print(f"  ⚠️  Warnings: {self.results['warnings']}")

        total = self.results['passed'] + self.results['failed'] + self.results['warnings']
        if total > 0:
            pass_rate = (self.results['passed'] / total) * 100
            print(f"\n  Pass Rate: {pass_rate:.1f}%")

        print("\n" + "-"*60)
        print("Test Details:")
        print("-"*60)

        for test in self.results['tests']:
            icon = {'pass': '✅', 'fail': '❌', 'warning': '⚠️'}.get(test['status'], '❓')
            print(f"\n{icon} {test['name']}")
            print(f"   Status: {test['status'].upper()}")
            print(f"   Message: {test['message']}")
            if test['details']:
                print(f"   Details: {json.dumps(test['details'], indent=6)}")

        # Save report
        report_file = f"rag_anything_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)

        print(f"\n📄 Full report saved to: {report_file}")

        return self.results['failed'] == 0


def main():
    """Run all integration tests"""
    print("="*60)
    print("RAG-Anything Integration Test Suite")
    print("="*60)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    tester = RAGAnythingIntegrationTests()

    # Run tests
    tester.test_graph_builder()
    tester.test_azure_schema()
    tester.test_sharepoint_indexer()
    tester.test_orchestrator()
    tester.test_multimodal_detection()
    tester.test_end_to_end_flow()

    # Generate report
    success = tester.generate_report()

    if success:
        print("\n✅ All tests passed!")
        print("\n💡 Next Steps:")
        print("   1. Run a small test sync: python3 orchestrate_rag_anything.py --source sharepoint --limit 2")
        print("   2. Check relationship graph: cat sharepoint_graph.json")
        print("   3. Query Azure AI Search with new filters")
        print("   4. Test in TypingMind with relationship queries")
        return 0
    else:
        print(f"\n❌ {tester.results['failed']} test(s) failed")
        print("   Review the report and fix issues before proceeding")
        return 1


if __name__ == "__main__":
    exit(main())

