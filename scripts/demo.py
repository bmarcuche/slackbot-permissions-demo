#!/usr/bin/env python3
"""
Demo Script for Slackbot Permissions Menu System.

Shows how the interactive menu system works with different user permissions.
"""

import json
from typing import Dict, Any

# Mock the slackbot-permissions module for demo purposes
class MockPermissionManager:
    def __init__(self):
        self.permissions = {
            "U123456": ["read_status", "deployment", "admin", "manage_permissions"],  # Admin user
            "U789012": ["read_status", "deployment", "read_logs"],                    # Developer
            "U345678": ["read_status"],                                               # Basic user
            "U999999": []                                                             # No permissions
        }
    
    def check_permission(self, user_id: str, permission: str) -> bool:
        return permission in self.permissions.get(user_id, [])

class MockCommandRegistry:
    def __init__(self):
        self.commands = [
            {"name": "status", "permission": "read_status", "description": "Check system status", "category": "Monitoring"},
            {"name": "health", "permission": "read_status", "description": "Detailed health check", "category": "Monitoring"},
            {"name": "deploy", "permission": "deployment", "description": "Deploy application", "category": "Development"},
            {"name": "build", "permission": "deployment", "description": "Build application", "category": "Development"},
            {"name": "logs", "permission": "read_logs", "description": "View application logs", "category": "Development"},
            {"name": "admin", "permission": "admin", "description": "Admin control panel", "category": "Administration"},
            {"name": "permissions", "permission": "manage_permissions", "description": "Manage permissions", "category": "Administration"},
            {"name": "users", "permission": "admin", "description": "Manage users", "category": "Administration"},
        ]
    
    def get_available_commands(self, user_id: str):
        permission_manager = MockPermissionManager()
        available = []
        for cmd in self.commands:
            if permission_manager.check_permission(user_id, cmd["permission"]):
                available.append(cmd)
        return available

class MockMenuBuilder:
    def __init__(self):
        self.command_registry = MockCommandRegistry()
        self.permission_manager = MockPermissionManager()
    
    def build_menu(self, user_id: str) -> Dict[str, Any]:
        available_commands = self.command_registry.get_available_commands(user_id)
        
        if not available_commands:
            return {
                "type": "no_commands",
                "message": "🔒 No Commands Available - Contact admin for permissions"
            }
        
        # Group by category
        categories = {}
        for cmd in available_commands:
            category = cmd["category"]
            if category not in categories:
                categories[category] = []
            categories[category].append(cmd)
        
        return {
            "type": "menu",
            "total_commands": len(available_commands),
            "categories": categories
        }

def demo_user_menu(user_id: str, username: str, role: str):
    """Demo menu for a specific user."""
    print(f"\n{'='*60}")
    print(f"🤖 SLACKBOT MENU DEMO - {username.upper()} ({role})")
    print(f"{'='*60}")
    
    menu_builder = MockMenuBuilder()
    menu_data = menu_builder.build_menu(user_id)
    
    if menu_data["type"] == "no_commands":
        print(f"\n{menu_data['message']}")
        return
    
    print(f"\n📋 Available Commands ({menu_data['total_commands']} total)")
    print("─" * 40)
    
    for category, commands in menu_data["categories"].items():
        emoji_map = {
            "Monitoring": "📊",
            "Development": "🚀", 
            "Administration": "⚙️"
        }
        emoji = emoji_map.get(category, "📋")
        
        print(f"\n{emoji} {category}")
        print("─" * 20)
        
        for cmd in commands:
            cmd_emoji_map = {
                "status": "📊", "health": "💚", "deploy": "🚀", "build": "🔨",
                "logs": "📝", "admin": "⚙️", "permissions": "🔐", "users": "👥"
            }
            cmd_emoji = cmd_emoji_map.get(cmd["name"], "🔹")
            
            print(f"  {cmd_emoji} /{cmd['name']} - {cmd['description']}")

def main():
    """Run the demo."""
    print("🎯 SLACKBOT PERMISSIONS DEMO")
    print("Showcasing dynamic menu system based on user permissions")
    
    # Demo different user types
    users = [
        ("U123456", "admin.user", "Administrator"),
        ("U789012", "dev.user", "Developer"), 
        ("U345678", "basic.user", "Basic User"),
        ("U999999", "new.user", "New User (No Permissions)")
    ]
    
    for user_id, username, role in users:
        demo_user_menu(user_id, username, role)
    
    print(f"\n{'='*60}")
    print("🎉 DEMO COMPLETE")
    print("This shows how the slackbot-permissions module creates")
    print("dynamic menus based on each user's specific permissions!")
    print(f"{'='*60}\n")
    
    print("🚀 To run the actual bot:")
    print("1. Set up your Slack app credentials in .env")
    print("2. Run: python src/slackbot_demo/main.py")
    print("3. Use /menu command in Slack to see your personalized menu")

if __name__ == "__main__":
    main()
