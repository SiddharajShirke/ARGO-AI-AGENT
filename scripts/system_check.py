import asyncio
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.database import db
from app.core.vector_db import vector_db
from app.agent.workflow import indian_ocean_argo_agent

async def full_system_check():
    print("🔍 COMPREHENSIVE SYSTEM CHECK")
    print("=" * 50)
    
    # Database connectivity
    try:
        db_health = db.health_check()
        print(f"✅ Database: {db_health.get('database_connected', False)}")
    except Exception as e:
        print(f"❌ Database Error: {e}")
    
    # Vector database connectivity  
    try:
        vector_health = vector_db.health_check()
        print(f"✅ Vector DB: {vector_health.get('vector_db_connected', False)}")
    except Exception as e:
        print(f"❌ Vector DB Error: {e}")
    
    # AI Agent test
    try:
        result = await indian_ocean_argo_agent.process_query("Test Arabian Sea query")
        print(f"✅ AI Agent: Working (response length: {len(result.get('response', ''))})")
    except Exception as e:
        print(f"❌ AI Agent Error: {e}")
    
    print("\n🎯 System Check Complete!")

if __name__ == "__main__":
    asyncio.run(full_system_check())
