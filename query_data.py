import argparse
from langchain_chroma import Chroma
from langchain.prompts import ChatPromptTemplate
from langchain_ollama import OllamaLLM
from get_embedding_function import get_embedding_function

CHROMA_PATH = "chroma"

PROMPT_TEMPLATE = """
You are a knowledgeable and friendly Computer Science college advisor at California State University, Fullerton. 
Answer the student's question in a clear, concise, and helpful way, using the provided context.

Context:
{context}

---

Student's Question: {question}

Advisor's Answer:
"""

PROMPT_TEMPLATE_2 = """
Answer the question based only on the following context:

{context}

---

Answer the question based on the above context: {question}
"""


def main():
    # Create CLI.
    # parser = argparse.ArgumentParser()

    history = ""

    ''' QUERYING THE TEXT '''

    response = None
    print("Hello, I'm a Chatbot from California State University, Fullerton! Ask me any questions! Type 'quit' to leave the interactive session.")
    while response != 'quit':
        input_query = input("")
        response = query_rag(input_query)
        # print(response)
        # history = history + " " + response

    # query_rag("What classes are available?")
    # query_rag("Does the computer science department offer any cybersecurity related classes?")
    # query_rag("Where can I go for undergraduate advising?")
    # query_rag("I'm thinking about applying for my master's, what graduate classes are offered at CSUF?")

    # parser.add_argument("query_text", type=str, help="The query text.")
    # args = parser.parse_args()
    # query_text = args.query_text
    # query_rag(query_text)


def query_rag(query_text: str) -> str:
    # Prepare the Chroma database with the embedding function
    embedding_function = get_embedding_function()
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)  

    # Search the database for the most relevant documents
    results = db.similarity_search_with_score(query_text, k=5)
    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])

    # Prepare the prompt
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query_text)

    # Initialize the model with JSON output format
    model = OllamaLLM(model="llama3.1", output_format="json")  # Explicitly set output_format to JSON
    # Get the model's response
    try:
        response_text = model.invoke(prompt)
    except Exception as e:
        response_text = f"Error occurred: {str(e)}"

    # Extract sources for reference
    sources = [doc.metadata.get("id", "unknown") for doc, _score in results]

    # Debug: Log the raw response
    print(f"Raw response: {response_text}")

    print("-")
    print("---")
    print("-")

    return response_text    

if __name__ == "__main__":
    
    # main()
    
    model = OllamaLLM(model="llama3.2", output_format="json")

    # Prepare your prompt string
    prompt_string = "What is the capital of California?"

    # Make the call
    response = model.invoke(prompt_string)
    print(response)
