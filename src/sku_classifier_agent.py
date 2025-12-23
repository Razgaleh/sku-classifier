import os
import subprocess
import pandas as pd
from typing import Annotated

from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage
from IPython.display import Image, display
from langchain_community.tools import BraveSearch
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import InMemorySaver
from langchain_nvidia_ai_endpoints import ChatNVIDIA


os.environ["NVIDIA_API_KEY"] = os.getenv("NVIDIA_API_KEY")    
os.environ["LANGSMITH_API_KEY"]= os.getenv("LANGSMITH_API_KEY")
os.environ["LANGSMITH_ENDPOINT"]="https://api.smith.langchain.com"
os.environ["LANGSMITH_TRACING"]="true"
os.environ["LANGCHAIN_PROJECT"]="sku-classifier" # Optional: Organize traces in specific projects

os.environ["BRAVE_SEARCH_API_KEY"]= os.getenv("BRAVE_SEARCH_API_KEY")


class State(TypedDict):
    # Messages have the type "list". The `add_messages` function
    # in the annotation defines how this state key should be updated
    # (in this case, it appends messages to the list, rather than overwriting them)
    messages: Annotated[list, add_messages]


graph_builder = StateGraph(State)

# Connect to local NVIDIA NIM instance
# Set base_url to your NIM endpoint (default: http://localhost:8000/v1)
# For hosted NIMs, remove base_url to use NVIDIA's cloud API
llm = ChatNVIDIA(
    base_url="http://localhost:8000/v1", 
    model="meta-llama/llama-3.1-8b-instruct"  # Model name from NIM (use meta-llama with dash)
)

tool = BraveSearch.from_search_kwargs(search_kwargs={"count": 3})
tools = [tool]
llm_with_tools = llm.bind_tools(tools)


def chatbot(state:State):
  return {"messages": [llm_with_tools.invoke(state["messages"])]}

def classify_part(part_number: str, part_seg: str, part_description: str) -> str:
    """
    Classify a part as hardware or software using the LLM with web search capabilities.
    """
    classification_prompt = f"""
    You are a technical product classifier. Your task is to determine if a product is HARDWARE or SOFTWARE based on the provided information.

    Product Information:
    - Part Number: {part_number}
    - Part Segment: {part_seg}
    - Part Description: {part_description}

    Classification Rules:
    - HARDWARE: Physical devices, appliances, equipment, hardware components, physical security appliances, network devices, servers, storage devices, physical appliances
    - SOFTWARE: Software licenses, software subscriptions, digital products, virtual appliances, software-only solutions, cloud services, digital downloads

    If you need more information to make a decision, use the web search tool to look up the specific product.

    Respond with ONLY one word: either "HARDWARE" or "SOFTWARE"
    """
    
    config = {"configurable": {"thread_id": f"classify_{part_number}"}}
    
    # Create a temporary state for this classification
    temp_state = {"messages": [HumanMessage(content=classification_prompt)]}
    
    # Use invoke instead of stream to get final result without generator issues
    try:
        final_state = graph.invoke(temp_state, config=config)
        if "messages" in final_state and final_state["messages"]:
            last_message = final_state["messages"][-1]
            if hasattr(last_message, 'content') and last_message.content:
                response = last_message.content.strip().upper()
                if "HARDWARE" in response:
                    return "HARDWARE"
                elif "SOFTWARE" in response:
                    return "SOFTWARE"
    except Exception as e:
        print(f"Warning: Error during classification: {e}")
    
    # Fallback classification based on keywords
    description_lower = part_description.lower()
    if any(keyword in description_lower for keyword in ['software', 'license', 'subscription', 'virtual', 'cloud', 'digital']):
        return "SOFTWARE"
    else:
        return "HARDWARE"

graph_builder.add_node("chatbot", chatbot)


tool_node = ToolNode(tools=[tool])
graph_builder.add_node("tools", tool_node)

graph_builder.add_conditional_edges(
    "chatbot",
    tools_condition,
)


graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("tools", "chatbot")

memory = InMemorySaver()
graph = graph_builder.compile(checkpointer=memory)


# Save the graph as PNG and open it
try:
    png_data = graph.get_graph().draw_mermaid_png()
    with open("../data/graph_diagram.png", "wb") as f:
        f.write(png_data)
    print("Graph diagram saved as '../data/graph_diagram.png'")
    
except Exception as e:
    print(f"Could not generate graph diagram: {e}")
    
def process_csv_classification(csv_file_path: str, output_file_path: str = None, max_rows: int = None):
    """
    Process the CSV file and classify parts as hardware or software.
    """
    if output_file_path is None:
        output_file_path = csv_file_path.replace('.csv', '_classified.csv')
    
    print(f"Loading CSV file: {csv_file_path}")
    df = pd.read_csv(csv_file_path)
    
    if max_rows:
        df = df.head(max_rows)
        print(f"Processing first {max_rows} rows for testing...")
    
    # Initialize PART_CATEGORY column as string type to avoid dtype warnings
    df['PART_CATEGORY'] = pd.Series(dtype='string')
    
    print(f"Total rows to process: {len(df)}")
    
    # Process each row
    for index, row in df.iterrows():
        part_number = str(row['PART_NUMBER'])
        part_seg = str(row['PART_SEG'])
        part_description = str(row['PART_DESCRIPTION'])
        
        print(f"\nProcessing row {index + 1}/{len(df)}: {part_number}")
        
        try:
            # Classify the part
            classification = classify_part(part_number, part_seg, part_description)
            df.at[index, 'PART_CATEGORY'] = classification
            print(f"Classified as: {classification}")
            
        except Exception as e:
            print(f"Error classifying {part_number}: {e}")
            # Fallback to hardware if classification fails
            df.at[index, 'PART_CATEGORY'] = "HARDWARE"
    
    # Save the updated CSV
    df.to_csv(output_file_path, index=False)
    print(f"\nClassification complete! Results saved to: {output_file_path}")
    
    # Print summary
    category_counts = df['PART_CATEGORY'].value_counts()
    print(f"\nClassification Summary:")
    for category, count in category_counts.items():
        print(f"  {category}: {count} parts")
    
    return df


def main():
    print("SKU Classifier Agent")
    print("===================")
    print("1. Test classification on sample data")
    print("2. Process CSV file for classification")
    
    choice = input("\nEnter your choice (1-2): ").strip()
    
    if choice == "1":
        # Test on sample data
        csv_path = input("Enter CSV file path (default: ../data/dataset.csv): ").strip()
        if not csv_path:
            csv_path = "../data/dataset.csv"
        
        max_rows_input = input("How many rows do you want to process? (Enter a number): ").strip()
        max_rows = int(max_rows_input) if max_rows_input.isdigit() else 200
        
        if not max_rows_input.isdigit():
            print(f"No number provided, defaulting to {max_rows} rows...")
        else:
            print(f"Testing classification on {max_rows} rows...")
        
        process_csv_classification(csv_path, max_rows=max_rows)
        
    elif choice == "2":
        # Process full CSV file
        csv_path = input("Enter CSV file path (default: ../data/dataset.csv): ").strip()
        if not csv_path:
            csv_path = "../data/dataset.csv"
        
        print("Processing all rows in the CSV file...")
        process_csv_classification(csv_path, max_rows=None)
        
    else:
        print("Invalid choice. Exiting...")

if __name__ == "__main__":
    main()