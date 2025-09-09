import asyncio
import sys
import os

# Add the parent directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.agent.workflow import indian_ocean_argo_agent

async def integration_test():
    print("🔄 END-TO-END INTEGRATION TEST")
    print("=" * 40)
    
    test_queries = [
        "Arabian Sea temperature trends",
        "Bay of Bengal salinity analysis",  
        "Indian Ocean monsoon patterns"
    ]
    
    for i, query in enumerate(test_queries, 1):
        try:
            print(f"\n{i}. Testing: {query}")
            result = await indian_ocean_argo_agent.process_query(query)
            
            profiles_found = result["data_summary"]["profiles_found"]
            processing_time = result["metadata"]["processing_time_seconds"]
            
            print(f"   ✅ Profiles found: {profiles_found}")
            print(f"   ⚡ Processing time: {processing_time}s")
            print(f"   📝 Response length: {len(result['response'])} chars")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n🎯 Integration Test Complete!")

if __name__ == "__main__":
    asyncio.run(integration_test())
