#!/usr/bin/env python3
"""Update m365_indexer.py to include Teams, Calendar, and Contacts"""

import os

# Read current m365_indexer.py
with open('m365_indexer.py', 'r') as f:
    content = f.read()

# Add imports for new indexers
new_imports = """from m365_teams_indexer import TeamsIndexer
from m365_calendar_indexer import CalendarIndexer
from m365_contacts_indexer import ContactsIndexer
"""

# Find where to insert imports (after existing imports)
import_pos = content.find("from m365_exchange_indexer import ExchangeIndexer")
if import_pos != -1:
    # Find end of line
    end_of_line = content.find('\n', import_pos)
    content = content[:end_of_line+1] + new_imports + content[end_of_line+1:]

# Add Teams sync command
teams_cmd = '''
    def cmd_sync_teams(self, args):
        """Sync Teams messages and channels"""
        indexer = TeamsIndexer()
        
        print("🔄 Syncing Microsoft Teams...")
        result = indexer.index_all_teams(message_limit=args.message_limit if hasattr(args, 'message_limit') else 50)
        
        if result.get('success'):
            print(f"✅ Teams sync complete!")
            print(f"   Teams: {result['teams_processed']}")
            print(f"   Channels: {result['channels_processed']}")
            print(f"   Messages: {result['messages_processed']}")
        else:
            print(f"❌ Teams sync failed: {result.get('error', 'Unknown error')}")
'''

# Add Calendar sync command
calendar_cmd = '''
    def cmd_sync_calendar(self, args):
        """Sync Calendar events"""
        indexer = CalendarIndexer()
        
        print("🔄 Syncing Calendar events...")
        result = indexer.index_all_users(
            days_back=args.days_back if hasattr(args, 'days_back') else 90,
            limit=args.limit if hasattr(args, 'limit') else None
        )
        
        if result.get('success'):
            print(f"✅ Calendar sync complete!")
            print(f"   Users: {result['users_processed']}")
            print(f"   Events: {result['events_processed']}")
        else:
            print(f"❌ Calendar sync failed: {result.get('error', 'Unknown error')}")
'''

# Add Contacts sync command
contacts_cmd = '''
    def cmd_sync_contacts(self, args):
        """Sync Outlook contacts"""
        indexer = ContactsIndexer()
        
        print("🔄 Syncing Outlook contacts...")
        result = indexer.index_all_users(limit=args.limit if hasattr(args, 'limit') else None)
        
        if result.get('success'):
            print(f"✅ Contacts sync complete!")
            print(f"   Users: {result['users_processed']}")
            print(f"   Contacts: {result['contacts_processed']}")
        else:
            print(f"❌ Contacts sync failed: {result.get('error', 'Unknown error')}")
'''

# Find where to insert commands (before if __name__ == "__main__")
main_pos = content.find('if __name__ == "__main__":')
if main_pos != -1:
    content = content[:main_pos] + teams_cmd + '\n' + calendar_cmd + '\n' + contacts_cmd + '\n\n' + content[main_pos:]

# Update cmd_sync to include Teams, Calendar, Contacts
sync_update = '''
        # Sync Teams
        print("\\n📱 Syncing Teams...")
        teams_indexer = TeamsIndexer()
        teams_result = teams_indexer.index_all_teams(message_limit=50)
        print(f"   Teams: {teams_result.get('teams_processed', 0)}")
        print(f"   Messages: {teams_result.get('messages_processed', 0)}")
        
        # Sync Calendar
        print("\\n📅 Syncing Calendar...")
        calendar_indexer = CalendarIndexer()
        calendar_result = calendar_indexer.index_all_users(days_back=90)
        print(f"   Users: {calendar_result.get('users_processed', 0)}")
        print(f"   Events: {calendar_result.get('events_processed', 0)}")
        
        # Sync Contacts
        print("\\n👥 Syncing Contacts...")
        contacts_indexer = ContactsIndexer()
        contacts_result = contacts_indexer.index_all_users()
        print(f"   Users: {contacts_result.get('users_processed', 0)}")
        print(f"   Contacts: {contacts_result.get('contacts_processed', 0)}")
'''

# Find cmd_sync method and add new syncs
cmd_sync_pos = content.find('def cmd_sync(self, args):')
if cmd_sync_pos != -1:
    # Find the end of Exchange sync
    exchange_sync_pos = content.find('exchange_result = exchange_indexer.index_all_users', cmd_sync_pos)
    if exchange_sync_pos != -1:
        # Find next print statement after exchange
        next_print = content.find('print(', exchange_sync_pos)
        if next_print != -1:
            # Find end of that line
            end_of_line = content.find('\n', next_print)
            # Find the next empty line or method
            insert_pos = end_of_line + 1
            content = content[:insert_pos] + sync_update + content[insert_pos:]

# Update cmd_status to include Teams, Calendar, Contacts
status_update = '''
        # Teams status
        try:
            teams_indexer = TeamsIndexer()
            teams_status = teams_indexer.get_status()
            status['teams'] = {
                'last_sync': teams_status.get('last_sync'),
                'teams_processed': teams_status.get('teams_processed', 0),
                'total_messages': teams_status.get('total_messages', 0)
            }
        except Exception as e:
            status['teams'] = {'error': str(e)}
        
        # Calendar status
        try:
            calendar_indexer = CalendarIndexer()
            calendar_status = calendar_indexer.get_status()
            status['calendar'] = {
                'last_sync': calendar_status.get('last_sync'),
                'users_processed': calendar_status.get('users_processed', 0),
                'total_events': calendar_status.get('total_events', 0)
            }
        except Exception as e:
            status['calendar'] = {'error': str(e)}
        
        # Contacts status
        try:
            contacts_indexer = ContactsIndexer()
            contacts_status = contacts_indexer.get_status()
            status['contacts'] = {
                'last_sync': contacts_status.get('last_sync'),
                'users_processed': contacts_status.get('users_processed', 0),
                'total_contacts': contacts_status.get('total_contacts', 0)
            }
        except Exception as e:
            status['contacts'] = {'error': str(e)}
'''

# Find cmd_status and add new status checks
cmd_status_pos = content.find('def cmd_status(self):')
if cmd_status_pos != -1:
    # Find return statement
    return_pos = content.find('return status', cmd_status_pos)
    if return_pos != -1:
        # Insert before return
        content = content[:return_pos] + status_update + '\n        ' + content[return_pos:]

# Write updated file
with open('m365_indexer.py', 'w') as f:
    f.write(content)

print("✅ Updated m365_indexer.py with Teams, Calendar, and Contacts support")
