"""
Microsoft Graph API client wrapper adapted for Elasticsearch
"""
from msgraph import GraphServiceClient
from azure.identity import DeviceCodeCredential, ClientSecretCredential, InteractiveBrowserCredential
from config_elasticsearch import Config
import logging

logger = logging.getLogger(__name__)

class GraphClientWrapper:
    """Wrapper for Microsoft Graph API client"""

    def __init__(self):
        self.client = None
        self._authenticate()

    def _authenticate(self):
        """Authenticate with Microsoft Graph API"""
        logger.info("Authenticating with Microsoft Graph API...")

        # Try different authentication methods in order
        credential = None

        # 1. Try Client Secret (best for automation)
        if Config.AZURE_CLIENT_SECRET:
            try:
                logger.info("Trying ClientSecretCredential...")
                credential = ClientSecretCredential(
                    tenant_id=Config.AZURE_TENANT_ID,
                    client_id=Config.AZURE_CLIENT_ID,
                    client_secret=Config.AZURE_CLIENT_SECRET
                )
                # Test the credential
                self.client = GraphServiceClient(credential, Config.GRAPH_SCOPES)
                # Try a simple API call to validate
                self.client.me.get()
                logger.info("✅ Authenticated with Client Secret")
                return
            except Exception as e:
                logger.warning(f"Client Secret auth failed: {e}")
                credential = None

        # 2. Try Device Code (interactive but easy)
        try:
            logger.info("Trying DeviceCodeCredential...")
            credential = DeviceCodeCredential(
                tenant_id=Config.AZURE_TENANT_ID,
                client_id=Config.AZURE_CLIENT_ID
            )
            self.client = GraphServiceClient(credential, Config.GRAPH_SCOPES)
            logger.info("✅ Authenticated with Device Code")
            return
        except Exception as e:
            logger.warning(f"Device Code auth failed: {e}")

        # 3. Fall back to Interactive Browser
        try:
            logger.info("Trying InteractiveBrowserCredential...")
            credential = InteractiveBrowserCredential(
                tenant_id=Config.AZURE_TENANT_ID,
                client_id=Config.AZURE_CLIENT_ID
            )
            self.client = GraphServiceClient(credential, Config.GRAPH_SCOPES)
            logger.info("✅ Authenticated with Interactive Browser")
            return
        except Exception as e:
            logger.error(f"Interactive Browser auth failed: {e}")
            raise Exception("All authentication methods failed")

    def get_sites(self):
        """Get all SharePoint sites"""
        try:
            return self.client.sites.get_all_sites().get()
        except Exception as e:
            logger.error(f"Error getting sites: {e}")
            return []

    def get_drives(self, site_id):
        """Get all drives (document libraries) for a site"""
        try:
            return self.client.sites.by_site_id(site_id).drives.get()
        except Exception as e:
            logger.error(f"Error getting drives for site {site_id}: {e}")
            return None

    def get_drive_items(self, site_id, drive_id, folder_id=None):
        """Get items in a drive or folder"""
        try:
            if folder_id:
                return self.client.sites.by_site_id(site_id)\
                    .drives.by_drive_id(drive_id)\
                    .items.by_drive_item_id(folder_id)\
                    .children.get()
            else:
                return self.client.sites.by_site_id(site_id)\
                    .drives.by_drive_id(drive_id)\
                    .root.children.get()
        except Exception as e:
            logger.error(f"Error getting drive items: {e}")
            return None

    def get_file_content(self, site_id, drive_id, item_id):
        """Download file content"""
        try:
            return self.client.sites.by_site_id(site_id)\
                .drives.by_drive_id(drive_id)\
                .items.by_drive_item_id(item_id)\
                .content.get()
        except Exception as e:
            logger.error(f"Error downloading file content: {e}")
            return None

    def get_users(self):
        """Get all users"""
        try:
            return self.client.users.get()
        except Exception as e:
            logger.error(f"Error getting users: {e}")
            return None

    def get_user_drive(self, user_id):
        """Get user's OneDrive"""
        try:
            return self.client.users.by_user_id(user_id).drive.get()
        except Exception as e:
            logger.error(f"Error getting drive for user {user_id}: {e}")
            return None

    def get_user_messages(self, user_id, filter_query=None):
        """Get user's emails"""
        try:
            if filter_query:
                return self.client.users.by_user_id(user_id)\
                    .messages.get(filter=filter_query)
            else:
                return self.client.users.by_user_id(user_id).messages.get()
        except Exception as e:
            logger.error(f"Error getting messages for user {user_id}: {e}")
            return None
