import asyncio
import time
import sys
import os

# Add the parent directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.agent.workflow import indian_ocean_argo_agent

async def performance_benchmark():
    print("⚡ PERFORMANCE BENCHMARK")
    print("=" * 30)
    
    # Single query performance
    start_time = time.time()
    result = await indian_ocean_argo_agent.process_query("Arabian Sea temperature")
    single_query_time = time.time() - start_time
    
    print(f"Single Query Time: {single_query_time:.2f}s")
    
    # Concurrent query performance  
    queries = ["Arabian Sea temperature"] * 3
    
    start_time = time.time()
    tasks = [indian_ocean_argo_agent.process_query(q) for q in queries]
    results = await asyncio.gather(*tasks)
    concurrent_time = time.time() - start_time
    
    print(f"3 Concurrent Queries: {concurrent_time:.2f}s")
    print(f"Average per query: {concurrent_time/3:.2f}s")
    
    # Validate all succeeded
    successful = sum(1 for r in results if "response" in r)
    print(f"Success rate: {successful}/{len(queries)} ({successful/len(queries)*100:.1f}%)")
    
    print("\n🎯 Performance Test Complete!")

if __name__ == "__main__":
    asyncio.run(performance_benchmark())
