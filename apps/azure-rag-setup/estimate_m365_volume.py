#!/usr/bin/env python3
"""
Microsoft 365 Volume Estimator
Estimates document counts and storage requirements for M365 data sources
"""

import json
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from m365_auth import M365Auth

class M365VolumeEstimator:
    """Estimate M365 data volume for indexing planning"""

    def __init__(self):
        self.auth = M365Auth()
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'sharepoint': {},
            'onedrive': {},
            'exchange': {},
            'summary': {}
        }

    def estimate_sharepoint(self) -> Dict[str, Any]:
        """Estimate SharePoint sites and document counts"""
        print("📊 Estimating SharePoint volume...")

        headers = self.auth.get_graph_headers()
        if not headers:
            return {'error': 'Authentication failed'}

        try:
            # Get all SharePoint sites
            sites_response = requests.get(
                'https://graph.microsoft.com/v1.0/sites?search=*',
                headers=headers,
                timeout=30
            )

            if sites_response.status_code != 200:
                return {'error': f'Failed to get sites: {sites_response.status_code}'}

            sites_data = sites_response.json()
            sites = sites_data.get('value', [])

            total_documents = 0
            total_size_bytes = 0
            site_details = []

            for site in sites[:10]:  # Limit to first 10 sites for estimation
                site_id = site.get('id')
                site_name = site.get('displayName', 'Unknown')

                # Get document libraries for this site
                try:
                    drives_response = requests.get(
                        f'https://graph.microsoft.com/v1.0/sites/{site_id}/drives',
                        headers=headers,
                        timeout=30
                    )

                    if drives_response.status_code == 200:
                        drives_data = drives_response.json()
                        drives = drives_data.get('value', [])

                        site_docs = 0
                        site_size = 0

                        for drive in drives:
                            # Get drive info
                            drive_id = drive.get('id')
                            drive_name = drive.get('name', 'Unknown')

                            # Get root folder items count
                            try:
                                root_response = requests.get(
                                    f'https://graph.microsoft.com/v1.0/drives/{drive_id}/root/children',
                                    headers=headers,
                                    timeout=30
                                )

                                if root_response.status_code == 200:
                                    root_data = root_response.json()
                                    items = root_data.get('value', [])

                                    for item in items:
                                        if 'folder' in item:
                                            # It's a folder, estimate contents
                                            site_docs += 10  # Rough estimate
                                        elif 'file' in item:
                                            site_docs += 1
                                            site_size += item.get('size', 0)

                            except Exception as e:
                                print(f"⚠️  Error getting drive {drive_name}: {e}")

                        total_documents += site_docs
                        total_size_bytes += site_size

                        site_details.append({
                            'name': site_name,
                            'id': site_id,
                            'documents': site_docs,
                            'size_bytes': site_size
                        })

                except Exception as e:
                    print(f"⚠️  Error processing site {site_name}: {e}")

            return {
                'total_sites': len(sites),
                'estimated_documents': total_documents,
                'estimated_size_bytes': total_size_bytes,
                'site_details': site_details
            }

        except Exception as e:
            return {'error': f'SharePoint estimation failed: {e}'}

    def estimate_onedrive(self) -> Dict[str, Any]:
        """Estimate OneDrive for Business users and storage"""
        print("📊 Estimating OneDrive volume...")

        headers = self.auth.get_graph_headers()
        if not headers:
            return {'error': 'Authentication failed'}

        try:
            # Get all users in the organization
            users_response = requests.get(
                'https://graph.microsoft.com/v1.0/users?$select=id,displayName,userPrincipalName',
                headers=headers,
                timeout=30
            )

            if users_response.status_code != 200:
                return {'error': f'Failed to get users: {users_response.status_code}'}

            users_data = users_response.json()
            users = users_data.get('value', [])

            total_documents = 0
            total_size_bytes = 0
            user_details = []

            # Sample first 20 users for estimation
            for user in users[:20]:
                user_id = user.get('id')
                user_name = user.get('displayName', 'Unknown')

                try:
                    # Get user's OneDrive
                    onedrive_response = requests.get(
                        f'https://graph.microsoft.com/v1.0/users/{user_id}/drive',
                        headers=headers,
                        timeout=30
                    )

                    if onedrive_response.status_code == 200:
                        drive_data = onedrive_response.json()
                        drive_id = drive_data.get('id')

                        # Get drive usage
                        usage_response = requests.get(
                            f'https://graph.microsoft.com/v1.0/drives/{drive_id}',
                            headers=headers,
                            timeout=30
                        )

                        if usage_response.status_code == 200:
                            usage_data = usage_response.json()
                            quota = usage_data.get('quota', {})

                            used_bytes = quota.get('used', 0)
                            total_bytes = quota.get('total', 0)

                            # Estimate document count (rough: 1MB per document average)
                            estimated_docs = max(1, used_bytes // (1024 * 1024))

                            total_documents += estimated_docs
                            total_size_bytes += used_bytes

                            user_details.append({
                                'name': user_name,
                                'id': user_id,
                                'estimated_documents': estimated_docs,
                                'used_bytes': used_bytes,
                                'total_quota': total_bytes
                            })

                except Exception as e:
                    print(f"⚠️  Error processing user {user_name}: {e}")

            # Extrapolate for all users
            if users:
                extrapolation_factor = len(users) / min(20, len(users))
                total_documents = int(total_documents * extrapolation_factor)
                total_size_bytes = int(total_size_bytes * extrapolation_factor)

            return {
                'total_users': len(users),
                'estimated_documents': total_documents,
                'estimated_size_bytes': total_size_bytes,
                'user_details': user_details
            }

        except Exception as e:
            return {'error': f'OneDrive estimation failed: {e}'}

    def estimate_exchange(self) -> Dict[str, Any]:
        """Estimate Exchange Online mailboxes and storage"""
        print("📊 Estimating Exchange volume...")

        headers = self.auth.get_graph_headers()
        if not headers:
            return {'error': 'Authentication failed'}

        try:
            # Get all users (same as OneDrive)
            users_response = requests.get(
                'https://graph.microsoft.com/v1.0/users?$select=id,displayName,userPrincipalName',
                headers=headers,
                timeout=30
            )

            if users_response.status_code != 200:
                return {'error': f'Failed to get users: {users_response.status_code}'}

            users_data = users_response.json()
            users = users_data.get('value', [])

            total_emails = 0
            total_size_bytes = 0

            # Sample first 10 users for estimation
            for user in users[:10]:
                user_id = user.get('id')
                user_name = user.get('displayName', 'Unknown')

                try:
                    # Get mailbox info
                    mailbox_response = requests.get(
                        f'https://graph.microsoft.com/v1.0/users/{user_id}/mailFolders',
                        headers=headers,
                        timeout=30
                    )

                    if mailbox_response.status_code == 200:
                        folders_data = mailbox_response.json()
                        folders = folders_data.get('value', [])

                        user_emails = 0
                        user_size = 0

                        for folder in folders:
                            folder_id = folder.get('id')
                            folder_name = folder.get('displayName', 'Unknown')

                            # Get folder message count
                            try:
                                messages_response = requests.get(
                                    f'https://graph.microsoft.com/v1.0/users/{user_id}/mailFolders/{folder_id}/messages?$count=true&$top=1',
                                    headers=headers,
                                    timeout=30
                                )

                                if messages_response.status_code == 200:
                                    messages_data = messages_response.json()
                                    count = messages_data.get('@odata.count', 0)
                                    user_emails += count

                                    # Estimate size (rough: 50KB per email average)
                                    user_size += count * 50 * 1024

                            except Exception as e:
                                print(f"⚠️  Error getting folder {folder_name}: {e}")

                        total_emails += user_emails
                        total_size_bytes += user_size

                except Exception as e:
                    print(f"⚠️  Error processing user {user_name}: {e}")

            # Extrapolate for all users
            if users:
                extrapolation_factor = len(users) / min(10, len(users))
                total_emails = int(total_emails * extrapolation_factor)
                total_size_bytes = int(total_size_bytes * extrapolation_factor)

            return {
                'total_users': len(users),
                'estimated_emails': total_emails,
                'estimated_size_bytes': total_size_bytes
            }

        except Exception as e:
            return {'error': f'Exchange estimation failed: {e}'}

    def generate_summary(self) -> Dict[str, Any]:
        """Generate summary with Azure AI Search tier recommendations"""
        sharepoint = self.results.get('sharepoint', {})
        onedrive = self.results.get('onedrive', {})
        exchange = self.results.get('exchange', {})

        total_documents = (
            sharepoint.get('estimated_documents', 0) +
            onedrive.get('estimated_documents', 0) +
            exchange.get('estimated_emails', 0)
        )

        total_size_gb = (
            sharepoint.get('estimated_size_bytes', 0) +
            onedrive.get('estimated_size_bytes', 0) +
            exchange.get('estimated_size_bytes', 0)
        ) / (1024 ** 3)

        # Azure AI Search tier recommendations
        if total_documents <= 10000 and total_size_gb <= 0.05:
            recommended_tier = "Free"
            monthly_cost = 0
        elif total_documents <= 100000 and total_size_gb <= 1:
            recommended_tier = "Basic"
            monthly_cost = 75
        elif total_documents <= 1000000 and total_size_gb <= 10:
            recommended_tier = "Standard S1"
            monthly_cost = 250
        else:
            recommended_tier = "Standard S2"
            monthly_cost = 500

        return {
            'total_documents': total_documents,
            'total_size_gb': round(total_size_gb, 2),
            'recommended_tier': recommended_tier,
            'estimated_monthly_cost': monthly_cost,
            'free_tier_sufficient': recommended_tier == "Free"
        }

    def run_estimation(self) -> Dict[str, Any]:
        """Run complete volume estimation"""
        print("🔍 Starting Microsoft 365 Volume Estimation...")
        print("=" * 60)

        if not self.auth.test_connection():
            print("❌ Authentication failed. Check your credentials.")
            return self.results

        # Estimate each service
        self.results['sharepoint'] = self.estimate_sharepoint()
        self.results['onedrive'] = self.estimate_onedrive()
        self.results['exchange'] = self.estimate_exchange()

        # Generate summary
        self.results['summary'] = self.generate_summary()

        return self.results

    def save_report(self, filename: str = None) -> str:
        """Save estimation report to file"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"m365_volume_estimate_{timestamp}.json"

        filepath = Path(filename)
        with open(filepath, 'w') as f:
            json.dump(self.results, f, indent=2)

        return str(filepath)

    def print_summary(self):
        """Print human-readable summary"""
        summary = self.results.get('summary', {})
        sharepoint = self.results.get('sharepoint', {})
        onedrive = self.results.get('onedrive', {})
        exchange = self.results.get('exchange', {})

        print("\n" + "=" * 60)
        print("📊 MICROSOFT 365 VOLUME ESTIMATION SUMMARY")
        print("=" * 60)

        print(f"\n📁 SharePoint:")
        print(f"   Sites: {sharepoint.get('total_sites', 0)}")
        print(f"   Documents: {sharepoint.get('estimated_documents', 0):,}")
        print(f"   Size: {sharepoint.get('estimated_size_bytes', 0) / (1024**3):.2f} GB")

        print(f"\n👥 OneDrive (All Users):")
        print(f"   Users: {onedrive.get('total_users', 0)}")
        print(f"   Documents: {onedrive.get('estimated_documents', 0):,}")
        print(f"   Size: {onedrive.get('estimated_size_bytes', 0) / (1024**3):.2f} GB")

        print(f"\n📧 Exchange (All Users):")
        print(f"   Users: {exchange.get('total_users', 0)}")
        print(f"   Emails: {exchange.get('estimated_emails', 0):,}")
        print(f"   Size: {exchange.get('estimated_size_bytes', 0) / (1024**3):.2f} GB")

        print(f"\n🎯 TOTAL ESTIMATION:")
        print(f"   Total Documents: {summary.get('total_documents', 0):,}")
        print(f"   Total Size: {summary.get('total_size_gb', 0):.2f} GB")

        print(f"\n💰 AZURE AI SEARCH RECOMMENDATION:")
        print(f"   Recommended Tier: {summary.get('recommended_tier', 'Unknown')}")
        print(f"   Estimated Monthly Cost: ${summary.get('estimated_monthly_cost', 0)}")

        if summary.get('free_tier_sufficient'):
            print("   ✅ Free tier should be sufficient!")
        else:
            print("   ⚠️  Paid tier required for full indexing")

def main():
    """Run volume estimation"""
    estimator = M365VolumeEstimator()

    try:
        results = estimator.run_estimation()

        # Print summary
        estimator.print_summary()

        # Save report
        report_file = estimator.save_report()
        print(f"\n📄 Detailed report saved to: {report_file}")

        return 0

    except Exception as e:
        print(f"❌ Estimation failed: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
