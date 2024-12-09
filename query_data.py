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

<<<<<<< HEAD

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


def query_rag(query_text: str):
    # Prepare the DB.
    embedding_function = get_embedding_function()
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)

    # Search the DB.
    results = db.similarity_search_with_score(query_text, k=5)
    # print(results)
    # print("Database searched.")

    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query_text)
    # print("Student: ", prompt)

    model = OllamaLLM(model="llama3.2")
    response_text = model.invoke(prompt)

    sources = [doc.metadata.get("id", None) for doc, _score in results]

    formatted_response = f"Response: {response_text}\nSources: {sources}"
    print(formatted_response)
=======
def main():
    history = ""  # Initialize conversation history.

    print("Hello, I'm a Chatbot from California State University, Fullerton! Ask me any questions! Type 'quit' to leave the interactive session.")
    while True:
        input_query = input(">>> ")
        print("")
        if input_query.lower() == 'quit':
            break  # Exit the loop if the user types 'quit'.

        # Pass the history to the query function and get the response.
        response = query_rag(input_query, history)
        print(response)
        
        # Append the current query and response to the history.
        history += f"Student's Question: {input_query}\nAdvisor's Answer: {response}\n\n"

        # Optionally truncate history to avoid exceeding token limits.
        max_history_length = 5000  # Adjust based on model token limits.
        if len(history) > max_history_length:
            history = history[-max_history_length:]

        print("")  # Add an empty line for better readability.


def query_rag(query_text: str, history: str) -> str:
    # Prepare the Chroma database with the embedding function.
    embedding_function = get_embedding_function()
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)  

    # Search the database for the most relevant documents.
    results = db.similarity_search_with_score(query_text, k=3)
    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])

    # Combine history with the current context.
    full_prompt = f"""
Previous Conversation:
{history}

Current Context:
{context_text}

---

Student's Question: {query_text}

Advisor's Answer:
"""

    # Initialize the model.
    model = OllamaLLM(model="llama3")  # Explicitly set output_format to JSON.
    response_text = model.invoke(full_prompt)

>>>>>>> origin/newBranch
    return response_text


if __name__ == "__main__":
<<<<<<< HEAD
    main()
=======

    '''
    Questions to ask:

        What classes are available?
        Does the computer science department offer any cybersecurity related classes?
        Where can I go for undergraduate advising?
        I'm thinking about applying for my master's, what graduate classes are offered at CSUF?
    '''
    main()
>>>>>>> origin/newBranch
